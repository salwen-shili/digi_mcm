# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
#change document
{
    'name': 'Partner Documents',
    'description': " App to upload and manage your documents. ",
    'author': "Houssem",
    'maintainer': 'DIGIMOOV',
    'category': 'Contact',
    'sequence': 15,
    'summary': 'Contact',
    'depends': [
        'base',
        'mail',
        'helpdesk',
        'documents',
        'portal',
        'web',
    ],
    'description': "App to upload and manage your documents.",
    'data': [
        'views/documents_document.xml',
        'views/partner_documents_templates.xml',
        'views/templates.xml',
        'views/document_template.xml',
        'views/digimoov_template_documents.xml',
        'views/digimoov_template_documents1.xml',
        'views/mcm_template_documents.xml',
        'views/digimoov_documents_manual.xml',
        'views/mcm_documents_manual.xml',
        'data/mail_template.xml',
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