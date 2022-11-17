from odoo import api, fields, models
import requests

class InheritConfig(models.TransientModel):
    _inherit = "res.config.settings"

    onfido_api_key_live = fields.Char("API Key Onfido ", related='website_id.onfido_api_key_live', readonly=False)
    onfido_workflow_id = fields.Char("Id Workflow",related='website_id.onfido_workflow_id', readonly=False)
    #referrer=fields.Char("Referrer",related='website_id.referrer', readonly=False)