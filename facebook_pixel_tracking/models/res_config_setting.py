# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from ast import literal_eval

from odoo import api, fields, models

from ast import literal_eval

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


    @api.depends('website_id')
    def has_facebook_pixel(self):
        self.has_facebook_pixel = bool(self.facebook_pixel_key)

    def inverse_has_facebook_pixel(self):
        if not self.has_facebook_pixel:
            self.facebook_pixel_key = False

    facebook_pixel_key = fields.Char('Facebook pixel key', related='website_id.facebook_pixel_key', readonly=False)
    has_facebook_pixel = fields.Boolean("Facebook Pixel", compute=has_facebook_pixel, inverse=inverse_has_facebook_pixel)
