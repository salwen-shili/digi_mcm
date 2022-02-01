# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from datetime import datetime, date
import werkzeug
import locale
import json

import requests
import logging
_logger = logging.getLogger(__name__)
class WebhookController(http.Controller):
    @http.route('/validate_cpf_digi', auth='public')
    def validate_cpf_digi(self, **kw):
        dossier = json.loads(request.httprequest.data)
        header=json.loads(request.httprequest.header)
        _logger.info("webhoooooooooook %s" % str(dossier))
        _logger.info("header %s" % str(header))
        company=request.env['res.company'].sudo().search([('id',"=",2)])
        api_key=""
        if company:
            api_key=company.wedof_api_key

        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
            'X-API-KEY': api_key,
        }

        externalid = dossier['externalId']
        _logger.info("external_id %s" %str(externalid))
        email = dossier['attendee']['email']
        email = email.replace("%", ".")  # remplacer % par .
        email = email.replace(" ", "")  # supprimer les espaces envoyés en paramètre email
        email = str(email).lower()  # recupérer l'email en miniscule pour éviter la création des deux comptes
        print('dossier', dossier)
        idform = dossier['trainingActionInfo']['externalId']
        training_id = ""
        if "_" in idform:
            idforma = idform.split("_", 1)
            if idforma:
                training_id = idforma[1]

        print('training', training_id)
        state = dossier['state']
        lastupdatestr = str(dossier['lastUpdate'])
        lastupdate = datetime.strptime(lastupdatestr, '%Y-%m-%dT%H:%M:%S.%fz')
        newformat = "%d/%m/%Y %H:%M:%S"
        lastupdateform = lastupdate.strftime(newformat)
        lastupd = datetime.strptime(lastupdateform, "%d/%m/%Y %H:%M:%S")
        residence = ""
        if "residence" in dossier['attendee']['address']:
            residence = dossier['attendee']['address']['residence']
        num_voie = ""
        if "number" in dossier['attendee']['address']:
            num_voie = dossier['attendee']['address']['number']

        voie = ""
        if "roadTypeLabel" in dossier['attendee']['address']:
            voie = dossier['attendee']['address']['roadTypeLabel']
        nom_voie = ""
        if "roadName" in dossier['attendee']['address']:
            nom_voie = dossier['attendee']['address']['roadName']
        street = str(num_voie) + ' ' + str(voie) + ' ' + str(nom_voie)
        if "phoneNumber" in dossier['attendee']:
            tel = dossier['attendee']['phoneNumber']
        else:
            tel = ""
        if "zipCode" in dossier['attendee']['address']:
            code_postal = dossier['attendee']['address']['zipCode']
        else:
            code_postal = ""
        if "city" in dossier['attendee']['address']:
            ville = dossier['attendee']['address']['city']
        else:
            ville = ""
        if 'firstName' in dossier['attendee']['firstName']:
            nom = dossier['attendee']['firstName']
        else:
            nom = ""

        if "lastName" in dossier['attendee']['lastName']:
            prenom = dossier['attendee']['lastName']
        else:
            prenom = ""
        diplome = dossier['trainingActionInfo']['title']

        today = date.today()
        datedebut = today + timedelta(days=15)
        datefin = str(datedebut + relativedelta(months=3) + timedelta(days=1))
        datedebutstr = str(datedebut)
        data = '{"trainingActionInfo":{"sessionStartDate":"' + datedebutstr + '","sessionEndDate":"' + datefin + '" }}'
        dat = '{\n  "weeklyDuration": 14,\n  "indicativeDuration": 102\n}'
        response_put = requests.put('https://www.wedof.fr/api/registrationFolders/' + externalid,
                                    headers=headers, data=data)

        status = str(response_put.status_code)
        statuss = str(json.loads(response_put.text))
        _logger.info("validate put _________ %s" % str(status))
        _logger.info("validate_________ %s" % str(statuss))
        response_post = requests.post('https://www.wedof.fr/api/registrationFolders/' + externalid + '/validate',
            headers=headers, data=dat)
        status = str(response_post.status_code)
        statuss = str(json.loads(response_post.text))
        _logger.info("validate_________ %s" % str(status))
        _logger.info("validate_________ %s" % str(statuss))
        """Si dossier passe à l'etat validé on met à jour statut cpf sur la fiche client"""
        if status == "200":
            print('validate', email)
            self.cpf_validate(training_id, email, residence, num_voie, nom_voie, voie, street, tel, code_postal,
                              ville,
                              diplome, dossier['attendee']['lastName'], dossier['attendee']['firstName'],
                              dossier['externalId'], lastupd)

        return "Hello, world"

#     @http.route('/test/test/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('test.listing', {
#             'root': '/test/test',
#             'objects': http.request.env['test.test'].search([]),
#         })

#     @http.route('/test/test/objects/<model("test.test"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('test.object', {
#             'object': obj
#         })
