# -*- coding: utf-8 -*-
import logging
import werkzeug
from datetime import date

from odoo import models, http, fields, SUPERUSER_ID
import http.client

_logger = logging.getLogger(__name__)
import requests


# integer Api calendly
# get TypeEvent
class calendly_integration(models.Model):
    _name = 'mcm_openedx.calendly_integration'
    _description = "mcm_openedx.calendly_integration"

    # Ajouter champs
    name = fields.Char(string="name")
    slug = fields.Char(string="nom de cour")
    color = fields.Char()

    active = fields.Boolean(string="active")
    created_at = fields.Date(string="created_at")
    owner = fields.Char(string="owner")
    scheduling_url = fields.Char(string="scheduling_ur")
    updated_at = fields.Date(string="updated_at")
    uri = fields.Char(string="uri ")


    def type_event_digi(self):
        for companys in self.env['res.company'].sudo().search([('id', "=", 2)]):
            _logger.info(companys.calendly_api_key_marwa)
            _logger.info(companys.calendly_api_key_abir)
            _logger.info(companys.calendly_api_key_selmine)

            querystring = {"active": "true",
                           "organization": "https://api.calendly.com/organizations/FHBHTA22WPOWFF2P",
                           "user": "https://api.calendly.com/users/b6009481-4791-4c1a-aa5f-4f94fcefbe5c"}
        for company in companys:
            listkey = ["calendly_api_key_marwa", "calendly_api_key", "calendly_api_key_abir",
                       "calendly_api_key_selmine"]

            headers = {
                "Content-Type": "application/json",
                "Authorization": company.calendly_api_key_selmine
            }
            response = requests.get('https://api.calendly.com/event_types', headers=headers, params=querystring)
            event = response.json()["collection"]
            for events in event:
                active = events['active']
                name = events['name']
                if '-' in name:
                    ownerr = name.split("-")
                    owner = ownerr[2]
                else:
                    owner = name
                slug = events['slug']
                created_at = events['created_at']
                # owner = events['profile']['owner']
                scheduling_url = events['scheduling_url']
                updated_at = events['updated_at']
                uri = events['uri']
                uuid_eventtype = uri.split("/")
                for existt in self.env['mcm_openedx.calendly_integration'].sudo().search(
                        [('id', '!=', False)]):
                    existe = self.env['mcm_openedx.calendly_integration'].sudo().search(
                        [('name', "like", events['name'])])
                    if not existe:
                        print("dont exist")
                        new = self.env['mcm_openedx.calendly_integration'].sudo().create({
                            'name': name,
                            'slug': slug,
                            'active': active,
                            'created_at': created_at,
                            'owner': owner,

                            'scheduling_url': scheduling_url,
                            'updated_at': updated_at,
                            'uri': uri,
                        })
                        print(new)
    def type_event(self):
        for companys in self.env['res.company'].sudo().search([('id', "=",2)]):
            _logger.info(companys.calendly_api_key_marwa)
            _logger.info(companys.calendly_api_key)
            _logger.info(companys.calendly_api_key_abir)
            _logger.info(companys.calendly_api_key_selmine)

            querystring = {"active": "true",
                           "organization": "https://api.calendly.com/organizations/c7e28d20-f7eb-475f-954a-7ae1a36705e3",
                           "user": "https://api.calendly.com/users/b6009481-4791-4c1a-aa5f-4f94fcefbe5c"}
        for company in companys:
            listkey = ["calendly_api_key_marwa", "calendly_api_key","calendly_api_key_abir","calendly_api_key_selmine"]

            headers = {
                "Content-Type": "application/json",
                "Authorization": company.calendly_api_key_selmine
            }
            response = requests.get('https://api.calendly.com/event_types', headers=headers, params=querystring)
            event = response.json()["collection"]
            for events in event:
                active = events['active']
                name = events['name']
                if '-' in name:
                    ownerr = name.split("-")
                    owner = ownerr[2]
                else:
                    owner = name
                slug = events['slug']
                created_at = events['created_at']
                # owner = events['profile']['owner']
                scheduling_url = events['scheduling_url']
                updated_at = events['updated_at']
                uri = events['uri']
                uuid_eventtype = uri.split("/")
                for existt in self.env['mcm_openedx.calendly_integration'].sudo().search(
                        [('id', '!=', False)]):
                    existe = self.env['mcm_openedx.calendly_integration'].sudo().search(
                        [('name', "like", events['name'])])
                    if not existe:
                        print("dont exist")
                        new = self.env['mcm_openedx.calendly_integration'].sudo().create({
                            'name': name,
                            'slug': slug,
                            'active': active,
                            'created_at': created_at,
                            'owner': owner,

                            'scheduling_url': scheduling_url,
                            'updated_at': updated_at,
                            'uri': uri,
                        })
                        print(new)

    def test_url(self):
        return {
            "url": self.scheduling_url,
            "type": "ir.actions.act_url"
        }

    def eventevnt(self):
        return {
            'view_mode': 'tree',
            'res_model': 'mcm_openedx.calendly_event',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }


class event_calendly(models.Model):
    _name = 'mcm_openedx.calendly_event'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    scheduling_url_name = fields.Char(string="name")
    scheduling_url_created_at = fields.Date(string="created_at")
    scheduling_url_updated_at = fields.Date(string="updated_at")
    scheduling_url_uri = fields.Char(string="uri")

    event_name = fields.Char(string="name")
    location = fields.Char(string="Location")
    start_at = fields.Date(string="Start_at")
    start_at_char = fields.Char(string="Start_at")
    status = fields.Boolean(string="Active")
    owner = fields.Char(string="Formateur")
    reschedule_url = fields.Char(string="reschedule_url")
    cancel_url = fields.Char(string="Cancel URL")
    partner_id = fields.Many2one('res.partner')

    def event(self):
        organization = ["FHBHTA22WPOWFF2P", "c7e28d20-f7eb-475f-954a-7ae1a36705e3"]
        users = ["b6009481-4791-4c1a-aa5f-4f94fcefbe5c", "68c23f1b-42a1-4eae-84f5-0f0d88098aa8",
                 "5aa95e72-35ab-4391-8ff6-34cdd4e34f86"]
        company = self.env['res.company'].sudo().search([('id', "!=", False)], limit=1)
        new_format = '%d %B, %Y, %H:%M:%S'
        headers = {
            "Content-Type": "application/json",
            "Authorization": company.calendly_api_key}
        for org in organization:
            for user in users:
                querystring = {"user": "https://api.calendly.com/users/%s" % user,
                               "organization": "https://api.calendly.com/organizations/%s" % org,
                               "status": "active", "min_start_time": date.today()}

                # Returns a list of Events.
                r = requests.get('https://api.calendly.com/scheduled_events',
                                 headers=headers, params=querystring)
                print("hahah", r.json()["collection"])
                shevent = r.json()["collection"]
                for shevents in shevent:
                    try:
                        scheduling_url_uri = shevents['uri']
                        scheduling_url_name = shevents['name']
                        print("scheduling_url_namescheduling_url_name", scheduling_url_name)
                        scheduling_url_created_at = shevents['created_at']
                        scheduling_url_updated_at = shevents['updated_at']
                        uuid_eventtype = scheduling_url_uri.split("/")
                        # Returns information about a specified Event.
                        params = {
                            'statuts': 'active'
                        }
                        headers = {
                            "Content-Type": "application/json",
                            "Authorization": company.calendly_api_key}

                        rep = requests.get('https://api.calendly.com/scheduled_events/%s' % (uuid_eventtype[4]),
                                           headers=headers, params=params)
                        response = rep.json()['resource']
                        print(response)
                        rep_inv = requests.get(
                            'https://api.calendly.com/scheduled_events//invitees' % (uuid_eventtype[4]),
                            headers=headers, params=params)
                        response_inv = rep_inv.json()['collection']
                        print("response_inv response_inv ", response_inv)

                        event_name = response['name']
                        if '-' in event_name:
                            ownerr = event_name.split("-")
                            owner = ownerr[2]
                        else:
                            owner = event_name
                        location = response['location']['location']
                        start_at = response['start_time']
                        start_at_char = response['start_time']
                        start_at_char = str(start_at_char).replace('T', ' ')
                        start_at_char = start_at_char.split(".")
                        start_at_char = start_at_char[0]
                        print("start_at_charstart_at_char", start_at_char)
                        status = response['status']
                        cancel_url = response_inv[0]['cancel_url']
                        reschedule_url = response_inv[0]['reschedule_url']

                        for existt in self.env['mcm_openedx.calendly_event'].sudo().search(
                                [('id', '!=', False)]):
                            if existt.start_at:
                                if existt.start_at < date.today():
                                    print("existeee nameeeee")
                                    existt.browse(existt.id).sudo().unlink()
                            existe = self.env['mcm_openedx.calendly_event'].sudo().search(
                                [('event_name', '=', shevents['name']), ('start_at', '=', response['start_time'])])

                            if not existe:
                                print("dont exist")
                                new = self.env['mcm_openedx.calendly_event'].sudo().create({
                                    'scheduling_url_name': scheduling_url_name,
                                    'scheduling_url_created_at': scheduling_url_created_at,
                                    'scheduling_url_updated_at': scheduling_url_updated_at,
                                    'scheduling_url_uri': scheduling_url_uri,
                                    'event_name': event_name,
                                    'location': location,
                                    'start_at': start_at,
                                    'start_at_char': start_at_char,
                                    'reschedule_url': reschedule_url,
                                    'cancel_url': cancel_url,
                                    'status': status,
                                    'owner': owner,
                                })
                                print(new)
                        # ajouter les apprenants manuellemnt a partire de  la fiche Client
                        self.env.cr.commit()
                        # self.env.cr.rollback() cancels the transaction's write operations since the last commit, or all if no commit was done.
                    except Exception:
                        self.env.cr.rollback()
                        _logger.info(" except Exception:")

    def test_url(self):
        return {
            "url": self.location,
            "type": "ir.actions.act_url"
        }

    def send_invitation(self):
        company = self.env['res.company'].sudo().search([('id', "=", 1)], limit=1)
        todays_date = date.today()
        count = 0
        print("envoyer invitation au apprenant selon leur formation")
        for partner in self.env['res.partner'].sudo().search(
                [('company_id', '=', 1), ('state', '=', "en_formation"), ('statut', "=", "won"),
                 ('mcm_session_id.date_exam', '!=', False), ('email', '=', "khouloudachour.97@gmail.com")]):
            try:
                if partner.mcm_session_id.date_exam:
                    if partner.mcm_session_id.date_exam.month == todays_date.month:
                        count = count + 1
                        if partner.module_id.product_id.default_code == "taxi":
                            print(partner.email)

                            # APi si il existe des event
                            # APi si il existe des event
                            for existe in self.env['mcm_openedx.calendly_event'].sudo().search(
                                    [('id', '!=', False),
                                     ('event_name', '!=', ["Cours en direct - Développement Commercial - Préscilia",
                                                           "Cours en direct - Réglementation VTC - Eric 1H"])]):
                                print(existe.event_name)
                                # Fiche Client odoo chercher si event
                                exist_event = self.env['calendly.rendezvous'].sudo().search(
                                    [('partner_id', '=', partner.id), ('name', '=', existe.event_name),
                                     ('event_starttime', '=', existe.start_at)])
                                print("exist_event.name", exist_event.name)
                                print(existe.event_name)
                                if not exist_event:
                                    if existe.start_at == todays_date:
                                        calendly = self.env['calendly.rendezvous'].sudo().create({
                                            'partner_id': partner.id,
                                            'email': partner.email,
                                            'phone': partner.phone,
                                            'name': existe.event_name,
                                            'zoomlink': existe.event_name,
                                        })
                                        calendly.event_starttime = existe.start_at
                                        calendly.event_starttime_char = existe.start_at_char
                                        calendly.event_endtime = existe.start_at
                        if partner.module_id.product_id.default_code == "vtc" or partner.module_id.product_id.default_code == "vtc_bolt":
                            print(partner.email)
                            # APi si il existe des event
                            # APi si il existe des event
                            for existe in self.env['mcm_openedx.calendly_event'].sudo().search(
                                    [('id', '!=', False),
                                     ]):
                                print(existe.event_name)
                                # Fiche Client odoo chercher si event
                                exist_event = self.env['calendly.rendezvous'].sudo().search(
                                    [('partner_id', '=', partner.id), ('name', '=', existe.event_name),
                                     ('event_starttime', '=', existe.start_at)])
                                print("exist_event.name", exist_event.name)
                                print(existe.event_name)
                                if not exist_event:
                                    if existe.start_at == todays_date:
                                        calendly = self.env['calendly.rendezvous'].sudo().create({
                                            'partner_id': partner.id,
                                            'email': partner.email,
                                            'phone': partner.phone,
                                            'name': existe.event_name,
                                            'zoomlink': existe.event_name,
                                        })
                                        calendly.event_starttime = existe.start_at
                                        calendly.event_starttime_char = existe.start_at_char
                                        calendly.event_endtime = existe.start_at

                                        print("created", calendly)
                print(count)
                # ajouter les apprenants manuellemnt a partire de  la fiche Client
                self.env.cr.commit()
                # self.env.cr.rollback() cancels the transaction's write operations since the last commit, or all if no commit was done.
            except Exception:
                self.env.cr.rollback()
                _logger.info("except Exception:")
