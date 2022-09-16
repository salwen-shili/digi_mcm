# -*- coding: utf-8 -*-
import logging
from datetime import date

import werkzeug

from odoo import models, http, fields
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

    active = fields.Boolean(string="active")
    created_at = fields.Date(string="created_at")
    owner = fields.Char(string="owner")
    scheduling_url = fields.Char(string="scheduling_ur")
    updated_at = fields.Date(string="updated_at")
    uri = fields.Char(string="uri ")

    def khou(self):
        querystring = {"active": "true",
                       "organization": "https://api.calendly.com/organizations/c7e28d20-f7eb-475f-954a-7ae1a36705e3",
                       "user": "https://api.calendly.com/users/5aa95e72-35ab-4391-8ff6-34cdd4e34f86"}
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer eyJraWQiOiIxY2UxZTEzNjE3ZGNmNzY2YjNjZWJjY2Y4ZGM1YmFmYThhNjVlNjg0MDIzZjdjMzJiZTgzNDliMjM4MDEzNWI0IiwidHlwIjoiUEFUIiwiYWxnIjoiRVMyNTYifQ.eyJpc3MiOiJodHRwczovL2F1dGguY2FsZW5kbHkuY29tIiwiaWF0IjoxNjYzMTQ4NjA2LCJqdGkiOiJkZDUwYWIxNy04ZDM3LTQyMjYtOGMzYy02NzMyNzI1MTM2NmUiLCJ1c2VyX3V1aWQiOiI1YWE5NWU3Mi0zNWFiLTQzOTEtOGZmNi0zNGNkZDRlMzRmODYifQ.TKiAMPGQFUdBODBHq8H-0LgQnbkldxW5V_hFacDyJgn53B-MbTQcBHLqwPx8uN_CiLfJahF_NJ1V4cc0Z5gmqg"
        }
        response = requests.get('https://api.calendly.com/event_types', headers=headers, params=querystring)
        event = response.json()["collection"]
        for events in event:
            active = events['active']
            name = events['name']
            owner = name.split("-")
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
                        'owner': owner[2],
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


class event_calendly(models.Model):
    _name = 'mcm_openedx.calendly_event'

    scheduling_url_name = fields.Char(string="name")
    scheduling_url_created_at = fields.Date(string="created_at")
    scheduling_url_updated_at = fields.Date(string="updated_at")
    scheduling_url_uri = fields.Char(string="uri")

    event_name = fields.Char(string="name")
    location = fields.Char(string="Location")
    start_at = fields.Date(string="start_at")
    status = fields.Boolean(string="active")

    def event(self):
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer eyJraWQiOiIxY2UxZTEzNjE3ZGNmNzY2YjNjZWJjY2Y4ZGM1YmFmYThhNjVlNjg0MDIzZjdjMzJiZTgzNDliMjM4MDEzNWI0IiwidHlwIjoiUEFUIiwiYWxnIjoiRVMyNTYifQ.eyJpc3MiOiJodHRwczovL2F1dGguY2FsZW5kbHkuY29tIiwiaWF0IjoxNjYzMTQ4NjA2LCJqdGkiOiJkZDUwYWIxNy04ZDM3LTQyMjYtOGMzYy02NzMyNzI1MTM2NmUiLCJ1c2VyX3V1aWQiOiI1YWE5NWU3Mi0zNWFiLTQzOTEtOGZmNi0zNGNkZDRlMzRmODYifQ.TKiAMPGQFUdBODBHq8H-0LgQnbkldxW5V_hFacDyJgn53B-MbTQcBHLqwPx8uN_CiLfJahF_NJ1V4cc0Z5gmqg"
        }
        querystring = {"user": "https://api.calendly.com/users/5aa95e72-35ab-4391-8ff6-34cdd4e34f86",
                       "organization": "https://api.calendly.com/organizations/c7e28d20-f7eb-475f-954a-7ae1a36705e3",
                       "status": "active", "min_start_time": date.today()}

        r = requests.get('https://api.calendly.com/scheduled_events',
                         headers=headers, params=querystring)
        print("hahah", r.json()["collection"])
        shevent = r.json()["collection"]
        for shevents in shevent:
            scheduling_url_uri = shevents['uri']
            scheduling_url_name = shevents['name']
            print(scheduling_url_name)
            scheduling_url_created_at = shevents['created_at']
            scheduling_url_updated_at = shevents['updated_at']
            uuid_eventtype = scheduling_url_uri.split("/")
            params = {
                'statuts': 'active'
            }
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer eyJraWQiOiIxY2UxZTEzNjE3ZGNmNzY2YjNjZWJjY2Y4ZGM1YmFmYThhNjVlNjg0MDIzZjdjMzJiZTgzNDliMjM4MDEzNWI0IiwidHlwIjoiUEFUIiwiYWxnIjoiRVMyNTYifQ.eyJpc3MiOiJodHRwczovL2F1dGguY2FsZW5kbHkuY29tIiwiaWF0IjoxNjYzMTQ4NjA2LCJqdGkiOiJkZDUwYWIxNy04ZDM3LTQyMjYtOGMzYy02NzMyNzI1MTM2NmUiLCJ1c2VyX3V1aWQiOiI1YWE5NWU3Mi0zNWFiLTQzOTEtOGZmNi0zNGNkZDRlMzRmODYifQ.TKiAMPGQFUdBODBHq8H-0LgQnbkldxW5V_hFacDyJgn53B-MbTQcBHLqwPx8uN_CiLfJahF_NJ1V4cc0Z5gmqg"
            }

            rep = requests.get('https://api.calendly.com/scheduled_events/%s' % (uuid_eventtype[4]),
                               headers=headers, params=params)
            response = rep.json()['resource']
            event_name = response['name']
            location = response['location']['location']
            start_at = response['start_time']
            status = response['status']

            for existt in self.env['mcm_openedx.calendly_event'].sudo().search(
                    [('id', '!=', False)]):
                existe = self.env['mcm_openedx.calendly_event'].sudo().search(
                    [('scheduling_url_created_at', '=', shevents['created_at'])])
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
                        'status': status,
                    })
                    print(new)

    def test_url(self):
        return {
            "url": self.location,
            "type": "ir.actions.act_url"
        }
