# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Adresse facturation',
    'description': """
ajouter addresse de facturation à la vue client
    """,
    'author': "Houssem",
    'maintainer': 'DIGIMOOV',
    'category': 'Session',
    'sequence': 15,
    'summary': 'Partner',
    'depends': [
        'mcm_session',
    ],
    'description': """
ajouter addresse de facturation à la vue client
    """,
    'data': [
        'views/partner.xml',
    ],
    'qweb': [],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
