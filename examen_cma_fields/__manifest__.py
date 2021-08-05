# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'cma_exam_result_fields ',
    'description': " Rajout des champs Examen théorique et pratique CMA ",
    'author': "Houssem",
    'maintainer': 'DIGIMOOV',
    'category': 'Contact',
    'sequence': 15,
    'summary': 'Contact',
    'depends': [
        'base',
        'mcm_session',
        'sale',
    ],
    'description': " Rajout des champs Examen théorique et pratique CMA ",
    'data': [
        'security/ir.model.access.csv',
        'security/session_security.xml',
        'views/res_partner_sessions.xml',
        'views/res_partner.xml',
        'data/ir_actions.server.xml',

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
