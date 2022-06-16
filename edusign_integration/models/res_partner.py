# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime


class resCompany(models.Model):
    _inherit = "res.company"

    edusign_api_key = fields.Char(string='API key Edusign')


class resPartner(models.Model):
    _inherit = "res.partner"

    id_apprenant_edusign = fields.Char(
        string='ID Apprenant Edusign', readonly=True)
