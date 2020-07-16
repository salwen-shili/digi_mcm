# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class Session(models.Model):
    _name = 'mcm.session'
    _description = 'session de formation'

    product_id=fields.Many2one('product.template',string="Formation",required=True)
    start_date=fields.Date()
    end_date=fields.Date()
    state=fields.Many2one('res.country.state',string="Département")
    partner_ids=fields.One2many('res.partner','session_id','Partners')