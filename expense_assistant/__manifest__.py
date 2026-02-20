# -*- coding: utf-8 -*-
{
    'name': 'Asistente de Gastos Corporativos',
    'version': '16.0.1.1.1',
    'summary': 'Asistente para registrar gastos, reembolsos y facturas por pagar.',
    'description': """
        Utiliza un formulario simplificado para registrar gastos corporativos,
        generando los asientos de diario correspondientes para su validación.
        Este módulo forma parte del Ecosistema de Asistentes de Asientos Contables.
    """,
    'author': 'Marlon Macario',
    'category': 'Accounting/Accounting',
    'depends': [
        'journal_entry_assistant_base',
        'hr'
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/expense_assistant_security.xml',
        'data/sequence_data.xml',
        'views/expense_category_views.xml',
        'views/expense_assistant_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}