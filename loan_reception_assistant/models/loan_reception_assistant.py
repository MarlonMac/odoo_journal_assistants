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
        domain="[('state', '=', 'draft'), ('company_id', '=', company_id)]"
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
        domain="[('type', 'in', ('bank', 'cash')), ('company_id', '=', company_id)]"
    )
    currency_id = fields.Many2one(
        'res.currency', 
        string='Moneda', 
        related='company_id.currency_id'
    )
    
    # --- CAMPOS NUEVOS ---
    attachment = fields.Binary(string="Comprobante", required=True, help="Seleccione el archivo del comprobante de la transacción.")
    attachment_filename = fields.Char(string="Nombre del Comprobante")
    # --------------------

    def action_post(self):
        # Primero, ejecuta la lógica base (crear y asentar el move)
        res = super(LoanReceptionAssistant, self).action_post()
        
        # Luego, ejecuta la lógica específica de este asistente
        for rec in self:
            # Adjuntar el comprobante al asiento contable
            if rec.attachment and rec.move_id:
                self.env['ir.attachment'].create({
                    'name': rec.attachment_filename,
                    'type': 'binary',
                    'datas': rec.attachment,
                    'res_model': 'account.move',
                    'res_id': rec.move_id.id,
                    'mimetype': 'application/octet-stream'
                })
            
            # Cambiar el estado del préstamo
            if rec.loan_id:
                rec.loan_id.write({'state': 'active'})
        
        return res

    def _get_journal(self):
        self.ensure_one()
        return self.reception_journal_id

    def _prepare_move_lines(self):
        self.ensure_one()
        if self.amount <= 0:
            raise UserError(_('El monto a recibir debe ser positivo.'))

        # Débito: Ingresa el dinero al banco
        debit_line = (0, 0, {
            'name': self.description,
            'account_id': self.reception_journal_id.default_account_id.id,
            'debit': self.amount,
            'credit': 0.0,
            'partner_id': self.loan_id.partner_id.id,
        })
        
        # Crédito: Se crea la deuda en la cuenta de pasivo
        credit_line = (0, 0, {
            'name': self.description,
            'account_id': self.loan_id.principal_account_id.id,
            'debit': 0.0,
            'credit': self.amount,
            'partner_id': self.loan_id.partner_id.id,
        })

        return [debit_line, credit_line]