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
        response_form = requests.get(
                'https://eu-api.jotform.com/form/222334146537352/submissions?apikey=98b07bd5ae3cd7054da0c386c4f699df&limit=1000&orderby=created_at')
        form_info = response_form.json()["content"]
        for form_infos in form_info:
            _logger.info(form_infos['id'])
            # Similar to form/form-id submissions. But only get a single submission
            response_sub_id = requests.get(
                'https://eu-api.jotform.com/submission/%s?apikey=98b07bd5ae3cd7054da0c386c4f699df' % (
                    form_infos['id']))
            form_info_sub = response_sub_id.json()["content"]
            _logger.info(form_info_sub)

            if 'answers' in form_info_sub:
                for i, valeur in form_info_sub["answers"].items():
                    if form_info_sub["answers"][i]["name"] == "email":
                        _logger.info(form_info_sub["answers"][i]["answer"])
                        for partner_email in self.env['res.partner'].search(
                                [('email', 'ilike', form_info_sub["answers"][i]["answer"])]):
                            existe_sub = self.env['mcm_openedx.form_info'].sudo().search(
                                [('email', "like", form_info_sub["answers"][i]["answer"])])
                            existe_sub.partner_id = partner_email.id
                            _logger.info(existe_sub.email)
                            if not existe_sub:
                                new = self.env['mcm_openedx.form_info'].sudo().create({
                                    'email': form_info_sub["answers"][i]["answer"]
                                })
                                print(new)

                    if form_info_sub["answers"][i]["name"] == "justificatifDe64":
                        url = form_info_sub["answers"][i]["answer"]
                        if url:
                            # 👉️ Check if my_var is not None (null)
                            _logger.info(form_info_sub["answers"][i]["answer"])
                            image_binary = base64.b64encode(requests.get(url[0].replace(" ", "%20")).content)
                            name = form_info_sub["answers"][i]["text"]
                            folder_id = self.env['documents.folder'].sudo().search(
                                [('name', "=", ('Documents MCM ACADEMY')), ('company_id', "=", 1)], limit=1)
                            for partner in self.env['res.partner'].search(
                                    [('email', '=', form_info_sub["answers"]["85"]["answer"])]):
                                existe_doc = self.env['documents.document'].search(
                                    [('name', '=', name), ('partner_id', '=', partner.id)])
                                if not existe_doc:
                                    document = self.env['documents.document'].create({'name': name,
                                                                                      'type': 'binary',
                                                                                      'partner_id': partner.id,
                                                                                      'folder_id': folder_id.id,
                                                                                      'datas': image_binary,
                                                                                      'state': 'validated', })

                                    self.urlToirAttachement(document, url[0].replace(" ", "%20"), name)
                                    self.env.cr.commit()

                    elif form_info_sub["answers"][i]["name"] == "attestationDhebergement":
                        url = form_info_sub["answers"][i]["answer"]
                        if url:
                            # 👉️ Check if my_var is not None (null)
                            _logger.info(form_info_sub["answers"][i]["answer"])
                            image_binary = base64.b64encode(requests.get(url[0].replace(" ", "%20")).content)
                            name = form_info_sub["answers"][i]["text"]
                            folder_id = self.env['documents.folder'].sudo().search(
                                [('name', "=", ('Documents Digimoov')), ('company_id', "=", 1)], limit=1)
                            for partner in self.env['res.partner'].search(
                                    [('email', '=', form_info_sub["answers"]["85"]["answer"])]):
                                existe_doc = self.env['documents.document'].search(
                                    [('name', '=', name), ('partner_id', '=', partner.id)])
                                if not existe_doc:
                                    document = self.env['documents.document'].create({'name': name,
                                                                                      'type': 'binary',
                                                                                      'partner_id': partner.id,
                                                                                      'folder_id': folder_id.id,
                                                                                      'datas': image_binary,
                                                                                      'state': 'waiting', })

                                    self.urlToirAttachement(document, url[0].replace(" ", "%20"), name)
                                    self.env.cr.commit()

                    elif form_info_sub["answers"][i]["name"] == "vousAvez" :
                        url = form_info_sub["answers"][i]["answer"]
                        if url:
                            # 👉️ Check if my_var is not None (null)
                            _logger.info(form_info_sub["answers"][i]["answer"])
                            image_binary = base64.b64encode(requests.get(url.replace(" ", "%20")).content)
                            name = form_info_sub["answers"][i]["text"]
                            folder_id = self.env['documents.folder'].sudo().search(
                                [('name', "=", ('Documents MCM ACADEMY')), ('company_id', "=", 1)], limit=1)
                            for partner in self.env['res.partner'].search(
                                    [('email', '=', form_info_sub["answers"]["85"]["answer"])]):
                                existe_doc = self.env['documents.document'].search(
                                    [('name', '=', name), ('partner_id', '=', partner.id)])
                                if not existe_doc:
                                    document = self.env['documents.document'].create({'name': name,
                                                                                      'type': 'binary',
                                                                                      'partner_id': partner.id,
                                                                                      'folder_id': folder_id.id,
                                                                                      'datas': image_binary,
                                                                                      'state': 'validated', })

                                    self.urlToirAttachement(document, url[0].replace(" ", "%20"), name)
                                    self.env.cr.commit()

                    elif form_info_sub["answers"][i]["name"] == "pieceDidentite":
                        url = form_info_sub["answers"][i]["answer"]
                        if url:
                            # 👉️ Check if my_var is not None (null)
                            _logger.info(form_info_sub["answers"][i]["answer"])
                            image_binary = base64.b64encode(requests.get(url[0].replace(" ", "%20")).content)
                            name = form_info_sub["answers"][i]["text"]
                            folder_id = self.env['documents.folder'].sudo().search(
                                [('name', "=", ('Documents MCM ACADEMY')), ('company_id', "=", 1)], limit=1)
                            for partner in self.env['res.partner'].search(
                                    [('email', '=', form_info_sub["answers"]["85"]["answer"])]):
                                existe_doc = self.env['documents.document'].search(
                                    [('name', '=', name), ('partner_id', '=', partner.id)])
                                if not existe_doc:
                                    document = self.env['documents.document'].create({'name': name,
                                                                                      'type': 'binary',
                                                                                      'partner_id': partner.id,
                                                                                      'folder_id': folder_id.id,
                                                                                      'datas': image_binary,
                                                                                      'state': 'validated', })

                                    self.urlToirAttachement(document, url[0].replace(" ", "%20"), name)
                                    self.env.cr.commit()

                    elif form_info_sub["answers"][i]["name"] == "pieceDidentite70":
                        url = form_info_sub["answers"][i]["answer"]
                        if url:
                            # 👉️ Check if my_var is not None (null)
                            _logger.info(form_info_sub["answers"][i]["answer"])
                            image_binary = base64.b64encode(requests.get(url[0].replace(" ", "%20")).content)
                            name = form_info_sub["answers"][i]["text"]
                            folder_id = self.env['documents.folder'].sudo().search(
                                [('name', "=", ('Documents MCM ACADEMY')), ('company_id', "=", 1)], limit=1)
                            for partner in self.env['res.partner'].search(
                                    [('email', '=', form_info_sub["answers"]["85"]["answer"])]):
                                existe_doc = self.env['documents.document'].search(
                                    [('name', '=', name), ('partner_id', '=', partner.id)])
                                if not existe_doc:
                                    document = self.env['documents.document'].create({'name': name,
                                                                                      'type': 'binary',
                                                                                      'partner_id': partner.id,
                                                                                      'folder_id': folder_id.id,
                                                                                      'datas': image_binary,
                                                                                      'state': 'validated', })

                                    self.urlToirAttachement(document, url[0].replace(" ", "%20"), name)
                                    self.env.cr.commit()
