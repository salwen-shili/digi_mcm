import base64
import requests

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
        # Get a list of forms for this account. Includes basic details such as title of the form, when it was created, number of new and total submissions.
        response = requests.get(
            'https://eu-api.jotform.com/user/folders?apikey=98b07bd5ae3cd7054da0c386c4f699df')
        form = response.json()["content"]
        formm = form["forms"]
        count = 0

        for formms in formm:
            form_id = formm[formms]["id"]
            title = formm[formms]["title"]
            statut = formm[formms]["status"]
            url = formm[formms]["url"]
            for existe in self.env['mcm_openedx.img'].sudo().search(
                    [('title', "=", formm[formms]["title"])]):
                _logger.info(existe.title)
                count = count + 1
        _logger.info(count)


class form_info(models.Model):
    _name = 'mcm_openedx.form_info'
    _description = "Jotform_sub"
    partner_id = fields.Many2one('res.partner')
    email = fields.Char(string="EMAIL")

    def form_sub(self):
        _logger.info("okokokokokokoko")
        emails = ["54" , "169" , "3", "31"]

        for existe in self.env['mcm_openedx.img'].sudo().search(
                []):
            # List of form responses. answers array has the submitted data. Created_at is the date of the submission.
            response_form = requests.get(
                'https://eu-api.jotform.com/form/%s/submissions?apikey=98b07bd5ae3cd7054da0c386c4f699df' % (
                    existe.form_id))
            form_info = response_form.json()["content"]
            for form_infos in form_info:
                # Similar to /form/{form-id}/submissions. But only get a single submission.
                response_sub_id = requests.get(
                    'https://eu-api.jotform.com/submission/5328399930415747604?apikey=98b07bd5ae3cd7054da0c386c4f699df ')
                form_info_sub = response_sub_id.json()["content"]
                if 'answers' in form_info_sub:
                    for i in emails:
                        if i in form_info_sub["answers"]:
                            if 'answer' in form_info_sub["answers"][i]:
                                email_form_info_sub = form_info_sub["answers"]["54"]['answer']
                                _logger.info(email_form_info_sub)

                        # for partner in self.env['res.partner'].search(
                        #         [('email', 'ilike', existe.email)]):
                        #     _logger.info("---------PARTNERR--------")
                        #          _logger.info(partner.email)
                        #         partner_id = partner.id
                        #         new = self.env['mcm_openedx.form_info'].sudo().create({
                        #             'email': partner.email,
                        #             'partner_id': partner.id,
                        #
                        #         })
                        #         print(new)
