# -*- coding: utf-8 -*-

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    # birthday = fields.Date('Date of Birth')
    question_signup = fields.Char('Comment avez vous découvert notre site')