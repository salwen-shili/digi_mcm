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
    @http.route(['/completed_workflow'], type='json', auth="user", methods=['POST'])
    def completed_workflow(self, data):
        print('************',data['document_front']['id'],data['document_back']['id'])
        document_front_id=data['document_front']['id']
        document_back_id=data['document_back']['id']
        partner=request.env.user.partner_id
        document=partner.getDocmument(document_front_id,request.website.onfido_api_key_live)
        print('document from api %s' %str(document))

        # data = json.loads(request.httprequest.payload)
        # _logger.info("webhoooooooooook onfido %s" % str(data))
        # workflow_run_id=data['object']['id']
        # _logger.info("workflow_run_id onfido %s" % str(workflow_run_id))
        # # get_workflow(workflow_run_id,token)
        return True