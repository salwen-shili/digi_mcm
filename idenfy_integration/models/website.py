import uuid
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
            raise ValidationError(_("Idenfy API/Secret key is not found!"))

        api_key = self.idenfy_api_key
        data = json.dumps(request_data)
        api_url = "https://ivs.idenfy.com/api/v2/{url}".format(url=request_url)
        try:
            req = requests.request(method, api_url, auth=(self.idenfy_api_key, self.idenfy_secret_key), data=data)
            req.raise_for_status()
            response_text = req.text
        except requests.HTTPError as e:
            raise Warning("%s" % req.text)
        response = json.loads(response_text) if response_text else {}
        return response

    def generate_idenfy_token(self, user_id=False):
        idenfy_data_obj = self.env['idenfy.data']
        user_id = user_id or self.env.uid
        for website in self:
            user = self.env['res.users'].sudo().search([('id', "=", user_id)])
            partner = user.partner_id
            if partner.is_idenfy_approved:
                    return True
            idenfy_data_obj.search([('partner_id', '=', partner.id)]).unlink()
            idenfy_id = uuid.uuid4().hex[:8]
            req_data = {"clientId": '{}'.format(idenfy_id), 'documents': ['ID_CARD', 'PASSPORT', 'RESIDENCE_PERMIT'], "tokenType": "DOCUMENT","locale":"fr"}
            res = website._idenfy_send_request('token', request_data=req_data)
            idenfy_data_obj.create(
                {
                    'type': 'other_documents',
                    'req_data': req_data,
                    'res_data': res,
                    'idenfy_id': idenfy_id,
                    'token': res.get('authToken', ''),
                    'scanref': res.get('scanRef', ''),
                    'partner_id': partner.id,
                    'website_id': website.id
                }
            )
        return True
