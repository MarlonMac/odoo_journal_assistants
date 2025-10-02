# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class LoanPaymentAssistant(models.Model):
    _name = 'loan.payment.assistant'
    _inherit = 'assistant.journal.entry.base'
    _description = 'Asistente de Pago de Préstamos'

    # Campos específicos
    loan_id = fields.Many2one(
        'loan.loan', 
        string='Préstamo a Pagar', 
        required=True,
        domain="[('company_id', '=', company_id)]"
    )
    principal_amount = fields.Float(string='Monto de Capital', required=True)
    interest_amount = fields.Float(string='Monto de Intereses', required=True)
    payment_journal_id = fields.Many2one(
        'account.journal', 
        string='Pagado desde (Diario)', 
        required=True, 
        domain="[('type', 'in', ('bank', 'cash')), ('company_id', '=', company_id)]"
    )
    
    # Heredamos el campo 'amount' pero lo hacemos computado y de solo lectura
    amount = fields.Float(string='Monto Total Pagado', compute='_compute_amount', store=True, readonly=True)

    @api.depends('principal_amount', 'interest_amount')
    def _compute_amount(self):
        for rec in self:
            rec.amount = rec.principal_amount + rec.interest_amount

    # --- IMPLEMENTACIÓN DE MÉTODOS HEREDADOS ---
    def _get_journal(self):
        self.ensure_one()
        return self.payment_journal_id

    def _prepare_move_lines(self):
        self.ensure_one()
        if self.amount <= 0:
            raise UserError(_('El monto total pagado debe ser positivo.'))
        if self.principal_amount < 0 or self.interest_amount < 0:
            raise UserError(_('Los montos de capital e interés no pueden ser negativos.'))

        lines = []
        # Línea de Débito 1 (Reducción de la deuda)
        lines.append((0, 0, {
            'name': f"{self.description} - Capital",
            'account_id': self.loan_id.principal_account_id.id,
            'debit': self.principal_amount,
            'credit': 0.0,
            'partner_id': self.loan_id.partner_id.id,
        }))
        
        # Línea de Débito 2 (Gasto por Interés)
        if self.interest_amount > 0:
            lines.append((0, 0, {
                'name': f"{self.description} - Intereses",
                'account_id': self.loan_id.interest_account_id.id,
                'debit': self.interest_amount,
                'credit': 0.0,
                'partner_id': self.loan_id.partner_id.id,
            }))

        # Línea de Crédito (Salida de Banco/Caja)
        lines.append((0, 0, {
            'name': self.description,
            'account_id': self.payment_journal_id.default_account_id.id,
            'debit': 0.0,
            'credit': self.amount,
            'partner_id': self.loan_id.partner_id.id,
        }))

        return lines