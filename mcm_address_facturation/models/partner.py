# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError
from datetime import date,datetime


class resPartner(models.Model):
    _inherit = "res.partner"

    addresse_facturation=fields.Selection([
        ('particulier', 'Particulier'),
        ('societe', 'Société'),
        ], string='Adresse de facturation')