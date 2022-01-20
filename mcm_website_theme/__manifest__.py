# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'mcm academy website theme',
    'version' : '1.1',
    'summary': 'Website',
    'sequence': 15,
    'description': """
add css and js files to website model
    """,
    'category': 'website',
    'website': 'https://www.odoo.com/page/billing',
    # 'images' : ['images/accounts.jpeg','images/bank_statement.jpeg','images/cash_register.jpeg','images/chart_of_accounts.jpeg','images/customer_invoice.jpeg','images/journal_entries.jpeg'],
    'depends' : ['web','website','website_sale','sale','payment','mcm_session','mcm_cpf_partner'],
    'data': [
        'security/ir.model.access.csv',
        'security/questionnaire_security.xml',
        # 'views/ressources.xml',
      
        'views/templates.xml',
        'views/product_public_category.xml',
        'views/payment_acquirer.xml',
        'views/formation_taxi.xml',
        'views/formation_vmdtr.xml',
        'views/formation_vtc.xml',
        'views/website_sale.xml',
        'views/faq.xml',
        'views/examen.xml',
        'views/quisommesnous.xml',
        'views/contact.xml',
        'views/financement.xml',
        'views/partner.xml',
        'views/validation.xml',
        'views/homepage.xml',
        'views/sale_order.xml',
        'views/edit_info.xml',
        # 'views/footer_custom.xml',
        'views/questionnaire.xml',
        'views/conditions.xml',
        'views/felicitations.xml',
        'views/website_sale/cart_multistep_integration.xml',
        'views/website_sale/template.xml',
        'views/custom_footer.xml',
        'views/test-bold.xml',
        'views/facture.xml'
    ],

    'installable': True,
    'application': False,
    'auto_install': False,
}
