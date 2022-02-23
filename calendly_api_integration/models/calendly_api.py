# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime, timedelta

from odoo import models, api, fields,_
import werkzeug
import json
import requests
from datetime import timedelta, datetime,date
import logging
_logger = logging.getLogger(__name__)


class Api(models.Model):
    _name = 'calendly.api'
    _description = "Calendly API"

    client_id = fields.Char(string="Calendly client ID", required=True,
                            default='90d14d3507c35d579924cf87a6de7fbc560211289ee1812e554c683c346f3a9c')
    client_secret = fields.Char(string="Calendly client Secret", required=True,
                                default='b863ae64bfa9ebd0d8aa8010028f3bf1041e1f678b682b710d4dec928d0fcca8')
    redirect_uri = fields.Char(string="Calendly redirect URI", required=True, default='https://www.mcm-academy.fr/')
    access_token = fields.Char(string="Calendly access token", required=True)
    refresh_token = fields.Char(string="Calendly refresh token", required=True)

    def _refresh_token(self):
        print('x')
        # calendly = self.env['calendly.api'].sudo().search([])
        # if calendly:
        #     headers = {
        #         'Content-Type': 'application/x-www-form-urlencoded',
        #     }
        #     data = {
        #         'client_id': calendly.client_id,
        #         'grant_type': 'authorization_code',
        #         'client_secret':  calendly.client_secret,
        #         'code': 'xWZ-pGYWw-DLdKZkqx3KxK0Q9quuv83MVbg_jWtEEI0',
        #         'redirect_uri': calendly.redirect_uri,
        #     }
        #
        # r = requests.post('https://auth.calendly.com/oauth/token', headers=headers, data=data)
        # response = werkzeug.utils.unescape(r.content.decode())
        # json_data = json.loads(r.text)
        # print(json_data)
        calendly = self.env['calendly.api'].sudo().search([])
        if calendly:
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
            }
            data = {'client_id': calendly.client_id,
                    'client_secret': calendly.client_secret,
                    'grant_type': 'refresh_token',
                    'refresh_token' : calendly.refresh_token,
                    }
            r = requests.post('https://auth.calendly.com/oauth/token', headers=headers, data=data)
            response = werkzeug.utils.unescape(r.content.decode())
            json_data = json.loads(r.text)
            print(json_data)
            if "access_token" in json_data:
                access=str(json_data["access_token"])
                refresh=str(json_data["refresh_token"])
                self._cr.execute("""UPDATE calendly_api SET access_token = %s WHERE id=%s""", (access,calendly.id,))
                self._cr.commit()
                self._cr.execute("""UPDATE calendly_api SET refresh_token = %s WHERE id=%s""", (refresh,calendly.id,))
                self._cr.commit()

                headers = {
                    'Authorization': 'Bearer ' + str(json_data["access_token"]),
                    'Content-Type': 'application/json',
                }
                params = {
                    'organization': 'https://api.calendly.com/organizations/GCFAGOCMF67ONDTO',
                    'user':'https://api.calendly.com/users/HEDHGMALE7VZKP3Q'
                }

                r = requests.get('https://api.calendly.com/event_types', headers=headers,params=params)
                response = werkzeug.utils.unescape(r.content.decode())
                json_data_events = json.loads(r.text)
                if "collection" in json_data_events:
                    collection = json_data_events["collection"]
                    for event in collection:
                        print ('uri_event:',event)
                        if 'ae1aafc2-ae62-4151-b6a6-e75d1db9c736' in event['uri'] :
                            headers = {
                                'Authorization': 'Bearer ' + str(json_data["access_token"]),
                                'Content-Type': 'application/json',
                            }
                            params = {
                                'statuts' : 'active'
                            }
                            uuid = 'ae1aafc2-ae62-4151-b6a6-e75d1db9c736'
                            r = requests.get('https://api.calendly.com/scheduled_events/%s/invitees' %(uuid),
                                                    headers=headers , params=params)
                            response = werkzeug.utils.unescape(r.content.decode())
                            event_invitees = json.loads(r.text)
                now = date.today()
                min_start_time=str(now)+'T23:59:59Z'
                headers = {
                    'Authorization': 'Bearer ' + str(json_data["access_token"]),
                    'Content-Type': 'application/json',
                }

                params = {
                    'organization': 'https://api.calendly.com/organizations/GCFAGOCMF67ONDTO',
                    'min_start_time': min_start_time,
                    'user': 'https://api.calendly.com/users/HEDHGMALE7VZKP3Q'
                }
                r = requests.get('https://api.calendly.com/scheduled_events', headers=headers, params=params)
                response = werkzeug.utils.unescape(r.content.decode())
                json_data_events = json.loads(r.text)
                if "collection" in json_data_events:
                    collection = json_data_events["collection"]
                    for event in collection:
                        print('event :',event)
                        start_time = event['start_time']
                        end_time = event['end_time']
                        event_name = event['name']
                        event_type = event["event_type"]
                        if 'ae1aafc2-ae62-4151-b6a6-e75d1db9c736' in str(event_type):

                            uri = event['uri']
                            headers = {
                                'Authorization': 'Bearer ' + str(json_data["access_token"]),
                                'Content-Type': 'application/json',
                            }

                            r = requests.get(str(uri)+'/invitees',headers=headers)
                            response = werkzeug.utils.unescape(r.content.decode())
                            json_data_event_invitees = json.loads(r.text)
                            if 'collection' in json_data_event_invitees:
                                invitee_collection = json_data_event_invitees['collection']
                                for invitee in invitee_collection :
                                    email = False
                                    if 'email' in invitee :
                                        email= str(invitee['email'])
                                    tel = False
                                    if 'text_reminder_number' in invitee :
                                        tel = invitee['text_reminder_number']
                                    odoo_contact = False
                                    res_user = self.env['res.users']
                                    if email :
                                        odoo_contact = res_user.search([('login', "=", str(email).lower().replace(' ', ''))], limit=1)
                                        if not odoo_contact:
                                            if tel:
                                                odoo_contact = self.env["res.users"].sudo().search([("phone", "=", str(tel))], limit=1)
                                                if not odoo_contact:
                                                    phone_number = str(tel).replace(' ','')
                                                    if '+33' not in str(phone_number):  # check if aircall api send the number of client with +33
                                                        phone = phone_number[0:2]
                                                        if str(phone) == '33' and ' ' not in str(tel):  # check if aircall api send the number of client in this format (number_format: 33xxxxxxx)
                                                            phone = '+' + str(tel)
                                                            odoo_contact = self.env["res.users"].sudo().search(
                                                                [("phone", "=", phone)], limit=1)
                                                            if not odoo_contact:
                                                                phone = phone[0:3] + ' ' + phone[3:4] + ' ' + phone[
                                                                                                              4:6] + ' ' + phone[
                                                                                                                           6:8] + ' ' + phone[
                                                                                                                                        8:10] + ' ' + phone[
                                                                                                                                                      10:]
                                                                odoo_contact = self.env["res.users"].sudo().search(
                                                                    [("phone", "=", phone)], limit=1)
                                                        phone = phone_number[0:2]
                                                        if str(phone) == '33' and ' ' in str(tel):  # check if aircall api send the number of client in this format (number_format: 33 x xx xx xx)
                                                            phone = '+' + str(tel)
                                                            odoo_contact = self.env["res.users"].sudo().search(
                                                                ['|', ("phone", "=", phone),
                                                                 ("phone", "=", phone.replace(' ', ''))], limit=1)
                                                        phone = phone_number[0:2]
                                                        if str(phone) in ['06', '07'] and ' ' not in str(tel):  # check if aircall api send the number of client in this format (number_format: 07xxxxxx)
                                                            odoo_contact = self.env["res.users"].sudo().search(
                                                                [("phone", "=", str(tel))],
                                                                limit=1)
                                                            if not odoo_contact:
                                                                phone = phone[0:2] + ' ' + phone[2:4] + ' ' + phone[
                                                                                                              4:6] + ' ' + phone[
                                                                                                                           6:8] + ' ' + phone[
                                                                                                                                        8:]
                                                                odoo_contact = self.env["res.users"].sudo().search(
                                                                    [("phone", "=", phone)], limit=1)
                                                        phone = phone_number[0:2]
                                                        if str(phone) in ['06', '07'] and ' ' in str(tel):  # check if aircall api send the number of client in this format (number_format: 07 xx xx xx)
                                                            odoo_contact = self.env["res.users"].sudo().search(
                                                                ['|',
                                                                 ("phone", "=", str(tel)),
                                                                 str(tel).replace(' ',
                                                                                                                   '')],
                                                                limit=1)
                                                    else:  # check if aircall api send the number of client with+33
                                                        if ' ' not in str(tel):
                                                            phone = str(tel)
                                                            phone = phone[0:3] + ' ' + phone[3:4] + ' ' + phone[
                                                                                                          4:6] + ' ' + phone[
                                                                                                                       6:8] + ' ' + phone[
                                                                                                                                    8:10] + ' ' + phone[
                                                                                                                                                  10:]
                                                            odoo_contact = self.env["res.users"].sudo().search(
                                                                [("phone", "=", phone)], limit=1)
                                                        if not odoo_contact:
                                                            odoo_contact = self.env["res.users"].sudo().search(
                                                                [("phone", "=", str(phone_number).replace(' ', ''))],
                                                                limit=1)
                                                            if not odoo_contact:
                                                                phone = str(phone_number)
                                                                phone = phone[3:]
                                                                phone = '0' + str(phone)
                                                                odoo_contact = self.env["res.users"].sudo().search(
                                                                    [("phone", "like", phone.replace(' ', ''))], limit=1)
                                    if odoo_contact :
                                        rendez_vous = self.env["calendly.rendezvous"].sudo().search(
                                                                    [("partner_id", "=", odoo_contact.id),("event_starttime", "=", str(start_time),("event_endtime", "=", str(end_time)))], limit=1)
                                        if not rendez_vous :
                                            rendez_vous = self.env['calendly.rendezvous'].sudo().create({
                                                'name': contact['first_name'] + ' ' + (contact['last_name'] if contact['last_name'] else ''),
                                                'login': str(email).lower().replace(' ', ''),
                                                'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])],
                                                'email': str(email).lower().replace(' ', ''),
                                                'notification_type': 'email',
                                                'company_id': 1,
                                                'company_ids': [1, 2]
                                            })
                                            
                                        