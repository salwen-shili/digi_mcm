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

        data = {'client_id': '90d14d3507c35d579924cf87a6de7fbc560211289ee1812e554c683c346f3a9c',
                'client_secret': 'b863ae64bfa9ebd0d8aa8010028f3bf1041e1f678b682b710d4dec928d0fcca8',
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': 'https://www.mcm-academy.fr/'}

        result1 = requests.post(url, data=data, headers=headers, timeout=60)
        resp=json.loads(result1.content)
        access_token = resp.get('access_token')
        calendly = request.env['calendly.api'].sudo().search([])
        if access_token:
            calendly.access_token = resp.get('access_token')
            calendly.refresh_token = resp.get('refresh_token')