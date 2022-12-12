import base64
from urllib import parse

import requests

from odoo import models, fields
from odoo.tools import json

import logging

_logger = logging.getLogger(__name__)


class sms_sendinblue(models.Model):
    _name = 'mcm_openedx.sendinbluesms'
    _description = "Sendinblue"

    sender = fields.Char(string="ID")
    recipient = fields.Char(string="ID")
    content = fields.Char(string="ID")
    type = fields.Selection([('marketing', 'Marketing'),
                             ('transactional', ' Transactional'),
                             ])
def sendsms(self):
    _logger.info("testttttttttttt")