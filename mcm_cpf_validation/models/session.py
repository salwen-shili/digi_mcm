# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models

class resComapny(models.Model):
    _inherit = "mcmacademy.session"

    id_edof=fields.Char("ID Sesssion EDOF")