# -*- coding: utf-8 -*-
from odoo import models, fields

class Loan(models.Model):
    _name = 'loan.loan'
    _description = 'Registro de Préstamo'

    name = fields.Char(string='Nombre o Referencia del Préstamo', required=True)
    partner_id = fields.Many2one('res.partner', string='Acreedor', required=True, help="Entidad o persona que otorgó el préstamo.")
    
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