# -*- coding: utf-8 -*-
import logging

from odoo import models, http, fields
import http.client

_logger = logging.getLogger(__name__)
import requests


class calendly_integration(models.Model):
    _name = 'mcm_openedx.calendly_integration'
    _description = "mcm_openedx.calendly_integration"

    # Ajouter champs
    name = fields.Char(string="name")
    slug = fields.Char(string="nom de cour")

    active = fields.Char(string="active")
    created_at = fields.Date(string="created_at")
    owner = fields.Char(string="owner")
    scheduling_url = fields.Char(string="scheduling_ur")
    updated_at = fields.Date(string="updated_ae")
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
            print("Test send mail calendly APPII TESTT", events)
            active = events['active']
            name = events['name']
            slug = events['slug']
            created_at = events['created_at']
            owner = events['profile']['owner']
            scheduling_url = events['scheduling_url']
            updated_at = events['updated_at']
            uri = events['uri']
            for existt in self.env['mcm_openedx.calendly_integration'].sudo().search(
                    []):
                print("aaaaaaaaaaaaaaaaaaaaaaaa", existt.name)

                if (existt):
                    print("deja existant")
                    print("aaaaaaaaaaaaaaaaaaaaaaaa", existt.name)

                if not existt:
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
