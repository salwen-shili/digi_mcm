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
        _logger.info("----------ok-----------")
        response = requests.get(
            'https://eu-api.jotform.com/user/forms?apikey=98b07bd5ae3cd7054da0c386c4f699df&limit=200&orderby=new')
        form = response.json()["content"]
        for forms in form:
            form_id = forms["id"]
            title = forms["title"]
            statut = forms["status"]
            url = forms["url"]
            for existe in self.env['mcm_openedx.img'].sudo().search([('url', "!=", False)]):
                form_sub = self.env['mcm_openedx.img'].sudo().search([('url', "=", forms["url"])])
                if not form_sub:
                    _logger.info(forms["id"])
                    _logger.info(forms["url"].split("/")[3])
                    new = self.env['mcm_openedx.img'].sudo().create({
                        'form_id': url.split("/")[3],
                        'title': title,
                        'statut': statut,
                        'url': url,
                    })


class form_info(models.Model):
    _name = 'mcm_openedx.form_info'
    _description = "Jotform_sub"
    partner_id = fields.Many2one('res.partner')
    email = fields.Char(string="EMAIL")

    def form_sub(self):
        # parcourir la liste des submission dans le form Form Demande de Jdom + JDC v15/11/2022:
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
            # parcourir la liste des reponse pour chaque submissions
            if 'answers' in form_info_sub:
                # parcourir la liste des reponse dans le form
                for i, valeur in form_info_sub["answers"].items():
                    if form_info_sub["answers"][i]["name"] == "email":
                        _logger.info(form_info_sub["answers"][i]["answer"])
                        for partner_email in self.env['res.partner'].search(
                                [('email', 'ilike', form_info_sub["answers"][i]["answer"])]):
                            existe_sub = self.env['mcm_openedx.form_info'].sudo().search(
                                [('email', "like", form_info_sub["answers"][i]["answer"])])
                            existe_sub.partner_id = partner_email.id
                            # verifier si la personne existe
                            # verifier fiche client
                            if not existe_sub:
                                new = self.env['mcm_openedx.form_info'].sudo().create({
                                    'email': form_info_sub["answers"][i]["answer"]
                                })
                                self.send_ticket(name)

                    if form_info_sub["answers"][i]["name"] == "justificatifDe64":
                        url = form_info_sub["answers"][i]["answer"]
                        if url:
                            # 👉️ Check if my_var is not None (null)
                            image_binary = base64.b64encode(requests.get(url[0].replace(" ", "%20")).content)
                            name = form_info_sub["answers"][i]["text"]
                            folder_id = self.env['documents.folder'].sudo().search(
                                [('name', "=", ('Documents Digimoov')), ('company_id', "=", 2)], limit=1)
                            for partner in self.env['res.partner'].search(
                                    [('email', '=', form_info_sub["answers"]["85"]["answer"])]):
                                existe_doc = self.env['documents.document'].search(
                                    [('name', '=', name), ('partner_id', '=', partner.id)])
                                # verifier les document si existe avec le nom jotform, et partner

                                if not existe_doc:
                                    document = self.env['documents.document'].create({'name': name,
                                                                                      'type': 'binary',
                                                                                      'partner_id': partner.id,
                                                                                      'folder_id': folder_id.id,
                                                                                      'datas': image_binary,
                                                                                      'state': 'waiting', })

                                    # replace " " avec  %20 pour eliminer les espace
                                    # Ajout ticket pour notiifer le service examn pour changer mp
                                    # ajouter condition sur ticket

                                    vals = {

                                        'description': 'New document Jotform JDOM %s' % (name),
                                        'name': 'Merci de verifer le document de %s' % (partner.name),
                                        'partner_id': partner.id,

                                        'team_id': self.env['helpdesk.team'].sudo().search(
                                            [('name', 'like', 'Service Examen Digimoov'), ('company_id', "=", 2)],
                                            limit=1).id,
                                    }
                                    description = "New document Jotform JDOM"
                                    ticket = self.env['helpdesk.ticket'].sudo().search(
                                        [("description", "=", description)])
                                    if not ticket:
                                        print("cree ticket")
                                        new_ticket = self.env['helpdesk.ticket'].sudo().create(
                                            vals)
                                    self.env.cr.commit()

                    elif form_info_sub["answers"][i]["name"] == "attestationDhebergement":
                        url = form_info_sub["answers"][i]["answer"]
                        if url:
                            # 👉️ Check if my_var is not None (null)
                            image_binary = base64.b64encode(requests.get(url[0].replace(" ", "%20")).content)
                            name = form_info_sub["answers"][i]["text"]
                            folder_id = self.env['documents.folder'].sudo().search(
                                [('name', "=", ('Documents Digimoov')), ('company_id', "=", 2)], limit=1)
                            for partner in self.env['res.partner'].search(
                                    [('email', '=', form_info_sub["answers"]["85"]["answer"])]):
                                existe_doc = self.env['documents.document'].search(
                                    [('name', '=', name), ('partner_id', '=', partner.id)])
                                # verifier les document si existe avec le nom jotform, et partner

                                if not existe_doc:
                                    document = self.env['documents.document'].create({'name': name,
                                                                                      'type': 'binary',
                                                                                      'partner_id': partner.id,
                                                                                      'folder_id': folder_id.id,
                                                                                      'datas': image_binary,
                                                                                      'state': 'waiting', })

                                    # replace " " avec  %20 pour eliminer les espace
                                    # Ajout ticket pour notiifer le service examn pour changer mp
                                    # ajouter condition sur ticket

                                    vals = {

                                        'description': 'New document Jotform JDOM %s' % (name),
                                        'name': 'Merci de verifer le document de %s' % (partner.name),
                                        'partner_id': partner.id,

                                        'team_id': self.env['helpdesk.team'].sudo().search(
                                            [('name', 'like', 'Service Examen Digimoov'), ('company_id', "=", 2)],
                                            limit=1).id,
                                    }
                                    description = "New document Jotform JDOM"
                                    ticket = self.env['helpdesk.ticket'].sudo().search(
                                        [("description", "=", description)])
                                    if not ticket:
                                        print("cree ticket")
                                        new_ticket = self.env['helpdesk.ticket'].sudo().create(
                                            vals)
                                    self.env.cr.commit()

                    elif form_info_sub["answers"][i]["name"] == "vousAvez":
                        url = form_info_sub["answers"][i]["answer"]
                        if url:
                            # 👉️ Check if my_var is not None (null)
                            image_binary = base64.b64encode(requests.get(url[0].replace(" ", "%20")).content)
                            name = form_info_sub["answers"][i]["text"]
                            folder_id = self.env['documents.folder'].sudo().search(
                                [('name', "=", ('Documents Digimoov')), ('company_id', "=", 2)], limit=1)
                            for partner in self.env['res.partner'].search(
                                    [('email', '=', form_info_sub["answers"]["85"]["answer"])]):
                                existe_doc = self.env['documents.document'].search(
                                    [('name', '=', name), ('partner_id', '=', partner.id)])
                                # verifier les document si existe avec le nom jotform, et partner
                                if not existe_doc:
                                    document = self.env['documents.document'].create({'name': name,
                                                                                      'type': 'binary',
                                                                                      'partner_id': partner.id,
                                                                                      'folder_id': folder_id.id,
                                                                                      'datas': image_binary,
                                                                                      'state': 'waiting', })

                                    # replace " " avec  %20 pour eliminer les espace
                                    # Ajout ticket pour notiifer le service examn pour changer mp
                                    # ajouter condition sur ticket

                                    vals = {

                                        'description': 'New document Jotform JDOM %s' % (name),
                                        'name': 'Merci de verifer le document de %s' % (partner.name),
                                        'partner_id': partner.id,

                                        'team_id': self.env['helpdesk.team'].sudo().search(
                                            [('name', 'like', 'Service Examen Digimoov'), ('company_id', "=", 2)],
                                            limit=1).id,
                                    }
                                    description = "New document Jotform JDOM"
                                    ticket = self.env['helpdesk.ticket'].sudo().search(
                                        [("description", "=", description)])
                                    if not ticket:
                                        print("cree ticket")
                                        new_ticket = self.env['helpdesk.ticket'].sudo().create(
                                            vals)
                                    self.env.cr.commit()

                    elif form_info_sub["answers"][i]["name"] == "pieceDidentite":
                        url = form_info_sub["answers"][i]["answer"]
                        if url:
                            # 👉️ Check if my_var is not None (null)
                            image_binary = base64.b64encode(requests.get(url[0].replace(" ", "%20")).content)
                            name = form_info_sub["answers"][i]["text"]
                            folder_id = self.env['documents.folder'].sudo().search(
                                [('name', "=", ('Documents Digimoov')), ('company_id', "=", 2)], limit=1)
                            for partner in self.env['res.partner'].search(
                                    [('email', '=', form_info_sub["answers"]["85"]["answer"])]):
                                existe_doc = self.env['documents.document'].search(
                                    [('name', '=', name), ('partner_id', '=', partner.id)])
                                # verifier les document si existe avec le nom jotform, et partner
                                if not existe_doc:
                                    document = self.env['documents.document'].create({'name': name,
                                                                                      'type': 'binary',
                                                                                      'partner_id': partner.id,
                                                                                      'folder_id': folder_id.id,
                                                                                      'datas': image_binary,
                                                                                      'state': 'waiting', })

                                    # replace " " avec  %20 pour eliminer les espace
                                    # Ajout ticket pour notiifer le service examn pour changer mp
                                    # ajouter condition sur ticket

                                    vals = {

                                        'description': 'New document Jotform JDOM %s' % (name),
                                        'name': 'Merci de verifer le document de %s' % (partner.name),
                                        'partner_id': partner.id,

                                        'team_id': self.env['helpdesk.team'].sudo().search(
                                            [('name', 'like', 'Service Examen Digimoov'), ('company_id', "=", 2)],
                                            limit=1).id,
                                    }
                                    description = "New document Jotform JDOM"
                                    ticket = self.env['helpdesk.ticket'].sudo().search(
                                        [("description", "=", description)])
                                    if not ticket:
                                        print("cree ticket")
                                        new_ticket = self.env['helpdesk.ticket'].sudo().create(
                                            vals)
                                    self.env.cr.commit()

                    elif form_info_sub["answers"][i]["name"] == "pieceDidentite70":
                        url = form_info_sub["answers"][i]["answer"]
                        if url:
                            # 👉️ Check if my_var is not None (null)
                            image_binary = base64.b64encode(requests.get(url[0].replace(" ", "%20")).content)
                            name = form_info_sub["answers"][i]["text"]
                            folder_id = self.env['documents.folder'].sudo().search(
                                [('name', "=", ('Documents Digimoov')), ('company_id', "=", 2)], limit=1)
                            # chercher si la submission est
                            for partner in self.env['res.partner'].search(
                                    [('email', '=', form_info_sub["answers"]["85"]["answer"])]):
                                existe_doc = self.env['documents.document'].search(
                                    [('name', '=', name), ('partner_id', '=', partner.id)])
                                # verifier les document si existe avec le nom jotform, et partner
                                if not existe_doc:
                                    document = self.env['documents.document'].create({'name': name,
                                                                                      'type': 'binary',
                                                                                      'partner_id': partner.id,
                                                                                      'folder_id': folder_id.id,
                                                                                      'datas': image_binary,
                                                                                      'state': 'waiting', })

                                    # replace " " avec  %20 pour eliminer les espace
                                    # Ajout ticket pour notiifer le service examn pour changer mp
                                    # ajouter condition sur ticket

                                    vals = {

                                        'description': 'New document Jotform JDOM %s' % (name),
                                        'name': 'Merci de verifer le document de %s' % (partner.name),
                                        'partner_id': partner.id,

                                        'team_id': self.env['helpdesk.team'].sudo().search(
                                            [('name', 'like', 'Service Examen Digimoov'), ('company_id', "=", 2)],
                                            limit=1).id,
                                    }
                                    description = "New document Jotform JDOM"
                                    ticket = self.env['helpdesk.ticket'].sudo().search(
                                        [("description", "=", description)])
                                    if not ticket:
                                        print("cree ticket")
                                        new_ticket = self.env['helpdesk.ticket'].sudo().create(
                                            vals)
                                    self.env.cr.commit()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
