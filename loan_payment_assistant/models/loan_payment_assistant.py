# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class LoanPaymentAssistant(models.Model):
    _name = 'loan.payment.assistant'
    _inherit = 'assistant.journal.entry.base'
    _description = 'Asistente de Pago de Préstamos'

    READONLY_STATES = {
        'to_approve': [('readonly', True)], 
        'approved': [('readonly', True)], 
        'posted': [('readonly', True)], 
        'cancelled': [('readonly', True)]
    }

    loan_id = fields.Many2one(
        'loan.loan', 
        string='Préstamo a Pagar', 
        required=True,
        states=READONLY_STATES,
        domain="[('state', '=', 'active'), ('company_id', '=', company_id)]"
    )

    currency_id = fields.Many2one(
        'res.currency', 
        string='Moneda del Pago', 
        required=True,
        default=lambda self: self.env.company.currency_id,
        states=READONLY_STATES,
        tracking=True
    )

    principal_amount = fields.Monetary(
        string='Monto de Capital', 
        currency_field='currency_id',
        required=True, 
        states=READONLY_STATES,
        tracking=True,
        help="Monto a pagar en la moneda seleccionada arriba."
    )
    interest_amount = fields.Monetary(
        string='Monto de Intereses', 
        currency_field='currency_id',
        required=True, 
        states=READONLY_STATES,
        tracking=True
    )

    payment_journal_id = fields.Many2one(
        'account.journal', 
        string='Pagado desde (Diario)', 
        required=True, 
        states=READONLY_STATES,
        domain="[('type', 'in', ('bank', 'cash')), ('company_id', '=', company_id)]"
    )
    
    amount = fields.Monetary(
        string='Monto Total Pagado', 
        compute='_compute_amount', 
        currency_field='currency_id',
        store=True, 
        readonly=True
    )

    @api.onchange('loan_id')
    def _onchange_loan_id(self):
        if self.loan_id and self.loan_id.currency_id:
            self.currency_id = self.loan_id.currency_id

    @api.onchange('payment_journal_id')
    def _onchange_payment_journal_id(self):
        """Si el usuario elige un banco en GTQ, sugerimos pagar en GTQ aunque el préstamo sea USD.
           Pero el usuario es libre de cambiarlo de nuevo si desea especificar el monto en USD."""
        if self.payment_journal_id and self.payment_journal_id.currency_id:
            self.currency_id = self.payment_journal_id.currency_id

    @api.depends('principal_amount', 'interest_amount')
    def _compute_amount(self):
        for rec in self:
            rec.amount = rec.principal_amount + rec.interest_amount

    def _get_amount_in_loan_currency(self, amount_transaction):
        """Helper para convertir monto de transacción -> monto deuda (Loan Currency)"""
        self.ensure_one()
        loan_currency = self.loan_id.currency_id
        payment_currency = self.currency_id
        
        if loan_currency == payment_currency:
            return amount_transaction
        
        return payment_currency._convert(
            amount_transaction, 
            loan_currency, 
            self.company_id, 
            self.date or fields.Date.today()
        )

    @api.constrains('principal_amount', 'loan_id', 'currency_id')
    def _check_principal_amount(self):
        for rec in self:
            if rec.loan_id and rec.loan_id.state == 'active':
                principal_in_debt_curr = rec._get_amount_in_loan_currency(rec.principal_amount)
                if principal_in_debt_curr > (rec.loan_id.outstanding_balance + 0.05):
                     raise ValidationError(_(
                        "El monto de capital a pagar excede el saldo pendiente."
                    ))
    
    @api.constrains('date', 'loan_id')
    def _check_payment_date(self):
        for rec in self:
            if rec.loan_id and rec.loan_id.date_start and rec.date:
                if rec.date < rec.loan_id.date_start:
                    raise ValidationError(_("La fecha del pago no puede ser anterior a la del préstamo."))

    def action_post(self):
        res = super(LoanPaymentAssistant, self).action_post()
        rainbow_effect = False

        for rec in self:
            if rec.loan_id:
                principal_deducted = rec._get_amount_in_loan_currency(rec.principal_amount)
                new_balance = rec.loan_id.outstanding_balance - principal_deducted
                
                if new_balance <= 0.05:
                    new_balance = 0.0
                    rec.loan_id.write({'outstanding_balance': new_balance, 'state': 'paid'})
                    rainbow_effect = {
                        'effect': {
                            'fadeout': 'slow',
                            'message': '¡Préstamo Liquidado!',
                            'img_url': '/web/static/img/smile.svg',
                            'type': 'rainbow_man',
                        }
                    }
                else:
                    rec.loan_id.write({'outstanding_balance': new_balance})

        if rainbow_effect:
            return rainbow_effect
        return res

    def action_cancel(self):
        posted_records = self.filtered(lambda r: r.state == 'posted')
        res = super(LoanPaymentAssistant, self).action_cancel()
        
        for rec in posted_records:
            if rec.loan_id:
                principal_restored = rec._get_amount_in_loan_currency(rec.principal_amount)
                new_balance = rec.loan_id.outstanding_balance + principal_restored
                vals = {'outstanding_balance': new_balance}
                if rec.loan_id.state == 'paid' and new_balance > 0.01:
                    vals['state'] = 'active'
                rec.loan_id.write(vals)
        return res

    def _get_journal(self):
        return self.payment_journal_id

    def _prepare_move_lines(self):
        self.ensure_one()
        
        company = self.company_id
        company_currency = self.company_currency_id
        transaction_currency = self.currency_id
        loan_currency = self.loan_id.currency_id
        date = self.date or fields.Date.today()

        # 1. Todo a Moneda Compañía
        principal_company = transaction_currency._convert(self.principal_amount, company_currency, company, date)
        interest_company = transaction_currency._convert(self.interest_amount, company_currency, company, date)
        total_company = principal_company + interest_company

        # === CORRECCIÓN MULTIMONEDA: Validar Cuentas Específicas ===
        
        # 2. Configuración Pasivo/Interés (Debe)
        loan_line_curr_id = False
        loan_line_amt_curr_principal = 0.0
        loan_line_amt_curr_interest = 0.0
        
        # Revisar si la cuenta de pasivo exige moneda o si estamos transando en otra moneda
        loan_account_principal = self.loan_id.principal_account_id
        loan_target_currency = loan_account_principal.currency_id or loan_currency

        if loan_target_currency != company_currency:
            loan_line_curr_id = loan_target_currency.id
            loan_line_amt_curr_principal = transaction_currency._convert(
                self.principal_amount, loan_target_currency, company, date
            )
            loan_line_amt_curr_interest = transaction_currency._convert(
                self.interest_amount, loan_target_currency, company, date
            )

        # 3. Configuración Banco (Haber)
        bank_account = self.payment_journal_id.default_account_id
        # PRIORIDAD CRÍTICA: Cuenta > Diario > Compañía
        bank_target_currency = bank_account.currency_id or self.payment_journal_id.currency_id or company_currency
        
        bank_line_curr_id = False
        bank_line_amt_curr = 0.0

        if bank_target_currency != company_currency:
            bank_line_curr_id = bank_target_currency.id
            total_transaction = self.principal_amount + self.interest_amount
            # Salida de dinero = Negativo
            converted_amount = transaction_currency._convert(total_transaction, bank_target_currency, company, date)
            bank_line_amt_curr = -converted_amount

        lines = []

        # A. Capital (Debe)
        lines.append((0, 0, {
            'name': f"{self.description} - Capital",
            'account_id': self.loan_id.principal_account_id.id,
            'debit': principal_company,
            'credit': 0.0,
            'currency_id': loan_line_curr_id,
            'amount_currency': loan_line_amt_curr_principal,
            'partner_id': self.loan_id.partner_id.id,
        }))

        # B. Intereses (Debe)
        if self.interest_amount > 0 or interest_company > 0:
            lines.append((0, 0, {
                'name': f"{self.description} - Intereses",
                'account_id': self.loan_id.interest_account_id.id,
                'debit': interest_company,
                'credit': 0.0,
                'currency_id': loan_line_curr_id,
                'amount_currency': loan_line_amt_curr_interest,
                'partner_id': self.loan_id.partner_id.id,
            }))

        # C. Banco (Haber)
        lines.append((0, 0, {
            'name': self.description,
            'account_id': bank_account.id,
            'debit': 0.0,
            'credit': total_company,
            'currency_id': bank_line_curr_id,
            'amount_currency': bank_line_amt_curr,
            'partner_id': self.loan_id.partner_id.id,
        }))

        return lines