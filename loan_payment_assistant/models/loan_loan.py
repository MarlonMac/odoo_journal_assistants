# -*- coding: utf-8 -*-
from odoo import models, fields, api

class Loan(models.Model):
    _name = 'loan.loan'
    _description = 'Registro de Préstamo'

    name = fields.Char(string='Nombre o Referencia del Préstamo', required=True)
    partner_id = fields.Many2one('res.partner', string='Acreedor', required=True, help="Entidad o persona que otorgó el préstamo.")
    
    original_amount = fields.Monetary(string="Monto Original", required=True, tracking=True)
    outstanding_balance = fields.Monetary(string="Saldo Pendiente", tracking=True)
    
    principal_account_id = fields.Many2one(
        'account.account', 
        string='Cuenta de Pasivo (Capital)', 
        required=True,
        domain="[('deprecated', '=', False), ('company_id', '=', company_id)]",
        help="Cuenta donde se registra la deuda del préstamo. Ej: Préstamos Bancarios por Pagar."
    )
    interest_account_id = fields.Many2one(
        'account.account', 
        string='Cuenta de Gasto (Intereses)', 
        required=True,
        domain="[('deprecated', '=', False), ('company_id', '=', company_id)]",
        help="Cuenta de gasto donde se registrarán los intereses de cada cuota."
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
    payment_assistant_ids = fields.One2many('loan.payment.assistant', 'loan_id', string='Pagos del Asistente')
    payment_count = fields.Integer(string="Pagos Registrados", compute='_compute_payment_count')

    @api.depends('payment_assistant_ids')
    def _compute_payment_count(self):
        for loan in self:
            loan.payment_count = len(loan.payment_assistant_ids)

    @api.onchange('original_amount')
    def _onchange_original_amount(self):
        self.outstanding_balance = self.original_amount

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