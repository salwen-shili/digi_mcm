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
        'views/renonce_template.xml',
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
        'views/nos-formations.xml',
        # 'views/test1.xml',
        # 'views/test2.xml',
        # 'views/test3.xml',
        # 'views/test4.xml',
        # 'views/test5.xml',
        # 'views/test7.xml',
        'views/test8.xml',
        'views/test9.xml',
        'views/test10.xml',

        'views/attestation-transport-leger-marchandises-carte-bleu.xml',
        'views/formation_capacité_de_transport_lourd_de_marchandise.xml',

        # 'views/charger_mes_documents'
        # 'views/sitemap.xml',

        'views/habilitation-eletrique.xml',
        # page de destination
        'views/devenir-coursier-paris.xml',
        'views/capacité-de-transport-marseille.xml',
        'views/livreur-de-colis-nantes.xml',
        'views/devenir-coursier-lyon.xml',
        'views/capacitaire-transport-bordeaux.xml',
        # page de blog
        # 'views/blog/website_blog_posts.xml',

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
