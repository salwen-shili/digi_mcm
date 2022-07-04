# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'API Evalbox Integration',
    'description': "",
    'author': "Takwa MEJRI",
    'maintainer': 'DIGIMOOV',
    'website': "https://www.digimoov.fr/",
    'category': 'Partner',
    'sequence': 21,
    'summary': '',
    'depends': ['partner_exam'

                ],
    'description': "",
    'data': ['views/inherit_session_form_view.xml',
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
