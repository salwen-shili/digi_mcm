import base64
from urllib import parse

import requests

from odoo import models, fields
from odoo.tools import json

import logging

_logger = logging.getLogger(__name__)


class sms_sendinblue(models.Model):
    _name = 'sendinblue.sendinbluesms'
    _description = "Sendinblue"

    sender = fields.Char(string="ID")
    recipient = fields.Char(string="ID")
    content = fields.Char(string="ID")
    type = fields.Selection([('marketing', 'Marketing'),
                             ('transactional', ' Transactional'),
                             ])
    def sendsms(self):
        _logger.info("testttttttttttt")

        url = "https://api.sendinblue.com/v3/transactionalSMS/sms"
        partner_data =self.env['res.partner'].sudo().search([])
        payload = {
            "type": "marketing",
            "unicodeEnabled": False,
            "sender":  partner_data.company_id.name,
            "recipient":  partner_data.phone,
            "content": "test api sendinblue"
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "api-key": "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"
        }

        response = requests.post(url, json=payload, headers=headers)

        print(response.text)