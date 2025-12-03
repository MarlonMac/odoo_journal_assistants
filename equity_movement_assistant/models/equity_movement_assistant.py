# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class EquityMovementAssistant(models.Model):
    _name = 'equity.movement.assistant'
    _inherit = 'assistant.journal.entry.base'
    _description = 'Asistente de Movimientos de Patrimonio'

    # Seguridad: Solo editable en borrador
    READONLY_STATES = {
        'to_approve': [('readonly', True)], 
        'approved': [('readonly', True)], 
        'posted': [('readonly', True)], 
        'cancelled': [('readonly', True)]
    }

    category_id = fields.Many2one(
        'equity.movement.category', 
        string='Categoría del Movimiento', 
        required=True,
        states=READONLY_STATES,
        domain="[('company_id', '=', company_id)]"
    )
    movement_type = fields.Selection(related='category_id.movement_type', string="Tipo", readonly=True, store=True)
    equity_account_id = fields.Many2one(related='category_id.equity_account_id', string="Cuenta de Patrimonio", readonly=True, store=True)
    liability_account_id = fields.Many2one(related='category_id.liability_account_id', readonly=True, store=True)

    partner_id = fields.Many2one('res.partner', string='Socio / Accionista', required=True, states=READONLY_STATES)
    amount = fields.Float(string='Monto', required=True, states=READONLY_STATES)
    payment_journal_id = fields.Many2one(
        'account.journal', 
        string='Diario de Pago/Cobro', 
        states=READONLY_STATES,
        domain="[('type', 'in', ('bank', 'cash')), ('company_id', '=', company_id)]", 
        help="Diario donde ingresa el aporte de capital."
    )

    # --- IMPLEMENTACIÓN DE MÉTODOS HEREDADOS ---
    def _get_journal(self):
        self.ensure_one()
        # Para aportes, es un cobro. Para dividendos, es una operación en el diario general.
        if self.movement_type == 'contribution':
            return self.payment_journal_id
        else:
            journal = self.env['account.journal'].search([('type', '=', 'general'), ('company_id', '=', self.company_id.id)], limit=1)
            if not journal:
                raise UserError(_('No se encuentra un diario de "Operaciones Varias" para esta compañía.'))
            return journal

    def _prepare_move_lines(self):
        self.ensure_one()
        if self.amount <= 0:
            raise UserError(_('El monto debe ser positivo.'))

        if self.movement_type == 'contribution': # Aporte de capital (pago directo)
            debit_account_id = self.payment_journal_id.default_account_id.id
            credit_account_id = self.equity_account_id.id
        elif self.movement_type == 'dividend': # Declaración de dividendos (crea pasivo)
            if not self.liability_account_id:
                raise UserError(_('La categoría "%s" debe tener una Cuenta de Pasivo configurada.') % self.category_id.name)
            debit_account_id = self.equity_account_id.id
            credit_account_id = self.liability_account_id.id
        
        return [
            (0, 0, {'name': self.description, 'account_id': debit_account_id, 'debit': self.amount, 'credit': 0.0, 'partner_id': self.partner_id.id}),
            (0, 0, {'name': self.description, 'account_id': credit_account_id, 'debit': 0.0, 'credit': self.amount, 'partner_id': self.partner_id.id})
        ]