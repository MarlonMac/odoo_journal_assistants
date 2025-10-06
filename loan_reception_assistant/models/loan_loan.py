# -*- coding: utf-8 -*-
from odoo import models, fields, _

class Loan(models.Model):
    _inherit = 'loan.loan'

    state = fields.Selection([
        ('draft', 'Borrador'),
        ('active', 'Activo'),
        ('paid', 'Pagado'),
    ], string='Estado', required=True, default='draft', tracking=True)

    def action_register_reception(self):
        self.ensure_one()
        return {
            'name': _('Registrar Recepción de Préstamo'),
            'type': 'ir.actions.act_window',
            'res_model': 'loan.reception.assistant',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_loan_id': self.id,
            }
        }