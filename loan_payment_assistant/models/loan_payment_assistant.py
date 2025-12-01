# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

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
    principal_amount = fields.Float(string='Monto de Capital', required=True, tracking=True)
    interest_amount = fields.Float(string='Monto de Intereses', required=True, tracking=True)
    payment_journal_id = fields.Many2one(
        'account.journal', 
        string='Pagado desde (Diario)', 
        required=True, 
        domain="[('type', 'in', ('bank', 'cash')), ('company_id', '=', company_id)]"
    )
    
    # Heredamos el campo 'amount' pero lo hacemos computado y de solo lectura
    amount = fields.Float(string='Monto Total Pagado', compute='_compute_amount', store=True, readonly=True)

    # --- CAMPOS PARA COMPROBANTE ---
    attachment = fields.Binary(string="Comprobante de Pago", help="Adjunte el comprobante de la transferencia o depósito.")
    attachment_filename = fields.Char(string="Nombre del Comprobante")

    @api.depends('principal_amount', 'interest_amount')
    def _compute_amount(self):
        for rec in self:
            rec.amount = rec.principal_amount + rec.interest_amount

    @api.constrains('principal_amount', 'loan_id')
    def _check_principal_amount(self):
        for rec in self:
            if rec.loan_id and rec.principal_amount > rec.loan_id.outstanding_balance:
                raise ValidationError(_(
                    "El monto de capital a pagar (%.2f) no puede ser mayor que el saldo pendiente del préstamo (%.2f)."
                ) % (rec.principal_amount, rec.loan_id.outstanding_balance))

    def action_post(self):
        # Ejecuta la lógica base para crear el asiento
        res = super(LoanPaymentAssistant, self).action_post()
        
        for rec in self:
            # Actualizar saldo del préstamo
            if rec.loan_id:
                new_balance = rec.loan_id.outstanding_balance - rec.principal_amount
                rec.loan_id.write({'outstanding_balance': new_balance})
            
            # Lógica de adjuntos: Vincular el archivo al asiento contable creado (move_id)
            if rec.attachment and rec.move_id:
                self.env['ir.attachment'].create({
                    'name': rec.attachment_filename or _('Comprobante de Pago'),
                    'type': 'binary',
                    'datas': rec.attachment,
                    'res_model': 'account.move',
                    'res_id': rec.move_id.id,
                    'mimetype': 'application/octet-stream'
                })

        return res

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