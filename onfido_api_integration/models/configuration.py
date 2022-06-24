from odoo import api, fields, models
import requests

class InheritConfig(models.TransientModel):
    _inherit = "res.config.settings"

    onfido_api_key_live = fields.Char("API Key Onfido Live", related='website_id.onfido_api_key_live',readonly=False)
    
