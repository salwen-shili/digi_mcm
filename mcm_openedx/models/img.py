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

    form_id = fields.Char(string="ID")
    title = fields.Char(string="Titre Formulaire")
    statut = fields.Char(string="Statut Formulaire")
    url = fields.Char(string="Titre Formulaire")
    partner_id = fields.Many2one('res.partner')
    email = fields.Char(string="EMAIL")

    def get_form(self):
        print("get events")
        response = requests.get('https://eu-api.jotform.com/user/folders?apikey=98b07bd5ae3cd7054da0c386c4f699df')
        form = response.json()["content"]
        formm = form["forms"]
        for formms in formm:

            _logger.info("----------ok-----------")
            _logger.info(formm[formms]["url"].split("/")[3])

            form_id = formm[formms]["id"]
            title = formm[formms]["title"]
            statut = formm[formms]["status"]
            url = formm[formms]["url"]
            new = self.env['mcm_openedx.img'].sudo().create({
                'title': title,
                'statut': statut,
                'url': url,

            })
            new.form_id = url.split("/")[3]
            print(new)

            for existe in self.env['mcm_openedx.img'].sudo().search(
                    [('form_id', "like", url.split("/")[3])]):
                _logger.info("-----get form info-------")
                response_form = requests.get(
                    'https://eu-api.jotform.com/form/%s/submissions?apikey=98b07bd5ae3cd7054da0c386c4f699df' % (
                        form_id))
                form_info = response_form.json()["content"]
                _logger.info("---------FORM submission--------")
                _logger.info(form_info)
                # for partner in self.env['res.partner'].search(
                #        [('email', '=', email)]):
                #   print()

                if not existe:
                    new = self.env['mcm_openedx.img'].sudo().create({
                        'form_id': url.split("/")[3],
                        'title': title,
                        'statut': statut,
                        'url': url,

                    })
                    print(new)





class form_info(models.Model):
    _name = 'mcm_openedx.form_info'
    _description = "Jotform"

    partner_id = fields.Many2one('res.partner')
    email = fields.Char(string="EMAIL")
