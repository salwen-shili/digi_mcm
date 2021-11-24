# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'digimoov website templates',
    'description': " digimoov website templates ",
    'author': "Houssem",
    'maintainer': 'DIGIMOOV',
    'category': 'website',
    'sequence': 15,
    'summary': 'website',
    'depends': [
        'base',
        'website_sale',
        'website',
        'web',
        'theme_centric',
        'digimoov_sessions_modules',
    ],
    'description': "digimoov website templates",
    'data': [
        'views/homepage.xml',
        # 'views/homepage2.xml',
        'views/faq.xml',
        'views/maintenance.xml',
        'views/financement.xml',
        'views/examen.xml',
        'views/formation.xml',
        'views/quisommesnous.xml',
        'views/noscentre.xml',
        'views/footer_template.xml',
        'views/website_sale.xml',
        'views/conditions.xml',
        'views/services.xml',
        'views/completer_mon_dossier_cpf.xml',
        'views/template.xml',
        'views/cpf_thanks.xml',
        'views/portal_my_details.xml',
        'views/confidentialite.xml',
        'views/feliciations.xml',
        'views/validation.xml',
        'views/contract_payment_notification.xml',
        'views/my_account_progress.xml',
        'views/cart_progressbar.xml',
        'views/edit_info.xml',
        # 'views/charger_mes_documents'
        # 'views/sitemap.xml',

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
