# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Partner Exam',
    'description': " Rajout note d'examen de condidat  ",
    'author': "Houssem",
    'maintainer': 'DIGIMOOV',
    'category': 'Partner',
    'sequence': 15,
    'summary': 'Partner',
    'depends': [
        'base',
        'mcm_session',
        'contacts',
    ],
    'description': "Rajout note d'examen de condidat ",
    'data': [
        'security/ir.model.access.csv',
        'views/partner.xml',
        'views/notes_examens_partner.xml',
        'views/add_signature.xml',
        'report/generation_covocation_en_pdf.xml',
        'report/menu.xml',
        'report/generate_releve_note_reussite.xml',
        'report/releve_note_ajournement.xml',
        'report/convocation_contact.xml',
    ],
    'qweb': [],
    'images': ['static/src/img/footer.png',
               'static/src/img/header.png',
               'static/src/img/signature.png', ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
