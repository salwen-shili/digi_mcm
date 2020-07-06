from odoo import http
from odoo.http import request
import requests
import werkzeug
import json

class CalendlyController(http.Controller):

    @http.route('/update_calendly/<string:code>', type="http", auth="user")
    def update_token(self,code=None, **kw):
        headers = {
            'Host': 'calendly.com',
            'Content - Type': 'application / x - www - form - urlencoded'
        }

        url = "http://calendly.com/oauth/token"

        data = {'client_id': '30619c87f05a76ccd4f44ee59d4281a3714395299a4b277492c7f0d149e09462',
                'client_secret': '86bd046a39760594cc2fdd7036571842db01ac3122c4e4df8d6b4e43933ea2ba',
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': 'https://test.mcm-academy.fr/'}

        result1 = requests.post(url, data=data, headers=headers, timeout=60)
        resp=json.loads(result1.content)
        access_token = resp.get('access_token')
        calendly = request.env['calendly.api'].sudo().search([])
        if access_token:
            calendly.access_token = resp.get('access_token')
            calendly.refresh_token = resp.get('refresh_token')