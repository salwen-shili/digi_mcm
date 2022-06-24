from odoo.exceptions import ValidationError
from odoo import api, fields, models
class Website(models.Model):
    _inherit = 'website'

    onfido_api_key_live = fields.Char("API Key Onfido Live") 
    

