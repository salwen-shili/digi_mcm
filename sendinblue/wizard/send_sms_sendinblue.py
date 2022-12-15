import base64
from urllib import parse

import requests

from odoo import models, fields, api
from odoo.addons.test_convert.tests.test_env import odoo
from odoo.tools import json, datetime

import logging

_logger = logging.getLogger(__name__)
from odoo import api, fields, models, _


class sms_sendinblue(models.TransientModel):
    _name = 'sendinblue.sendinbluesms'
    _description = "Sendinblue"

    def get_user_phone(self):
        user_phone_number = self.env['res.partner'].browse(self.env.context.get('active_ids'))
        return user_phone_number.phone

    content = fields.Text(string="content")
    type = fields.Selection([('marketing', 'Marketing'),
                             ('transactional', ' Transactional'),
                             ])
    # recipients
    partner_ids = fields.Many2one('res.users', 'Current User', default=lambda self: self.env.uid)
    company_ids = fields.Many2many('res.company')
    sanitized_numbers = fields.Char('Sanitized Number', compute='_compute_sanitized_numbers', compute_sudo=False)

    def get_user_phone(self):

        user_phone_number = self.env['res.partner'].browse(self.env.context.get('active_ids'))
        return user_phone_number.phone

    recipient = fields.Char('Recipients (Numbers)', default=get_user_phone)

    def get_user_id(self):
        current_user = self.env['res.partner'].browse(self.env.context.get('active_ids'))
        return current_user

    current_user = fields.Many2one('res.partner', 'Current User', default=get_user_id)

    def get_sneder(self):
        sender_name = self.env['res.partner'].browse(self.env.context.get('active_ids'))
        return sender_name.company_id.name

    sender = fields.Char(string="Sender", default=get_sneder)

    sender = fields.Char(string="Sender", default=get_sneder)

    def sendsms(self):

        _logger.info("sendinblue sms")
        api_key = self.env['sendinblue.accounts'].sudo().search([('api_key','!=',False)])
        _logger.info(api_key.api_key)


        url = "https://api.sendinblue.com/v3/transactionalSMS/sms"

        payload = {
            'type': "transactional",
            'unicodeEnabled': False,
            'sender': "%s" % self.sender,
            'recipient': "%s" % self.recipient.replace(" ", ""),
            'content': self.content
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "api-key":   api_key.api_key
        }

        response = requests.post(url, json=payload, headers=headers)
        _logger.info(self.sender)
        _logger.info(self.recipient.replace(" ", ""))
        _logger.info(self.content)

        note_tag = "<b>" + "📨📨 À :  " + self.current_user.name + " " "</b><br/>"
        if (response.status_code == 201):
            values = {
                'record_name': self.current_user.name,
                'model': 'res.partner',
                'message_type': 'comment',
                'subtype_id': self.current_user.env['mail.message.subtype'].search([('name', '=', 'Note')]).id,
                'res_id': self.current_user.id,
                'author_id': self.current_user.env.user.partner_id.id,
                'date': datetime.now(),
                'body': note_tag + "\n" + self.content
            }
            self.current_user.env['mail.message'].sudo().create(values)
        else:
            values = {
                'record_name': self.current_user.name,
                'model': 'res.partner',
                'message_type': 'comment',
                'subtype_id': self.current_user.env['mail.message.subtype'].search([('name', '=', 'Note')]).id,
                'res_id': self.current_user.id,
                'author_id': self.current_user.env.user.partner_id.id,
                'date': datetime.now(),
                'body': "Sms erreur" + response.text
            }
            self.current_user.env['mail.message'].sudo().create(values)

        _logger.info(response.text)
        _logger.info(response.status_code)
