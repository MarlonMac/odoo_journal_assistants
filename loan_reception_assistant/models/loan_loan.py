# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class Loan(models.Model):
    _name = 'loan.loan'
    _description = 'Registro de Préstamo'
    _inherit = ['mail.thread', 'mail.activity.mixin'] # Añadido para Chatter

    name = fields.Char(string='Nombre o Referencia del Préstamo', required=True, tracking=True)
    partner_id = fields.Many2one('res.partner', string='Acreedor', required=True, help="Entidad o persona que otorgó el préstamo.", tracking=True)
    
    # Montos
    original_amount = fields.Monetary(string="Monto Original", required=True, tracking=True)
    outstanding_balance = fields.Monetary(string="Saldo Pendiente", tracking=True, readonly=True)
    
    # Fechas y Condiciones
    date_start = fields.Date(string="Fecha de Inicio", tracking=True)
    maturity_date = fields.Date(string="Fecha de Vencimiento", tracking=True, help="Fecha límite para cancelar el préstamo.")
    payment_term_id = fields.Many2one('account.payment.term', string="Términos de Pago", help="Condiciones de pago acordadas.")

    # Cuentas
    principal_account_id = fields.Many2one(
        'account.account', 
        string='Cuenta de Pasivo (Capital)', 
        required=True,
        domain="[('deprecated', '=', False), ('company_id', '=', company_id)]",
        help="Cuenta donde se registra la deuda del préstamo."
    )
    interest_account_id = fields.Many2one(
        'account.account', 
        string='Cuenta de Gasto (Intereses)', 
        required=True,
        domain="[('deprecated', '=', False), ('company_id', '=', company_id)]",
        help="Cuenta de gasto para intereses."
    )
    
    company_id = fields.Many2one(
        'res.company', 
        string='Compañía', 
        required=True, 
        default=lambda self: self.env.company
    )
    currency_id = fields.Many2one(
        'res.currency', 
        string='Moneda', 
        related='company_id.currency_id', 
        store=True
    )
    
    # Relaciones
    payment_assistant_ids = fields.One2many('loan.payment.assistant', 'loan_id', string='Pagos del Asistente')
    payment_count = fields.Integer(string="Pagos Registrados", compute='_compute_payment_count')

    state = fields.Selection([
        ('draft', 'Borrador'),
        ('active', 'Activo'),
        ('paid', 'Pagado'),
    ], string='Estado', default='draft', tracking=True)

    @api.depends('payment_assistant_ids')
    def _compute_payment_count(self):
        for loan in self:
            loan.payment_count = len(loan.payment_assistant_ids)

    @api.onchange('original_amount')
    def _onchange_original_amount(self):
        if self.state == 'draft':
            self.outstanding_balance = self.original_amount

    def write(self, vals):
        # Bloqueo de seguridad: No permitir editar campos clave si está activo o pagado
        # Excepción: outstanding_balance (se actualiza por sistema) y state (transiciones)
        for rec in self:
            if rec.state in ['active', 'paid']:
                protected_fields = ['original_amount', 'partner_id', 'principal_account_id', 'interest_account_id', 'company_id']
                if any(field in vals for field in protected_fields):
                    # Permitimos si es un superusuario o sistema (podríamos refinar esto)
                    # Pero para usuarios normales, esto es un error.
                    raise UserError(_('No se pueden modificar las condiciones estructurales de un préstamo Activo o Pagado. Revierta las transacciones primero.'))
        return super(Loan, self).write(vals)

    def action_view_payments(self):
        self.ensure_one()
        return {
            'name': 'Pagos del Préstamo',
            'type': 'ir.actions.act_window',
            'res_model': 'loan.payment.assistant',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.payment_assistant_ids.ids)],
            'context': dict(self._context, create=False)
        }