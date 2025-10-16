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
            # --- MODIFICACIÓN: AÑADIDO ASISTENTE FALTANTE ---
            ('loan.reception.assistant', 'Asistente de Recepción de Préstamos'),
        ],
        string="Origen del Asistente"
    )

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    # Campo para enlazar el pago con un asistente
    # --- MODIFICACIÓN: Se elimina compute='_compute_assistant_id' y store=True ---
    # El campo no debe ser calculado; debe asignarse directamente.
    # El método de cómputo generaba consultas SQL erróneas (integer = character varying)
    # al intentar adivinar el asistente desde las líneas de la factura.
    assistant_id = fields.Reference(
        selection=[
            ('expense.assistant', 'Asistente de Gasto'),
            ('asset.purchase.assistant', 'Asistente de Compra de Activo'),
            ('loan.payment.assistant', 'Asistente de Pago de Préstamo'),
            ('equity.movement.assistant', 'Asistente de Movimiento de Patrimonio'),
            # --- MODIFICACIÓN: AÑADIDO ASISTENTE FALTANTE ---
            ('loan.reception.assistant', 'Asistente de Recepción de Préstamos'),
        ],
        string="Origen del Asistente"
        # compute='_compute_assistant_id', (Línea eliminada)
        # store=True (Línea eliminada)
    )

    # --- MODIFICACIÓN: Se comenta el método de cómputo ---
    # Este método es la causa del error. Lo comentamos en lugar de eliminarlo
    # para respetar la directiva de integridad de código.
    # def _compute_assistant_id(self):
    #     for payment in self:
    #         # Buscamos el asistente a través de los asientos que este pago está reconciliando
    #         assistant = self.env['account.move'].search([
    #             ('line_ids.id', 'in', payment.reconciled_bill_ids.line_ids.ids)
    #         ]).mapped('assistant_id')
    #         payment.assistant_id = assistant[0] if assistant else False