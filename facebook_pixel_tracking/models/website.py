# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from ast import literal_eval

from odoo import api, fields, models


class Website(models.Model):

    _inherit = "website"

    facebook_pixel_key = fields.Char('Facebook Pixel Key')
