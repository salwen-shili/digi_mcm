{
    'name': 'MCM Auth Signup Form',
    'version': '13.0.1.0.0',
    'category': 'Website',
    'summary': ' MCM Auth signup form with extra fields',
    'description': """
        This module add firstname
    """,
    'sequence': 1,
    'author': 'Houssem',
    'website': 'mcm-academy.fr',
    'depends': ['auth_signup','fl_auth_signup'],
    'data': [
        'views/auth_signup_extend_views.xml',
    ],
    'images': [
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3'
}