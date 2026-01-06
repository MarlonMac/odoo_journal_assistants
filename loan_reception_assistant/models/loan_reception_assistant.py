# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class LoanReceptionAssistant(models.Model):
    _name = 'loan.reception.assistant'
    _inherit = 'assistant.journal.entry.base'
    _description = 'Asistente de Recepción de Préstamos'

    loan_id = fields.Many2one(
        'loan.loan', 
        string='Préstamo', 
        required=True,
        domain="[('state', '=', 'draft'), ('company_id', '=', company_id)]",
        states={'posted': [('readonly', True)], 'cancelled': [('readonly', True)], 'approved': [('readonly', True)]}
    )

    partner_id = fields.Many2one(
        'res.partner', 
        related='loan_id.partner_id', 
        string='Acreedor',
        readonly=True,
        store=True
    )

    currency_id = fields.Many2one(
        'res.currency', 
        string='Moneda del Préstamo', 
        required=True,
        readonly=True,
        states={'posted': [('readonly', True)], 'cancelled': [('readonly', True)], 'approved': [('readonly', True)]}
    )

    amount = fields.Monetary(
        string="Monto a Recibir", 
        currency_field='currency_id',
        required=True,
        readonly=True,
        help="Monto original definido en el contrato del préstamo.",
        states={'posted': [('readonly', True)], 'cancelled': [('readonly', True)], 'approved': [('readonly', True)]}
    )
    
    reception_journal_id = fields.Many2one(
        'account.journal', 
        string='Recibido en (Diario)', 
        required=True, 
        domain="[('type', 'in', ('bank', 'cash')), ('company_id', '=', company_id)]",
        states={'posted': [('readonly', True)], 'cancelled': [('readonly', True)], 'approved': [('readonly', True)]}
    )

    # Inputs de Configuración
    maturity_date = fields.Date(
        string="Fecha de Vencimiento", 
        required=True, 
        help="Fecha límite para pagar el préstamo.",
        states={'posted': [('readonly', True)], 'cancelled': [('readonly', True)], 'approved': [('readonly', True)]}
    )
    payment_term_id = fields.Many2one(
        'account.payment.term', 
        string="Términos de Pago", 
        required=True,
        states={'posted': [('readonly', True)], 'cancelled': [('readonly', True)], 'approved': [('readonly', True)]}
    )

    @api.onchange('loan_id')
    def _onchange_loan_id(self):
        if self.loan_id:
            self.currency_id = self.loan_id.currency_id
            self.amount = self.loan_id.original_amount
            if self.loan_id.maturity_date:
                self.maturity_date = self.loan_id.maturity_date
            if self.loan_id.payment_term_id:
                self.payment_term_id = self.loan_id.payment_term_id

    def action_post(self):
        res = super(LoanReceptionAssistant, self).action_post()
        for rec in self:
            if rec.loan_id:
                rec.loan_id.write({
                    'state': 'active',
                    'date_start': rec.date,
                    'maturity_date': rec.maturity_date,
                    'payment_term_id': rec.payment_term_id.id,
                    'outstanding_balance': rec.amount
                })
        return res

    def _get_journal(self):
        self.ensure_one()
        return self.reception_journal_id

    def _prepare_move_lines(self):
        self.ensure_one()
        if self.amount <= 0:
            raise UserError(_('El monto a recibir debe ser positivo.'))

        company = self.company_id
        company_currency = self.company_currency_id
        loan_currency = self.currency_id
        date = self.date or fields.Date.today()

        # 1. Calcular monto en moneda de la compañía
        amount_company_curr = loan_currency._convert(
            self.amount, company_currency, company, date
        )

        # 2. Configurar Moneda para Préstamo (Pasivo)
        # CORRECCIÓN: Si es misma moneda, usamos company_currency.id, NUNCA False.
        loan_line_currency = loan_currency.id
        loan_line_amount_currency = 0.0
        if loan_currency != company_currency:
             loan_line_amount_currency = -self.amount

        # 3. Configurar Moneda para Banco
        bank_journal = self.reception_journal_id
        bank_currency = bank_journal.currency_id or company_currency
        
        bank_line_currency = bank_currency.id
        bank_line_amount_currency = 0.0

        if bank_currency != company_currency:
            # Convertimos GTQ -> Moneda Banco
            bank_line_amount_currency = company_currency._convert(
                amount_company_curr, bank_currency, company, date
            )

        # A. Línea de Banco (Débito)
        debit_line = (0, 0, {
            'name': f"{self.description} (Recepción)",
            'account_id': self.reception_journal_id.default_account_id.id,
            'debit': amount_company_curr,
            'credit': 0.0,
            'currency_id': bank_line_currency, # ID obligatorio
            'amount_currency': bank_line_amount_currency,
            'partner_id': self.loan_id.partner_id.id,
        })
        
        # B. Línea de Préstamo (Crédito)
        credit_line = (0, 0, {
            'name': f"Préstamo: {self.loan_id.name}",
            'account_id': self.loan_id.principal_account_id.id,
            'debit': 0.0,
            'credit': amount_company_curr,
            'currency_id': loan_line_currency, # ID obligatorio
            'amount_currency': loan_line_amount_currency,
            'partner_id': self.loan_id.partner_id.id,
        })

        return [debit_line, credit_line]