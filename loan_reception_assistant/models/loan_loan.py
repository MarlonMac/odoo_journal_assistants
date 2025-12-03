# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class Loan(models.Model):
    _name = 'loan.loan' 
    _inherit = 'loan.loan'  
    
    # RELACIÓN CON EL ASISTENTE DE RECEPCIÓN
    reception_ids = fields.One2many('loan.reception.assistant', 'loan_id', string='Recepciones')
    reception_count = fields.Integer(compute='_compute_reception_count')

    @api.depends('reception_ids')
    def _compute_reception_count(self):
        for rec in self:
            rec.reception_count = len(rec.reception_ids)

    def write(self, vals):
        for rec in self:
            if rec.state in ['active', 'paid']:
                protected_fields = ['original_amount', 'partner_id', 'principal_account_id', 'interest_account_id', 'company_id']
                if any(field in vals for field in protected_fields):
                    raise UserError(_('No se pueden modificar las condiciones estructurales de un préstamo Activo o Pagado. Revierta las transacciones primero.'))
        return super(Loan, self).write(vals)

    # ACCIÓN SMART BUTTON: Ver Recepción
    def action_view_reception(self):
        self.ensure_one()
        return {
            'name': 'Recepción',
            'type': 'ir.actions.act_window',
            'res_model': 'loan.reception.assistant',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.reception_ids.ids)],
            'context': dict(self._context, create=False)
        }

    # ACCIÓN HEADER: Registrar Recepción
    def action_register_reception(self):
        self.ensure_one()
        return {
            'name': 'Registrar Recepción',
            'type': 'ir.actions.act_window',
            'res_model': 'loan.reception.assistant',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_loan_id': self.id,
            }
        }