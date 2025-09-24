# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class AssetPurchaseAssistant(models.Model):
    _name = 'asset.purchase.assistant'
    _inherit = 'assistant.journal.entry.base'
    _description = 'Asistente de Compra de Activos'

    # --- CAMPOS ---
    amount = fields.Float(string='Monto', required=True, states={'posted': [('readonly', True)], 'cancelled': [('readonly', True)]}, tracking=True)
    supplier_id = fields.Many2one('res.partner', string='Proveedor', required=True)
    category_id = fields.Many2one('asset.category', string='Categoría de Activo', required=True)
    asset_account_id = fields.Many2one('account.account', string='Cuenta de Activo', related='category_id.asset_account_id', store=True, readonly=True)
    
    is_pending_payment = fields.Boolean(
        string='Pendiente de Pago',
        default=True,
        help="Marque esta casilla si la compra del activo genera una cuenta por pagar. Desmárquela si fue un pago directo."
    )
    due_date = fields.Date(
        string='Fecha de Vencimiento',
        states={'posted': [('readonly', True)], 'cancelled': [('readonly', True)]}
    )
    payable_account_id = fields.Many2one(
        'account.account', 
        string='Cuenta por Pagar',
        domain="[('deprecated', '=', False)]"
    )
    payment_journal_id = fields.Many2one(
        'account.journal', 
        string='Diario de Pago (Empresa)', 
        domain="[('type', 'in', ('bank', 'cash'))]",
        help="Diario de la empresa utilizado para realizar el pago directo del activo."
    )

    # --- RESTRICCIONES Y LÓGICA ---
    @api.constrains('is_pending_payment', 'payable_account_id', 'payment_journal_id')
    def _check_payment_fields(self):
        for rec in self:
            if rec.is_pending_payment:
                if not rec.payable_account_id:
                    raise ValidationError(_('Para una compra pendiente de pago, debe especificar la cuenta por pagar.'))
            else:
                if not rec.payment_journal_id:
                    raise ValidationError(_('Para un pago directo, debe especificar el diario de pago.'))

    def _get_journal(self):
        self.ensure_one()
        if self.is_pending_payment:
            journal = self.env['account.journal'].search([('type', '=', 'purchase'), ('company_id', '=', self.company_id.id)], limit=1)
            if not journal:
                raise UserError(_('No se encuentra un diario de "Compras" para esta compañía.'))
            return journal
        else:
            return self.payment_journal_id

    def _prepare_move_lines(self):
        self.ensure_one()
        
        if not self.message_attachment_count > 0:
            raise UserError(_('¡Adjunto Requerido! Debe adjuntar al menos un documento de respaldo.'))
        
        if self.amount <= 0:
            raise UserError(_('El monto del activo debe ser positivo.'))

        debit_line_vals = (0, 0, {
            'name': self.description,
            'account_id': self.asset_account_id.id,
            'debit': self.amount,
            'credit': 0.0,
            'partner_id': self.supplier_id.id,
        })
        
        credit_account_id = self.payable_account_id.id if self.is_pending_payment else self.payment_journal_id.default_account_id.id
        
        credit_line_vals = (0, 0, {
            'name': self.description,
            'account_id': credit_account_id,
            'debit': 0.0,
            'credit': self.amount,
            'partner_id': self.supplier_id.id,
        })

        return [debit_line_vals, credit_line_vals]