# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Partner CPF Validation',
    'description': " Validate cpf  ",
    'author': "Houssem",
    'maintainer': 'DIGIMOOV',
    'category': 'Partner',
    'sequence': 15,
    'summary': 'Partner',
    'depends': [
        'base',
        'mcm_session',
        'mcm_cpf_partner',
        'portal_contract',
        'helpdesk',
    ],
    'description': " Validate cpf  ",
    'data': [
        'views/templates.xml',
        'views/module.xml',
        'views/session.xml',
        'views/res_partner.xml',
    ],
    'qweb': [],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
