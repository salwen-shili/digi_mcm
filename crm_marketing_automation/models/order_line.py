# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
#
from odoo import api, fields, models, _
import calendar
from datetime import date, datetime
import logging
_logger = logging.getLogger(__name__)
class SaleLine(models.Model):
     _inherit = 'sale.order.line'
    # @api.model
    # def create(self, vals):
    #     print('********',vals)
    #     res = super(SaleLine, self).create(vals)
    #     print('drafttt', vals)
    #     order_id = vals['order_id']
    #     product_id=vals['product_id']
    #     product=self.env['product.product'].sudo().search([('id',"=",product_id)])
    #     if product:
    #         code=product.default_code
    #         if code=="vtc_bolt":
    #             sale=self.env['sale.order'].sudo().search([('id',"=",order_id)])
    #             if sale:
    #                 partner_id=sale.partner_id
    #                 sale.change_stage_lead("Bolt-Prospection", partner_id)
    #     return res