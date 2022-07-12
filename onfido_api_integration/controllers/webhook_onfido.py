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
import base64
import locale
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError
from unidecode import unidecode
import pyshorteners
import logging
_logger = logging.getLogger(__name__)

class OnfidoController(http.Controller):
    """get event workflowrund is completed with js callback  """
    @http.route(['/completed_workflow'], type='json', auth="user", methods=['POST'])
    def completed_workflow(self, data):
        print('************',data['document_front']['id'],data['document_back']['id'])
        document_front_id=data['document_front']['id']
        document_back_id=data['document_back']['id']
        partner=request.env.user.partner_id
        website = request.env['website'].get_current_website()

        document=partner.getDocmument(website.onfido_api_key_live,document_front_id)
        print('document from api %s' %str(document))
        download_document=partner.downloadDocument(document_front_id,website.onfido_api_key_live)
        print('download_document from api %s' % str(download_document))
        # data = json.loads(request.httprequest.payload)
        # _logger.info("webhoooooooooook onfido %s" % str(data))
        # workflow_run_id=data['object']['id']
        # _logger.info("workflow_run_id onfido %s" % str(workflow_run_id))
        # # get_workflow(workflow_run_id,token)
        _logger.info('document download %s' % str(download_document))
        image_binary = base64.b64encode(download_document)
        folder_id = request.env['documents.folder'].sudo().search(
            [('name', "=", _('Documents Digimoov')), ('company_id', "=", 2)], limit=1)
        _logger.info('partner_id %s' % str(request.env.user.partner_id.id))
        _logger.info('partner_id %s' % str(folder_id))
        vals = {
            'name': document,
            'datas': image_binary,
            'type': 'binary',
            'partner_id': request.env.user.partner_id,
            'folder_id': folder_id.id,
            'state': 'validated'
        }
        attachement = request.env['documents.document'].sudo().create(
            {
                'name': "document",
                'datas': image_binary,
                'type': 'binary',
                'partner_id': request.env.user.partner_id.id,
                'folder_id': folder_id.id,
                'state': 'validated'
            }
        )
        _logger.info('partner_id %s' % str(attachement))

        return True


    """get event workflowrund is completed with webhook """
    @http.route(['/completed_workflow_webhook'], type='http', auth="user", methods=['POST'])
    def completed_workflow_webhook(self,**kw):

        data = json.loads(request.httprequest.data)
        _logger.info("webhoooooooooook onfido %s" % str(kw))
        workflow_run_id=data['object']['id']
        _logger.info("workflow_run_id onfido %s" % str(workflow_run_id))
        partner = request.env.user.partner_id
        company_id = request.env.user.company_id.id
        website = request.env['website'].get_current_website()

        workflow_runs=partner.get_workflow_runs(workflow_run_id,website.onfido_api_key_live)
        _logger.info("workflow_run onfido response %s" % str(workflow_runs))
        return True