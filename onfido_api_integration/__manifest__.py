# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Onfido',
    'summary': """
        Onfido api integration""",
    'version': '1.0',
    'license': 'AGPL-3',
    'category': 'API',
    'author': 'Ines Lahmer',
    'website': '',
    'depends': ['web','base','mcm_session','crm','website','mcm_website_theme','partner_exam','portal'
    ],
    'data': [
        'views/configuration.xml',
        'views/load_document.xml',
        'views/rejected_document.xml',
    ],
    'demo': [

    ],
    'development_status': '',
    'application': False,
    'installable': True,
}
