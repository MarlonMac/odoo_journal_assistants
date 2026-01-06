# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import timedelta

class Loan(models.Model):
    _name = 'loan.loan'
    _description = 'Registro de Préstamo'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Nombre o Referencia del Préstamo', required=True, tracking=True)
    partner_id = fields.Many2one('res.partner', string='Acreedor', required=True, help="Entidad o persona que otorgó el préstamo.", tracking=True)
    
    # Moneda y Montos
    currency_id = fields.Many2one(
        'res.currency', 
        string='Moneda del Préstamo', 
        required=True, 
        default=lambda self: self.env.company.currency_id,
        tracking=True
    )
    original_amount = fields.Monetary(string="Monto Original", required=True, tracking=True, currency_field='currency_id')
    outstanding_balance = fields.Monetary(string="Saldo Pendiente", tracking=True, currency_field='currency_id')
    
    # Progreso
    progress = fields.Float(string="Progreso Pagado", compute='_compute_progress', store=False)

    # Campos de Gestión
    date_start = fields.Date(string="Fecha de Inicio", tracking=True)
    maturity_date = fields.Date(string="Fecha de Vencimiento", tracking=True, help="Fecha límite para cancelar el préstamo.")
    
    # ELIMINADO: payment_term_id

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

    @api.depends('original_amount', 'outstanding_balance')
    def _compute_progress(self):
        for rec in self:
            if rec.original_amount > 0:
                paid = rec.original_amount - rec.outstanding_balance
                if paid < 0: paid = 0
                rec.progress = (paid / rec.original_amount) * 100
            else:
                rec.progress = 0.0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'original_amount' in vals and vals.get('outstanding_balance', 0) == 0:
                vals['outstanding_balance'] = vals['original_amount']
        return super(Loan, self).create(vals_list)

    @api.onchange('original_amount')
    def _onchange_original_amount(self):
        if not self.outstanding_balance:
            self.outstanding_balance = self.original_amount

    def unlink(self):
        for rec in self:
            if rec.outstanding_balance < (rec.original_amount - 0.01):
                raise UserError(_(
                    'No se puede eliminar el préstamo "%s" porque ya tiene pagos procesados. '
                    'Por favor, cancele o revierta los pagos asociados primero.'
                ) % rec.name)
            
            if rec.state not in ['draft']:
                raise UserError(_(
                    'Solo se pueden eliminar préstamos en estado "Borrador". '
                    'El préstamo "%s" está en estado "%s".'
                ) % (rec.name, rec.state))
                
        return super(Loan, self).unlink()

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

    def action_register_payment(self):
        self.ensure_one()
        return {
            'name': 'Registrar Pago de Cuota',
            'type': 'ir.actions.act_window',
            'res_model': 'loan.payment.assistant',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_loan_id': self.id,
                'default_payment_journal_id': False
            }
        }
    
    # ELIMINADO: _onchange_payment_term (Causante del error)