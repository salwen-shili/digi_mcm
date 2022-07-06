# -*- coding: utf-8 -*-
import functools
import xmlrpc.client
from odoo import http
from odoo.http import request
import requests
from requests.structures import CaseInsensitiveDict
from datetime import datetime, timedelta, date
import re
import json
from odoo import _
import locale
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError
from unidecode import unidecode
import pyshorteners
import logging
_logger = logging.getLogger(__name__)

class OnfidoController(http.Controller):
    """get event workflowrund is completed with webhoook  """
    @http.route(['/completed_workflow'], type='json', auth="public", methods=['POST'])
    def completed_workflow(self, **kw):
        data = json.loads(request.httprequest.data)
        _logger.info("webhoooooooooook onfido %s" % str(data))
 
        return true