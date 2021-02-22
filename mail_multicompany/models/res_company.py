# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import datetime

from werkzeug import urls

from odoo import api, fields, models, tools

class ResCompany(models.Model):

    _inherit = 'res.company'

    alias_domain = fields.Char('Alias Domain')