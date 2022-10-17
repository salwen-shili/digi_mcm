# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class resComapny(models.Model):
    _inherit = "res.company"

    plateforme_api_key=fields.Char('clé API')
    plateforme_company_key=fields.Char('ID Société')
    