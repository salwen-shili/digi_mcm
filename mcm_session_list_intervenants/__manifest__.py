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

    ],
    'description': "Gestion de la  Liste des intervenants",
    'data': [
        'security/ir.model.access.csv',
        'security/liste_intervenats_security_inherit.xml',
        'views/intervenant_view.xml',
        'views/inherit_intervenant_partner_view.xml',
        # 'views/script_view_portal.xml'
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