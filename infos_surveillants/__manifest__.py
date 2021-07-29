{
    'name': 'Les infos des surveillants',
    'description': "Les infos des surveillants",
    'author': "Mejri Takwa",
    'maintainer': 'DIGIMOOV',
    'category': 'Partner',
    'sequence': 17,
    'summary': 'Les infos des surveillants',
    'depends': [
        'base',
        'contacts',
        'account',
        'mcm_session',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/inherit_partner_view.xml',
        'views/surveillants_view.xml',
        'views/inherit_session_view.xml',
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
