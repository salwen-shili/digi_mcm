import random

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import functools
import xmlrpc.client
import requests
from requests.structures import CaseInsensitiveDict
from unidecode import unidecode
import locale


class Session(models.Model):
    _inherit = 'mcmacademy.session'

    def tes(self):
        print("test")
        for partner in self.env['mcmacademy.session'].sudo().search([('company_id', '=', 1),('name','!=','')]):

            print(partner.name)
            print(partner.date_fin)
            print(partner.clients_count)
