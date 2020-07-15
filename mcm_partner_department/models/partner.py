# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class resComapny(models.Model):
    _inherit = "res.partner"

    partner_departement = fields.Selection(selection=[
        ('59000', '59000'),
        ('62000', '62000'),
    ], string='Département')