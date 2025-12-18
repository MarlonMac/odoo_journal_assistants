# -*- coding: utf-8 -*-
from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    assistant_id = fields.Reference(
        selection=[
            ('expense.assistant', 'Asistente de Gasto'),
            ('asset.purchase.assistant', 'Asistente de Compra de Activo'),
            ('loan.payment.assistant', 'Asistente de Pago de Préstamo'),
            ('equity.movement.assistant', 'Asistente de Movimiento de Patrimonio'),
            ('loan.reception.assistant', 'Asistente de Recepción de Préstamos'),
        ],
        string="Origen del Asistente"
    )

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    assistant_id = fields.Reference(
        selection=[
            ('expense.assistant', 'Asistente de Gasto'),
            ('asset.purchase.assistant', 'Asistente de Compra de Activo'),
            ('loan.payment.assistant', 'Asistente de Pago de Préstamo'),
            ('equity.movement.assistant', 'Asistente de Movimiento de Patrimonio'),
            ('loan.reception.assistant', 'Asistente de Recepción de Préstamos'),
        ],
        string="Origen del Asistente"
    )

    def action_post(self):
        """ 
        Sobrescribimos para que al publicar un pago, 
        el asistente relacionado actualice su estado de pago.
        """
        res = super(AccountPayment, self).action_post()
        for payment in self:
            if payment.assistant_id:
                # Obtenemos el registro del asistente usando el Reference
                assistant = payment.assistant_id
                if assistant:
                    # Invalidamos el caché para forzar el recálculo de los campos de montos y estado
                    assistant.invalidate_recordset(['amount_paid', 'amount_due', 'payment_status'])
                    # Forzamos la ejecución del cómputo de estado
                    assistant._compute_payment_status()
        return res

    def action_draft(self):
        """ Asegura el recálculo si el pago vuelve a borrador o se anula """
        res = super(AccountPayment, self).action_draft()
        for payment in self:
            if payment.assistant_id:
                payment.assistant_id._compute_payment_status()
        return res  