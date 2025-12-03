# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class LoanReceptionAssistant(models.Model):
    _name = 'loan.reception.assistant'
    _inherit = 'assistant.journal.entry.base'
    _description = 'Asistente de Recepción de Préstamos'

    # Seguridad: Solo editable en borrador
    READONLY_STATES = {
        'to_approve': [('readonly', True)], 
        'approved': [('readonly', True)], 
        'posted': [('readonly', True)], 
        'cancelled': [('readonly', True)]
    }

    # Aplicamos states a loan_id para bloquearlo post-borrador
    loan_id = fields.Many2one(
        'loan.loan', 
        string='Préstamo', 
        required=True,
        domain="[('state', '=', 'draft'), ('company_id', '=', company_id)]",
        states=READONLY_STATES
    )
    amount = fields.Monetary(
        string="Monto a Recibir", 
        related='loan_id.original_amount', 
        readonly=True
    )
    # Bloqueo de seguridad en diario
    reception_journal_id = fields.Many2one(
        'account.journal', 
        string='Recibido en (Diario)', 
        required=True, 
        domain="[('type', 'in', ('bank', 'cash')), ('company_id', '=', company_id)]",
        states=READONLY_STATES
    )
    currency_id = fields.Many2one(
        'res.currency', 
        string='Moneda', 
        related='company_id.currency_id'
    )
    
    # Bloqueo de seguridad en adjunto
    attachment = fields.Binary(
        string="Comprobante", 
        required=True, 
        help="Seleccione el archivo del comprobante de la transacción.",
        states=READONLY_STATES
    )
    attachment_filename = fields.Char(string="Nombre del Comprobante", states=READONLY_STATES)

    # --- NUEVOS CAMPOS DE GESTIÓN (Con Seguridad de Estados) ---
    maturity_date = fields.Date(
        string="Fecha de Vencimiento", 
        required=True, 
        help="Fecha límite para pagar el préstamo.",
        states=READONLY_STATES
    )
    payment_term_id = fields.Many2one(
        'account.payment.term', 
        string="Términos de Pago", 
        required=True,
        states=READONLY_STATES
    )

    # --- CAMPOS PARA DASHBOARD ---
    loan_payment_ids = fields.One2many(related='loan_id.payment_assistant_ids', string="Tabla de Pagos")
    loan_outstanding_balance = fields.Monetary(related='loan_id.outstanding_balance', string="Saldo Actual", store=False)
    loan_status_display = fields.Selection([
        ('active', 'Activo / Pendiente'),
        ('paid', 'Pagado Totalmente')
    ], string="Estado del Préstamo", compute='_compute_loan_status_display')

    @api.depends('loan_id.outstanding_balance', 'loan_id.state')
    def _compute_loan_status_display(self):
        for rec in self:
            if rec.loan_id.state == 'paid' or rec.loan_id.outstanding_balance <= 0.01:
                rec.loan_status_display = 'paid'
            else:
                rec.loan_status_display = 'active'

    def action_post(self):
        res = super(LoanReceptionAssistant, self).action_post()
        for rec in self:
            # Adjuntar comprobante
            if rec.attachment and rec.move_id:
                self.env['ir.attachment'].create({
                    'name': rec.attachment_filename,
                    'type': 'binary',
                    'datas': rec.attachment,
                    'res_model': 'account.move',
                    'res_id': rec.move_id.id,
                    'mimetype': 'application/octet-stream'
                })
            
            # Actualizar y Activar Préstamo
            if rec.loan_id:
                rec.loan_id.write({
                    'state': 'active',
                    'date_start': rec.date, # Registramos la fecha de inicio real
                    'maturity_date': rec.maturity_date,
                    'payment_term_id': rec.payment_term_id.id
                })
        return res

    def _get_journal(self):
        self.ensure_one()
        return self.reception_journal_id

    def _prepare_move_lines(self):
        self.ensure_one()
        if self.amount <= 0:
            raise UserError(_('El monto a recibir debe ser positivo.'))

        debit_line = (0, 0, {
            'name': self.description,
            'account_id': self.reception_journal_id.default_account_id.id,
            'debit': self.amount,
            'credit': 0.0,
            'partner_id': self.loan_id.partner_id.id,
        })
        
        credit_line = (0, 0, {
            'name': self.description,
            'account_id': self.loan_id.principal_account_id.id,
            'debit': 0.0,
            'credit': self.amount,
            'partner_id': self.loan_id.partner_id.id,
        })

        return [debit_line, credit_line]