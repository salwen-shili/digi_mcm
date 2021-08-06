# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Session Ville',
    'description': "Ce module contient principalement les deux classe pour les villes "
                   "et les adresses des villes avec ses informations",
    'author': "Mejri Takwa",
    'maintainer': 'DIGIMOOV',
    'category': 'Partner',
    'sequence': 15,
    'summary': 'Automatisation des villes dans la session et dans les autre enplacement '
               'telque module vente, client, module',
    'depends': [
        'base',
        'mcm_session',
        'partner_exam',
        'auto_mass_mailing_marketing',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/address_class_exams.xml',
        'views/session_ville_view.xml',
        'views/adresse_centre_examen.xml',
        'views/inherit_mcmacademy_session.xml',
        'views/inherit_info_exam.xml',
        'views/inherit_res_partner.xml',
        'views/inherit_mcmacademy_module.xml',
        'views/res_partner_adresse_view.xml',
    ],
    'qweb': [],
    'images': [],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
