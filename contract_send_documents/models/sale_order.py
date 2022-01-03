# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models,SUPERUSER_ID
from odoo.exceptions import AccessError, UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def write(self,values):
        order=super(SaleOrder,self).write(values)
        subtype_id = self.env['ir.model.data'].xmlid_to_res_id('mt_note')
        if 'signed_by' in values and 'signed_on' in values and 'signature' in values and self.state != 'cancel' and self.state != 'draft':
            message = self.env['mail.message'].sudo().create({
                'subject': 'Contrat signé',
                'model': 'res.partner',
                'res_id': self.partner_id.id,
                'message_type': 'notification',
                'subtype_id': subtype_id,
                'body': 'Contrat signé par ' + str(values['signed_by']),
            })
            for order in self:
                order.partner_id.step = 'finish'
        return order