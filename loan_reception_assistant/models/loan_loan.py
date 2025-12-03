# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class Loan(models.Model):
    _name = 'loan.loan' 
    _inherit = 'loan.loan'  
    
    def write(self, vals):
        # Mantenemos solo la lógica de seguridad extra
        for rec in self:
            if rec.state in ['active', 'paid']:
                protected_fields = ['original_amount', 'partner_id', 'principal_account_id', 'interest_account_id', 'company_id']
                if any(field in vals for field in protected_fields):
                    raise UserError(_('No se pueden modificar las condiciones estructurales de un préstamo Activo o Pagado. Revierta las transacciones primero.'))
        return super(Loan, self).write(vals)