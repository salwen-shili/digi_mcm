# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Email CC BCC With Reply to option in Odoo',
    'version': '13.0.0.0',
    'category': 'Extra Tools',
    'summary': 'Email CC BCC With Reply to Option Odoo App helps users to send email to multiple partners in CC and multiple partners in BCC of mail with specific reply to option. Users can select partners for CC, BCC and also make BCC or CC visible in emails by enabling them from general settings, according to the requirement.Also have option for Customer Email Reply-which helps to add Reply-To to every mail. User can set deafult Reply-To customer to mail from the general settings.',
    'description' :"""
      
        Email CC BCC With Reply to Option in Odoo,
        Email CC in odoo,
        Email BCC in odoo,
        Email Reply to option in odoo,
        Default CC & BCC for Email in odoo,
        Default Reply to for Email in odoo,
        Send Mail to the Customers with CC & BCC in odoo,
        Send Mail to the Customers with Reply to in odoo,

    """,
    'author': 'BrowseInfo',
    "price": 00,
    "currency": 'EUR',
    'website': 'https://www.browseinfo.in',
    'depends': ['sale_management','account'],
    'data': [
        'views/res_settings_views.xml',
        'views/sale_mail_views.xml',
        'views/account_mail_views.xml',
        'views/mail_views.xml',
    
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'live_test_url':'https://youtu.be/vt8mY1RwBg4',
    "images":['static/description/Banner.png'],
}