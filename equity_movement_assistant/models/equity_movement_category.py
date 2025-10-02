# -*- coding: utf-8 -*-
from odoo import models, fields

class EquityMovementCategory(models.Model):
    _name = 'equity.movement.category'
    _description = 'Categoría de Movimiento de Patrimonio'

    name = fields.Char(string='Nombre de la Categoría', required=True)
    movement_type = fields.Selection([
        ('contribution', 'Entrada (Aportes de Capital)'),
        ('dividend', 'Salida (Declaración de Dividendos)')
    ], string='Tipo de Movimiento', required=True)
    
    equity_account_id = fields.Many2one(
        'account.account', 
        string='Cuenta de Patrimonio', 
        required=True,
        domain="[('deprecated', '=', False), ('company_id', '=', company_id)]",
        help="La cuenta de patrimonio afectada. Ej: Capital Social, Utilidades Retenidas."
    )
    liability_account_id = fields.Many2one(
        'account.account', 
        string='Cuenta de Pasivo (Crédito para Dividendos)', 
        domain="[('deprecated', '=', False), ('company_id', '=', company_id)]",
        help="La cuenta de deuda que se crea al declarar un dividendo. Ej: Dividendos por Pagar."
    )
    company_id = fields.Many2one(
        'res.company', 
        string='Compañía', 
        required=True, 
        default=lambda self: self.env.company
    )