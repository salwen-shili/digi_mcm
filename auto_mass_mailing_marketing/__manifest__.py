{
    'name': 'auto_mass_mailing_marketing',
    'description': " Create auto mass mailing marketing ",
    'author': "Takwa",
    'maintainer': 'DIGIMOOV',
    'category': 'Mail',
    'sequence': 15,
    'summary': 'Mail',
    'depends': [
        'sale',
        'mcm_session',
        'digest',
        'base',
    ],
    'description': "Create auto mass mailing marketing",
    'data': [
        'views/inherit_session_add_fields.xml',
        'views/inherit_template_abonnement.xml',
        # 'views/inherit_mail_compose_message.xml',
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