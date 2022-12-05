# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import functools
import xmlrpc.client
import requests
from requests.structures import CaseInsensitiveDict
from unidecode import unidecode
import locale

class resCompany(models.Model):
    _inherit = "res.company"

    calendly_api_key = fields.Char(string='API key Calendly')
    # calendly_api_key_marwa = fields.Char(string='API key Calendly Marwa')
    # calendly_api_key_abir = fields.Char(string='API key Calendly Abir')
    # calendly_api_key_selmine = fields.Char(string='API key Calendly Selmine')
    moocit_api_key = fields.Char(string='API key MOOCIT')

class Session(models.Model):
    _inherit = 'mcmacademy.session'

    def test_url(self):
        return {
        "type" : "ir.actions.act_window",
        "res_model" : self._name,
        "view_mode": "form",
        "res_id": self.id
        }
