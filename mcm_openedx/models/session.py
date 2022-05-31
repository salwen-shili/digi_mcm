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

