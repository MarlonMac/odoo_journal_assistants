# -*- coding: utf-8 -*-
from odoo import models, fields

class AssetCategory(models.Model):
    _name = 'asset.category'
    _description = 'Categoría de Activo'

    name = fields.Char(string='Nombre de la Categoría', required=True)
    asset_account_id = fields.Many2one(
        'account.account',
        string='Cuenta Contable de Activo',
        required=True,
        domain="[('deprecated', '=', False), ('company_id', '=', company_id)]",
        help="La cuenta contable que se usará para los activos de esta categoría."
    )
    company_id = fields.Many2one(
        'res.company', 
        string='Compañía', 
        required=True, 
        default=lambda self: self.env.company
    )