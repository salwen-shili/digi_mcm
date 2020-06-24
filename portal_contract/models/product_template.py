# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class Session(models.Model):
    _inherit = 'product.template'

    formation_price=fields.Monetary('Prix Formation',compute='_compute_price_formation',store=True)

