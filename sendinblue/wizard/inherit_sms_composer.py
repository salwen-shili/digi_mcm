import requests

from odoo import api, fields, models, tools
import logging

from odoo.tools import datetime

_logger = logging.getLogger(__name__)


class InheritSmsComposer(models.TransientModel):
    _inherit = 'sms.composer'

    def send_sms(self):
        statut_code_sendinblue = 0

        _logger.info("sendinblue sms inherits ")
        # recuperer les clé api
        api_key = self.env['sendinblue.accounts'].sudo().search([('api_key', '!=', False)])
        _logger.info(api_key.api_key)
        records = self._get_records()
        url = "https://api.sendinblue.com/v3/transactionalSMS/sms"
        selected_ids = self.env.context.get('active_ids', [])
        selected_records = self.env['res.partner'].browse(selected_ids)

        if selected_records:
            _logger.info("selected_records %s " % selected_records)

            for i_sms in selected_records:
                phone = str(i_sms.phone.replace(' ', ''))[-9:]
                phone = '33' + ' ' + phone[0:1] + ' ' + phone[1:3] + ' ' + phone[
                                                                           3:5] + ' ' + phone[
                                                                                        5:7] + ' ' + phone[
                                                                                                     7:]
                _logger.info("recipient => phone to snd sms %s " % phone.replace(" ", ""))
                _logger.info("i_sms.company_id.name %s " % i_sms.company_id.name.replace(" ", ""))

                payload = {
                    'type': "transactional",
                    'unicodeEnabled': False,
                    'sender': i_sms.company_id.name.replace(" ", ""),
                    'recipient': phone.replace(" ", ""),
                    'content': self.body
                }
                headers = {
                    "accept": "application/json",
                    "content-type": "application/json",
                    "api-key": api_key.api_key
                }
                sms = self.env['mail.message'].sudo().search(
                    [("body", "ilike", self.body), ("message_type", "=", 'comment')
                     ('model', "=", "res.partner"),('record_name','like', i_sms.name)])


                _logger.info("sms")
                if sms:
                    statut_code_sendinblue = "300"

                if not sms:
                    _logger.info("not exist")

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

                    _logger.info(response.status_code)
                    statut_code_sendinblue = response.status_code
        else:

            records = self._get_records()

            phone = str(records.phone.replace(' ', ''))[-9:]
            phone = '33' + ' ' + phone[0:1] + ' ' + phone[1:3] + ' ' + phone[
                                                                       3:5] + ' ' + phone[
                                                                                    5:7] + ' ' + phone[
                                                                                                 7:]
            _logger.info("recipient => phone to snd sms %s " % phone.replace(" ", ""))
            _logger.info("i_sms.company_id.name %s " % records.company_id.name.replace(" ", ""))
            note_tag = "<b>" + " Sent 📨📨 À :  " + records.name + " " "</b><br/>"

            payload = {
                'type': "transactional",
                'unicodeEnabled': False,
                'sender': records.company_id.name.replace(" ", ""),
                'recipient': phone.replace(" ", ""),
                'content': self.body
            }
            headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "api-key": api_key.api_key
            }
            sms = self.env['mail.message'].sudo().search(
                [("body", "ilike", self.body), ("message_type", "=", 'comment'),

                 ('model', "=", "res.partner")])

            _logger.info("okkkkkkk")
            if sms:
                statut_code_sendinblue = "300"

            if not sms:
                _logger.info("not exist")

                response = requests.post(url, json=payload, headers=headers)
                # if 201 message envoyée
                # add message id-track
                response_text = response.json()

                if (response.status_code == 201):
                    messeageid = response_text["messageId"]  # if 201 message envoyée

                    values = {
                        'record_name': records.name,
                        'model': 'res.partner',
                        'subject': messeageid,
                        'message_type': 'comment',
                        'subtype_id': records.env['mail.message.subtype'].search([('name', '=', 'Note')]).id,
                        'res_id': records.id,
                        'author_id': records.env.user.partner_id.id,
                        'date': datetime.now(),
                        'body': note_tag + "\n" + self.body
                    }
                    records.env['mail.message'].sudo().create(values)

                _logger.info(response.status_code)
                statut_code_sendinblue = response.status_code
        return statut_code_sendinblue

    def _action_send_sms(self):
        fn = self.send_sms()
        _logger.info(fn)
        _logger.info("response statut code sms suivi")

        if fn == 201 or fn == 300:
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
