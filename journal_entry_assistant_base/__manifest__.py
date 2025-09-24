# -*- coding: utf-8 -*-
{
    'name': 'Asistente de Asientos de Diario (Base)',
    'version': '16.0.1.0.0',
    'summary': 'Módulo base para el ecosistema de asistentes de asientos contables.',
    'description': """
        Este módulo proporciona el modelo abstracto y la lógica común
        (estados, botones, chatter) para todos los módulos del ecosistema
        de asistentes de asientos de diario. No tiene interfaz de usuario visible.
    """,
    'author': 'Marlon Macario',
    'category': 'Accounting/Accounting',
    'depends': ['account', 'mail'],
    'data': [
        'security/security.xml',        
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}