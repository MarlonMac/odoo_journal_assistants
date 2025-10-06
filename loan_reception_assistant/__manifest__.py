# -*- coding: utf-8 -*-
{
    'name': 'Asistente de Recepción de Préstamos',
    'version': '16.0.1.0.0',
    'summary': 'Asistente para registrar el ingreso de fondos de un préstamo.',
    'description': """
        Introduce un flujo para registrar la recepción del dinero de un préstamo,
        activando el préstamo para que puedan comenzar a registrarse los pagos.
    """,
    'author': 'Marlon Macario',
    'category': 'Accounting/Accounting',
    'depends': [
        'loan_payment_assistant',
        'expense_assistant',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/loan_reception_assistant_security.xml',
        'data/sequence_data.xml',
        'views/loan_loan_views.xml',
        'views/loan_reception_assistant_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}