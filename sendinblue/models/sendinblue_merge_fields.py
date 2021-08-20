# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class sendinblueMergeFields(models.Model):
    _name = "sendinblue.merge.fields"
    _description = "Sendinblue Merge Fields"

    name = fields.Char("Name", required=True, copy=False)
    category = fields.Char("Category", readonly=True, copy=False)
    type = fields.Char("Type")
    account_id = fields.Many2one("sendinblue.accounts", string="Associated sendinblue Account", copy=False)
    field_id = fields.Many2one('ir.model.fields', string='Odoo Field', help="""Odoo will fill value of selected field while contact is going to export or update""", domain="[('model_id.model', '=', 'res.partner')]")