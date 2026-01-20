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

    @api.onchange('loan_id')
    def _onchange_loan_id(self):
        if self.loan_id:
            self.currency_id = self.loan_id.currency_id
            self.amount = self.loan_id.original_amount
            if self.loan_id.maturity_date:
                self.maturity_date = self.loan_id.maturity_date

    def action_post(self):
        res = super(LoanReceptionAssistant, self).action_post()
        for rec in self:
            if rec.loan_id:
                rec.loan_id.write({
                    'state': 'active',
                    'date_start': rec.date,
                    'maturity_date': rec.maturity_date,
                    'outstanding_balance': rec.amount
                })
        return res

    def action_cancel(self):
        posted_records = self.filtered(lambda r: r.state == 'posted')
        res = super(LoanReceptionAssistant, self).action_cancel()
        
        for rec in posted_records:
            if rec.loan_id:
                new_balance = rec.loan_id.outstanding_balance - rec.amount
                if new_balance < 0: 
                    new_balance = 0.0

                vals = {'outstanding_balance': new_balance}

                if new_balance <= 0.01:
                    vals['state'] = 'draft'
                    vals['date_start'] = False
                
                rec.loan_id.write(vals)
                
                rec.loan_id.message_post(body=_(
                    "La recepción %s ha sido cancelada. El préstamo ha vuelto a estado Borrador."
                ) % rec.name)
        
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

        # 1. Conversión a moneda base (GTQ) para el débito y crédito oficial
        amount_company_curr = loan_currency._convert(
            self.amount, company_currency, company, date
        )

        # === LÓGICA DE MULTIMONEDA CORREGIDA ===

        # --- A. Preparación Línea de Banco (Debe) ---
        bank_account = self.reception_journal_id.default_account_id
        # PRIORIDAD CRÍTICA: La moneda la dicta la CUENTA, no solo el diario.
        bank_currency = bank_account.currency_id or self.reception_journal_id.currency_id or company_currency
        
        bank_line_currency_id = False
        bank_line_amount_currency = 0.0

        if bank_currency != company_currency:
            bank_line_currency_id = bank_currency.id
            # Optimización: Si la cuenta de banco y el préstamo son la misma moneda (ej. USD),
            # usamos el monto original directo para evitar errores de redondeo en conversión.
            if bank_currency == loan_currency:
                bank_line_amount_currency = self.amount
            else:
                bank_line_amount_currency = company_currency._convert(
                    amount_company_curr, bank_currency, company, date
                )

        # --- B. Preparación Línea de Pasivo/Préstamo (Haber) ---
        loan_account = self.loan_id.principal_account_id
        # Misma lógica: verificar si la cuenta de pasivo tiene moneda forzada
        liability_currency = loan_account.currency_id or loan_currency
        
        loan_line_currency_id = False
        loan_line_amount_currency = 0.0

        # Generalmente la cuenta de pasivo sigue la moneda del préstamo, 
        # pero verificamos contra la moneda de la compañía por si acaso.
        if liability_currency != company_currency:
             loan_line_currency_id = liability_currency.id
             # Debe ser negativo porque es crédito
             if liability_currency == loan_currency:
                 loan_line_amount_currency = -self.amount
             else:
                 # Caso raro: Préstamo en EUR, Pasivo en USD
                 amt_converted = company_currency._convert(amount_company_curr, liability_currency, company, date)
                 loan_line_amount_currency = -amt_converted

        # --- Creación de Líneas ---
        
        debit_line = (0, 0, {
            'name': f"{self.description} (Recepción)",
            'account_id': bank_account.id,
            'debit': amount_company_curr,
            'credit': 0.0,
            'currency_id': bank_line_currency_id,
            'amount_currency': bank_line_amount_currency,
            'partner_id': self.loan_id.partner_id.id,
        })
        
        credit_line = (0, 0, {
            'name': f"Préstamo: {self.loan_id.name}",
            'account_id': loan_account.id,
            'debit': 0.0,
            'credit': amount_company_curr,
            'currency_id': loan_line_currency_id,
            'amount_currency': loan_line_amount_currency,
            'partner_id': self.loan_id.partner_id.id,
        })

        return [debit_line, credit_line]