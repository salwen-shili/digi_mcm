# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Crm marketing automation',
    'summary': """
        Crm integration""",
    'version': '1.0',
    'license': 'AGPL-3',
    'category': 'API',
    'author': 'MCM ACADEMY',
    'website': '',
    'depends': ['base','crm','sale','plateforme_pedagogique','calendly_api_integration',
    ],
    'data': [
      'security/security.xml',
      'security/ir.model.access.csv',
      'views/crm_lead.xml',
      'views/crm_stage.xml',
      'data/ir_cron.xml',
      'views/assets.xml',
      'views/partner.xml',
    ],
    'demo': [
    ],
    'development_status': '',
    'application': False,
    'installable': True,
    'qweb' : [
     'static/src/xml/qweb.xml',
    ]
}
