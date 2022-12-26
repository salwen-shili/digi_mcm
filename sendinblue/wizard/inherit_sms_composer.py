import requests

from odoo import api, fields, models, tools
import logging

from odoo.tools import datetime

_logger = logging.getLogger(__name__)


class InheritSmsComposer(models.TransientModel):
    _inherit = 'sms.composer'

    def sendsms(self):

        _logger.info("sendinblue sms")
        # recuperer les clé api
        api_key = self.env['sendinblue.accounts'].sudo().search([('api_key', '!=', False)])
        _logger.info(api_key.api_key)

        url = "https://api.sendinblue.com/v3/transactionalSMS/sms"

        payload = {
            'type': "transactional",
            'unicodeEnabled': False,
            'sender': "DIGIMOOV",
            'recipient':  self.partner_ids.mobile  or self.partner_ids.phone,
            'content': self.body
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "api-key": "api_key.api_keyeegit"
        }

        response = requests.post(url, json=payload, headers=headers)

        _logger.info(self.partner_ids[0].mobile or self.partner_ids[0].phone)
        _logger.info(response.status_code)
        statut_code_sendinblue = response.status_code
        return statut_code_sendinblue

    def _action_send_sms(self):
        if self.sendsms() == 201:
            return False
            _logger.info("_____________SMS.COMPoSER___________ %s", self.sendsms())
        else:
            records = self._get_records()
            if self.composition_mode == 'numbers':
                return self._action_send_sms_numbers()
            elif self.composition_mode == 'comment':
                if records is not None and issubclass(type(records), self.pool['mail.thread']):
                    return self._action_send_sms_comment(records)
                return self._action_send_sms_numbers()
            else:
                return self._action_send_sms_mass(records)
