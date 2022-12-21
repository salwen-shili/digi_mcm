# Copyright 2018 Pierre Faniel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Metricool tracking Odoo Integration',
    'category': 'Website',
    'summary': 'Metricool tracking Odoo Integration',
    'version': '1.0.0',
    'license': 'AGPL-3',
    'description': '''
Includes Metricool tracking script in head of website
    ''',
    'author': 'Houssem Ben Mbarek',
    'depends': [
        'website',
        'web'
    ],
    'data': [
        'templates/website_layout.xml',
        'views/website_config_settings.xml',
        'views/website_views.xml',
    ],
    'images': [
    ],
    'installable': True,
    'application': False,
}


