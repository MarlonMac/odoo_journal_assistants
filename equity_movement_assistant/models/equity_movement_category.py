# -*- coding: utf-8 -*-
from odoo import models, fields

class EquityMovementCategory(models.Model):
    _name = 'equity.movement.category'
    _description = 'Categoría de Movimiento de Patrimonio'

    name = fields.Char(string='Nombre de la Categoría', required=True)
    movement_type = fields.Selection([
        ('contribution', 'Entrada (Aportes de Capital)'),
        ('dividend', 'Salida (Pago de Dividendos)')
    ], string='Tipo de Movimiento', required=True)
    
    equity_account_id = fields.Many2one(
        'account.account', 
        string='Cuenta de Patrimonio', 
        required=True,
        domain="[('deprecated', '=', False)]",
        help="La cuenta de patrimonio afectada. Ej: Capital Social, Utilidades Retenidas."
    )