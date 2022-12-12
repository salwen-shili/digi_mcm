{
    "name": "Odoo SendinBlue Connector",
    "version": "13.0.1.3",
    "category": "Marketing",
    'summary': 'Integrate & Manage SendinBlue Operations from Odoo',

    "depends": ["mass_mailing"],

    'data': [
        'data/ir_cron.xml',
        'data/ir_sequence_data.xml',
        'views/assets.xml',
        'views/sendinblue_accounts_view.xml',
        'views/sendinblue_lists_view.xml',
        'views/sendinblue_folder_view.xml',
        'wizard/import_export_operation_view.xml',
        'views/mass_mailing_contact_view.xml',
        'views/mass_mailing_list_view.xml',
        'views/sendinblue_template_view.xml',
        'views/mass_mailing_view.xml',
        'views/res_partner_views.xml',
        'views/sendinblue_senders_view.xml',
        'views/sendinblue_queue_process_view.xml',
        'wizard/partner_export_update_wizard.xml',
        'security/ir.model.access.csv'
    ],

    'images': ['static/description/sendinblue_odoo.png'],

    "author": "Teqstars",
    "website": "https://teqstars.com",
    'support': 'support@teqstars.com',
    'maintainer': 'Teqstars',
    "description": """
        - Manage your sendinblue operation from Odoo
        - Integration sendinblue
        - Connector sendinblue
        - sendinblue Connector
        - Odoo sendinblue Connector
        - sendinblue integration
        - sendinblue odoo connector
        - sendinblue odoo integration
        - odoo sendinblue integration
        - odoo integration with sendinblue
        - odoo teqstars apps
        - teqstars odoo apps
        - manage audience
        - manage champaign
        - email Marketing
        - sendinblue marketing
        - odoo and sendinblue
        - marketing email
        - sms marketing
        - marketing sms
        """,

    'demo': [],
    'license': 'OPL-1',
    'live_test_url': 'http://bit.ly/2wwoyL5',
    'auto_install': False,
    "installable": True,
    'application': True,
    'qweb': [],
    "price": "169.00",
    "currency": "EUR",
}
