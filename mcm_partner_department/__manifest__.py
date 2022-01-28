# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Partner TAXI department',
    'description': " Département de client lorsqu'il choisi formation taxi  ",
    'author': "Houssem",
    'maintainer': 'DIGIMOOV',
    'category': 'Partner',
    'sequence': 15,
    'summary': 'Partner',
    'depends': [
        'base',
        'mcm_session',
        'website_sale',
    ],
    'description': "Département de client lorsqu'il choisi formation taxi  ",
    'data': [
        'data/base_automation_statut_client.xml',
        'views/partner.xml',
        'views/templates.xml',
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
