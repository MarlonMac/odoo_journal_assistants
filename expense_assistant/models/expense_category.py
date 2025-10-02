# -*- coding: utf-8 -*-
from odoo import models, fields

class ExpenseCategory(models.Model):
    _name = 'expense.category'
    _description = 'Categoría de Gasto Corporativo'

    name = fields.Char(string='Nombre de la Categoría', required=True)
    expense_account_id = fields.Many2one(
        'account.account', 
        string='Cuenta Contable de Gasto', 
        required=True, 
        domain="[('deprecated', '=', False), ('company_id', '=', company_id)]", 
        help="La cuenta contable que se usará por defecto para los gastos de esta categoría."
    )
    company_id = fields.Many2one(
        'res.company', 
        string='Compañía', 
        required=True, 
        default=lambda self: self.env.company
    )