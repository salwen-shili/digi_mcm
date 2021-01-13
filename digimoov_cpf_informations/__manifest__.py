# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Digimoov Partner CPF Informations',
    'description': " Rajout des champs ",
    'author': "Houssem",
    'maintainer': 'DIGIMOOV',
    'category': 'Partner',
    'sequence': 15,
    'summary': 'Partner',
    'depends': [
        'base',
        'mcm_cpf_partner',
    ],
    'description': "Rajout des champs",
    'data': [
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
