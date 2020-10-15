# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Partner mail Documents',
    'description': " Create mail template of send documents ",
    'author': "Houssem",
    'maintainer': 'DIGIMOOV',
    'category': 'Mail',
    'sequence': 15,
    'summary': 'Mail',
    'depends': [
        'sale',
        'mail',
    ],
    'description': "Create mail template of send documents",
    'data': [
        'data/mail_data.xml',
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