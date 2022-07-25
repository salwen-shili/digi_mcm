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
    """get event workflowrund is completed with js callback"""
    @http.route(['/completed_workflow'], type='json', auth="user", methods=['POST'])
    def completed_workflow(self, data):
        """Recupérer ID des documents chargés"""
        partner = request.env.user.partner_id
        folder_id = request.env['documents.folder'].sudo().search(
            [('name', "=", _('Documents Digimoov')), ('company_id', "=", 2)], limit=1)
        _logger.info('partner_id %s' % str(request.env.user.partner_id.id))
        _logger.info('partner_id %s' % str(folder_id))
        website = request.env['website'].get_current_website()
        for document in data:
            _logger.info('get document %s' %str(document))
        if 'document_front' in data:
            document_front_id=data['document_front']['id']
            name_front = str(data['document_front']['type']) + "_" + str(data['document_front']['side'])
            """Telecharger les documents sous format binaire par l'api onfido"""
            download_document_front = partner.downloadDocument(document_front_id, website.onfido_api_key_live)
            image_front_binary = base64.b64encode(download_document_front)
            print('document from api %s' % str(document_front_id))
            """Creer les documents pour l'utilisateur courant"""
            attachement_front = request.env['documents.document'].sudo().create(
                {
                    'name': name_front,
                    'datas': image_front_binary,
                    'type': 'binary',
                    'partner_id': request.env.user.partner_id.id,
                    'folder_id': folder_id.id,
                    'state': 'waiting'
                }
            )
            _logger.info('front %s' % str(attachement_front))
            extraction = partner.autofill(document_front_id, website.onfido_api_key_live)
            """Si les informations sont correctement extraits,
            on fait la mise à jour de la fiche client """
            if 'extracted_data' in extraction:
                _logger.info("extract date %s" % str(extraction['extracted_data']['date_of_birth']))
                partner.birthday = extraction['extracted_data']['date_of_birth']
                if 'nationality' in extraction['extracted_data']:
                    partner.nationality = extraction['extracted_data']['nationality']
                if 'place_of_birth' in extraction['extracted_data']:
                    partner.birth_city = extraction['extracted_data']['place_of_birth']

        if 'document_back' in data:
            document_back_id=data['document_back']['id']
            name_back=str(data['document_back']['type'])+"_"+str(data['document_back']['side'])
            download_document_back = partner.downloadDocument(document_back_id, website.onfido_api_key_live)
            download_face_photo = partner.downloadFace(partner.onfido_applicant_id, website.onfido_api_key_live)
            image_back_binary = base64.b64encode(download_document_back)
            attachement_back = request.env['documents.document'].sudo().create(
                {
                    'name': name_back,
                    'datas': image_back_binary,
                    'type': 'binary',
                    'partner_id': request.env.user.partner_id.id,
                    'folder_id': folder_id.id,
                    'state': 'waiting'
                }
            )
            _logger.info('back %s' % str(attachement_back))
        if 'face' in data:
            face_id=data['face']['id']
            face_binary = base64.b64encode(download_face_photo)
            attachement_face = request.env['documents.document'].sudo().create(
                {
                    'name': "Visage",
                    'datas': face_binary,
                    'type': 'binary',
                    'partner_id': request.env.user.partner_id.id,
                    'folder_id': folder_id.id,
                    'state': 'waiting'
                }
            )
            _logger.info('face %s' % str(attachement_face))

        # document_front=partner.getDocmument(website.onfido_api_key_live,document_front_id)

        # print('download_document from api %s' % str(download_document_front))
        # _logger.info('document download %s' % str(download_document_front))
        return True

    """get event workflowrund is completed with webhook """
    @http.route(['/workflow_webhook'], type='json', auth="public", csrf=False)
    def completed_workflow_event(self, **kw):
        values = {}
        _logger.info("webhoooooooooook onfido %s" %str(kw))
        data = json.loads(request.httprequest.data)
        # data = json.loads(kw)
        workflow_run_id = data['payload']['object']['id']
        _logger.info("workflow_run_id onfido %s" % str(workflow_run_id))
        partner = request.env.user.partner_id
        company_id = request.env.user.company_id.id
        website = request.env['website'].get_current_website()
        workflow_runs = partner.get_workflow_runs(workflow_run_id, website.onfido_api_key_live)
        _logger.info("workflow_run onfido response %s" % str(workflow_runs))
        applicant_id = workflow_runs['applicant_id']
        list_document = partner.get_listDocument(applicant_id, website.onfido_api_key_live)
        _logger.info('*************************************DOCUMENT***************** %s' % str(list_document))

        if str(workflow_runs['finished'])=='True' and workflow_runs['state'] == 'fail':
            _logger.info('state document %s' %str(workflow_runs['state']))
            partner.validation_onfido="fail"
            documents=request.env['documents.document'].sudo().search([('partner_id',"=",partner.id)])
            if documents:
                
                for document in documents:
                    document.state = "refused"
                    _logger.info("documents %s" % str(document.state))
            return True
        if str(workflow_runs['finished'])=='True' and workflow_runs['state'] == 'clear':
            _logger.info('else state document %s' % str(workflow_runs['state']))
            partner.validation_onfido = "clear"
            documents = request.env['documents.document'].sudo().search([('partner_id', "=", partner.id)])
            if documents:
                for document in documents:
                    document.state="validated"
                    _logger.info("documents %s" % str(document.state))

            return True

    """send state of document to frontend """
    @http.route(['/send_state_document'], type='json', auth="public", csrf=False)
    def sendStateDocument(self):
        partner_id=request.env.user.partner_id
        _logger.info("sendStateDocument onfido %s" %str(partner_id))
        partner=request.env['res.partner'].sudo().search([('id',"=",partner_id)])
        if partner:
           return {'validation_onfid': partner.validation_onfido }
        else :
            return {'validation_onfid': False }

    