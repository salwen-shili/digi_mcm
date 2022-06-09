from odoo import api, fields, models


class InheritConfig(models.TransientModel):
    _inherit = "res.config.settings"

    Onfido_api_key_test = fields.Char("API Key Onfido Test")
    Onfido_api_key_live = fields.Char("API Key Onfido Live")

