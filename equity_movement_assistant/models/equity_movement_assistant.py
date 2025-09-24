# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class EquityMovementAssistant(models.Model):
    _name = 'equity.movement.assistant'
    _inherit = 'assistant.journal.entry.base'
    _description = 'Asistente de Movimientos de Patrimonio'

    category_id = fields.Many2one('equity.movement.category', string='Categoría del Movimiento', required=True)
    movement_type = fields.Selection(related='category_id.movement_type', string="Tipo", readonly=True, store=True)
    equity_account_id = fields.Many2one(related='category_id.equity_account_id', string="Cuenta de Patrimonio", readonly=True, store=True)

    partner_id = fields.Many2one('res.partner', string='Socio / Accionista', required=True)
    amount = fields.Float(string='Monto', required=True)
    payment_journal_id = fields.Many2one('account.journal', string='Diario de Pago/Cobro', required=True, domain="[('type', 'in', ('bank', 'cash'))]")

    # --- IMPLEMENTACIÓN DE MÉTODOS HEREDADOS ---
    def _get_journal(self):
        self.ensure_one()
        return self.payment_journal_id

    def _prepare_move_lines(self):
        self.ensure_one()
        if self.amount <= 0:
            raise UserError(_('El monto debe ser positivo.'))

        debit_account_id = False
        credit_account_id = False

        if self.movement_type == 'contribution': # Aporte de capital
            debit_account_id = self.payment_journal_id.default_account_id.id
            credit_account_id = self.equity_account_id.id
        elif self.movement_type == 'dividend': # Pago de dividendos
            debit_account_id = self.equity_account_id.id
            credit_account_id = self.payment_journal_id.default_account_id.id
            
        debit_line_vals = (0, 0, {
            'name': self.description,
            'account_id': debit_account_id,
            'debit': self.amount,
            'credit': 0.0,
            'partner_id': self.partner_id.id,
        })

        credit_line_vals = (0, 0, {
            'name': self.description,
            'account_id': credit_account_id,
            'debit': 0.0,
            'credit': self.amount,
            'partner_id': self.partner_id.id,
        })

        return [debit_line_vals, credit_line_vals]