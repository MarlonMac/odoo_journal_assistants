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

class AccountPaymentRegister(models.TransientModel):
    """
    Heredamos el wizard de registro de pagos para asegurar que
    el assistant_id se transfiera desde el contexto hasta el pago final.
    """
    _inherit = 'account.payment.register'

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

    def _create_payments(self):
        """
        Sobrescribimos para inyectar el assistant_id en los pagos creados.
        """
        payments = super(AccountPaymentRegister, self)._create_payments()
        if self.assistant_id:
            # Asignamos el asistente a los pagos generados
            payments.write({'assistant_id': self.assistant_id})
        return payments

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

    # --- CAMPO PARA GESTIÓN DE ADJUNTOS EN POPUP ---
    attachment_ids = fields.Many2many(
        'ir.attachment', 
        string='Documentos Adjuntos',
        compute='_compute_attachment_ids',
        inverse='_inverse_attachment_ids',
        help='Adjuntos vinculados a este pago. Permite carga/descarga desde el popup.'
    )

    # --- CAMPOS PARA PREVISUALIZACIÓN ---
    preview_pdf = fields.Binary(compute='_compute_previews', string="Vista Previa PDF")
    preview_image = fields.Binary(compute='_compute_previews', string="Vista Previa Imagen")
    preview_filename = fields.Char(compute='_compute_previews')

    def _compute_attachment_ids(self):
        for rec in self:
            # Buscamos adjuntos que apunten a este modelo y a este ID
            rec.attachment_ids = self.env['ir.attachment'].search([
                ('res_model', '=', 'account.payment'),
                ('res_id', '=', rec.id)
            ])

    def _inverse_attachment_ids(self):
        for rec in self:
            # Al guardar (subir/borrar), actualizamos la referencia en ir.attachment
            for attachment in rec.attachment_ids:
                attachment.write({
                    'res_model': 'account.payment', 
                    'res_id': rec.id
                })

    @api.depends('attachment_ids')
    def _compute_previews(self):
        for rec in self:
            # Limpiamos valores previos
            rec.preview_pdf = False
            rec.preview_image = False
            rec.preview_filename = False
            
            # Buscamos el último adjunto que sea PDF o Imagen
            last_att = self.env['ir.attachment'].search([
                ('res_model', '=', 'account.payment'),
                ('res_id', '=', rec.id),
                ('mimetype', 'in', ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg'])
            ], limit=1, order='create_date desc') # El más reciente

            if last_att:
                rec.preview_filename = last_att.name
                if 'pdf' in last_att.mimetype:
                    rec.preview_pdf = last_att.datas
                else:
                    rec.preview_image = last_att.datas
                    
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