# Copyright 2018 Pierre Faniel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Tidio Integration',
    'category': 'Website',
    'summary': 'Tidio - Odoo integration',
    'version': '1.0.0',
    'license': 'AGPL-3',
    'description': '''
Includes Tidio script before the closing </body>
    ''',
    'author': 'DIGIMOOV,Houssem Ben Mbarek',
    'depends': [
        'website',
        'web'
    ],
    'data': [
        'templates/website_layout.xml',
    ],
    'images': [
        'static/description/tidio_icon.png',
    ],
    'installable': True,
    'application': False,
}


