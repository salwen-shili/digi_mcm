from odoo import api, fields, models, tools, _
import requests
import urllib.request
import base64

from datetime import datetime, timedelta, date
from odoo.modules.module import get_resource_path
from PIL import Image
import json
import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"
    onfido_sdk_token = fields.Char("SDK Token")
    onfido_applicant_id = fields.Char('Applicant ID')
    exp_date_sdk_token = fields.Datetime("Date d'expiration sdk token")
    validation_onfido = fields.Selection(selection=[
        ('clear', 'Validé'),
        ('fail', 'Refusé'),
        ('in_progress', 'en cours de vérification'),
    ], string='Statut des Documents')
    onfido_information_ids = fields.One2many('onfido.info', 'partner_id', string="Onfido information")

    def create_applicant(self, partner, token):
        """Creer un nouveau applicant avec api Onfido"""
        url_post = "https://api.eu.onfido.com/v3.4/applicants"
        headers = {
            'Authorization': 'Token token=' + token,
            # Already added when you pass json= but not when you pass data=
            #     'Content-Type': 'application/json',
        }
        partner.diviser_nom(partner)
        _logger.info('lastname %s' % str(partner.lastName))

        json_data = {
            "first_name": partner.firstName,
            "last_name": partner.lastName,

        }
        response = requests.post(url_post, headers=headers, data=json.dumps(json_data))
        applicant = response.json()
        _logger.info('ressssssssssppp %s' % str(applicant))
        if applicant['id']:
            partner.onfido_applicant_id = applicant['id']
        return applicant['id']

    def generateSdktoken(self, applicant_id, token, partner):
        """Génerer un sdk token avec API pour chaque applicant """
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        _logger.info("base urll %s" % str(base_url))
        url_sdk = "https://api.eu.onfido.com/v3.4/sdk_token"
        headers = {
            'Authorization': 'Token token=' + token,
            # Already added when you pass json= but not when you pass data=
            #     'Content-Type': 'application/json',
        }
        data = {
            "applicant_id": applicant_id,
            # "referrer": "http://localhost:8069/*",
             "referrer": "https://mcm-academy-staging-externe-5774940.dev.odoo.com/*"
        }
        response_token = requests.post(url_sdk, headers=headers, data=json.dumps(data))
        token_sdk = response_token.json()
        _logger.info("sdk token %s" % str(response_token.json()))
        _logger.info("sdk data %s" % str(data))
        if token_sdk['token']:
            partner.onfido_sdk_token = token_sdk['token']
            time_change = timedelta(minutes=90)
            partner.exp_date_sdk_token = datetime.now() + time_change
        return token_sdk['token']

    def workflow_run(self, applicant_id, token, workflow_id):
        url_workflow = "https://api.eu.onfido.com/v4/workflow_runs/"
        headers = {
            'Authorization': 'Token token=' + token,
            # Already added when you pass json= but not when you pass data=
            #     'Content-Type': 'application/json',
        }
        data = {
            "workflow_id": workflow_id,
            "applicant_id": applicant_id,

        }
        response_workflow_run = requests.post(url_workflow, headers=headers, data=json.dumps(data))
        workflow_run = response_workflow_run.json()
        _logger.info("hiiiiiiii %s" % str(response_workflow_run.json()))
        return workflow_run['id']

    def get_workflow_runs(self, workflow_run_id, token):
        """recuperer workflow_runs activé """
        url_wrkflow = "https://api.eu.onfido.com/v4/workflow_runs/" + workflow_run_id
        headers = {
            'Authorization': 'Token token=' + token,
            # Already added when you pass json= but not when you pass data=
            #     'Content-Type': 'application/json',
        }
        response_workflow_runs = requests.get(url_wrkflow, headers=headers)
        workflow_runs = response_workflow_runs.json()
        _logger.info('workflow_runs %s' % str(workflow_runs))
        return workflow_runs

    def get_listDocument(self, applicant_id, token):
        """recuperer le workflow """
        url_documents = "https://api.eu.onfido.com/v3.4/documents"
        headers = {
            'Authorization': 'Token token=' + token,
            # Already added when you pass json= but not when you pass data=
            #     'Content-Type': 'application/json',
        }
        params = {
            'applicant_id': applicant_id
        }

        response_documents = requests.get(url_documents, headers=headers, params=params)
        documents = response_documents.json()
        _logger.info('documents %s' % str(documents))
        return documents

    def getDocmument(self, token, documentid):
        """recupérer les informations lié aux documents chargés"""
        url_document = "https://api.eu.onfido.com/v3.4/documents/" + documentid
        headers = {
            'Authorization': 'Token token=' + token,
            # Already added when you pass json= but not when you pass data=
            #     'Content-Type': 'application/json',
        }
        response_documents = requests.get(url_document, headers=headers)
        document = response_documents.json()
        _logger.info('document %s' % str(document))
        return document

    def downloadDocument(self, document_id, token):
        """récupérer la version binaire des documents"""
        url_documentdownload = "https://api.eu.onfido.com/v3.4/documents/" + document_id + "/download"
        headers = {
            'Authorization': 'Token token=' + token,
            # Already added when you pass json= but not when you pass data=
            #     'Content-Type': 'application/json',
        }
        response_download = requests.get(url_documentdownload, headers=headers)
        download = response_download.content
        type_data = type(response_download)
        return download

    def downloadFace(self, applicant_id, token):
        """récupérer la version binaire de face photo """
        url_face_download = "https://api.eu.onfido.com/v3.4/applicants/" + applicant_id + "/face/download"
        headers = {
            'Authorization': 'Token token=' + token,
            # Already added when you pass json= but not when you pass data=
            #     'Content-Type': 'application/json',
        }
        response_download = requests.get(url_face_download, headers=headers)
        face = response_download.content
        type_data = type(response_download)
        return face

    def autofill(self, document_id, token):
        """récupérer les informations récupérées à partir des documents"""
        url_extraction = "https://api.eu.onfido.com/v3.4/extractions"
        headers = {
            'Authorization': 'Token token=' + token,
            # Already added when you pass json= but not when you pass data=
            #     'Content-Type': 'application/json',
        }
        data = {
            "document_id": document_id
        }
        response_extraction = requests.post(url_extraction, data=json.dumps(data), headers=headers)
        extractions = response_extraction.json()
        type_data = type(response_extraction)
        _logger.info('extracttttttttttttt %s' % str(extractions))
        return extractions

    def download_report(self, document_front_id, document_back_id, token):
        """récupérer le rapport de document"""
        url_rapport = "https://api.eu.onfido.com/v3.4/reports"
        headers = {
            'Authorization': 'Token token=' + token,

        }

        params = {
            'document_ids': [document_front_id, document_back_id]

        }
        response_report = requests.get(url_rapport, headers=headers, params=params)
        report = response_report.json()
        type_data = type(response_report)
        _logger.info('repooorttttttt %s' % str(report))
        return report