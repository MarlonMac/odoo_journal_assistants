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

    # MODIFICADO: Campo normal (no related) para evitar lag en la UI
    currency_id = fields.Many2one(
        'res.currency', 
        string='Moneda del Préstamo', 
        required=True,
        readonly=True, # El usuario no la elige, viene del préstamo
        states={'posted': [('readonly', True)], 'cancelled': [('readonly', True)], 'approved': [('readonly', True)]}
    )

    # MODIFICADO: Campo normal (no related) para garantizar el widget monetario correcto
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

    # --- LÓGICA DE HERENCIA EXPLÍCITA ---
    @api.onchange('loan_id')
    def _onchange_loan_id(self):
        """
        Al seleccionar el préstamo, forzamos la carga de su moneda y monto.
        Esto asegura que la vista se actualice inmediatamente con el símbolo correcto.
        """
        if self.loan_id:
            self.currency_id = self.loan_id.currency_id
            self.amount = self.loan_id.original_amount
            # También sugerimos fecha y términos si el préstamo ya los tuviera (opcional)
            if self.loan_id.maturity_date:
                self.maturity_date = self.loan_id.maturity_date
            if self.loan_id.payment_term_id:
                self.payment_term_id = self.loan_id.payment_term_id

    def action_post(self):
        res = super(LoanReceptionAssistant, self).action_post()
        for rec in self:
            if rec.loan_id:
                # Activamos el préstamo asegurando que los datos coinciden
                rec.loan_id.write({
                    'state': 'active',
                    'date_start': rec.date,
                    'maturity_date': rec.maturity_date,
                    'payment_term_id': rec.payment_term_id.id,
                    # El saldo inicial nace del monto recibido (que es igual al original)
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
        loan_currency = self.currency_id # Ahora viene cargada por el onchange
        date = self.date or fields.Date.today()

        # 1. Calcular monto en moneda de la compañía (Base Contable GTQ)
        amount_company_curr = loan_currency._convert(
            self.amount, company_currency, company, date
        )

        # 2. Configurar Moneda para la línea del Préstamo (Pasivo)
        # El pasivo DEBE registrarse en la moneda del préstamo para control de deuda
        loan_line_currency = loan_currency.id if loan_currency != company_currency else False
        loan_line_amount_currency = -self.amount if loan_currency != company_currency else 0.0

        # 3. Configurar Moneda para la línea de Banco
        # Depende estrictamente del diario seleccionado
        bank_journal = self.reception_journal_id
        bank_currency = bank_journal.currency_id or company_currency
        
        bank_line_currency = False
        bank_line_amount_currency = 0.0

        if bank_currency != company_currency:
            # Si el banco tiene moneda extranjera (ej. EUR o el mismo USD), calculamos el importe en ESA moneda
            bank_line_currency = bank_currency.id
            # Convertimos GTQ -> Moneda Banco
            bank_line_amount_currency = company_currency._convert(
                amount_company_curr, bank_currency, company, date
            )

        # A. Línea de Banco (Débito) - Entra dinero
        debit_line = (0, 0, {
            'name': f"{self.description} (Recepción)",
            'account_id': self.reception_journal_id.default_account_id.id,
            'debit': amount_company_curr,
            'credit': 0.0,
            'currency_id': bank_line_currency,
            'amount_currency': bank_line_amount_currency,
            'partner_id': self.loan_id.partner_id.id,
        })
        
        # B. Línea de Préstamo (Crédito) - Aumenta Pasivo
        credit_line = (0, 0, {
            'name': f"Préstamo: {self.loan_id.name}",
            'account_id': self.loan_id.principal_account_id.id,
            'debit': 0.0,
            'credit': amount_company_curr,
            'currency_id': loan_line_currency,
            'amount_currency': loan_line_amount_currency,
            'partner_id': self.loan_id.partner_id.id,
        })

        return [debit_line, credit_line]