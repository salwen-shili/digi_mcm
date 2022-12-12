import base64
from urllib import parse

import requests

from odoo import models, fields, api
from odoo.tools import json

import logging

_logger = logging.getLogger(__name__)
from odoo import api, fields, models, _


class sms_sendinblue(models.TransientModel):
    _name = 'sendinblue.sendinbluesms'
    _description = "Sendinblue"

    sender = fields.Char(string="Sender")
    recipient = fields.Char(string="Recipient")
    content = fields.Text(string="Body")
    type = fields.Selection([('marketing', 'Marketing'),
                             ('transactional', ' Transactional'),
                             ])
    # recipients
    recipient_description = fields.Text('Recipients (Partners)', compute='_compute_recipients', compute_sudo=False)
    recipient_count = fields.Integer('# Valid recipients', compute='_compute_recipients', compute_sudo=False)
    recipient_invalid_count = fields.Integer('# Invalid recipients', compute='_compute_recipients', compute_sudo=False)
    number_field_name = fields.Char(string='Field holding number')
    partner_ids = fields.Many2many('res.partner')
    numbers = fields.Char('Recipients (Numbers)')
    sanitized_numbers = fields.Char('Sanitized Number', compute='_compute_sanitized_numbers', compute_sudo=False)

    @api.depends('partner_ids',
                 'number_field_name', 'sanitized_numbers')
    def _compute_recipients(self):
        self.recipient_description = False
        self.recipient_count = 0
        self.recipient_invalid_count = 0

        if self.partner_ids:
            if len(self.partner_ids) == 1:
                self.recipient_description = '%s (%s)' % (self.partner_ids[0].display_name,
                                                          self.partner_ids[0].mobile or self.partner_ids[0].phone or _(
                                                              'Missing number'))
            self.recipient_count = len(self.partner_ids)


    def sendsms(self):

        _logger.info("sendinblue sms")
        url = "https://api.sendinblue.com/v3/transactionalSMS/sms"
        payload = {
            "type": "marketing",
            "unicodeEnabled": False,

            "content": "test api sendinblue"
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "api-key": "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"
        }

        response = requests.post(url, json=payload, headers=headers)

        _logger.info(response.text)
