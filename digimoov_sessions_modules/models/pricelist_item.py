# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models,api


class PricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    price_difference=fields.Monetary('Différence de prix',compute='compute_price_difference',store=True)

    @api.depends('product_tmpl_id','fixed_price')
    def compute_price_difference(self):
        for rec in self:
            rec.price_difference=rec.product_tmpl_id.list_price-rec.fixed_price