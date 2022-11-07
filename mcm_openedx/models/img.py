import base64
import requests

from odoo import models, fields
from odoo.tools import json


class img(models.Model):
    _name = 'mcm_openedx.img'
    _description = "Jotform"

    id = fields.Char(string="ID")
    title = fields.Char(string="Titre Formulaire")
    statut = fields.Char(string="Statut Formulaire")
    url = fields.Char(string="Titre Formulaire")


    def get_form(self):
        print("get events")
