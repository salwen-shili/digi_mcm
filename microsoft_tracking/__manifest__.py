{
    'name': 'Microsoft Tracking Integration',
    'version': '13.0.1.0.0',
    'category': 'Website',
    'summary': 'Microsoft Tracking Integration',
    'description': """
        This module integrate microsoft tracking in website
    """,
    'author': 'Houssem',
    'depends': ['base','website'],
    'data': [
        'views/res_config_setting.xml',
        'views/website_templates.xml',
    ],
    'images': [
        'static/description/apps_facebook-pixel.png',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3'
}