from odoo import api, fields, models, tools
import requests
import onfido
import urllib.request
from odoo.modules.module import get_resource_path
from PIL import Image
import json
class InheritConfig(models.Model):
    _inherit = "res.partner"


    def create_applicant(self,partner):
        # api_instance = onfido.Api('api_sandbox.SwW0JwK3WRL.4ntnjwCs6IWIbVv882-QPjQ0Q_UiPSCz','region')
        url_post="https://api.eu.onfido.com/v3.4/applicants"

        token_test="api_sandbox.SwW0JwK3WRL.4ntnjwCs6IWIbVv882-QPjQ0Q_UiPSCz"

        # applicant_details = {
        #     "first_name": "Jane",
        #     "last_name": "Consider",
        #     "dob": "1990-01-31",
        #     "address": {
        #     "building_number": "100",
        #     "street": "Main Street",
        #     "town": "London",
        #     "postcode": "SW4 6EH",
        #     "country": "GBR",
        #
        # },}
        #
        # res=api_instance.applicant.create(applicant_details)
        # print('ressssssssssppp',res)

        headers = {
            'Authorization':'Token token='+token_test,
            # Already added when you pass json= but not when you pass data=
        #     'Content-Type': 'application/json',
        }

        json_data = {
            "first_name": partner.name,
            "last_name": "test",
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
        print('ressssssssssppp',applicant)
        return applicant['id']
        # self.upload_document(headers,applicant_id)
        # self.upload_photo(headers,applicant_id)



    def generateSdktoken(self,applicant_id):
        url_sdk = "https://api.eu.onfido.com/v3.4/sdk_token"

        token_test = "api_sandbox.SwW0JwK3WRL.4ntnjwCs6IWIbVv882-QPjQ0Q_UiPSCz"
        headers = {
            'Authorization': 'Token token=' + token_test,
            # Already added when you pass json= but not when you pass data=
            #     'Content-Type': 'application/json',
        }
        data = {
            "applicant_id": applicant_id,
            "referrer": "http://localhost:8069/upload_document"
        }
        response_token = requests.post(url_sdk, headers=headers, data=json.dumps(data))
        token_sdk=response_token.json()
        print(response_token.json())
        return token_sdk['token']

    def upload_document(self,headers,applicant_id):


        files = {
            'file': open('/home/ines/PycharmProjects/site_mcm_academy/onfido_api_integration/static/src/sample_driving_licence.png','rb'),

        }
        data={
            'applicant_id': applicant_id
        }

        post_document = requests.post('https://api.eu.onfido.com/v3.4/documents/', headers=headers, files=files,data=data)
        print('document',post_document)

    def upload_photo(self,headers,applicant_id):
        files = {
            'file': open(
                '/home/ines/PycharmProjects/site_mcm_academy/onfido_api_integration/static/src/sample_photo-e5e3561c.png;type=image/png',
                ),

        }
        data = {
            'applicant_id': applicant_id
        }

        post_photo = requests.post('https://api.eu.onfido.com/v3.4/live_photos', headers=headers, files=files,
                                      data=data)
        print('photo', post_photo)
        