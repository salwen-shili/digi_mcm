from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class Company(models.Model):
    _inherit = "res.company"
    wedof_api_key = fields.Char("Jetons d'API Wedof ") #jeton d'api visible seulement en mode developpeur