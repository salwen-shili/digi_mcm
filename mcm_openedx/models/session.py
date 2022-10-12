# -*- coding: utf-8 -*-

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

    def test_url(self):
        return {
            "type" : "ir.actions.act_window",
        "res_model" : self._name,
        "view_mode": "form",
        "res_id": self.id
        }
