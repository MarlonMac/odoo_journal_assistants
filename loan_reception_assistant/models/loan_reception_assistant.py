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

    amount = fields.Monetary(
        string="Monto a Recibir", 
        related='loan_id.original_amount', 
        readonly=True
    )
    reception_journal_id = fields.Many2one(
        'account.journal', 
        string='Recibido en (Diario)', 
        required=True, 
        domain="[('type', 'in', ('bank', 'cash')), ('company_id', '=', company_id)]",
        states={'posted': [('readonly', True)], 'cancelled': [('readonly', True)], 'approved': [('readonly', True)]}
    )
    currency_id = fields.Many2one(
        'res.currency', 
        string='Moneda', 
        related='company_id.currency_id'
    )
    
    # ELIMINADO: attachment y attachment_filename (heredados del base)

    # Campos de Input para configurar el préstamo
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

    def action_post(self):
        # El super() ya maneja el adjunto y la creación del asiento
        res = super(LoanReceptionAssistant, self).action_post()
        
        for rec in self:
            # ELIMINADO: Lógica manual de ir.attachment.create
            
            # Actualizar y Activar Préstamo
            if rec.loan_id:
                rec.loan_id.write({
                    'state': 'active',
                    'date_start': rec.date,
                    'maturity_date': rec.maturity_date,
                    'payment_term_id': rec.payment_term_id.id
                })
        return res

    def _get_journal(self):
        self.ensure_one()
        return self.reception_journal_id

    def _prepare_move_lines(self):
        self.ensure_one()
        if self.amount <= 0:
            raise UserError(_('El monto a recibir debe ser positivo.'))

        debit_line = (0, 0, {
            'name': self.description,
            'account_id': self.reception_journal_id.default_account_id.id,
            'debit': self.amount,
            'credit': 0.0,
            'partner_id': self.loan_id.partner_id.id,
        })
        
        credit_line = (0, 0, {
            'name': self.description,
            'account_id': self.loan_id.principal_account_id.id,
            'debit': 0.0,
            'credit': self.amount,
            'partner_id': self.loan_id.partner_id.id,
        })

        return [debit_line, credit_line]