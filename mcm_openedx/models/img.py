import base64
import requests
from jotform import *

from odoo import models, fields
from odoo.tools import json

import logging

_logger = logging.getLogger(__name__)


class img(models.Model):
    _name = 'mcm_openedx.img'
    _description = "Jotform"

    id = fields.Char(string="ID")
    title = fields.Char(string="Titre Formulaire")
    statut = fields.Char(string="Statut Formulaire")
    url = fields.Char(string="Titre Formulaire")

    def get_form(self):
        print("get events")
        jotformAPIClient = JotformAPIClient("98b07bd5ae3cd7054da0c386c4f699df")
        forms = jotformAPIClient.get_forms()
        for form in forms:
            _logger.info(form["title"])
