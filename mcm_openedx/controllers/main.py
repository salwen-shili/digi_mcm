# -*- coding: utf-8 -*-
import base64

from odoo import http
from odoo.http import request, _logger
import dateutil
import werkzeug
import locale
import json
import logging
import requests
import odoo
from odoo.tools import datetime

_logger = logging.getLogger(__name__)


class JotformConnector(http.Controller):

    @http.route(['/webhook_digi_form'], type='http', auth="public", csrf=False)
    def importer_from_jotform_webhook(self, **kw):
        _logger.info("webhoook form jedom jotform %s" % (kw))
        rawRequest = kw['rawRequest']
        # convert response of webhook to json format
        rawRequest = json.loads(rawRequest)
        _logger.info("rawRequest1 : %s" % (rawRequest))
        email = str(rawRequest['q85_email']).lower().replace(' ', '')
        _logger.info("email %s" % (str(email)))
        for partner_email in request.env['res.partner'].sudo().search(
                [('email', "=", email)]):
            _logger.info("find partner %s" % (str(partner_email)))
            # add if Vous allez ajouter votre justificatif de domicile. Mais avant nous souhaitons savoir s'il est à votre nom
            # if oui => 1 submission
            # if non => 4 submission
            if rawRequest['q62_saisissezUne63'] == "Oui":
                if rawRequest['justificatifDe64']:
                    url = rawRequest['justificatifDe64']

                    if url:
                        _logger.info("justificatifDe64 %s" % (str(url)))
                        # 👉️ Check if my_var is not None (null)
                        image_binary = base64.b64encode(requests.get(url[0].replace(" ", "%20")).content)
                        name = "Justificatif de domicile)"
                        folder_id = request.env['documents.folder'].sudo().search(
                            [('name', "=", ('Documents Digimoov')), ('company_id', "=", 2)], limit=1)
                        for partner in request.env['res.partner'].sudo().search(
                                [('email', '=', email)]):
                            existe_sub = request.env['mcm_openedx.form_info'].sudo().search([('email', "like", email)])
                            if not existe_sub:
                                new = request.env['mcm_openedx.form_info'].sudo().create({
                                    'email': email,
                                    'partner_id': partner.id,
                                    'societe': "DIGIMOOV",
                                })

                            existe_doc = request.env['documents.document'].sudo().search(
                                [('name', '=', name), ('partner_id', '=', partner.id)])
                            # verifier les document si existe avec le nom jotform, et partner

                            if not existe_doc:
                                _logger.info("not exist")

                                document = request.env['documents.document'].sudo().create({'name': name,
                                                                                            'type': 'binary',
                                                                                            'partner_id': partner.id,
                                                                                            'folder_id': folder_id.id,
                                                                                            'datas': image_binary,
                                                                                            'state': 'validated', })

                                request.env.cr.commit()

                                # replace " " avec  %20 pour eliminer les espace
                                # Ajout ticket pour notiifer le service examn pour changer mp
                                # ajouter condition sur ticket

                                vals = {

                                    'description': 'New document Jotform JDOM %s' % (name),
                                    'name': 'Merci de verifer le document de %s' % (partner.name),
                                    'partner_id': partner.id,

                                    'team_id': request.env['helpdesk.team'].sudo().search(
                                        [('name', 'like', 'Service Examen Digimoov'), ('company_id', "=", 2)],
                                        limit=1).id,
                                }
                                description = "New document Jotform JDOM"
                                ticket = request.env['helpdesk.ticket'].sudo().search(
                                    [("description", "=", description)])
                                if not ticket:
                                    print("cree ticket")
                                    new_ticket = request.env['helpdesk.ticket'].sudo().create(
                                        vals)
            if rawRequest['q62_saisissezUne63'] == "Non":
                if rawRequest['justificatifDe64']:
                    url = rawRequest['justificatifDe64']

                    if url:
                        _logger.info("justificatifDe64 %s" % (str(url)))
                        # 👉️ Check if my_var is not None (null)
                        image_binary = base64.b64encode(requests.get(url[0].replace(" ", "%20")).content)
                        name = "Justificatif de domicile)"
                        folder_id = request.env['documents.folder'].sudo().search(
                            [('name', "=", ('Documents Digimoov')), ('company_id', "=", 2)], limit=1)
                        for partner in request.env['res.partner'].sudo().search(
                                [('email', '=', email)]):
                            existe_sub = request.env['mcm_openedx.form_info'].sudo().search([('email', "like", email)])
                            if not existe_sub:
                                new = request.env['mcm_openedx.form_info'].sudo().create({
                                    'email': email,
                                    'partner_id': partner.id,
                                    'societe': "DIGIMOOV",
                                })

                            existe_doc = request.env['documents.document'].sudo().search(
                                [('name', '=', name), ('partner_id', '=', partner.id)])
                            # verifier les document si existe avec le nom jotform, et partner

                            if not existe_doc:
                                _logger.info("not exist")

                                document = request.env['documents.document'].sudo().create({'name': name,
                                                                                            'type': 'binary',
                                                                                            'partner_id': partner.id,
                                                                                            'folder_id': folder_id.id,
                                                                                            'datas': image_binary,
                                                                                            'state': 'validated', })

                                request.env.cr.commit()

                                # replace " " avec  %20 pour eliminer les espace
                                # Ajout ticket pour notiifer le service examn pour changer mp
                                # ajouter condition sur ticket

                                vals = {

                                    'description': 'New document Jotform JDOM %s' % (name),
                                    'name': 'Merci de verifer le document de %s' % (partner.name),
                                    'partner_id': partner.id,

                                    'team_id': request.env['helpdesk.team'].sudo().search(
                                        [('name', 'like', 'Service Examen Digimoov'), ('company_id', "=", 2)],
                                        limit=1).id,
                                }
                                description = "New document Jotform JDOM"
                                ticket = request.env['helpdesk.ticket'].sudo().search(
                                    [("description", "=", description)])
                                if not ticket:
                                    print("cree ticket")
                                    new_ticket = request.env['helpdesk.ticket'].sudo().create(
                                        vals)
                if rawRequest['attestationDhebergement']:
                    url = rawRequest['attestationDhebergement']

                    if url:
                        _logger.info("attestationDhebergement %s" % (str(url)))

                        # 👉️ Check if my_var is not None (null)
                        image_binary = base64.b64encode(requests.get(url[0].replace(" ", "%20")).content)
                        name = "Attestation d'hébergement"
                        folder_id = request.env['documents.folder'].sudo().search(
                            [('name', "=", ('Documents Digimoov')), ('company_id', "=", 2)], limit=1)
                        for partner in request.env['res.partner'].sudo().search(
                                [('email', '=', email)]):
                            existe_sub = request.env['mcm_openedx.form_info'].sudo().search([('email', "like", email)])
                            if not existe_sub:
                                new = request.env['mcm_openedx.form_info'].sudo().create({
                                    'email': email,
                                    'partner_id': partner.id,
                                    'societe': "DIGIMOOV",
                                })

                            existe_doc = request.env['documents.document'].sudo().search(
                                [('name', '=', name), ('partner_id', '=', partner.id)])
                            # verifier les document si existe avec le nom jotform, et partner

                            if not existe_doc:
                                _logger.info("not exist")

                                document = request.env['documents.document'].sudo().create({'name': name,
                                                                                            'type': 'binary',
                                                                                            'partner_id': partner.id,
                                                                                            'folder_id': folder_id.id,
                                                                                            'datas': image_binary,
                                                                                            'state': 'validated', })

                                request.env.cr.commit()

                                # replace " " avec  %20 pour eliminer les espace
                                # Ajout ticket pour notiifer le service examn pour changer mp
                                # ajouter condition sur ticket

                                vals = {

                                    'description': 'New document Jotform JDOM %s' % (name),
                                    'name': 'Merci de verifer le document de %s' % (partner.name),
                                    'partner_id': partner.id,

                                    'team_id': request.env['helpdesk.team'].sudo().search(
                                        [('name', 'like', 'Service Examen Digimoov'), ('company_id', "=", 2)],
                                        limit=1).id,
                                }
                                description = "New document Jotform JDOM"
                                ticket = request.env['helpdesk.ticket'].sudo().search(
                                    [("description", "=", description)])
                                if not ticket:
                                    print("cree ticket")
                                    new_ticket = request.env['helpdesk.ticket'].sudo().create(
                                        vals)
                if rawRequest['pieceDidentite']:
                    url = rawRequest['pieceDidentite']
                    if url:
                        _logger.info("pieceDidentite %s" % (str(url)))

                        # 👉️ Check if my_var is not None (null)
                        image_binary = base64.b64encode(requests.get(url[0].replace(" ", "%20")).content)
                        name = "Pièce d'identité de l'hébergeur - Recto"
                        folder_id = request.env['documents.folder'].sudo().search(
                            [('name', "=", ('Documents Digimoov')), ('company_id', "=", 2)], limit=1)
                        for partner in request.env['res.partner'].sudo().search(
                                [('email', '=', email)]):
                            existe_sub = request.env['mcm_openedx.form_info'].sudo().search([('email', "like", email)])
                            if not existe_sub:
                                new = request.env['mcm_openedx.form_info'].sudo().create({
                                    'email': email,
                                    'partner_id': partner.id,
                                    'societe': "DIGIMOOV",
                                })
                            existe_doc = request.env['documents.document'].sudo().search(
                                [('name', '=', name), ('partner_id', '=', partner.id)])
                            # verifier les document si existe avec le nom jotform, et partner

                            if not existe_doc:
                                _logger.info("not exist")

                                document = request.env['documents.document'].sudo().create({'name': name,
                                                                                            'type': 'binary',
                                                                                            'partner_id': partner.id,
                                                                                            'folder_id': folder_id.id,
                                                                                            'datas': image_binary,
                                                                                            'state': 'validated', })

                                request.env.cr.commit()

                                # replace " " avec  %20 pour eliminer les espace
                                # Ajout ticket pour notiifer le service examn pour changer mp
                                # ajouter condition sur ticket

                                vals = {

                                    'description': 'New document Jotform JDOM %s' % (name),
                                    'name': 'Merci de verifer le document de %s' % (partner.name),
                                    'partner_id': partner.id,

                                    'team_id': request.env['helpdesk.team'].sudo().search(
                                        [('name', 'like', 'Service Examen Digimoov'), ('company_id', "=", 2)],
                                        limit=1).id,
                                }
                                description = "New document Jotform JDOM"
                                ticket = request.env['helpdesk.ticket'].sudo().search(
                                    [("description", "=", description)])
                                if not ticket:
                                    print("cree ticket")
                                    new_ticket = request.env['helpdesk.ticket'].sudo().create(
                                        vals)
                if rawRequest['pieceDidentite70']:
                    url = rawRequest['pieceDidentite70']
                    if url:
                        # 👉️ Check if my_var is not None (null)
                        image_binary = base64.b64encode(requests.get(url[0].replace(" ", "%20")).content)
                        name = "Pièce d'identité de l'hébergeur - Verso"
                        folder_id = request.env['documents.folder'].sudo().search(
                            [('name', "=", ('Documents Digimoov')), ('company_id', "=", 2)], limit=1)
                        for partner in request.env['res.partner'].sudo().search(
                                [('email', '=', email)]):
                            existe_sub = request.env['mcm_openedx.form_info'].sudo().search([('email', "like", email)])
                            if not existe_sub:
                                new = request.env['mcm_openedx.form_info'].sudo().create({
                                    'email': email,
                                    'partner_id': partner.id,
                                    'societe': "DIGIMOOV",
                                })
                            existe_doc = request.env['documents.document'].sudo().search(
                                [('name', '=', name), ('partner_id', '=', partner.id)])
                            # verifier les document si existe avec le nom jotform, et partner

                            if not existe_doc:
                                _logger.info("not exist")

                                document = request.env['documents.document'].sudo().create({'name': name,
                                                                                            'type': 'binary',
                                                                                            'partner_id': partner.id,
                                                                                            'folder_id': folder_id.id,
                                                                                            'datas': image_binary,
                                                                                            'state': 'validated', })
                                request.env.cr.commit()

                                # replace " " avec  %20 pour eliminer les espace
                                # Ajout ticket pour notiifer le service examn pour changer mp
                                # ajouter condition sur ticket

                                vals = {

                                    'description': 'New document Jotform JDOM %s' % (name),
                                    'name': 'Merci de verifer le document de %s' % (partner.name),
                                    'partner_id': partner.id,

                                    'team_id': request.env['helpdesk.team'].sudo().search(
                                        [('name', 'like', 'Service Examen Digimoov'), ('company_id', "=", 2)],
                                        limit=1).id,
                                }
                                description = "New document Jotform JDOM"
                                ticket = request.env['helpdesk.ticket'].sudo().search(
                                    [("description", "=", description)])
                                if not ticket:
                                    print("cree ticket")
                                    new_ticket = request.env['helpdesk.ticket'].sudo().create(
                                        vals)
            if rawRequest['q74_avezVous'] == "Non":
                if rawRequest['vousAvez']:
                    url = rawRequest['vousAvez']
                    if url:
                        _logger.info("vousAvez %s" % (str(url)))

                        # 👉️ Check if my_var is not None (null)
                        image_binary = base64.b64encode(requests.get(url[0].replace(" ", "%20")).content)
                        name = "Attestation Journée Défense et Citoyenneté"
                        folder_id = request.env['documents.folder'].sudo().search(
                            [('name', "=", ('Documents Digimoov')), ('company_id', "=", 2)], limit=1)
                        for partner in request.env['res.partner'].sudo().search(
                                [('email', '=', email)]):
                            existe_sub = request.env['mcm_openedx.form_info'].sudo().search([('email', "like", email)])
                            if not existe_sub:
                                new = request.env['mcm_openedx.form_info'].sudo().create({
                                    'email': email,
                                    'partner_id': partner.id,
                                    'societe': "DIGIMOOV",
                                })
                            existe_doc = request.env['documents.document'].sudo().search(
                                [('name', '=', name), ('partner_id', '=', partner.id)])
                            # verifier les document si existe avec le nom jotform, et partner

                            if not existe_doc:
                                _logger.info("not exist")

                                document = request.env['documents.document'].sudo().create({'name': name,
                                                                                            'type': 'binary',
                                                                                            'partner_id': partner.id,
                                                                                            'folder_id': folder_id.id,
                                                                                            'datas': image_binary,
                                                                                            'state': 'validated', })

                                request.env.cr.commit()

                                # replace " " avec  %20 pour eliminer les espace
                                # Ajout ticket pour notiifer le service examn pour changer mp
                                # ajouter condition sur ticket

                                vals = {

                                    'description': 'New document Jotform JDOM %s' % (name),
                                    'name': 'Merci de verifer le document de %s' % (partner.name),
                                    'partner_id': partner.id,

                                    'team_id': request.env['helpdesk.team'].sudo().search(
                                        [('name', 'like', 'Service Examen Digimoov'), ('company_id', "=", 2)],
                                        limit=1).id,
                                }
                                description = "New document Jotform JDOM"
                                ticket = request.env['helpdesk.ticket'].sudo().search(
                                    [("description", "=", description)])
                                if not ticket:
                                    print("cree ticket")
                                    new_ticket = request.env['helpdesk.ticket'].sudo().create(
                                        vals)

    # Webhook MCM DOC

    @http.route(['/webhook_mcm_form'], type='http', auth="public", csrf=False)
    def importer_from_jotform_mcm_webhook(self, **kw):
        _logger.info("webhoook Charger vos documents %s" % (kw))
        rawRequest = kw['rawRequest']
        # convert response of webhook to json format
        rawRequest = json.loads(rawRequest)
        _logger.info("rawRequest1 : %s" % (rawRequest))
        email = str(rawRequest['q54_email']).lower().replace(' ', '')
        examen = str(rawRequest['q144_veuillezChoisir'])
        _logger.info(examen)
        for partner_email in request.env['res.partner'].sudo().search(
                [('email', "=", email)]):
            _logger.info(partner_email)

            if examen == "Examen TAXI":
                if rawRequest['q36_vousAllez'] == "Oui":
                    if rawRequest['justificatifDe']:
                        url = rawRequest['justificatifDe']
                        if url:
                            _logger.info("justificatifDe %s" % (str(url)))
                            # 👉️ Check if my_var is not None (null)
                            image_binary = base64.b64encode(requests.get(url[0].replace(" ", "%20")).content)
                            name = " Justificatif de domicile de moins de 3 mois"
                            folder_id = request.env['documents.folder'].sudo().search(
                                [('name', "=", ('Documents MCM ACADEMY')), ('company_id', "=", 1)], limit=1)
                            for partner in request.env['res.partner'].sudo().search(
                                    [('email', '=', email)]):
                                existe_sub = request.env['mcm_openedx.form_info'].sudo().search(
                                    [('email', "like", email)])
                                if not existe_sub:
                                    new = request.env['mcm_openedx.form_info'].sudo().create({
                                        'email': email,
                                        'partner_id': partner.id,
                                        'societe': "MCM ACADEMY",
                                        'examen': 'pasrelle',
                                    })
                                existe_doc = request.env['documents.document'].sudo().search(
                                    [('name', '=', name), ('partner_id', '=', partner.id)])
                                # verifier les document si existe avec le nom jotform, et partner

                                if not existe_doc:
                                    _logger.info("not exist")

                                    document = request.env['documents.document'].sudo().create({'name': name,
                                                                                                'type': 'binary',
                                                                                                'partner_id': partner.id,
                                                                                                'folder_id': folder_id.id,
                                                                                                'datas': image_binary,
                                                                                                'state': 'waiting', })

                                    request.env.cr.commit()
                else:
                    if rawRequest['justificatifDe']:
                        url = rawRequest['justificatifDe']
                        if url:
                            _logger.info("justificatifDe %s" % (str(url)))
                            # 👉️ Check if my_var is not None (null)
                            image_binary = base64.b64encode(requests.get(url[0].replace(" ", "%20")).content)
                            name = " Justificatif de domicile de moins de 3 mois"
                            folder_id = request.env['documents.folder'].sudo().search(
                                [('name', "=", ('Documents MCM ACADEMY')), ('company_id', "=", 1)], limit=1)
                            for partner in request.env['res.partner'].sudo().search(
                                    [('email', '=', email)]):
                                existe_sub = request.env['mcm_openedx.form_info'].sudo().search(
                                    [('email', "like", email)])
                                if not existe_sub:
                                    new = request.env['mcm_openedx.form_info'].sudo().create({
                                        'email': email,
                                        'partner_id': partner.id,
                                        'societe': "MCM ACADEMY",
                                        'examen': 'pasrelle',
                                    })
                                existe_doc = request.env['documents.document'].sudo().search(
                                    [('name', '=', name), ('partner_id', '=', partner.id)])
                                # verifier les document si existe avec le nom jotform, et partner

                                if not existe_doc:
                                    _logger.info("not exist")

                                    document = request.env['documents.document'].sudo().create({'name': name,
                                                                                                'type': 'binary',
                                                                                                'partner_id': partner.id,
                                                                                                'folder_id': folder_id.id,
                                                                                                'datas': image_binary,
                                                                                                'state': 'waiting', })

                                    request.env.cr.commit()

                                    # replace " " avec  %20 pour eliminer les espace
                                    # Ajout ticket pour notiifer le service examn pour changer mp
                                    # ajouter condition sur ticket

                    if rawRequest['attestationDhebergement']:
                        url = rawRequest['attestationDhebergement']
                        if url:
                            _logger.info("attestationDhebergement  %s" % (str(url)))
                            # 👉️ Check if my_var is not None (null)
                            image_binary = base64.b64encode(requests.get(url[0].replace(" ", "%20")).content)
                            name = "  Attestation d'hébergement"
                            folder_id = request.env['documents.folder'].sudo().search(
                                [('name', "=", ('Documents MCM ACADEMY')), ('company_id', "=", 1)], limit=1)
                            for partner in request.env['res.partner'].sudo().search(
                                    [('email', '=', email)]):
                                existe_sub = request.env['mcm_openedx.form_info'].sudo().search(
                                    [('email', "like", email)])
                                if not existe_sub:
                                    new = request.env['mcm_openedx.form_info'].sudo().create({
                                        'email': email,
                                        'partner_id': partner.id,
                                        'societe': "MCM ACADEMY",
                                        'examen': 'pasrelle',
                                    })
                                existe_doc = request.env['documents.document'].sudo().search(
                                    [('name', '=', name), ('partner_id', '=', partner.id)])
                                # verifier les document si existe avec le nom jotform, et partner

                                if not existe_doc:
                                    _logger.info("not exist")

                                    document = request.env['documents.document'].sudo().create({'name': name,
                                                                                                'type': 'binary',
                                                                                                'partner_id': partner.id,
                                                                                                'folder_id': folder_id.id,
                                                                                                'datas': image_binary,
                                                                                                'state': 'waiting', })

                                    request.env.cr.commit()

                                    # replace " " avec  %20 pour eliminer les espace
                                    # Ajout ticket pour notiifer le service examn pour changer mp
                                    # ajouter condition sur ticket

                    if rawRequest['siHeberge11']:
                        url = rawRequest['siHeberge11']
                        if url:
                            _logger.info("siHeberge11 %s" % (str(url)))
                            # 👉️ Check if my_var is not None (null)
                            image_binary = base64.b64encode(requests.get(url[0].replace(" ", "%20")).content)
                            name = "Pièce d'identité de l'hébergeur - Face arrière"
                            folder_id = request.env['documents.folder'].sudo().search(
                                [('name', "=", ('Documents MCM ACADEMY')), ('company_id', "=", 1)], limit=1)
                            for partner in request.env['res.partner'].sudo().search(
                                    [('email', '=', email)]):
                                existe_sub = request.env['mcm_openedx.form_info'].sudo().search(
                                    [('email', "like", email)])
                                if not existe_sub:
                                    new = request.env['mcm_openedx.form_info'].sudo().create({
                                        'email': email,
                                        'partner_id': partner.id,
                                        'societe': "MCM ACADEMY",
                                        'examen': 'pasrelle',
                                    })
                                existe_doc = request.env['documents.document'].sudo().search(
                                    [('name', '=', name), ('partner_id', '=', partner.id)])
                                # verifier les document si existe avec le nom jotform, et partner

                                if not existe_doc:
                                    _logger.info("not exist")

                                    document = request.env['documents.document'].sudo().create({'name': name,
                                                                                                'type': 'binary',
                                                                                                'partner_id': partner.id,
                                                                                                'folder_id': folder_id.id,
                                                                                                'datas': image_binary,
                                                                                                'state': 'waiting', })

                                    request.env.cr.commit()

                                    # replace " " avec  %20 pour eliminer les espace
                                    # Ajout ticket pour notiifer le service examn pour changer mp
                                    # ajouter condition sur ticket

            if rawRequest['pieceDidentite10']:
                url = rawRequest['pieceDidentite10']
                if url:
                    _logger.info("pieceDidentite10 %s" % (str(url)))
                    # 👉️ Check if my_var is not None (null)
                    image_binary = base64.b64encode(requests.get(url[0].replace(" ", "%20")).content)
                    name = " Pièce d'identité de l'hébergeur - Face avant"
                    folder_id = request.env['documents.folder'].sudo().search(
                        [('name', "=", ('Documents MCM ACADEMY')), ('company_id', "=", 1)], limit=1)
                    for partner in request.env['res.partner'].sudo().search(
                            [('email', '=', email)]):
                        existe_sub = request.env['mcm_openedx.form_info'].sudo().search(
                            [('email', "like", email)])
                        if not existe_sub:
                            new = request.env['mcm_openedx.form_info'].sudo().create({
                                'email': email,
                                'partner_id': partner.id,
                                'societe': "MCM ACADEMY",
                                'examen': 'pasrelle',
                            })
                        existe_doc = request.env['documents.document'].sudo().search(
                            [('name', '=', name), ('partner_id', '=', partner.id)])
                        # verifier les document si existe avec le nom jotform, et partner

                        if not existe_doc:
                            _logger.info("not exist")

                            document = request.env['documents.document'].sudo().create({'name': name,
                                                                                        'type': 'binary',
                                                                                        'partner_id': partner.id,
                                                                                        'folder_id': folder_id.id,
                                                                                        'datas': image_binary,
                                                                                        'state': 'waiting', })

                            request.env.cr.commit()

                            # replace " " avec  %20 pour eliminer les espace
                            # Ajout ticket pour notiifer le service examn pour changer mp
                            # ajouter condition sur ticket

            if rawRequest['fileUpload2']:
                url = rawRequest['fileUpload2']
                if url:
                    _logger.info("fileUpload2 %s" % (str(url)))
                    # 👉️ Check if my_var is not None (null)
                    image_binary = base64.b64encode(requests.get(url[0].replace(" ", "%20")).content)
                    name = "Photo d'identité officielle"
                    folder_id = request.env['documents.folder'].sudo().search(
                        [('name', "=", ('Documents MCM ACADEMY')), ('company_id', "=", 1)], limit=1)
                    for partner in request.env['res.partner'].sudo().search(
                            [('email', '=', email)]):
                        existe_sub = request.env['mcm_openedx.form_info'].sudo().search([('email', "like", email)])
                        if not existe_sub:
                            new = request.env['mcm_openedx.form_info'].sudo().create({
                                'email': email,
                                'partner_id': partner.id,
                                'societe': "MCM ACADEMY",
                                'examen': 'pasrelle',
                            })
                        existe_doc = request.env['documents.document'].sudo().search(
                            [('name', '=', name), ('partner_id', '=', partner.id)])
                        # verifier les document si existe avec le nom jotform, et partner

                        if not existe_doc:
                            _logger.info("not exist")

                            document = request.env['documents.document'].sudo().create({'name': name,
                                                                                        'type': 'binary',
                                                                                        'partner_id': partner.id,
                                                                                        'folder_id': folder_id.id,
                                                                                        'datas': image_binary,
                                                                                        'state': 'waiting', })

                            request.env.cr.commit()

                            # replace " " avec  %20 pour eliminer les espace
                            # Ajout ticket pour notiifer le service examn pour changer mp
                            # ajouter condition sur ticket

            if rawRequest['merciDe']:
                url = rawRequest['merciDe']
                if url:
                    _logger.info("merciDe %s" % (str(url)))
                    # 👉️ Check if my_var is not None (null)
                    image_binary = base64.b64encode(requests.get(url[0].replace(" ", "%20")).content)
                    name = "Photo de  signature sur papier blanc"
                    folder_id = request.env['documents.folder'].sudo().search(
                        [('name', "=", ('Documents MCM ACADEMY')), ('company_id', "=", 1)], limit=1)
                    for partner in request.env['res.partner'].sudo().search(
                            [('email', '=', email)]):
                        existe_sub = request.env['mcm_openedx.form_info'].sudo().search([('email', "like", email)])
                        if not existe_sub:
                            new = request.env['mcm_openedx.form_info'].sudo().create({
                                'email': email,
                                'partner_id': partner.id,
                                'societe': "MCM ACADEMY",
                                'examen': 'pasrelle',
                            })
                        existe_doc = request.env['documents.document'].sudo().search(
                            [('name', '=', name), ('partner_id', '=', partner.id)])
                        # verifier les document si existe avec le nom jotform, et partner

                        if not existe_doc:
                            _logger.info("not exist")

                            document = request.env['documents.document'].sudo().create({'name': name,
                                                                                        'type': 'binary',
                                                                                        'partner_id': partner.id,
                                                                                        'folder_id': folder_id.id,
                                                                                        'datas': image_binary,
                                                                                        'state': 'waiting', })

                            request.env.cr.commit()
            if rawRequest['envoiDe']:
                url = rawRequest['envoiDe']
                if url:
                    _logger.info("envoiDe %s" % (str(url)))
                    # 👉️ Check if my_var is not None (null)
                    image_binary = base64.b64encode(requests.get(url[0].replace(" ", "%20")).content)
                    name = "Attestation de réussite à l’examen VTC/TAXI"
                    folder_id = request.env['documents.folder'].sudo().search(
                        [('name', "=", ('Documents MCM ACADEMY')), ('company_id', "=", 1)], limit=1)
                    for partner in request.env['res.partner'].sudo().search(
                            [('email', '=', email)]):
                        existe_sub = request.env['mcm_openedx.form_info'].sudo().search([('email', "like", email)])
                        if not existe_sub:
                            new = request.env['mcm_openedx.form_info'].sudo().create({
                                'email': email,
                                'partner_id': partner.id,
                                'societe': "MCM ACADEMY",
                                'examen': 'pasrelle',
                            })
                        existe_doc = request.env['documents.document'].sudo().search(
                            [('name', '=', name), ('partner_id', '=', partner.id)])
                        # verifier les document si existe avec le nom jotform, et partner

                        if not existe_doc:
                            _logger.info("not exist")

                            document = request.env['documents.document'].sudo().create({'name': name,
                                                                                        'type': 'binary',
                                                                                        'partner_id': partner.id,
                                                                                        'folder_id': folder_id.id,
                                                                                        'datas': image_binary,
                                                                                        'state': 'waiting', })

                            request.env.cr.commit()


            elif examen == "Examen VTC":
                if rawRequest['q36_vousAllez'] == "Oui":
                    if rawRequest['justificatifDe']:
                        url = rawRequest['justificatifDe']
                        if url:
                            _logger.info("justificatifDe %s" % (str(url)))
                            # 👉️ Check if my_var is not None (null)
                            image_binary = base64.b64encode(requests.get(url[0].replace(" ", "%20")).content)
                            name = " Justificatif de domicile de moins de 3 mois"
                            folder_id = request.env['documents.folder'].sudo().search(
                                [('name', "=", ('Documents MCM ACADEMY')), ('company_id', "=", 1)], limit=1)
                            for partner in request.env['res.partner'].sudo().search(
                                    [('email', '=', email)]):
                                existe_sub = request.env['mcm_openedx.form_info'].sudo().search(
                                    [('email', "like", email)])
                                if not existe_sub:
                                    new = request.env['mcm_openedx.form_info'].sudo().create({
                                        'email': email,
                                        'partner_id': partner.id,
                                        'societe': "MCM ACADEMY",
                                        'examen': 'pasrelle',
                                    })
                                existe_doc = request.env['documents.document'].sudo().search(
                                    [('name', '=', name), ('partner_id', '=', partner.id)])
                                # verifier les document si existe avec le nom jotform, et partner

                                if not existe_doc:
                                    _logger.info("not exist")

                                    document = request.env['documents.document'].sudo().create({'name': name,
                                                                                                'type': 'binary',
                                                                                                'partner_id': partner.id,
                                                                                                'folder_id': folder_id.id,
                                                                                                'datas': image_binary,
                                                                                                'state': 'waiting', })

                                    request.env.cr.commit()
                else:
                    if rawRequest['justificatifDe']:
                        url = rawRequest['justificatifDe']
                        if url:
                            _logger.info("justificatifDe %s" % (str(url)))
                            # 👉️ Check if my_var is not None (null)
                            image_binary = base64.b64encode(requests.get(url[0].replace(" ", "%20")).content)
                            name = " Justificatif de domicile de moins de 3 mois"
                            folder_id = request.env['documents.folder'].sudo().search(
                                [('name', "=", ('Documents MCM ACADEMY')), ('company_id', "=", 1)], limit=1)
                            for partner in request.env['res.partner'].sudo().search(
                                    [('email', '=', email)]):
                                existe_sub = request.env['mcm_openedx.form_info'].sudo().search(
                                    [('email', "like", email)])
                                if not existe_sub:
                                    new = request.env['mcm_openedx.form_info'].sudo().create({
                                        'email': email,
                                        'partner_id': partner.id,
                                        'societe': "MCM ACADEMY",
                                        'examen': 'pasrelle',
                                    })
                                existe_doc = request.env['documents.document'].sudo().search(
                                    [('name', '=', name), ('partner_id', '=', partner.id)])
                                # verifier les document si existe avec le nom jotform, et partner

                                if not existe_doc:
                                    _logger.info("not exist")

                                    document = request.env['documents.document'].sudo().create({'name': name,
                                                                                                'type': 'binary',
                                                                                                'partner_id': partner.id,
                                                                                                'folder_id': folder_id.id,
                                                                                                'datas': image_binary,
                                                                                                'state': 'waiting', })

                                    request.env.cr.commit()

                                    # replace " " avec  %20 pour eliminer les espace
                                    # Ajout ticket pour notiifer le service examn pour changer mp
                                    # ajouter condition sur ticket

                    if rawRequest['attestationDhebergement']:
                        url = rawRequest['attestationDhebergement']
                        if url:
                            _logger.info("attestationDhebergement  %s" % (str(url)))
                            # 👉️ Check if my_var is not None (null)
                            image_binary = base64.b64encode(requests.get(url[0].replace(" ", "%20")).content)
                            name = "  Attestation d'hébergement"
                            folder_id = request.env['documents.folder'].sudo().search(
                                [('name', "=", ('Documents MCM ACADEMY')), ('company_id', "=", 1)], limit=1)
                            for partner in request.env['res.partner'].sudo().search(
                                    [('email', '=', email)]):
                                existe_sub = request.env['mcm_openedx.form_info'].sudo().search(
                                    [('email', "like", email)])
                                if not existe_sub:
                                    new = request.env['mcm_openedx.form_info'].sudo().create({
                                        'email': email,
                                        'partner_id': partner.id,
                                        'societe': "MCM ACADEMY",
                                        'examen': 'pasrelle',
                                    })
                                existe_doc = request.env['documents.document'].sudo().search(
                                    [('name', '=', name), ('partner_id', '=', partner.id)])
                                # verifier les document si existe avec le nom jotform, et partner

                                if not existe_doc:
                                    _logger.info("not exist")

                                    document = request.env['documents.document'].sudo().create({'name': name,
                                                                                                'type': 'binary',
                                                                                                'partner_id': partner.id,
                                                                                                'folder_id': folder_id.id,
                                                                                                'datas': image_binary,
                                                                                                'state': 'waiting', })

                                    request.env.cr.commit()

                                    # replace " " avec  %20 pour eliminer les espace
                                    # Ajout ticket pour notiifer le service examn pour changer mp
                                    # ajouter condition sur ticket

                    if rawRequest['siHeberge11']:
                        url = rawRequest['siHeberge11']
                        if url:
                            _logger.info("siHeberge11 %s" % (str(url)))
                            # 👉️ Check if my_var is not None (null)
                            image_binary = base64.b64encode(requests.get(url[0].replace(" ", "%20")).content)
                            name = "Pièce d'identité de l'hébergeur - Face arrière"
                            folder_id = request.env['documents.folder'].sudo().search(
                                [('name', "=", ('Documents MCM ACADEMY')), ('company_id', "=", 1)], limit=1)
                            for partner in request.env['res.partner'].sudo().search(
                                    [('email', '=', email)]):
                                existe_sub = request.env['mcm_openedx.form_info'].sudo().search(
                                    [('email', "like", email)])
                                if not existe_sub:
                                    new = request.env['mcm_openedx.form_info'].sudo().create({
                                        'email': email,
                                        'partner_id': partner.id,
                                        'societe': "MCM ACADEMY",
                                        'examen': 'pasrelle',
                                    })
                                existe_doc = request.env['documents.document'].sudo().search(
                                    [('name', '=', name), ('partner_id', '=', partner.id)])
                                # verifier les document si existe avec le nom jotform, et partner

                                if not existe_doc:
                                    _logger.info("not exist")

                                    document = request.env['documents.document'].sudo().create({'name': name,
                                                                                                'type': 'binary',
                                                                                                'partner_id': partner.id,
                                                                                                'folder_id': folder_id.id,
                                                                                                'datas': image_binary,
                                                                                                'state': 'waiting', })

                                    request.env.cr.commit()

                                    # replace " " avec  %20 pour eliminer les espace
                                    # Ajout ticket pour notiifer le service examn pour changer mp
                                    # ajouter condition sur ticket

            if rawRequest['pieceDidentite10']:
                url = rawRequest['pieceDidentite10']
                if url:
                    _logger.info("pieceDidentite10 %s" % (str(url)))
                    # 👉️ Check if my_var is not None (null)
                    image_binary = base64.b64encode(requests.get(url[0].replace(" ", "%20")).content)
                    name = " Pièce d'identité de l'hébergeur - Face avant"
                    folder_id = request.env['documents.folder'].sudo().search(
                        [('name', "=", ('Documents MCM ACADEMY')), ('company_id', "=", 1)], limit=1)
                    for partner in request.env['res.partner'].sudo().search(
                            [('email', '=', email)]):
                        existe_sub = request.env['mcm_openedx.form_info'].sudo().search(
                            [('email', "like", email)])
                        if not existe_sub:
                            new = request.env['mcm_openedx.form_info'].sudo().create({
                                'email': email,
                                'partner_id': partner.id,
                                'societe': "MCM ACADEMY",
                                'examen': 'pasrelle',
                            })
                        existe_doc = request.env['documents.document'].sudo().search(
                            [('name', '=', name), ('partner_id', '=', partner.id)])
                        # verifier les document si existe avec le nom jotform, et partner

                        if not existe_doc:
                            _logger.info("not exist")

                            document = request.env['documents.document'].sudo().create({'name': name,
                                                                                        'type': 'binary',
                                                                                        'partner_id': partner.id,
                                                                                        'folder_id': folder_id.id,
                                                                                        'datas': image_binary,
                                                                                        'state': 'waiting', })

                            request.env.cr.commit()

                            # replace " " avec  %20 pour eliminer les espace
                            # Ajout ticket pour notiifer le service examn pour changer mp
                            # ajouter condition sur ticket

            if rawRequest['fileUpload2']:
                url = rawRequest['fileUpload2']
                if url:
                    _logger.info("fileUpload2 %s" % (str(url)))
                    # 👉️ Check if my_var is not None (null)
                    image_binary = base64.b64encode(requests.get(url[0].replace(" ", "%20")).content)
                    name = "Photo d'identité officielle"
                    folder_id = request.env['documents.folder'].sudo().search(
                        [('name', "=", ('Documents MCM ACADEMY')), ('company_id', "=", 1)], limit=1)
                    for partner in request.env['res.partner'].sudo().search(
                            [('email', '=', email)]):
                        existe_sub = request.env['mcm_openedx.form_info'].sudo().search([('email', "like", email)])
                        if not existe_sub:
                            new = request.env['mcm_openedx.form_info'].sudo().create({
                                'email': email,
                                'partner_id': partner.id,
                                'societe': "MCM ACADEMY",
                                'examen': 'pasrelle',
                            })
                        existe_doc = request.env['documents.document'].sudo().search(
                            [('name', '=', name), ('partner_id', '=', partner.id)])
                        # verifier les document si existe avec le nom jotform, et partner

                        if not existe_doc:
                            _logger.info("not exist")

                            document = request.env['documents.document'].sudo().create({'name': name,
                                                                                        'type': 'binary',
                                                                                        'partner_id': partner.id,
                                                                                        'folder_id': folder_id.id,
                                                                                        'datas': image_binary,
                                                                                        'state': 'waiting', })

                            request.env.cr.commit()

                            # replace " " avec  %20 pour eliminer les espace
                            # Ajout ticket pour notiifer le service examn pour changer mp
                            # ajouter condition sur ticket

            if rawRequest['merciDe']:
                url = rawRequest['merciDe']
                if url:
                    _logger.info("merciDe %s" % (str(url)))
                    # 👉️ Check if my_var is not None (null)
                    image_binary = base64.b64encode(requests.get(url[0].replace(" ", "%20")).content)
                    name = "Photo de  signature sur papier blanc"
                    folder_id = request.env['documents.folder'].sudo().search(
                        [('name', "=", ('Documents MCM ACADEMY')), ('company_id', "=", 1)], limit=1)
                    for partner in request.env['res.partner'].sudo().search(
                            [('email', '=', email)]):
                        existe_sub = request.env['mcm_openedx.form_info'].sudo().search([('email', "like", email)])
                        if not existe_sub:
                            new = request.env['mcm_openedx.form_info'].sudo().create({
                                'email': email,
                                'partner_id': partner.id,
                                'societe': "MCM ACADEMY",
                                'examen': 'pasrelle',
                            })
                        existe_doc = request.env['documents.document'].sudo().search(
                            [('name', '=', name), ('partner_id', '=', partner.id)])
                        # verifier les document si existe avec le nom jotform, et partner

                        if not existe_doc:
                            _logger.info("not exist")

                            document = request.env['documents.document'].sudo().create({'name': name,
                                                                                        'type': 'binary',
                                                                                        'partner_id': partner.id,
                                                                                        'folder_id': folder_id.id,
                                                                                        'datas': image_binary,
                                                                                        'state': 'waiting', })

                            request.env.cr.commit()
            if rawRequest['envoiDe']:
                url = rawRequest['envoiDe']
                if url:
                    _logger.info("envoiDe %s" % (str(url)))
                    # 👉️ Check if my_var is not None (null)
                    image_binary = base64.b64encode(requests.get(url[0].replace(" ", "%20")).content)
                    name = "Attestation de réussite à l’examen VTC/TAXI"
                    folder_id = request.env['documents.folder'].sudo().search(
                        [('name', "=", ('Documents MCM ACADEMY')), ('company_id', "=", 1)], limit=1)
                    for partner in request.env['res.partner'].sudo().search(
                            [('email', '=', email)]):
                        existe_sub = request.env['mcm_openedx.form_info'].sudo().search([('email', "like", email)])
                        if not existe_sub:
                            new = request.env['mcm_openedx.form_info'].sudo().create({
                                'email': email,
                                'partner_id': partner.id,
                                'societe': "MCM ACADEMY",
                                'examen': 'pasrelle',
                            })
                        existe_doc = request.env['documents.document'].sudo().search(
                            [('name', '=', name), ('partner_id', '=', partner.id)])
                        # verifier les document si existe avec le nom jotform, et partner

                        if not existe_doc:
                            _logger.info("not exist")

                            document = request.env['documents.document'].sudo().create({'name': name,
                                                                                        'type': 'binary',
                                                                                        'partner_id': partner.id,
                                                                                        'folder_id': folder_id.id,
                                                                                        'datas': image_binary,
                                                                                        'state': 'waiting', })

                            request.env.cr.commit()



            elif examen == "Examen VMDTR":
               if rawRequest['q36_vousAllez'] == "Oui":
                   if rawRequest['justificatifDe']:
                       url = rawRequest['justificatifDe']
                       if url:
                           _logger.info("justificatifDe %s" % (str(url)))
                           # 👉️ Check if my_var is not None (null)
                           image_binary = base64.b64encode(requests.get(url[0].replace(" ", "%20")).content)
                           name = " Justificatif de domicile de moins de 3 mois"
                           folder_id = request.env['documents.folder'].sudo().search(
                               [('name', "=", ('Documents MCM ACADEMY')), ('company_id', "=", 1)], limit=1)
                           for partner in request.env['res.partner'].sudo().search(
                                   [('email', '=', email)]):
                               existe_sub = request.env['mcm_openedx.form_info'].sudo().search(
                                   [('email', "like", email)])
                               if not existe_sub:
                                   new = request.env['mcm_openedx.form_info'].sudo().create({
                                       'email': email,
                                       'partner_id': partner.id,
                                       'societe': "MCM ACADEMY",
                                       'examen': 'pasrelle',
                                   })
                               existe_doc = request.env['documents.document'].sudo().search(
                                   [('name', '=', name), ('partner_id', '=', partner.id)])
                               # verifier les document si existe avec le nom jotform, et partner

                               if not existe_doc:
                                   _logger.info("not exist")

                                   document = request.env['documents.document'].sudo().create({'name': name,
                                                                                               'type': 'binary',
                                                                                               'partner_id': partner.id,
                                                                                               'folder_id': folder_id.id,
                                                                                               'datas': image_binary,
                                                                                               'state': 'waiting', })

                                   request.env.cr.commit()
               else:
                    if rawRequest['justificatifDe']:
                        url = rawRequest['justificatifDe']
                        if url:
                            _logger.info("justificatifDe %s" % (str(url)))
                            # 👉️ Check if my_var is not None (null)
                            image_binary = base64.b64encode(requests.get(url[0].replace(" ", "%20")).content)
                            name = " Justificatif de domicile de moins de 3 mois"
                            folder_id = request.env['documents.folder'].sudo().search(
                                [('name', "=", ('Documents MCM ACADEMY')), ('company_id', "=", 1)], limit=1)
                            for partner in request.env['res.partner'].sudo().search(
                                    [('email', '=', email)]):
                                existe_sub = request.env['mcm_openedx.form_info'].sudo().search(
                                    [('email', "like", email)])
                                if not existe_sub:
                                    new = request.env['mcm_openedx.form_info'].sudo().create({
                                        'email': email,
                                        'partner_id': partner.id,
                                        'societe': "MCM ACADEMY",
                                        'examen': 'pasrelle',
                                    })
                                existe_doc = request.env['documents.document'].sudo().search(
                                    [('name', '=', name), ('partner_id', '=', partner.id)])
                                # verifier les document si existe avec le nom jotform, et partner

                                if not existe_doc:
                                    _logger.info("not exist")

                                    document = request.env['documents.document'].sudo().create({'name': name,
                                                                                                'type': 'binary',
                                                                                                'partner_id': partner.id,
                                                                                                'folder_id': folder_id.id,
                                                                                                'datas': image_binary,
                                                                                                'state': 'waiting', })

                                    request.env.cr.commit()

                                    # replace " " avec  %20 pour eliminer les espace
                                    # Ajout ticket pour notiifer le service examn pour changer mp
                                    # ajouter condition sur ticket

                    if rawRequest['attestationDhebergement']:
                        url = rawRequest['attestationDhebergement']
                        if url:
                            _logger.info("attestationDhebergement  %s" % (str(url)))
                            # 👉️ Check if my_var is not None (null)
                            image_binary = base64.b64encode(requests.get(url[0].replace(" ", "%20")).content)
                            name = "  Attestation d'hébergement"
                            folder_id = request.env['documents.folder'].sudo().search(
                                [('name', "=", ('Documents MCM ACADEMY')), ('company_id', "=", 1)], limit=1)
                            for partner in request.env['res.partner'].sudo().search(
                                    [('email', '=', email)]):
                                existe_sub = request.env['mcm_openedx.form_info'].sudo().search(
                                    [('email', "like", email)])
                                if not existe_sub:
                                    new = request.env['mcm_openedx.form_info'].sudo().create({
                                        'email': email,
                                        'partner_id': partner.id,
                                        'societe': "MCM ACADEMY",
                                        'examen': 'pasrelle',
                                    })
                                existe_doc = request.env['documents.document'].sudo().search(
                                    [('name', '=', name), ('partner_id', '=', partner.id)])
                                # verifier les document si existe avec le nom jotform, et partner

                                if not existe_doc:
                                    _logger.info("not exist")

                                    document = request.env['documents.document'].sudo().create({'name': name,
                                                                                                'type': 'binary',
                                                                                                'partner_id': partner.id,
                                                                                                'folder_id': folder_id.id,
                                                                                                'datas': image_binary,
                                                                                                'state': 'waiting', })

                                    request.env.cr.commit()

                                    # replace " " avec  %20 pour eliminer les espace
                                    # Ajout ticket pour notiifer le service examn pour changer mp
                                    # ajouter condition sur ticket

                    if rawRequest['siHeberge11']:
                        url = rawRequest['siHeberge11']
                        if url:
                            _logger.info("siHeberge11 %s" % (str(url)))
                            # 👉️ Check if my_var is not None (null)
                            image_binary = base64.b64encode(requests.get(url[0].replace(" ", "%20")).content)
                            name = "Pièce d'identité de l'hébergeur - Face arrière"
                            folder_id = request.env['documents.folder'].sudo().search(
                                [('name', "=", ('Documents MCM ACADEMY')), ('company_id', "=", 1)], limit=1)
                            for partner in request.env['res.partner'].sudo().search(
                                    [('email', '=', email)]):
                                existe_sub = request.env['mcm_openedx.form_info'].sudo().search(
                                    [('email', "like", email)])
                                if not existe_sub:
                                    new = request.env['mcm_openedx.form_info'].sudo().create({
                                        'email': email,
                                        'partner_id': partner.id,
                                        'societe': "MCM ACADEMY",
                                        'examen': 'pasrelle',
                                    })
                                existe_doc = request.env['documents.document'].sudo().search(
                                    [('name', '=', name), ('partner_id', '=', partner.id)])
                                # verifier les document si existe avec le nom jotform, et partner

                                if not existe_doc:
                                    _logger.info("not exist")

                                    document = request.env['documents.document'].sudo().create({'name': name,
                                                                                                'type': 'binary',
                                                                                                'partner_id': partner.id,
                                                                                                'folder_id': folder_id.id,
                                                                                                'datas': image_binary,
                                                                                                'state': 'waiting', })

                                    request.env.cr.commit()

                                    # replace " " avec  %20 pour eliminer les espace
                                    # Ajout ticket pour notiifer le service examn pour changer mp
                                    # ajouter condition sur ticket

            if rawRequest['pieceDidentite10']:
                        url = rawRequest['pieceDidentite10']
                        if url:
                            _logger.info("pieceDidentite10 %s" % (str(url)))
                            # 👉️ Check if my_var is not None (null)
                            image_binary = base64.b64encode(requests.get(url[0].replace(" ", "%20")).content)
                            name = " Pièce d'identité de l'hébergeur - Face avant"
                            folder_id = request.env['documents.folder'].sudo().search(
                                [('name', "=", ('Documents MCM ACADEMY')), ('company_id', "=", 1)], limit=1)
                            for partner in request.env['res.partner'].sudo().search(
                                    [('email', '=', email)]):
                                existe_sub = request.env['mcm_openedx.form_info'].sudo().search(
                                    [('email', "like", email)])
                                if not existe_sub:
                                    new = request.env['mcm_openedx.form_info'].sudo().create({
                                        'email': email,
                                        'partner_id': partner.id,
                                        'societe': "MCM ACADEMY",
                                        'examen': 'pasrelle',
                                    })
                                existe_doc = request.env['documents.document'].sudo().search(
                                    [('name', '=', name), ('partner_id', '=', partner.id)])
                                # verifier les document si existe avec le nom jotform, et partner

                                if not existe_doc:
                                    _logger.info("not exist")

                                    document = request.env['documents.document'].sudo().create({'name': name,
                                                                                                'type': 'binary',
                                                                                                'partner_id': partner.id,
                                                                                                'folder_id': folder_id.id,
                                                                                                'datas': image_binary,
                                                                                                'state': 'waiting', })

                                    request.env.cr.commit()

                                    # replace " " avec  %20 pour eliminer les espace
                                    # Ajout ticket pour notiifer le service examn pour changer mp
                                    # ajouter condition sur ticket

            if rawRequest['fileUpload2']:
                    url = rawRequest['fileUpload2']
                    if url:
                        _logger.info("fileUpload2 %s" % (str(url)))
                        # 👉️ Check if my_var is not None (null)
                        image_binary = base64.b64encode(requests.get(url[0].replace(" ", "%20")).content)
                        name = "Photo d'identité officielle"
                        folder_id = request.env['documents.folder'].sudo().search(
                            [('name', "=", ('Documents MCM ACADEMY')), ('company_id', "=", 1)], limit=1)
                        for partner in request.env['res.partner'].sudo().search(
                                [('email', '=', email)]):
                            existe_sub = request.env['mcm_openedx.form_info'].sudo().search([('email', "like", email)])
                            if not existe_sub:
                                new = request.env['mcm_openedx.form_info'].sudo().create({
                                    'email': email,
                                    'partner_id': partner.id,
                                    'societe': "MCM ACADEMY",
                                    'examen': 'pasrelle',
                                })
                            existe_doc = request.env['documents.document'].sudo().search(
                                [('name', '=', name), ('partner_id', '=', partner.id)])
                            # verifier les document si existe avec le nom jotform, et partner

                            if not existe_doc:
                                _logger.info("not exist")

                                document = request.env['documents.document'].sudo().create({'name': name,
                                                                                            'type': 'binary',
                                                                                            'partner_id': partner.id,
                                                                                            'folder_id': folder_id.id,
                                                                                            'datas': image_binary,
                                                                                            'state': 'waiting', })

                                request.env.cr.commit()

                                # replace " " avec  %20 pour eliminer les espace
                                # Ajout ticket pour notiifer le service examn pour changer mp
                                # ajouter condition sur ticket

            if rawRequest['merciDe']:
                    url = rawRequest['merciDe']
                    if url:
                        _logger.info("merciDe %s" % (str(url)))
                        # 👉️ Check if my_var is not None (null)
                        image_binary = base64.b64encode(requests.get(url[0].replace(" ", "%20")).content)
                        name = "Photo de  signature sur papier blanc"
                        folder_id = request.env['documents.folder'].sudo().search(
                            [('name', "=", ('Documents MCM ACADEMY')), ('company_id', "=", 1)], limit=1)
                        for partner in request.env['res.partner'].sudo().search(
                                [('email', '=', email)]):
                            existe_sub = request.env['mcm_openedx.form_info'].sudo().search([('email', "like", email)])
                            if not existe_sub:
                                new = request.env['mcm_openedx.form_info'].sudo().create({
                                    'email': email,
                                    'partner_id': partner.id,
                                    'societe': "MCM ACADEMY",
                                    'examen': 'pasrelle',
                                })
                            existe_doc = request.env['documents.document'].sudo().search(
                                [('name', '=', name), ('partner_id', '=', partner.id)])
                            # verifier les document si existe avec le nom jotform, et partner

                            if not existe_doc:
                                _logger.info("not exist")

                                document = request.env['documents.document'].sudo().create({'name': name,
                                                                                            'type': 'binary',
                                                                                            'partner_id': partner.id,
                                                                                            'folder_id': folder_id.id,
                                                                                            'datas': image_binary,
                                                                                            'state': 'waiting', })

                                request.env.cr.commit()
            if rawRequest['envoiDe']:
                    url = rawRequest['envoiDe']
                    if url:
                        _logger.info("envoiDe %s" % (str(url)))
                        # 👉️ Check if my_var is not None (null)
                        image_binary = base64.b64encode(requests.get(url[0].replace(" ", "%20")).content)
                        name = "Attestation de réussite à l’examen VTC/TAXI"
                        folder_id = request.env['documents.folder'].sudo().search(
                            [('name', "=", ('Documents MCM ACADEMY')), ('company_id', "=", 1)], limit=1)
                        for partner in request.env['res.partner'].sudo().search(
                                [('email', '=', email)]):
                            existe_sub = request.env['mcm_openedx.form_info'].sudo().search([('email', "like", email)])
                            if not existe_sub:
                                new = request.env['mcm_openedx.form_info'].sudo().create({
                                    'email': email,
                                    'partner_id': partner.id,
                                    'societe': "MCM ACADEMY",
                                    'examen': 'pasrelle',
                                })
                            existe_doc = request.env['documents.document'].sudo().search(
                                [('name', '=', name), ('partner_id', '=', partner.id)])
                            # verifier les document si existe avec le nom jotform, et partner

                            if not existe_doc:
                                _logger.info("not exist")

                                document = request.env['documents.document'].sudo().create({'name': name,
                                                                                            'type': 'binary',
                                                                                            'partner_id': partner.id,
                                                                                            'folder_id': folder_id.id,
                                                                                            'datas': image_binary,
                                                                                            'state': 'waiting', })

                                request.env.cr.commit()
