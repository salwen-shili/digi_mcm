# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models,tools

class ResPartner(models.Model):
    _inherit = "res.partner"
    
    # Function to return user's signatures.
    def get_signatures(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Signatures',
            'view_mode': 'tree,form',
            'res_model': 'res.user.signature',
            'domain': [('user_id.partner_id', '=', self.id)],
            'context': "{'create': False}"
        }

