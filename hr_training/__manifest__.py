# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Training Management',
    'category': 'Hidden',
    'version': '1.0',
    'summary': 'Manage Training of employees',
    'description':
        """
Training for HR
========================

This module introduces training management for employees.
        """,
    'depends': ['hr'],
    'data': [
        'security/hr_training_security.xml',
        'security/ir.model.access.csv',
        'views/hr_views.xml',
    ],
    'installable': True,
    'application': False,
}
