# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models,api


class Sale(models.Model):
    _inherit = "sale.order"

    ville = fields.Selection(selection=[
        ('bordeaux', 'Bordeaux'),
        ('lille', 'Lille'),
        ('lyon', 'Lyon'),
        ('marseille', 'Marseille'),
        ('nantes', 'Nantes'),
        ('paris', 'Paris'),
        ('strasbourg', 'Strasbourg'),
        ('toulouse', 'Toulouse'),
    ], string='Ville')
    exam_center_error= fields.Char('Error Exam Center',default='')
    exam_date_error= fields.Char('Error Exam Center',default='')
    conditions_error=fields.Char('Error Condition',default='')