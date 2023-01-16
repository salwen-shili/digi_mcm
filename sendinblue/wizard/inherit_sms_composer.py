import requests

from odoo import api, fields, models, tools
import logging

from odoo.tools import datetime

_logger = logging.getLogger(__name__)


class InheritSmsComposer(models.TransientModel):
    _inherit = 'sms.composer'

    def sendsms(self):
        statut_code_sendinblue = 0
        _logger.info("sendinblue sms")
        # recuperer les clé api
        api_key = self.env['sendinblue.accounts'].sudo().search([('api_key', '!=', False)])
        _logger.info(api_key.api_key)
        records = self._get_records()

        url = "https://api.sendinblue.com/v3/transactionalSMS/sms"
        selected_ids = self.env.context.get('active_ids', [])
        selected_records = self.env['res.partner'].browse(selected_ids)
        for i_sms in selected_records:
            _logger.info("for i_sms in selected_records:  %s", % i_sms.name)

        for i_sms in selected_records:
            payload = {
                'type': "transactional",
                'unicodeEnabled': False,
                'sender': i_sms.company_id.name,
                'recipient': i_sms.phone ,
                'content':self.body
            }
            headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "api-key": api_key.api_key
            }

            response = requests.post(url, json=payload, headers=headers)
            note_tag = "<b>" + " Sent 📨📨 À :  " + i_sms.name + " " "</b><br/>"
            # if 201 message envoyée
            # add message id-track
            response_text = response.json()

            if (response.status_code == 201):
                messeageid = response_text["messageId"]  # if 201 message envoyée

                values = {
                    'record_name': i_sms.name,
                    'model': 'res.partner',
                    'subject': messeageid,
                    'message_type': 'comment',
                    'subtype_id': i_sms.env['mail.message.subtype'].search([('name', '=', 'Note')]).id,
                    'res_id': i_sms.id,
                    'author_id': i_sms.env.user.partner_id.id,
                    'date': datetime.now(),
                    'body': note_tag + "\n" + self.body
                }
                records.env['mail.message'].sudo().create(values)


            _logger.info(i_sms.name)
            _logger.info(i_sms.phone)
            _logger.info(response.status_code)
            statut_code_sendinblue = response.status_code
        return statut_code_sendinblue

    def _action_send_sms(self):
        if self.sendsms() == 201:

            return False
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
