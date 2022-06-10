from odoo import api, fields, models
import requests

class InheritConfig(models.Model):
    _inherit = "res.partner"


    def test_api_onfido(self):
        url_post="https://api.eu.onfido.com/v3.4/applicants"
        token_test="api_sandbox.SwW0JwK3WRL.4ntnjwCs6IWIbVv882-QPjQ0Q_UiPSCz"
        headers = {
            'Authorization':token_test,
            # Already added when you pass json= but not when you pass data=
        #     'Content-Type': 'application/json',
        }

        json_data = {
            'applicant_id': '<APPLICANT_ID>',
            'referrer': 'https://*.example.com/example_page/*',
            'cross_device_url': 'https://example.com',
        }

        response = requests.post('https://api.eu.onfido.com/v3.4/sdk_token', headers=headers, json=json_data)

        print('ressssssssssppp',response.json())