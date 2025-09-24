# -*- coding: utf-8 -*-
{
    'name': 'Asistente de Compra de Activos',
    'version': '16.0.1.0.0',
    'summary': 'Asistente para registrar la compra de activos fijos.',
    'description': """
        Utiliza un formulario simplificado para registrar la compra de activos fijos
        (equipo de cómputo, vehículos, etc.), generando el asiento de diario inicial
        para su posterior gestión y depreciación.
    """,
    'author': 'Marlon Macario',
    'category': 'Accounting/Accounting',
    'depends': [
        'journal_entry_assistant_base',
        'base_accounting_kit', # <-- Dependencia de Cybrosys para cuentas contables
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'views/asset_category_views.xml',
        'views/asset_purchase_assistant_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}