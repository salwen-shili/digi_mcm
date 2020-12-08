# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models,SUPERUSER_ID

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def write(self,values):
        order=super(SaleOrder,self).write(values)
        if 'signed_by' in values and 'signed_on' in values and 'signature' in values and self.state != 'cancel' and self.state != 'draft':
            historic = self.env['partner.sessions'].sudo().create({
                'client_id': self.partner_id,
                'session_id': self.session_id,
                'company_id': self.company_id
            })
        return order

