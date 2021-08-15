{
    'name': 'mcm_session_list_intervenants',
    'description': "Gestion de la  Liste des intervenants",
    'author': "Seif",
    'maintainer': 'DIGIMOOV',
    'category': 'Session',
    'sequence': 15,
    'summary': 'Les informations des intervenants',
    'depends': [
        'base',
        'contacts',
        'documents',
        'mcm_session',
        'sale',
        'base',
        'contacts',
        'account',
        'partner_exam',
        'account',
        'crm',
        'mcm_add_fields',
        'examen_cma_fields',
        'plateforme_pedagogique',
        'account_reports',
        'calendly_api_integration',

    ],
    'description': "Gestion de la  Liste des intervenants",
    'data': [
        'security/ir.model.access.csv',
        'security/liste_intervenats_security_inherit.xml',
        'views/intervenant_view.xml',
        'views/inherit_intervenant_partner_view.xml',
        'views/inherit_session_view_intervenant.xml',
        # 'views/inherit_views_partner_invisible_fields_intervenants.xml',
        'views/add_js_intervenant.xml',


    ],
    # 'js': ['static/src/js/portal_intervenant.js'],
    'qweb': [],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}