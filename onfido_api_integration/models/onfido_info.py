from odoo import api, fields, models, tools, _
import requests
import urllib.request
import base64

from datetime import datetime, timedelta, date
from odoo.modules.module import get_resource_path
from PIL import Image
import json
import logging

_logger = logging.getLogger(__name__)


class InheritConfig(models.Model):
    _name = "onfido.info"
    sdk_token = fields.Char("SDK Token")
    id_document_front = fields.Char("Id document front")
    id_document_back = fields.Char("Id document back")
    type_front = fields.Char("Type de document front")
    type_back = fields.Char("Type de document back")
    exp_date_sdk_token = fields.Datetime("Date d'expiration sdk token")
    validation_onfido = fields.Selection(selection=[
        ('clear', 'Validé'),
        ('fail', 'Refusé'),
        ('in_progress', 'en cours de vérification'),
    ], string='Statut des Documents')
    partner_id = fields.Many2one('res.partner', string="Client")
    workflow_run_id = fields.Char("Workflow run id")
