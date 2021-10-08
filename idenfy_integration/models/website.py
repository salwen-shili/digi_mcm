import json
import requests
from odoo import fields,models,api,_
from odoo.exceptions import ValidationError

class Website(models.Model):
    _inherit = 'website'

    idenfy_api_key = fields.Char('Idenfy API Key')
    idenfy_secret_key = fields.Char('Idenfy Secret Key')

    @api.model
    def _idenfy_send_request(self, request_url, request_data, params=False, method='GET'):
        if not self.idenfy_api_key:
            raise ValidationError(_("sendinblue API key is not found!"))

        api_key = self.idenfy_api_key
        data = json.dumps(request_data)
        api_url = "https://ivs.idenfy.com/api/v2/{url}".format(url=request_url)
        try:
            # req = requests.request(method, api_url, auth=('apikey', api_key), headers=headers, params=params, data=data)
            req = requests.request(method, api_url, auth=(self.idenfy_api_key, self.idenfy_secret_key), data=data)
            req.raise_for_status()
            response_text = req.text
        except requests.HTTPError as e:
            raise Warning("%s" % req.text)
        response = json.loads(response_text) if response_text else {}
        return response