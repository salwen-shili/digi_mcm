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
DOCUMENT_IDs={}
class OnfidoController(http.Controller):
    """get event workflowrund is completed with js callback  """
    @http.route(['/completed_workflow'], type='json', auth="user", methods=['POST'])
    def completed_workflow(self, data):
        print('************',data['document_front']['id'],data['document_back']['id'])
        """Recupérer ID des documents chargés"""
        for document in data:
            _logger.info('get document %s' %str(document))
        document_front_id=data['document_front']['id']
        document_back_id=data['document_back']['id']
        face_id=data['face']['id']

        name_front=str(data['document_front']['type'])+"_"+str(data['document_front']['side'])
        name_back=str(data['document_back']['type'])+"_"+str(data['document_back']['side'])

        partner=request.env.user.partner_id
        website = request.env['website'].get_current_website()

        document_front=partner.getDocmument(website.onfido_api_key_live,document_front_id)
        print('document from api %s' %str(document_front))
        """Telecharger les documents sous format binaire par l'api onfido"""
        download_document_front=partner.downloadDocument(document_front_id,website.onfido_api_key_live)
        download_document_back = partner.downloadDocument(document_back_id, website.onfido_api_key_live)
        download_face_photo = partner.downloadFace(partner.onfido_applicant_id, website.onfido_api_key_live)
        # print('download_document from api %s' % str(download_document_front))
        # _logger.info('document download %s' % str(download_document_front))
        image_front_binary = base64.b64encode(download_document_front)
        image_back_binary = base64.b64encode(download_document_back)
        face_binary = base64.b64encode(download_face_photo)
        folder_id = request.env['documents.folder'].sudo().search(
            [('name', "=", _('Documents Digimoov')), ('company_id', "=", 2)], limit=1)
        _logger.info('partner_id %s' % str(request.env.user.partner_id.id))
        _logger.info('partner_id %s' % str(folder_id))
        """Creer les documents pour l'utilisateur courant """
        attachement_front = request.env['documents.document'].sudo().create(
            {
                'name': name_front,
                'datas': image_front_binary,
                'type': 'binary',
                'partner_id': request.env.user.partner_id.id,
                'folder_id': folder_id.id,
                'state': 'validated'
            }
        )
        attachement_back = request.env['documents.document'].sudo().create(
            {
                'name': name_back,
                'datas': image_back_binary,
                'type': 'binary',
                'partner_id': request.env.user.partner_id.id,
                'folder_id': folder_id.id,
                'state': 'validated'
            }
        )
        attachement_face = request.env['documents.document'].sudo().create(
            {
                'name': "Visage",
                'datas': face_binary,
                'type': 'binary',
                'partner_id': request.env.user.partner_id.id,
                'folder_id': folder_id.id,
                'state': 'validated'
            }
        )
        _logger.info('front %s' % str(attachement_front))
        _logger.info('back %s' % str(attachement_back))
        _logger.info('face %s' % str(attachement_face))
        extraction=partner.autofill(document_back_id,website.onfido_api_key_live)
        """Si les informations sont correctement extraits,
        on fait la mise à jour de la fiche client """
        if 'extracted_data' in extraction:
            _logger.info("extract date %s" %str(extraction['extracted_data']['date_of_birth']))
            partner.birthday=extraction['extracted_data']['date_of_birth']
            if 'nationality' in extraction['extracted_data']:
                partner.nationality = extraction['extracted_data']['nationality']
            if 'place_of_birth' in extraction['extracted_data']:
                partner.birth_city = extraction['extracted_data']['place_of_birth']
        return True

    """get event workflowrund is completed with webhook """
    @http.route(['/workflow_webhook'], type='json', auth="public", csrf=False)
    def completed_workflow_event(self, **kw):
        _logger.info("webhoooooooooook onfido %s" %str(kw))
        data = json.loads(request.httprequest.data)
        # data = json.loads(kw)
        workflow_run_id = data['payload']['object']['id']
        _logger.info("workflow_run_id onfido %s" % str(workflow_run_id))
        partner = request.env.user.partner_id
        company_id = request.env.user.company_id.id
        website = request.env['website'].get_current_website()
        workflow=partner.get_workflow('')
        workflow_runs = partner.get_workflow_runs(workflow_run_id, website.onfido_api_key_live)
        _logger.info("workflow_run onfido response %s" % str(workflow_runs))
        if str(workflow_runs['finished'])=='True' and workflow_runs['state'] == 'fail':
            _logger.info('state document %s' %str(workflow_runs['state']))
            return True
        if str(workflow_runs['finished'])=='True' and workflow_runs['state'] == 'clear':
            _logger.info('else state document %s' % str(workflow_runs['state']))

            return werkzeug.utils.redirect("/shop/cart", 301)

    """get document ids  is completed with js callback """
    @http.route(['/get_document_ids'], type='json', auth="user", methods=['POST'])
    def get_document_ids(self, data):
        print('************', data['document_front']['id'], data['document_back']['id'])
        DOCUMENT_IDs=data
        _logger.info('************ %s' %str(DOCUMENT_IDs))
        return True

    def create_documents(self):
        """Recupérer ID des documents chargés"""
        for document in DOCUMENT_IDs:
            _logger.info('get document %s' % str(document))
        document_front_id = DOCUMENT_IDs['document_front']['id']
        document_back_id = DOCUMENT_IDs['document_back']['id']
        face_id=DOCUMENT_IDs['face']['id']
        name_front = str(DOCUMENT_IDs['document_front']['type']) + "_" + str(DOCUMENT_IDs['document_front']['side'])
        name_back = str(DOCUMENT_IDs['document_back']['type']) + "_" + str(DOCUMENT_IDs['document_back']['side'])

        partner = request.env.user.partner_id
        website = request.env['website'].get_current_website()
        document_front = partner.getDocmument(website.onfido_api_key_live, document_front_id)
        print('document from api %s' % str(document_front))
        """Telecharger les documents sous format binaire par l'api onfido"""
        download_document_front = partner.downloadDocument(document_front_id, website.onfido_api_key_live)
        download_document_back = partner.downloadDocument(document_back_id, website.onfido_api_key_live)
        download_face_photo=partner.downloadFace(face_id,website.onfido_api_key_live)
        # print('download_document from api %s' % str(download_document_front))
        # _logger.info('document download %s' % str(download_document_front))
        image_front_binary = base64.b64encode(download_document_front)
        image_back_binary = base64.b64encode(download_document_back)
        face_binary=base64.b64encode(download_face_photo)
        folder_id = request.env['documents.folder'].sudo().search(
            [('name', "=", _('Documents Digimoov')), ('company_id', "=", 2)], limit=1)
        _logger.info('partner_id %s' % str(request.env.user.partner_id.id))
        _logger.info('partner_id %s' % str(folder_id))
        """Creer les documents pour l'utilisateur courant """
        attachement_front = request.env['documents.document'].sudo().create(
            {
                'name': name_front,
                'datas': image_front_binary,
                'type': 'binary',
                'partner_id': request.env.user.partner_id.id,
                'folder_id': folder_id.id,
                'state': 'validated'
            }
        )
        attachement_back = request.env['documents.document'].sudo().create(
            {
                'name': name_back,
                'datas': image_back_binary,
                'type': 'binary',
                'partner_id': request.env.user.partner_id.id,
                'folder_id': folder_id.id,
                'state': 'validated'
            }
        )
        attachement_face = request.env['documents.document'].sudo().create(
            {
                'name': "Visage",
                'datas': face_binary,
                'type': 'binary',
                'partner_id': request.env.user.partner_id.id,
                'folder_id': folder_id.id,
                'state': 'validated'
            }
        )
        _logger.info('front %s' % str(attachement_front))
        _logger.info('back %s' % str(attachement_back))
        _logger.info('face %s' % str(attachement_face))
        extraction = partner.autofill(document_back_id, website.onfido_api_key_live)
        """Si les informations sont correctement extraits,
        on fait la mise à jour de la fiche client """
        if 'extracted_data' in extraction:
            _logger.info("extract date %s" % str(extraction['extracted_data']['date_of_birth']))
            partner.birthday = extraction['extracted_data']['date_of_birth']
            if 'nationality' in extraction['extracted_data']:
                partner.nationality = extraction['extracted_data']['nationality']
            if 'place_of_birth' in extraction['extracted_data']:
                partner.birth_city = extraction['extracted_data']['place_of_birth']

        return True