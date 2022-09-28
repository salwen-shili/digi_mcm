# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Onfido',
    'summary': """
        Onfido api integration, OnfidoIDV SDK 9.0.0-beta.5""",
    'version': '1.0',
    'license': 'AGPL-3',
    'category': 'API',
    'author': 'Ines Lahmer, Salwen SHILI',
    'website': '',
    'depends': ['web','base','mcm_session','crm','website','mcm_website_theme','partner_exam','portal'
    ],
    'data': [
        'views/configuration.xml',
        'views/load_document.xml',
        'views/rejected_document.xml',
        'views/partner_add_onfido.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [

    ],
    'development_status': '',
    'application': False,
    'installable': True,
}
