# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from ast import literal_eval

from odoo import api, fields, models

from ast import literal_eval

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


    @api.depends('website_id')
    def has_microsoft_tracking(self):
        self.has_microsoft_tracking = bool(self.microsoft_tracking_key)

    def inverse_has_microsoft_tracking(self):
        if not self.has_microsoft_tracking:
            self.microsoft_tracking_key = False

    microsoft_tracking_key = fields.Char('Microsoft Tracking key', related='website_id.microsoft_tracking_key', readonly=False)
    has_microsoft_tracking = fields.Boolean("Microsoft Tracking", compute=has_microsoft_tracking, inverse=inverse_has_microsoft_tracking)
