# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
import functools
import xmlrpc.client
import requests
from requests.structures import CaseInsensitiveDict
from datetime import datetime, timedelta, date
import re
import json
from odoo import _
import locale
from unidecode import unidecode
import logging
import pyshorteners

_logger = logging.getLogger(__name__)

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    def write(self, values):
        res = super(SaleOrder, self).write(values)
        if values.get('state') == 'sale':
            _logger.info('write******** %s' %str(values))
            self.partner_id.ajouter_iOne_manuelle(self.partner_id)
        return res