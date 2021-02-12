# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Digimoov sessions',
    'description': " Personaliser la vue session de digimoov",
    'author': "Houssem",
    'maintainer': 'DIGIMOOV',
    'category': 'Session',
    'sequence': 15,
    'summary': 'Session',
    'depends': [
        'website',
        'website_sale',
        'base',
        'product',
        'portal',
        'mcm_session',
        'mcm_website_theme',
        'sale',
    ],
    'description': "Rajout des champs",
    'data': [
        'data/sign_data.xml',
        'security/sign_security.xml',
        'views/session.xml',
        'views/module.xml',
        'views/templates.xml',
        'views/template.xml',
        'views/sale_portal_templates.xml',
        'views/sale_order_report.xml',
        'views/sign_request.xml',
        'views/sign_template.xml',
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
