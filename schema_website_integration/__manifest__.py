# Copyright 2022 Salwen SHILI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Schema Website Integration',
    'category': 'Website',
    'summary': 'Schema Website Intergration',
    'version': '1.0.0',
    'license': 'AGPL-3',
    'description': '''
    Includes schema.org script in head of website
    ''',
    'author': 'Salwen SHILI',
    'depends': [
        'website',
        'web'
    ],
    'data': [
        'templates/website_template.xml',
    ],
    'images': [
    ],
    'installable': True,
    'application': False,
}