# -*- coding: utf-8 -*-
{
    'name': 'Asistente de Pago de Préstamos',
    'version': '16.0.1.1.0',
    'summary': 'Asistente para registrar pagos de préstamos, separando capital e intereses.',
    'description': """
        Simplifica el registro de pagos de cuotas de préstamos, generando un asiento
        contable de tres líneas (capital, intereses, salida de banco) a partir
        de un formulario sencillo.
    """,
    'author': 'Marlon Macario',
    'category': 'Accounting/Accounting',
    'depends': [
        'journal_entry_assistant_base',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/loan_payment_assistant_security.xml',
        'data/sequence_data.xml',
        'views/loan_loan_views.xml',
        'views/loan_payment_assistant_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}