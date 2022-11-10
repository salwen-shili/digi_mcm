import base64
from urllib import parse

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
        response = requests.get(
            'https://eu-api.jotform.com/user/folders?apikey=98b07bd5ae3cd7054da0c386c4f699df&limit=1000&orderby=status')
        form = response.json()["content"]
        formm = form["forms"]
        for formms in formm:
            _logger.info("----------ok-----------")
            _logger.info(formm[formms]["url"].split("/")[3])
            form_id = formm[formms]["id"]
            title = formm[formms]["title"]
            statut = formm[formms]["status"]
            url = formm[formms]["url"]
            print(new)
            for existe in self.env['mcm_openedx.img'].sudo().search(
                    [('title', "like", self.title)]):

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
    _description = "Jotform_sub"
    partner_id = fields.Many2one('res.partner')
    email = fields.Char(string="EMAIL")

    def urlToirAttachement(self, document, url, name):
        _logger.info("Trying to Add url=%s to ir attachement.", url)
        attachment_obj = self.env["ir.attachment"]
        fileUrl = parse.urlparse(url)

        if not fileUrl.scheme:
            fileUrl = parse.urlparse("{}{}".format("http://", fileUrl))
        attachment = {
            "name": name,
            "type": "url",
            "url": fileUrl.geturl(),
            "res_id": document.id,
            "res_model": "documents.document",
        }
        attachment_obj.create(attachment)

    def form_sub(self):
        _logger.info("okokokokokokoko")
        response_sub_id = requests.get(
            'https://eu-api.jotform.com/submission/5328399930415747604?apikey=98b07bd5ae3cd7054da0c386c4f699df')
        form_info_sub = response_sub_id.json()["content"]
        if 'answers' in form_info_sub:
            for i, valeur in form_info_sub["answers"].items():
                if form_info_sub["answers"][i]["name"] == "email":
                    _logger.info(form_info_sub["answers"][i]["answer"])
                    for partner in self.env['res.partner'].search(
                            [('email', 'ilike', form_info_sub["answers"][i]["answer"])]):
                        _logger.info("---------PARTNERR--------")
                        existe_sub = self.env['mcm_openedx.form_info'].sudo().search(
                            [('email', "like", form_info_sub["answers"][i]["answer"])])
                        existe_sub.partner_id = partner.id
                        _logger.info(existe_sub.email)
                        if not existe_sub:
                            new = self.env['mcm_openedx.form_info'].sudo().create({
                                'email': form_info_sub["answers"][i]["answer"]
                            })
                            print(new)

                if form_info_sub["answers"][i]["name"] == "fileUpload2":

                    url = form_info_sub["answers"][i]["answer"][0]
                    name = form_info_sub["answers"][i]["answer"][0]
                    _logger.info("urll")
                    _logger.info(url)
                    image_binary = base64.b64encode(requests.get(url).content)
                    namee = form_info_sub["answers"][i]["text"]

                folder_id = self.env['documents.folder'].sudo().search(
                    [('name', "=", ('Documents MCM ACADEMY')), ('company_id', "=", 1)], limit=1)
                for partner in self.env['res.partner'].search(
                        [('email', '=', "lokaha8119@lenfly.com")]):
                    document = self.env['documents.document'].create({'name': namee,
                                                                      'type': 'binary',
                                                                      'partner_id': partner.id,
                                                                      'folder_id': folder_id.id,
                                                                      'datas': image_binary,

                                                                      'state': 'validated', })

                    self.urlToirAttachement(document, url, name)

            # _logger.info(i)
            # _logger.info(valeur['name'])
            # if valeur['name'] == "email":
            # _logger.info(form_info_sub["answers"][i])

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
