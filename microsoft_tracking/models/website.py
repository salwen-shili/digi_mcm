# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from ast import literal_eval

from odoo import api, fields, models


class Website(models.Model):

    _inherit = "website"

    microsoft_tracking_key = fields.Char('Microsoft Tracking')
