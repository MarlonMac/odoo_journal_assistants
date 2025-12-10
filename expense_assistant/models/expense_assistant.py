# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class ExpenseAssistant(models.Model):
    _name = 'expense.assistant'
    _inherit = 'assistant.journal.entry.base'
    _description = 'Asistente de Gastos Corporativos'

    # Reutilizamos el diccionario definido en el padre o lo definimos localmente para claridad
    READONLY_STATES = {
        'to_approve': [('readonly', True)], 
        'approved': [('readonly', True)], 
        'posted': [('readonly', True)], 
        'cancelled': [('readonly', True)]
    }

    # --- CAMPOS ESPECÍFICOS DE GASTOS ---
    amount = fields.Float(
        string='Monto', 
        required=True, 
        states=READONLY_STATES, 
        tracking=True
    )
    due_date = fields.Date(
        string='Fecha de Vencimiento', 
        states=READONLY_STATES, 
        help="Fecha límite para pagar la factura o recibo asociado."
    )
    payment_method = fields.Selection(
        [('cash', 'Efectivo'), ('credit_card', 'Tarjeta de Crédito'), ('debit_card', 'Tarjeta de Débito'), ('transfer', 'Transferencia Bancaria'), ('other', 'Otro')], 
        string='Método de Pago Original', 
        tracking=True, 
        states=READONLY_STATES, 
        help="Método de pago utilizado originalmente para el gasto."
    )
    is_reimbursement = fields.Boolean(
        string='Es Cuenta por Pagar / Reembolso', 
        default=False, 
        states=READONLY_STATES,
        help="Marque esta casilla si el gasto debe ser reembolsado o si es una factura que aún no ha sido pagada."
    )
    reimburse_partner_id = fields.Many2one(
        'res.partner', 
        string='Pagar A', 
        states=READONLY_STATES,
        help="El empleado o proveedor al que se le debe el dinero."
    )
    payable_account_id = fields.Many2one(
        'account.account', 
        string='Cuenta por Pagar', 
        domain="[('deprecated', '=', False), ('company_id', '=', company_id)]", 
        states=READONLY_STATES,
        help="Cuenta de pasivo que se usará para registrar la deuda."
    )
    responsible_employee_ids = fields.Many2many(
        'hr.employee', 
        string='Empleados Responsables',
        states=READONLY_STATES
    )
    category_id = fields.Many2one(
        'expense.category', 
        string='Categoría de Gasto', 
        required=True, 
        states=READONLY_STATES, 
        domain="[('company_id', '=', company_id)]"
    )
    expense_account_id = fields.Many2one(
        'account.account', 
        string='Cuenta de Gasto', 
        related='category_id.expense_account_id', 
        store=True, 
        readonly=True
    )
    payment_journal_id = fields.Many2one(
        'account.journal', 
        string='Diario de Pago (Empresa)', 
        domain="[('type', 'in', ('bank', 'cash')), ('company_id', '=', company_id)]", 
        states=READONLY_STATES,
        help="Diario de la empresa utilizado para realizar el pago directo."
    )
    partner_id = fields.Many2one(
        'res.partner', 
        string='Proveedor/Contacto Original', 
        states=READONLY_STATES
    )
    
    document_type = fields.Selection([
        ('invoice', 'Factura'),
        ('receipt', 'Recibo/Comprobante'),
        ('forecast', 'Gasto Previsto (Borrador)')
    ], string='Tipo de Documento', required=True, default='receipt', tracking=True, states=READONLY_STATES,
       help="Seleccione 'Gasto Previsto' si aún no tiene el documento. Debe cambiarlo a Factura o Recibo antes de aprobar.")
    
    # Campos para Facturas (DTE)
    dte_number = fields.Char(string='Número DTE', tracking=True, states=READONLY_STATES)
    dte_series = fields.Char(string='Serie DTE', tracking=True, states=READONLY_STATES)
    dte_authorization = fields.Char(string='Autorización DTE', tracking=True, states=READONLY_STATES)
    
    # Campo para Recibos
    document_number = fields.Char(string='Número de Documento', tracking=True, states=READONLY_STATES)

    # Nota: Los campos 'attachment' y 'attachment_filename' se han eliminado de aquí
    # porque ahora se heredan del modelo base.

    @api.constrains('is_reimbursement', 'reimburse_partner_id', 'payable_account_id', 'payment_journal_id')
    def _check_reimbursement_fields(self):
        for rec in self:
            if rec.is_reimbursement:
                if not rec.reimburse_partner_id or not rec.payable_account_id:
                    raise ValidationError(_('Para una cuenta por pagar, debe especificar a quién pagar y la cuenta por pagar.'))
            else:
                if not rec.payment_journal_id:
                    raise ValidationError(_('Para un pago directo, debe especificar el diario de pago.'))

    @api.constrains('state', 'document_type', 'dte_number', 'dte_series', 'dte_authorization', 'document_number')
    def _check_document_requirements(self):
        """ Valida que se tengan los datos completos antes de enviar a aprobación """
        for rec in self:
            if rec.state in ['to_approve', 'approved', 'posted'] and rec.document_type == 'forecast':
                raise ValidationError(_(
                    'No se puede enviar a aprobación un "Gasto Previsto". '
                    'Por favor, cambie el Tipo de Documento a "Factura" o "Recibo" e ingrese los datos correspondientes.'
                ))
            
            if rec.state in ['to_approve', 'approved', 'posted'] and rec.document_type == 'invoice':
                if not rec.dte_number or not rec.dte_series or not rec.dte_authorization:
                    raise ValidationError(_(
                        'Para registrar una Factura, los campos "Número DTE", "Serie DTE" y "Autorización DTE" son obligatorios.'
                    ))

            if rec.state in ['to_approve', 'approved', 'posted'] and rec.document_type == 'receipt':
                if not rec.document_number:
                    raise ValidationError(_(
                        'Para registrar un Recibo/Comprobante, el campo "Número de Documento" es obligatorio.'
                    ))

    # Nota: Se eliminó action_post() sobrescrito porque la lógica de adjuntos ahora está en el padre.

    def _get_journal(self):
        self.ensure_one()
        if self.is_reimbursement:
            journal = self.env['account.journal'].search([('type', '=', 'general'), ('company_id', '=', self.company_id.id)], limit=1)
            if not journal:
                 raise UserError(_('No se encuentra un diario de "Operaciones Varias" para esta compañía.'))
            return journal
        else:
            return self.payment_journal_id

    def _prepare_move_lines(self):
        self.ensure_one()
        if self.amount <= 0:
            raise UserError(_('El monto del gasto debe ser positivo.'))

        # Mantenemos la validación de adjunto requerido usando el campo heredado
        if not self.message_attachment_count > 0 and not self.attachment:
            raise UserError(_('¡Adjunto Requerido! Debe adjuntar un documento de respaldo, ya sea en el chatter o en el campo de comprobante.'))

        ref_prefix = ""
        if self.document_type == 'invoice':
            ref_prefix = f"FAC {self.dte_series}-{self.dte_number}: "
        elif self.document_type == 'receipt':
            ref_prefix = f"DOC {self.document_number}: "
        
        full_ref = f"{ref_prefix}{self.description}"

        debit_line_vals = (0, 0, {
            'name': full_ref,
            'account_id': self.expense_account_id.id,
            'debit': self.amount,
            'credit': 0.0,
            'partner_id': self.partner_id.id,
        })

        if self.is_reimbursement:
            credit_account_id = self.payable_account_id.id
            credit_partner_id = self.reimburse_partner_id.id
        else:
            credit_account_id = self.payment_journal_id.default_account_id.id
            credit_partner_id = self.partner_id.id
            
        credit_line_vals = (0, 0, {
            'name': full_ref,
            'account_id': credit_account_id,
            'debit': 0.0,
            'credit': self.amount,
            'partner_id': credit_partner_id,
        })

        return [debit_line_vals, credit_line_vals]