# -*- coding: utf-8 -*-
{
    'name': "EHCS Sign up Captcha",
    'summary': """
        Add reCAPTCHA in your Sign up page.""",
    'description': """
        CAPTCHA stands for Completely Automated Public Turing Test to Tell Computers and Humans Apart. 
        It's goal is to check if a user is a real person or a bot.
    """,
    'author': "ERP Harbor Consulting Services",
    'website': "http://www.erpharbor.com",
    'license': 'AGPL-3',
    'category': 'Web',
    'version': '13.0.1.0.0',
    'depends': ['auth_signup'],
    'data': [
        'views/signup_templates.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
}
