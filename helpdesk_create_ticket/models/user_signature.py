# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import _, api, exceptions, fields, models, tools, registry, SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)


class UserSignature(models.Model):
    _name = 'res.user.signature'

    user_id = fields.Many2one('res.users')
    signature = fields.Html(string="Email Signature")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    email_from = fields.Char('From',
                             help="Sender address (placeholders may be used here). If not set, the default "
                                  "value will be the author's email alias if configured, or email address.")
