# -*- coding: utf-8 -*-
{
    'name': 'Asistente de Movimientos de Patrimonio',
    'version': '16.0.1.1.1',
    'summary': 'Asistente para registrar aportes de capital y pago de dividendos.',
    'description': """
        Simplifica el registro de transacciones de patrimonio como aportes de socios
        o el pago de dividendos, generando los asientos de diario correspondientes.
    """,
    'author': 'Marlon Macario',
    'website': "https://github.com/sponsors/MarlonMac/",
    'category': 'Accounting/Accounting',
    'depends': [
        'journal_entry_assistant_base',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/equity_movement_assistant_security.xml',
        'data/sequence_data.xml',
        'views/equity_movement_category_views.xml',
        'views/equity_movement_assistant_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}