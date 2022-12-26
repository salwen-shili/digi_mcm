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

    content = fields.Text(string="Message")
    # recipients
    partner_ids = fields.Many2one('res.users', 'Current User', default=lambda self: self.env.uid)

    def get_user_phone(self):

        user_phone_number = self.env['res.partner'].browse(self.env.context.get('active_ids'))
        # modifier le numero de l'utilisateur pour qu'il soit accepter par l'api

        return user_phone_number.phone.replace("+", "00").replace(" ", "") or user_phone_number.phone.replace("0",
                                                                                                              "33").replace(
            " ", "")

    # get recipient from odoo
    recipient = fields.Char('Destinataires', default=get_user_phone)

    # get current user (la personne que on va lui envoyer l'sms
    def get_user_id(self):
        current_user = self.env['res.partner'].browse(self.env.context.get('active_ids'))
        return current_user

    current_user = fields.Many2one('res.partner', 'Destinataires', default=get_user_id)

    # get sender (le nom de la societé)

    def get_sneder(self):
        sender_name = self.env['res.partner'].browse(self.env.context.get('active_ids'))
        return sender_name.company_id.phone.replace("+", "").replace(" ", "")

    sender = fields.Char(string="Sender", default=get_sneder)

    def sendsms(self):

        _logger.info("sendinblue sms")
        # recuperer les clé api
        api_key = self.env['sendinblue.accounts'].sudo().search([('api_key', '!=', False)])
        _logger.info(api_key.api_key)
        url = "https://api.sendinblue.com/v3/transactionalSMS/sms"

        payload = {
            'type': "transactional",
            'unicodeEnabled': False,
            'sender': self.sender.replace(" ", ""),
            'recipient': self.recipient.replace(" ", ""),
            'content': self.content
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "api-key": "dddapi_key.api_key"
        }

        response = requests.post(url, json=payload, headers=headers)
        _logger.info(self.sender)
        _logger.info(self.recipient.replace(" ", ""))
        _logger.info(self.content)

        note_tag = "<b>" + " Sent 📨📨 À :  " + self.current_user.name + " " "</b><br/>"
        # if 201 message envoyée
        # add message id-track
        response_text = response.json()

        if (response.status_code == 201):
            messeageid = response_text["messageId"]  # if 201 message envoyée

            values = {
                'record_name': self.current_user.name,
                'model': 'res.partner',
                'subject': messeageid,
                'message_type': 'comment',
                'subtype_id': self.current_user.env['mail.message.subtype'].search([('name', '=', 'Note')]).id,
                'res_id': self.current_user.id,
                'author_id': self.current_user.env.user.partner_id.id,
                'date': datetime.now(),
                'body': note_tag + "\n" + self.content
            }
            self.current_user.env['mail.message'].sudo().create(values)
        # if !201 message envoyée
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

    def action_sms(self):
        api_key = self.env['sendinblue.accounts'].sudo().search([('api_key', '!=', False)])

        headers = {
            'accept': 'application/json',
            'api-key': api_key.api_key,
        }

        params = {
            'limit': '50',
            'offset': '0',
            'sort': 'desc',
        }

        response = requests.get('https://api.sendinblue.com/v3/transactionalSMS/statistics/events', params=params,
                                headers=headers)

        events = response.json()
        event_result = events["events"]
        subtype_id = self.env['ir.model.data'].xmlid_to_res_id('mail.mt_note')
        # chercher les event
        for event in event_result:
            # si reponse a un sms
            if event["event"] == "replies":
                _logger.info("reponse_logger %s" % event["reply"])
                # chercher le recepteur de message a partir de numero de telephone
                numero_recepteur = event["phoneNumber"]
                _logger.info("numeroo %s" % numero_recepteur)

                for recepteur in self.env['res.partner'].sudo().search(
                        [('phone', '!=', False)]):
                    if recepteur.phone.replace("+", "00").replace(" ",
                                                                  "") == numero_recepteur or recepteur.phone.replace(
                            "0", "33").replace(" ", "") == numero_recepteur:
                        _logger.info(recepteur.phone)

                        note_tag = "<b>" + " Reply 📨📨 From :  " + recepteur.name + " " "</b><br/>"
                        sms = self.env['mail.message'].sudo().search(
                            [("body", "=", note_tag + event["reply"]), ("res_id", "=", recepteur.id),
                             ])
                        if not sms:
                            values = {
                                'record_name': recepteur.name,
                                'subject': event["messageId"],
                                'model': 'res.partner',
                                'message_type': 'comment',
                                'subtype_id': recepteur.env['mail.message.subtype'].search(
                                    [('name', '=', 'Note')]).id,
                                'res_id': recepteur.id,
                                'author_id': self.env.user.partner_id.id,
                                'date': datetime.now(),
                                'body': note_tag + event["reply"]
                            }
                            recepteur.env['mail.message'].sudo().create(values)
            if event["event"] != "replies":
                _logger.info("reponse_logger %s" % event["event"])
                # chercher le recepteur de message a partir de numero de telephone
                numero_recepteur = event["phoneNumber"]
                _logger.info("numeroo %s" % numero_recepteur)
                for recepteur in self.env['res.partner'].sudo().search(
                        [('phone', '!=', False)]):
                    if recepteur.phone.replace("+", "").replace(" ", "") == numero_recepteur or recepteur.phone.replace(
                            "0", "33").replace(" ", "") == numero_recepteur:
                        _logger.info(recepteur.phone)
                        date_event = event["date"].split('.')[0].replace("T", " ")
                        commentaire = "<b>" + "Message" + " " + event[
                            "event"] + " " + "At" + " " + date_event + " " "</b><br/>"
                        sms = self.env['mail.message'].sudo().search(
                            [("body", "=", commentaire), ("res_id", "=", recepteur.id),
                             ])
                        if not sms:
                            values = {
                                'record_name': recepteur.name,
                                'subject': event["messageId"],
                                'model': 'res.partner',
                                'message_type': 'comment',
                                'subtype_id': recepteur.env['mail.message.subtype'].search(
                                    [('name', '=', 'Note')]).id,
                                'res_id': recepteur.id,
                                'author_id': self.env.user.partner_id.id,
                                'date': datetime.now(),
                                'body': commentaire
                            }
                            recepteur.env['mail.message'].sudo().create(values)
