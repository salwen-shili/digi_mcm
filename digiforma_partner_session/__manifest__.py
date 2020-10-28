# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'digiforma sessions',
    'version': '1.1',
    'summary': 'partner',
    'sequence': 15,
    'description': """
add page for digiforma sessions
    """,
    'category': 'partner',
    'website': 'https://www.mcm-academy.fr/',
    'depends': ['base'],
    'data': [
        'views/resPartner.xml',
    ],

    'installable': True,
    'application': False,
    'auto_install': False,
}