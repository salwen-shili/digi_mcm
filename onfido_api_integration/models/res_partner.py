from odoo import api, fields, models, tools
import requests
import urllib.request
from datetime import datetime, timedelta, date
from odoo.modules.module import get_resource_path
from PIL import Image
import json
import logging

_logger = logging.getLogger(__name__)
class InheritConfig(models.Model):
    _inherit = "res.partner"
    onfido_sdk_token=fields.Char("SDK Token")
    onfido_applicant_id=fields.Char('Applicant ID')
    exp_date_sdk_token=fields.Datetime("Date d'expiration sdk token ")

    def create_applicant(self,partner,token):
        """Creer un nouveau applicant avec api Onfido"""
        url_post = "https://api.eu.onfido.com/v3.4/applicants"
        headers = {
            'Authorization':'Token token='+token,
            # Already added when you pass json= but not when you pass data=
        #     'Content-Type': 'application/json',
        }
        partner.diviser_nom(partner)
        _logger.info('lastname %s'%str(partner.lastName))
        
        json_data = {
            "first_name": partner.firstName,
            "last_name": partner.lastName,
            "dob": "1990-01-31",
            "address": {
            "building_number": "100",
            "street": "Main Street",
            "town": "London",
            "postcode": "SW4 6EH",
            "country": "GBR",
            }
        }
        response = requests.post(url_post, headers=headers, data=json.dumps(json_data))
        applicant=response.json()
        _logger.info('ressssssssssppp %s' %str(applicant))
        if applicant['id']:
            partner.onfido_applicant_id=applicant['id']
        return applicant['id']

    def generateSdktoken(self,applicant_id,token,partner):
        """Génerer un sdk token avec API pour chaque applicant """
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        _logger.info("base urll %s"%str(base_url))
        url_sdk = "https://api.eu.onfido.com/v3.4/sdk_token"
        headers = {
            'Authorization': 'Token token=' + token,
            # Already added when you pass json= but not when you pass data=
            #     'Content-Type': 'application/json',
        }
        data = {
            "applicant_id": applicant_id,
            "referrer": "https://dev.digimoov.fr/*"
        }
        response_token = requests.post(url_sdk, headers=headers, data=json.dumps(data))
        token_sdk=response_token.json()
        _logger.info("sdk token %s" %str(response_token.json()))
        if token_sdk['token']:
            partner.onfido_sdk_token=token_sdk['token']
            time_change =timedelta(minutes=90)
            partner.exp_date_sdk_token=datetime.now()+time_change
        return token_sdk['token']

    def workflow_run(self,applicant_id,token):
        url_workflow = "https://api.eu.onfido.com/v4/workflow_runs/"
        headers = {
            'Authorization': 'Token token=' + token,
            # Already added when you pass json= but not when you pass data=
            #     'Content-Type': 'application/json',
        }
        data = {
            "workflow_id": "4201e707-42fd-4935-8a64-2c621712af11",
            "applicant_id": applicant_id,

        }
        response_workflow_run = requests.post(url_workflow, headers=headers, data=json.dumps(data))
        workflow_run = response_workflow_run.json()
        _logger.info("hiiiiiiii %s" %str(response_workflow_run.json()))
        return workflow_run['id']


        