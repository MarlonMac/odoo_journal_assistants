# -*- coding: utf-8 -*-
from odoo import models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    # Campo para enlazar el asiento con un asistente
    assistant_id = fields.Reference(
        selection=[
            ('expense.assistant', 'Asistente de Gasto'),
            ('asset.purchase.assistant', 'Asistente de Compra de Activo'),
            ('loan.payment.assistant', 'Asistente de Pago de Préstamo'),
            ('equity.movement.assistant', 'Asistente de Movimiento de Patrimonio'),
        ],
        string="Origen del Asistente"
    )

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    # Campo para enlazar el pago con un asistente
    assistant_id = fields.Reference(
        selection=[
            ('expense.assistant', 'Asistente de Gasto'),
            ('asset.purchase.assistant', 'Asistente de Compra de Activo'),
            ('loan.payment.assistant', 'Asistente de Pago de Préstamo'),
            ('equity.movement.assistant', 'Asistente de Movimiento de Patrimonio'),
        ],
        string="Origen del Asistente",
        compute='_compute_assistant_id',
        store=True
    )

    def _compute_assistant_id(self):
        for payment in self:
            # Buscamos el asistente a través de los asientos que este pago está reconciliando
            assistant = self.env['account.move'].search([
                ('line_ids.id', 'in', payment.reconciled_bill_ids.line_ids.ids)
            ]).mapped('assistant_id')
            payment.assistant_id = assistant[0] if assistant else False