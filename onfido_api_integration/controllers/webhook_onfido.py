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
import time
import pycountry
import gettext

_logger = logging.getLogger(__name__)


class OnfidoController(http.Controller):
    """get event workflowrund is completed with js callback"""

    @http.route(['/completed_workflow'], type='json', auth="user", methods=['POST'])
    def completed_workflow(self, data):
        """Recupérer ID des documents chargés"""
        partner = request.env.user.partner_id
        partner.validation_onfido = "in_progress"
        data_onfido = request.env['onfido.info'].sudo().search([('partner_id', '=', partner.id)], limit=1,
                                                               order="id desc")

        folder_id = request.env['documents.folder'].sudo().search(
            [('name', "=", _('Documents Digimoov')), ('company_id', "=", 2)], limit=1)
        _logger.info('partner_id %s' % str(request.env.user.partner_id.id))
        _logger.info('partner_id %s' % str(folder_id))
        website = request.env['website'].get_current_website()
        document_state = "waiting"
        # if data_onfido:
        #     if data_onfido.validation_onfido=="clear":
        #         document_state = "validated"
        #     if data_onfido.validation_onfido=="fail":
        #         document_state = "refused"
        if 'document_front' in data:
            document_front_id = data['document_front']['id']
            name_front = str(data['document_front']['type']) + "_" + str(data['document_front']['side'])
            """Telecharger les documents sous format binaire par l'api onfido"""
            download_document_front = partner.downloadDocument(document_front_id, website.onfido_api_key_live)
            image_front_binary = base64.b64encode(download_document_front)
            """Creer les documents pour l'utilisateur courant"""

            attachement_front = request.env['documents.document'].sudo().create(
                {
                    'name': name_front,
                    'datas': image_front_binary,
                    'type': 'binary',
                    'partner_id': request.env.user.partner_id.id,
                    'folder_id': folder_id.id,
                    'state': document_state
                }
            )
            if data_onfido:
                data_onfido.id_document_front = document_front_id
            # _logger.info('front %s' % str(attachement_front))
            extraction = partner.autofill(document_front_id, website.onfido_api_key_live)
            """Si les informations sont correctement extraits,
            on fait la mise à jour de la fiche client """
            if 'extracted_data' in extraction:
                _logger.info("extract date %s" % str(extraction['extracted_data']))
                if 'document_type' in extraction['extracted_data']:
                    data_onfido.type_front = extraction['extracted_data']['document_type']

                if 'date_of_birth' in extraction['extracted_data']:
                    partner.birthday = extraction['extracted_data']['date_of_birth']
                if 'nationality' in extraction['extracted_data']:
                    code_pays = extraction['extracted_data']['nationality']
                    nationality = pycountry.countries.get(alpha_3=code_pays)
                    translation = gettext.translation('iso3166', pycountry.LOCALES_DIR, languages=['fr'])
                    translation.install()
                    country = _(nationality.name)
                    # _logger.info("translated_nationality %s" % str(translation))
                    _logger.info("translated_nationality %s" % str(country))
                    partner.nationality = country
                    # partner.nationality= pycountry.countries.get(alpha_3=code_pays)
                if 'place_of_birth' in extraction['extracted_data']:
                    partner.birth_city = extraction['extracted_data']['place_of_birth']
                # if 'gender' in extraction['extracted_data']:
                #     partner.civilte=extraction['extracted_data']['gender']
                if 'document_number' in extraction['extracted_data'] and 'document_type' in extraction[
                    'extracted_data']:
                    if extraction['extracted_data']['document_type'] == "national_identity_card":
                        partner.numero_carte_identite = extraction['extracted_data']['document_number']
                        if 'issuing_country' in extraction['document_classification']:
                            code_pays = extraction['document_classification']['issuing_country']
                            _logger.info("issuing_country %s" % str(pycountry.countries.get(alpha_3=code_pays)))
                            nationality = pycountry.countries.get(alpha_3=code_pays)
                            translation = gettext.translation('iso3166', pycountry.LOCALES_DIR,
                                                              languages=['fr'])
                            translation.install()
                            country = _(nationality.name)
                            _logger.info("translated_nationality %s" % str(country))
                            # _logger.info("translated_nationality %s" % str(translation))
                            partner.nationality = country
        if 'document_back' in data:
            document_back_id = data['document_back']['id']
            name_back = str(data['document_back']['type']) + "_" + str(data['document_back']['side'])
            download_document_back = partner.downloadDocument(document_back_id, website.onfido_api_key_live)
            image_back_binary = base64.b64encode(download_document_back)
            attachement_back = request.env['documents.document'].sudo().create(
                {
                    'name': name_back,
                    'datas': image_back_binary,
                    'type': 'binary',
                    'partner_id': request.env.user.partner_id.id,
                    'folder_id': folder_id.id,
                    'state': document_state
                }
            )
            if data_onfido:
                data_onfido.id_document_back = document_back_id
            # _logger.info('back %s' % str(attachement_back))
        if 'face' in data:
            face_id = data['face']['id']
            download_face_photo = partner.downloadLivephoto(face_id, website.onfido_api_key_live)
            face_binary = base64.b64encode(download_face_photo)
            # _logger.info('face %s' % str(face_binary))
            attachement_face = request.env['documents.document'].sudo().create(
                {
                    'name': "Visage",
                    'datas': face_binary,
                    'type': 'binary',
                    'partner_id': request.env.user.partner_id.id,
                    'folder_id': folder_id.id,
                    'state': document_state
                }
            )
            # _logger.info('face %s' % str(attachement_face))
        return True

    """get event workflowrund is completed with webhook """

    @http.route(['/workflow_webhook'], type='json', auth="public", csrf=False)
    def completed_workflow_event(self, **kw):
        values = {}
        motif_fiche = ""
        message_ticket = ""
        _logger.info("webhoooooooooook onfido %s" % str(kw))
        data = json.loads(request.httprequest.data)
        # data = json.loads(kw)
        workflow_run_id = data['payload']['object']['id']
        _logger.info("workflow_run_id onfido %s" % str(workflow_run_id))

        website = request.env['website'].get_current_website()
        partner = request.env.user.partner_id
        workflow_runs = partner.get_workflow_runs(workflow_run_id, website.onfido_api_key_live)
        _logger.info("workflow_run onfido response %s" % str(workflow_runs))
        applicant_id = workflow_runs['applicant_id']
        currentUser = request.env['res.partner'].sudo().search([('onfido_applicant_id', "=", applicant_id)])
        data_onfido = request.env['onfido.info'].sudo().search([('partner_id', '=', currentUser.id)], limit=1,
                                                               order="id desc")

        list_document = partner.get_listDocument(applicant_id, website.onfido_api_key_live)
        _logger.info('*************************************DOCUMENT***************** %s' % str(currentUser))
        if currentUser:
            """get result of validation, if fail we check the reason in brakdown and notify the user"""
            if str(workflow_runs['finished']) == 'True' and workflow_runs['state'] == 'fail':
                _logger.info('state document %s' % str(workflow_runs['state']))
                currentUser.validation_onfido = "fail"
                if data_onfido:
                    data_onfido.validation_onfido = "fail"
                    _logger.info(
                        '*************************************curreed'
                        'ntUser.validation_onfido***************** %s' % str(
                            currentUser.id))
                    documents = request.env['documents.document'].sudo().search([('partner_id', "=", currentUser.id)])
                    _logger.info("document %s" % str(documents))
                    if documents:
                        for document in documents:
                            document.state = "refused"
                            request.env.cr.commit()

                # self.create_document(data_onfido.id_document_front,"front",data_onfido.type_front,"refused",currentUser)
                # self.create_document(data_onfido.id_document_back,"back",data_onfido.type_back,"refused",currentUser)
                #
                # else:
                #     time.sleep(9)
                #     _logger.info(
                #         '*************************************after waite***************** %s' % str(
                #             currentUser.id))
                #     documents = request.env['documents.document'].sudo().search(
                #         [('partner_id', "=", currentUser.id)])
                #     _logger.info("document %s" % str(documents))
                #     if documents:
                #         for document in documents:
                #             document.state = "refused"
                """get report document"""
                check = currentUser.get_checks(applicant_id, website.onfido_api_key_live)
                if check['checks']:
                    report_id = check['checks'][0]['report_ids'][0]
                    # _logger.info("report_id %s" % str(report_id))
                    report = currentUser.get_report(report_id, website.onfido_api_key_live)
                    _logger.info("reppooort %s" % str(report))
                    properties = report['properties']
                    if properties['document_type'] == "driving_licence" and "driving_licence_information" in properties:
                        driving_licence_info = properties['driving_licence_information']
                        for info in driving_licence_info :
                            _logger.info("drive_licence %s" % str(info))
                            if info['category']=="B":
                                obtainment_date_str=info['obtainment_date']
                                obtainment_date = datetime.strptime(obtainment_date_str, '%Y-%m-%d')
                                _logger.info("dateeeeeeeeeeeee %s" % str(obtainment_date))
                                date_years = obtainment_date + relativedelta(years=3)
                                if date_years >= datetime.today():
                                    message_ticket = "Permis non probatoire"
                                    _logger.info("permis non probatoire %s " % str(date_years))
                                    currentUser.validation_onfido = "fail"
                                    """créer ticket pour service client et mettre la motif de refus sur la fiche"""
                                    data_onfido.motif = message_ticket

                    if 'visual_authenticity' in report['breakdown']:
                        breakdown_origin = report['breakdown']['visual_authenticity']['breakdown'][
                            'original_document_present']
                        if report['breakdown']['visual_authenticity']['result'] != 'clear':
                            message_ticket = "Les éléments visuels (non textuels) sont incorrects,"
                        if breakdown_origin['result'] != 'clear':
                            message_ticket = message_ticket + "Format du document non original,"
                            _logger.info('breakdown %s' % str(breakdown_origin['result']))
                    if 'data_consistency' in report['breakdown']:
                        breakdown_data_consist = report['breakdown']['data_consistency']
                        if breakdown_data_consist['result'] != 'clear':
                            message_ticket = message_ticket + "Données non cohérentes,"
                            _logger.info('breakdown %s' % str(breakdown_data_consist['result']))
                    if 'age_validation' in report['breakdown']:
                        breakdown_age_validation = report['breakdown']['age_validation']
                        if breakdown_age_validation['result'] != 'clear':
                            message_ticket = message_ticket + "Âge non accepté,"
                            _logger.info('breakdown %s' % str(breakdown_age_validation['result']))

                    if 'image_integrity' in report['breakdown']:
                        breakdown_quality = report['breakdown']['image_integrity']
                        if breakdown_quality['result'] != 'clear':
                            message_ticket = message_ticket + "Document de mauvaise qualité."
                            _logger.info('breakdown %s' % str(breakdown_quality['result']))
                    if 'data_validation' in report['breakdown'] and 'document_expiration' in \
                            report['breakdown']['data_validation']['breakdown']:
                        breakdown_expiration = report['breakdown']['data_validation']['breakdown'][
                            'document_expiration']
                        if breakdown_expiration['result'] != 'clear':
                            message_ticket = message_ticket + "Le document expirera au bout de 4 mois,"
                            _logger.info('breakdown %s' % str(breakdown_expiration['result']))
                """créer ticket pour service client et mettre la motif de refus sur la fiche"""
                data_onfido.motif = message_ticket

                vals = {
                    'partner_email': '',
                    'description': "Client:" + " " + currentUser.name + " Motif:" + message_ticket,
                    'name': 'Documents refusés',
                    'team_id': request.env['helpdesk.team'].sudo().search(
                        [('name', "like", _('Client')), ('company_id', "=", 2)],
                        limit=1).id,
                }
                new_ticket = request.env['helpdesk.ticket'].sudo().create(
                    vals)
            if str(workflow_runs['finished']) == 'True' and workflow_runs['state'] == 'clear':
                _logger.info('else state document %s' % str(workflow_runs['state']))
                """Si le type de document permis de conduire, on doit verifier s'il est probatoire"""
                check = currentUser.get_checks(applicant_id, website.onfido_api_key_live)
                if check['checks']:
                    report_id = check['checks'][0]['report_ids'][0]
                    # _logger.info("report_id %s" % str(report_id))
                    report = currentUser.get_report(report_id, website.onfido_api_key_live)
                    _logger.info("reppooort %s" % str(report))
                    properties = report['properties']
                    if properties['document_type'] == "driving_licence" and "driving_licence_information" in properties:
                        """rextraire les information lié à categorie B sur le permis de conduire """
                        driving_licence_info = properties['driving_licence_information']
                        for info in driving_licence_info:
                            _logger.info("drive_licence %s" % str(info))
                            if info['category'] == "B":
                                obtainment_date_str = info['obtainment_date']
                                obtainment_date = datetime.strptime(obtainment_date_str, '%Y-%m-%d')
                                _logger.info("dateeeeeeeeeeeee %s" % str(obtainment_date))
                                date_years=obtainment_date + relativedelta(years=3)
                                if date_years >= datetime.today() :
                                    message_ticket="Permis non probatoire"
                                    _logger.info("permis non probatoire %s " %str(date_years))
                                    currentUser.validation_onfido = "fail"
                                    """créer ticket pour service client et mettre la motif de refus sur la fiche"""
                                    data_onfido.motif = message_ticket

                                    vals = {
                                        'partner_email': '',
                                        'description': "Client:" + " " + currentUser.name + " Motif:" + message_ticket,
                                        'name': 'Documents refusés',
                                        'team_id': request.env['helpdesk.team'].sudo().search(
                                            [('name', "like", _('Client')), ('company_id', "=", 1)],
                                            limit=1).id,
                                    }
                                    new_ticket = request.env['helpdesk.ticket'].sudo().create(
                                        vals)
                                    if data_onfido:
                                        data_onfido.validation_onfido = "fail"
                                        documents = request.env['documents.document'].sudo().search([('partner_id', "=", currentUser.id)])
                                        _logger.info("document %s" % str(documents))
                                        if documents:
                                            for document in documents:
                                                document.state = "refused"
                                                request.env.cr.commit()
                                else :
                                    currentUser.validation_onfido = "clear"
                                    if data_onfido:

                                        data_onfido.validation_onfido = "clear"
                                        documents = request.env['documents.document'].sudo().search([('partner_id', "=", currentUser.id)])
                                        _logger.info("document %s" % str(documents))
                                        if documents:
                                            for document in documents:
                                                document.state = "validated"
                                                request.env.cr.commit()
                                        # self.create_document(data_onfido.id_document_front,"front",data_onfido.type_front,"validated",currentUser)
                                        # self.create_document(data_onfido.id_document_back,"back",data_onfido.type_back,"validated",currentUser)
                                        # else:
                                        #     time.sleep(9)
                                        #     _logger.info(
                                        #         '*************************************after waite clear  ***************** %s' % str(
                                        #             currentUser.id))
                                        #     documents = request.env['documents.document'].sudo().search(
                                        #         [('partner_id', "=", currentUser.id)])
                                        #     _logger.info("document %s" % str(documents))
                                        #     if documents:
                                        #         for document in documents:
                                        #             document.state = "validated"

        return True

    """send state of document to frontend """

    @http.route(['/onfido/get_state_document'], methods=["POST"], type='json', auth="user", csrf=False)
    def sendStateDocument(self):
        partner_id = request.env.user.partner_id
        partner = request.env['res.partner'].sudo().search([('id', "=", partner_id.id)])
        data_onfido = request.env['onfido.info'].sudo().search([('partner_id', "=", partner_id.id)],
                                                               limit=1, order="id desc")
        _logger.info("request.env.user.partner_id %s name=%s" % (str(partner.validation_onfido), str(partner_id.name)))
        if partner:
            # if partner.validation_onfido == "fail":
            return {'validation_onfido': partner.validation_onfido}

        else:

            return {'validation_onfido': "partner not found"}

    def create_document(self, document_id, side, type, state, currentUser):
        folder_id = request.env['documents.folder'].sudo().search(
            [('name', "=", _('Documents Digimoov')), ('company_id', "=", 2)], limit=1)
        _logger.info('partner_id %s' % str(request.env.user.partner_id.id))
        _logger.info('partner_id %s' % str(folder_id))
        website = request.env['website'].get_current_website()
        name = str(type) + "_" + str(side)
        """Telecharger les documents sous format binaire par l'api onfido"""
        download_document = currentUser.downloadDocument(document_id, website.onfido_api_key_live)
        image_binary = base64.b64encode(download_document)
        """Creer les documents pour l'utilisateur courant"""
        attachement = request.env['documents.document'].sudo().create(
            {
                'name': name,
                'datas': image_binary,
                'type': 'binary',
                'partner_id': currentUser.id,
                'folder_id': folder_id.id,
                'state': state
            }
        )

        return True