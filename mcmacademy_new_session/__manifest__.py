# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Session',
    'description': """
Modifications sur le module des sessions
    """,
    'author': "MCM",
    'maintainer': 'MCM',
    'category': '',
    'sequence': 15,
    'summary': 'Sessions mcm academy',
    'depends': [
        'product',
        'base',
        'fl_auth_signup',
        'account',
        'website_sale',
        'sale',
        'payment',
        'mcm_add_fields',
        'portal',
        'mcm_session',
        'session_ville',
    ],
    'description': """
Modifications sur le module des sessions
    """,
    'data': [
        # 'data/modules.xml',
        'views/views.xml',
        # 'data/villes.xml',

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
