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
import odoo
from odoo import _
import locale
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError
from unidecode import unidecode
import pyshorteners
import logging
_logger = logging.getLogger(__name__)

class WebhookController(http.Controller):
    """valider les dossier cpf pour digimoov  apres la creation par webhook"""
    @http.route(['/validate_cpf_digi'], type='json', auth="public", methods=['POST'])
    def validate_cpf_digi(self, **kw):
        request.uid = odoo.SUPERUSER_ID
        dossier = json.loads(request.httprequest.data)
        event=request.httprequest.headers.get('X-Wedof-Event')
        _logger.info("webhoooooooooook %s" % str(dossier))
        _logger.info("header %s" % str(event))
        """recuperer l'api_key de wedof pour digimoov"""
        company = request.env['res.company'].sudo().search([('id', "=", 2)])
        api_key = ""
        if company:
            api_key = company.wedof_api_key
        return self.validate_folder_cpf(dossier,event,api_key)

    """valider les dossier cpf pour MCM  apres la creation par webhook"""

    @http.route(['/validate_cpf_mcm'], type='json', auth="public", methods=['POST'])
    def validate_cpf_mcm(self, **kw):
        request.uid = odoo.SUPERUSER_ID
        dossier = json.loads(request.httprequest.data)
        event = request.httprequest.headers.get('X-Wedof-Event')
        _logger.info("webhoooooooooook %s" % str(dossier))
        _logger.info("header %s" % str(event))
        """recuperer l'api_key de wedof pour MCM"""
        company = request.env['res.company'].sudo().search([('id', "=", 1)])
        api_key = ""
        if company:
            api_key = company.wedof_api_key
        return self.validate_folder_cpf(dossier, event, api_key)
    
    def validate_folder_cpf(self,dossier,event,api_key):
        request.uid = odoo.SUPERUSER_ID
        externalid = dossier['externalId']
        _logger.info("external_id %s" % str(externalid))
        email = dossier['attendee']['email']
        email = email.replace("%", ".")  # remplacer % par .
        email = email.replace(" ", "")  # supprimer les espaces envoyés en paramètre email
        email = str(email).lower()  # recupérer l'email en miniscule pour éviter la création des deux comptes
        print('dossier', dossier)
        idform = dossier['trainingActionInfo']['externalId']
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
            'X-API-KEY': api_key,
        }

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
        """recuperer date debut de session minimale """
        url = "https://www.wedof.fr/api/registrationFolders/utils/sessionMinDates"
        date_session_min = requests.request("GET", url, headers=headers)
        print(date_session_min.text)
        datemin = date_session_min.json()
        date_debutstr = datemin.get('cpfSessionMinDate')
        date_debut = datetime.strptime(date_debutstr, '%Y-%m-%dT%H:%M:%S.%fz')

        if str(event) == "registrationFolder.created":
            """chercher user sur odoo par tel ou par email """
            user = request.env['res.users'].sudo().search([('login', "=", email)], limit=1)
            exist = True
            if not user:
                if tel:
                    res_users = request.env["res.users"]
                    user = res_users.find_user_with_phone(str(tel)) #call find user using phone function
                if not user:
                    """si l'apprenant n'est pas sur odoo, date debut de session sera celle de cpfSessionMinDate"""
                    date_debutstr = datemin.get('cpfSessionMinDate')
                    date_debut = datetime.strptime(date_debutstr, '%Y-%m-%dT%H:%M:%S.%fz')
                    _logger.info("cpf")
            if user:
                _logger.info("if userrr++++++++ %s" %str(user.email))
                """Si pole emploi coché , l'apprenant commence sa formation apres 21 jours"""
                if user.partner_id.is_pole_emploi:
                    date_debutstr = datemin.get('poleEmploiSessionMinDate')
                    date_debut = datetime.strptime(date_debutstr, '%Y-%m-%dT%H:%M:%S.%fz')
                    _logger.info("pole emploi")
                else:
                    """Si non l'apprenant commence sa formation apres 14 jours"""
                    date_debutstr = datemin.get('cpfSessionMinDate')
                    date_debut = datetime.strptime(date_debutstr, '%Y-%m-%dT%H:%M:%S.%fz')
                    _logger.info("cpf")

            datefin = str(date_debut + relativedelta(months=3) + timedelta(days=1))
            datedebutstr = str(date_debut)
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
                return self.cpf_validate(training_id, email, residence, num_voie, nom_voie, voie, street, tel,
                                         code_postal,
                                         ville,
                                         diplome, dossier['attendee']['lastName'], dossier['attendee']['firstName'],
                                         dossier['externalId'], lastupd)
        return True
    
    
    """faire la mise à jour de statut cpf sur fiche client """
    def cpf_validate(self, module, email, residence, num_voie, nom_voie, voie, street, tel, code_postal, ville, diplome,
                     nom,
                     prenom, dossier, lastupd):
        _logger.info('cpf validate 2')
        request.uid = odoo.SUPERUSER_ID
        user = request.env['res.users'].sudo().search([('login', "=", email)])
        exist = True
        if not user:
            if tel:
                user = request.env["res.users"].sudo().search(
                    [("phone", "=", str(tel))], limit=1)
                if not user:
                    res_users = request.env["res.users"]
                    user = res_users.find_user_with_phone(str(tel))
            # if user:
            #     if not(user.partner_id.date_examen_edof) or not(user.partner_id.session_ville_id):
            #         """Envoyez un SMS aux apprenants qui arrivent de CPF."""
            #         url = '%smy' %str(user.partner_id.company_id.website)  # get the signup_url
            #         short_url = pyshorteners.Shortener()
            #         short_url = short_url.tinyurl.short(
            #             url)  # convert the url to be short using pyshorteners library
            #
            #         sms_body_contenu = 'Chere(e) %s , Vous avez été invité par %s  à compléter votre inscription : %s . Votre courriel de connection est: %s' % (
            #         user.partner_id.name, user.partner_id.company_id.name, short_url,
            #         user.partner_id.email)  # content of sms
            #         sms = request.env['mail.message'].sudo().search(
            #              [("body", "like", short_url), ("message_type", "=", 'sms'), ('partner_ids', 'in', user.partner_id.id),('model',"=","res.partner")])
            #         if not sms:
            #             user.partner_id.send_sms(sms_body_contenu,user.partner_id)

            if not user:
                # créer
                exist = False

                if "digimoov" in str(module):  # module from wedof
                    user = request.env['res.users'].sudo().create({
                        'name': str(prenom) + " " + str(nom),
                        'login': str(email),
                        'groups_id': [(6, 0, [request.env.ref('base.group_portal').id])],
                        'email': email,
                        'notification_type': 'email',
                        'website_id': 2,
                        'company_ids': [2],
                        'company_id': 2,
                        'inscription_cpf':"moncompteformation.gouv.fr"
                    })
                    user.company_id = 2
                    user.partner_id.company_id = 2
                else:
                    user = request.env['res.users'].sudo().create({
                        'name': str(prenom) + " " + str(nom),
                        'login': str(email),
                        'groups_id': [(6, 0, [request.env.ref('base.group_portal').id])],
                        'email': email,
                        'notification_type': 'email',
                        'website_id': 1,
                        'company_ids': [1],
                        'company_id': 1,
                        'inscription_cpf': "moncompteformation.gouv.fr"

                    })
                    user.company_id = 1
                    user.partner_id.company_id = 1
                # if user:
                    # phone = str(tel.replace(' ', ''))[-9:]
                    # phone = '+33' + ' ' + phone[0:1] + ' ' + phone[1:3] + ' ' + phone[3:5] + ' ' + phone[
                    #                                                                                5:7] + ' ' + phone[
                    #                                                                                             7:]  # convert the number in this format : +33 x xx xx xx xx
                    # url = str(user.signup_url)  # get the signup_url
                    # short_url = pyshorteners.Shortener()
                    # short_url = short_url.tinyurl.short(
                    #     url)  # convert the signup_url to be short using pyshorteners library
                    # body = 'Chere(e) %s , Vous avez été invité par %s  à compléter votre inscription : %s . Votre courriel de connection est: %s' % (
                    # user.partner_id.name, user.partner_id.company_id.name, short_url,
                    # user.partner_id.email)  # content of sms
                    # sms_body_contenu = 'Chere(e) %s , Vous avez été invité par %s  à compléter votre inscription : %s . Votre courriel de connection est: %s' % (
                    # user.partner_id.name, user.partner_id.company_id.name, short_url,
                    # user.partner_id.email)  # content of sms
                    # sms = request.env['sms.sms'].sudo().create({
                    #     'partner_id': user.partner_id.id,
                    #     'number': phone,
                    #     'body': str(body)
                    # })  # create sms
                    # sms_id = sms.id
                    # if (sms):
                    #     sms.send()  # send the sms
                    #     subtype_id = request.env['ir.model.data'].xmlid_to_res_id('mt_note')
                    #     body = False
                    #     sms = request.env["sms.sms"].sudo().search(
                    #         [("id", "=", sms_id)], limit=1)
                    #     if (sms):
                    #         if sms.state == 'error':
                    #             body = "Le SMS suivant n'a pas pu être envoyé : %s " % (sms_body_contenu)
                    #     else:
                    #         body = "Le SMS suivant a été bien envoyé : %s " % (sms_body_contenu)
                    #     if body:
                    #         message = request.env['mail.message'].sudo().create({
                    #             'subject': 'Invitation de rejoindre le site par sms',
                    #             'model': 'res.partner',
                    #             'res_id': user.partner_id.id,
                    #             'message_type': 'notification',
                    #             'subtype_id': subtype_id,
                    #             'body': body,
                    #         })  # create note in client view
            # user = request.env['res.users'].sudo().search([('login', "=", email)])
        if user:
            client = request.env['res.partner'].sudo().search(
                [('id', '=', user.partner_id.id)])
            if client:
                """get the chosen city from cpf """
                city_cpf = ""
                if "_" in module:
                    idforma = module.split("_")
                    if idforma:
                        city_cpf = idforma[len(idforma) - 1]
                city = request.env['session.ville'].sudo().search(
                    [('name_ville', "=", city_cpf)], limit=1)
                _logger.info("split***************** %s " % str(city_cpf))
                client.session_ville_id = city if city else client.session_ville_id
                _logger.info("if client %s" % str(client.email))
                _logger.info("dossier %s" % str(dossier))
                client.mode_de_financement = 'cpf'
                client.funding_type = 'cpf'
                client.numero_cpf = dossier
                client.statut_cpf = 'validated'
                client.statut = 'indecis'
                client.street2 = residence
                client.phone = '0' + str(tel.replace(' ', ''))[-9:]
                client.street = street
                client.num_voie = num_voie
                client.nom_voie = nom_voie
                client.voie = voie
                if code_postal != "":
                    client.zip = code_postal
                client.city = ville
                client.diplome = diplome  # attestation capacitév ....
                client.date_cpf = lastupd
                client.name = str(prenom) + " " + str(nom)
                module_id = False
                product_id = False
                """Envoyez un SMS aux apprenants pour accepter leurs dossiers cpf."""
                sms_body_ = "%s! Votre demande de financement par CPF a été validée. Connectez-vous sur moncompteformation.gouv.fr en partant dans l’onglet. Dossiers, Proposition de l’organisme, Financement, ensuite confirmer mon inscription." % (
                    user.partner_id.company_id.name)  # content of sms
                sms = request.env['mail.message'].sudo().search(
                    [("body", "like", sms_body_), ("message_type", "=", 'sms'),
                     ('partner_ids', 'in', user.partner_id.id),
                     ('model', "=", "res.partner")])
                if not sms:
                    user.partner_id.send_sms(sms_body_, user.partner_id)
                if "digimoov" in str(module):
                    user.write({'company_ids': [1, 2], 'company_id': 2})
                    product_ids = request.env['product.template'].sudo().search(
                        [('company_id', "=", 2)])
                    for product_id in product_ids:
                        if product_id.id_edof and product_id.id_edof in module:
                            _logger.info("id_edof %s" % str(product_id))
                            print("product id validate digi", product_id.id_edof)
                            if product_id:
                                client.id_edof = product_id.id_edof
                                """Créer un devis et Remplir le panier par produit choisit sur edof"""
                                sale = request.env['sale.order'].sudo().search([('partner_id', '=', client.id),
                                                                             ('company_id', '=', 2),
                                                                             ('website_id', '=', 2),
                                                                             ('order_line.product_id', '=', product_id.id)])

                                if not sale:
                                    so = request.env['sale.order'].sudo().create({
                                        'partner_id': client.id,
                                        'company_id': 2,
                                        'website_id': 2
                                    })

                                    so_line = request.env['sale.order.line'].sudo().create({
                                        'name': product_id.name,
                                        'product_id': product_id.id,
                                        'product_uom_qty': 1,
                                        'product_uom': product_id.uom_id.id,
                                        'price_unit': product_id.list_price,
                                        'order_id': so.id,
                                        'tax_id': product_id.taxes_id,
                                        'company_id': 2,
                                    })
                                    #
                                    # prix de la formation dans le devis
                                    amount_before_instalment = so.amount_total
                                    # so.amount_total = so.amount_total * 0.25
                                    so.id_edof=module

                                    for line in so.order_line:
                                        line.price_unit = so.amount_total
                else:
                    user.write({'company_ids': [(4, 2)], 'company_id': 1})
                    product_ids = request.env['product.template'].sudo().search(
                        [('company_id', "=", 1)])
                    for product_id in product_ids:
                        if product_id.id_edof and product_id.id_edof in module:
                            _logger.info("id_edof %s" % str(product_id))
                            print("product id validate digi", product_id.id_edof)
                            if product_id:
                                client.id_edof = product_id.id_edof
                                """Créer un devis et Remplir le panier par produit choisit sur edof"""
                                sale = request.env['sale.order'].sudo().search([('partner_id', '=', client.id),
                                                                             ('company_id', '=', 1),
                                                                             ('website_id', '=', 1),
                                                                             ('order_line.product_id', '=', product_id.id)])

                                if not sale:
                                    so = request.env['sale.order'].sudo().create({
                                        'partner_id': client.id,
                                        'company_id': 1,
                                        'website_id': 1
                                    })
                                    so_line = request.env['sale.order.line'].sudo().create({
                                        'name': product_id.name,
                                        'product_id': product_id.id,
                                        'product_uom_qty': 1,
                                        'product_uom': product_id.uom_id.id,
                                        'price_unit': product_id.list_price,
                                        'order_id': so.id,
                                        'tax_id': product_id.taxes_id,
                                        'company_id': 1,
                                    })
                                    #
                                    # prix de la formation dans le devis
                                    amount_before_instalment = so.amount_total
                                    # so.amount_total = so.amount_total * 0.25
                                    for line in so.order_line:
                                        line.price_unit = so.amount_total

        return True



    """Mettre à jour la fiche client  apres l'acceptation sur edof """
    @http.route(['/accepte_cpf'], type='json', auth="public", methods=['POST'])
    def accepted_cpf_statut(self, **kw):
        request.uid = odoo.SUPERUSER_ID
        dossier = json.loads(request.httprequest.data)
        event = request.httprequest.headers.get('X-Wedof-Event')
        _logger.info("webhoook accepted %s" % str(dossier))
        _logger.info("header %s" % str(event))
        externalId = dossier['externalId']
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
        if "zipCode" in dossier['attendee']['address']:
            code_postal = dossier['attendee']['address']['zipCode']
        else:
            code_postal = ""
        if "city" in dossier['attendee']['address']:
            ville = dossier['attendee']['address']['city']
        else:
            ville = ""
        if 'firstName' in dossier['attendee']:
            nom = dossier['attendee']['firstName']
        else:
            nom = ""

        if "lastName" in dossier['attendee']:
            prenom = dossier['attendee']['lastName']
        else:
            prenom = ""
        if "phoneNumber" in dossier['attendee']:
            tel = dossier['attendee']['phoneNumber']
        else:
            tel = ""
        diplome = dossier['trainingActionInfo']['title']
        print('training', training_id)
        today = date.today()
        date_min = today - relativedelta(months=2)
        user=False
        users = request.env['res.users'].sudo().search([('login', "=", email)])
        """si apprenant non trouvé par email on cherche par numero telephone"""
        if not users:
            if tel:
                users = request.env["res.users"].sudo().search(
                    [("phone", "=", str(tel))], limit=1)
                if not users:
                    res_users = request.env["res.users"]
                    users = res_users.find_user_with_phone(str(tel))

        if users and len(users) > 1:
            user = users[1]
            for utilisateur in users:
                if utilisateur.partner_id.id_edof and utilisateur.partner_id.date_examen_edof and utilisateur.partner_id.ville:
                    user = utilisateur

        else:
            user = users
        if user:
             """Si un nouveau utilisateur envoyer 
             un sms d'invitation"""
             if user.state == "new":
                url = str(user.signup_url)  # get the signup_url
                short_url = pyshorteners.Shortener()
                short_url = short_url.tinyurl.short(
                    url)  # convert the signup_url to be short using pyshorteners library
                sms_body_contenu = 'Chere(e) %s , Vous avez été invité par %s  à compléter votre inscription : %s . Votre courriel de connection est: %s' % (
                    user.partner_id.name, user.partner_id.company_id.name, short_url,
                    user.partner_id.email)  # content of sms
                sms = request.env['mail.message'].sudo().search(
                    [("body", "like", short_url), ("message_type", "=", 'sms'),
                     ('partner_ids', 'in', user.partner_id.id),
                     ('model', "=", "res.partner")])
                if not sms:
                    _logger.info('if not sms %s' % str(sms_body_contenu))
                    user.partner_id.send_sms(sms_body_contenu, user.partner_id)

             else :
                if not (user.partner_id.date_examen_edof) or not (user.partner_id.session_ville_id):
                    """Envoyez un SMS aux apprenants qui arrivent de CPF."""
                    url = '%smy' % str(user.partner_id.company_id.website)  # get the signup_url
                    short_url = pyshorteners.Shortener()
                    short_url = short_url.tinyurl.short(
                        url)  # convert the url to be short using pyshorteners library

                    sms_body_contenu = 'Chere(e) %s , Vous avez été invité par %s  à compléter votre inscription : %s . Votre courriel de connection est: %s' % (
                        user.partner_id.name, user.partner_id.company_id.name, short_url,
                        user.partner_id.email)  # content of sms

                    sms = request.env['mail.message'].sudo().search(
                        [("body", "like", short_url), ("message_type", "=", 'sms'), ('partner_ids', 'in', user.partner_id.id),
                         ('model', "=", "res.partner")])
                    if not sms:
                        _logger.info('if not sms %s' % str(sms_body_contenu))
                        user.partner_id.send_sms(sms_body_contenu, user.partner_id)

        if not user:
            # créer
            exist = False

            if "digimoov" in str(training_id):  # module from wedof
                user = request.env['res.users'].sudo().create({
                    'name': str(prenom) + " " + str(nom),
                    'login': str(email),
                    'groups_id': [(6, 0, [request.env.ref('base.group_portal').id])],
                    'email': email,
                    'notification_type': 'email',
                    'website_id': 2,
                    'company_ids': [2],
                    'company_id': 2
                })
                user.company_id = 2
                user.partner_id.company_id = 2
            else:
                user = request.env['res.users'].sudo().create({
                    'name': str(prenom) + " " + str(nom),
                    'login': str(email),
                    'groups_id': [(6, 0, [request.env.ref('base.group_portal').id])],
                    'email': email,
                    'notification_type': 'email',
                    'website_id': 1,
                    'company_ids': [1],
                    'company_id': 1

                })
                user.company_id = 1
                user.partner_id.company_id = 1
            if user:
                phone = str(tel.replace(' ', ''))[-9:]
                phone = '+33' + ' ' + phone[0:1] + ' ' + phone[1:3] + ' ' + phone[3:5] + ' ' + phone[
                                                                                               5:7] + ' ' + phone[
                                                                                                            7:]  # convert the number in this format : +33 x xx xx xx xx
                url = str(user.signup_url)  # get the signup_url
                short_url = pyshorteners.Shortener()
                short_url = short_url.tinyurl.short(
                    url)  # convert the signup_url to be short using pyshorteners library
                body = 'Chere(e) %s , Vous avez été invité par %s  à compléter votre inscription : %s . Votre courriel de connection est: %s' % (
                    user.partner_id.name, user.partner_id.company_id.name, short_url,
                    user.partner_id.email)  # content of sms
                sms_body_contenu = 'Chere(e) %s , Vous avez été invité par %s  à compléter votre inscription : %s . Votre courriel de connection est: %s' % (
                    user.partner_id.name, user.partner_id.company_id.name, short_url,
                    user.partner_id.email)  # content of sms
                sms = request.env['sms.sms'].sudo().create({
                    'partner_id': user.partner_id.id,
                    'number': phone,
                    'body': str(body)
                })  # create sms
                sms_id = sms.id
                if (sms):
                    sms.send()  # send the sms
                    subtype_id = request.env['ir.model.data'].xmlid_to_res_id('mt_note')
                    body = False
                    sms = request.env["sms.sms"].sudo().search(
                        [("id", "=", sms_id)], limit=1)
                    if (sms):
                        if sms.state == 'error':
                            body = "Le SMS suivant n'a pas pu être envoyé : %s " % (sms_body_contenu)
                    else:
                        body = "Le SMS suivant a été bien envoyé : %s " % (sms_body_contenu)
                    if body:
                        message = request.env['mail.message'].sudo().create({
                            'subject': 'Invitation de rejoindre le site par sms',
                            'model': 'res.partner',
                            'res_id': user.partner_id.id,
                            'message_type': 'notification',
                            'subtype_id': subtype_id,
                            'body': body,
                        })  # create note in client view                
        if user:
            """mettre à jour les informations sur fiche client"""
            _logger.info("if user %s " %str(user.login) )
            """get the chosen city from cpf """
            city_cpf = ""
            if "_" in training_id:
                idforma = training_id.split("_")
                if idforma:
                    city_cpf = idforma[len(idforma) - 1]
            city = request.env['session.ville'].sudo().search(
                [('name_ville', "=", city_cpf)], limit=1)
            _logger.info("split***************** %s " % str(city_cpf))
            user.partner_id.session_ville_id = city if city else user.partner_id.session_ville_id
            user.partner_id.mode_de_financement = 'cpf'
            user.partner_id.statut_cpf = 'accepted'
            user.partner_id.date_cpf = lastupd
            user.partner_id.numero_cpf = externalId
            user.partner_id.diplome = diplome
            user.partner_id.street2 = residence
            user.partner_id.phone = '0' + str(tel.replace(' ', ''))[-9:]
            user.partner_id.street = street
            user.partner_id.num_voie = num_voie
            user.partner_id.nom_voie = nom_voie
            user.partner_id.voie = voie
            user.partner_id.zip = code_postal
            user.partner_id.city = ville
            user.partner_id.diplome = diplome  # attestation capacitév ....
            user.partner_id.date_cpf = lastupd
            user.partner_id.name = str(dossier['attendee']['firstName']) + " " + str(dossier['attendee']['lastName'])
            module_id = False
            product_id = False
            """chercher le produit sur odoo selon id edof de formation"""
            product_ids = request.env['product.template'].sudo().search(
                [])
            for product_id in product_ids:
                if product_id.id_edof and product_id.id_edof in training_id:
                    _logger.info("id_edof %s" % str(product_id))
                    print("product id validate digi", product_id.id_edof)
                    if product_id:
                        user.partner_id.id_edof = product_id.id_edof
                        if product_id.company_id.id == 2 and user.partner_id.id_edof and user.partner_id.date_examen_edof and user.partner_id.session_ville_id:

                            _logger.info('if product_id digimoov %s' %str(product_id.id_edof))
                            module_id = request.env['mcmacademy.module'].sudo().search(
                                [('company_id', "=", 2), ('session_ville_id', "=", user.partner_id.session_ville_id.id),
                                 ('date_exam', "=", user.partner_id.date_examen_edof), ('product_id', "=", product_id.id),
                                 ('session_id.number_places_available', '>', 0)], limit=1)
                            print('before if modulee', module_id)
                            if module_id:
                                _logger.info('if modulee %s' %str(module_id))
                                user.partner_id.module_id = module_id
                                user.partner_id.mcm_session_id = module_id.session_id
                                product_id = request.env['product.product'].sudo().search(
                                    [('product_tmpl_id', '=', module_id.product_id.id)])
                                user.partner_id.mcm_session_id = module_id.session_id
                                user.partner_id.module_id = module_id
                                request.env.user.company_id = 2
                                """chercher facture avec numero de dossier si n'existe pas on crée une facture"""
                                # invoice = request.env['account.move'].sudo().search(
                                #     [('numero_cpf', "=", externalId),
                                #      ('state', "=", 'posted'),
                                #      ('partner_id', "=", user.partner_id.id)], limit=1)
                                # print('invoice', invoice.name)
                                # if not invoice:
                                #     print('if  not invoice digi ')
                                #     so = request.env['sale.order'].sudo().create({
                                #         'partner_id': user.partner_id.id,
                                #         'company_id': 2,
                                #     })
                                #     so.module_id = module_id
                                #     so.session_id = module_id.session_id
                                #
                                #     so_line = request.env['sale.order.line'].sudo().create({
                                #         'name': product_id.name,
                                #         'product_id': product_id.id,
                                #         'product_uom_qty': 1,
                                #         'product_uom': product_id.uom_id.id,
                                #         'price_unit': product_id.list_price,
                                #         'order_id': so.id,
                                #         'tax_id': product_id.taxes_id,
                                #         'company_id': 2,
                                #     })
                                #     # prix de la formation dans le devis
                                #     amount_before_instalment = so.amount_total
                                #     # so.amount_total = so.amount_total * 0.25
                                #     for line in so.order_line:
                                #         line.price_unit = so.amount_total
                                #     so.action_confirm()
                                #     ref = False
                                #     # Creation de la Facture Cpf
                                #     # Si la facture est de type CPF :  On parse le pourcentage qui est 25 %
                                #     # methode_payment prend la valeur CPF pour savoir bien qui est une facture CPF qui prend la valeur 25 % par default
                                #
                                #     if so.amount_total > 0 and so.order_line:
                                #         moves = so._create_invoices(final=True)
                                #         for move in moves:
                                #             move.type_facture = 'interne'
                                #             # move.cpf_acompte_invoice= True
                                #             # move.cpf_invoice =True
                                #             move.methodes_payment = 'cpf'
                                #             move.numero_cpf = externalId
                                #             move.pourcentage_acompte = 25
                                #             move.module_id = so.module_id
                                #             move.session_id = so.session_id
                                #             if so.pricelist_id.code:
                                #                 move.pricelist_id = so.pricelist_id
                                #             move.company_id = so.company_id
                                #             move.price_unit = so.amount_total
                                #             # move.cpf_acompte_invoice=True
                                #             # move.cpf_invoice = True
                                #             move.methodes_payment = 'cpf'
                                #             move.post()
                                #             ref = move.name
                                #
                                #     so.action_cancel()
                                #     so.unlink()
                                user.partner_id.statut = 'won'
                                # create vals of wizard change state
                                vals = {
                                    'partner_id': user.partner_id.id,
                                    'statut': 'won',
                                    'session_id': module_id.session_id.id,
                                    'module_id': module_id.id,
                                }
                                session_wizard = request.env['res.partner.session.wizard'].sudo().create(
                                    vals) #create wizard with vals
                                session_wizard.action_modify_partner() #call action of modify partner
                                if not user.partner_id.renounce_request and product_id.default_code != 'habilitation-electrique':
                                    if user.partner_id.phone:
                                        phone = str(user.partner_id.phone.replace(' ', ''))[-9:]
                                        phone = '+33' + ' ' + phone[0:1] + ' ' + phone[1:3] + ' ' + phone[3:5] + ' ' + phone[
                                                                                                                       5:7] + ' ' + phone[
                                                                                                                                    7:]
                                        user.partner_id.phone = phone
                                    url = 'https://www.digimoov.fr/my'
                                    body = "Chere(e) %s félicitation pour votre inscription, votre formation commence dans 14 jours. Si vous souhaitez commencer dès maintenant cliquez sur le lien suivant : %s" % (
                                        user.partner_id.name, url)
                                    if body:
                                        composer = request.env['sms.composer'].with_context(
                                            default_res_model='res.partner',
                                            default_res_ids=user.partner_id.id,
                                            default_composition_mode='mass',
                                        ).sudo().create({
                                            'body': body,
                                            'mass_keep_log': True,
                                            'mass_force_send': True,
                                        })
                                        sms = request.env['mail.message'].sudo().search(
                                            [("body", "=", body), ("message_type", "=", 'sms'),
                                             ("res_id", "=", user.partner_id.id)])
                                        if not sms:
                                            composer.action_send_sms()  # envoyer un sms de félicitation d'inscription
                                        if user.partner_id.phone:
                                            user.partner_id.phone = '0' + str(user.partner_id.phone.replace(' ', ''))[-9:]
                                """changer step à validé dans espace client """
                                user.partner_id.step = 'finish'
                                session = request.env['partner.sessions'].search([('client_id', '=', user.partner_id.id),
                                                                               (
                                                                                   'session_id', '=', module_id.session_id.id)])
                                if not session:
                                    new_history = request.env['partner.sessions'].sudo().create({
                                        'client_id': user.partner_id.id,
                                        'session_id': module_id.session_id.id,
                                        'module_id': module_id.id,
                                        'company_id': 2,
                                    })

                        elif  product_id.company_id.id == 1 and user.partner_id.id_edof and user.partner_id.date_examen_edof and user.partner_id.session_ville_id:
                            print('if product_id mcm', product_id, user.login)
                            user.partner_id.id_edof = product_id.id_edof
                            module_id = request.env['mcmacademy.module'].sudo().search(
                                [('company_id', "=", 1), ('session_ville_id', "=", user.partner_id.session_ville_id.id),
                                 ('date_exam', "=", user.partner_id.date_examen_edof), ('product_id', "=", product_id.id),
                                 ('session_id.number_places_available', '>', 0)], limit=1)
                            if module_id:
                                user.partner_id.module_id = module_id
                                user.partner_id.mcm_session_id = module_id.session_id
                                product_id = request.env['product.product'].sudo().search(
                                    [('product_tmpl_id', '=', module_id.product_id.id)])
                                user.partner_id.mcm_session_id = module_id.session_id
                                user.partner_id.module_id = module_id
                                request.env.user.company_id = 1
                                today = date.today()
                                date_min = today - relativedelta(months=2)
                                """chercher facture avec numero de dossier si n'existe pas on crée une facture"""
                                # invoice = request.env['account.move'].sudo().search(
                                #     [('numero_cpf', "=", externalId),
                                #      ('state', "=", 'posted'),
                                #      ('partner_id', "=", user.partner_id.id)], limit=1)
                                # print('invoice', invoice)
                                # if not invoice:
                                #     print('if  not invoice mcm')
                                #     so = request.env['sale.order'].sudo().create({
                                #         'partner_id': user.partner_id.id,
                                #         'company_id': 1,
                                #     })
                                #     request.env['sale.order.line'].sudo().create({
                                #         'name': product_id.name,
                                #         'product_id': product_id.id,
                                #         'product_uom_qty': 1,
                                #         'product_uom': product_id.uom_id.id,
                                #         'price_unit': product_id.list_price,
                                #         'order_id': so.id,
                                #         'tax_id': product_id.taxes_id,
                                #         'company_id': 1
                                #     })
                                #     # Enreggistrement des valeurs de la facture
                                #     # Parser le pourcentage d'acompte
                                #     # Creation de la fcture étape Finale
                                #     # Facture comptabilisée
                                #     so.action_confirm()
                                #     so.module_id = module_id
                                #     so.session_id = module_id.session_id
                                #     moves = so._create_invoices(final=True)
                                #     for move in moves:
                                #         move.type_facture = 'interne'
                                #         move.module_id = so.module_id
                                #         # move.cpf_acompte_invoice=True
                                #         # move.cpf_invoice =True
                                #         move.methodes_payment = 'cpf'
                                #         move.numero_cpf = externalId
                                #         move.pourcentage_acompte = 25
                                #         move.session_id = so.session_id
                                #         move.company_id = so.company_id
                                #         move.website_id = 1
                                #         for line in move.invoice_line_ids:
                                #             if line.account_id != line.product_id.property_account_income_id and line.product_id.property_account_income_id:
                                #                 line.account_id = line.product_id.property_account_income_id
                                #         move.post()
                                #     so.action_cancel()
                                #     so.unlink()
                                user.partner_id.statut = 'won'
                                #create vals of wizard change state
                                vals = {
                                    'partner_id': user.partner_id.id,
                                    'statut': 'won',
                                    'session_id': module_id.session_id.id,
                                    'module_id': module_id.id,
                                }
                                session_wizard = request.env['res.partner.session.wizard'].sudo().create(
                                    vals) #create wizard with vals
                                session_wizard.action_modify_partner() #call action of modify partner

                                # mail_compose_message = request.env['mail.compose.message']
                                # mail_compose_message.fetch_sendinblue_template()
                                # template_id = request.env['mail.template'].sudo().search(
                                #     [('subject', "=", "Passez votre examen blanc avec MCM ACADEMY X BOLT"),
                                #      ('model_id', "=", 'res.partner')],
                                #     limit=1)  # when the webhook of wedof send the state accepted we send an email to client to register in CMA. we get the mail template from sendinblue
                                # if template_id:
                                #     message = request.env['mail.message'].sudo().search(
                                #         [('subject', "=", "Passez votre examen blanc avec MCM ACADEMY X BOLT"),
                                #          ('model', "=", 'res.partner'), ('res_id', "=", request.env.user.partner_id.id)],
                                #         limit=1)  # check if we have already sent the email
                                #     if not message:
                                #         user.partner_id.with_context(force_send=True).message_post_with_template(template_id.id,
                                #                                                                          composition_mode='comment',
                                #                                                                          )  # send the email to client

                                if not user.partner_id.renounce_request:
                                    if user.partner_id.phone:
                                        phone = str(user.partner_id.phone.replace(' ', ''))[-9:]
                                        phone = '+33' + ' ' + phone[0:1] + ' ' + phone[1:3] + ' ' + phone[
                                                                                                    3:5] + ' ' + phone[
                                                                                                                 5:7] + ' ' + phone[
                                                                                                                              7:]
                                        user.partner_id.phone = phone
                                    url = 'https://www.mcm-academy.fr/my'
                                    body = "Chere(e) %s félicitation pour votre inscription, votre formation commence dans 14 jours. Si vous souhaitez commencer dès maintenant cliquez sur le lien suivant : %s" % (
                                        user.partner_id.name, url)
                                    if body:
                                        composer = request.env['sms.composer'].with_context(
                                            default_res_model='res.partner',
                                            default_res_ids=user.partner_id.id,
                                            default_composition_mode='mass',
                                        ).sudo().create({
                                            'body': body,
                                            'mass_keep_log': True,
                                            'mass_force_send': True,
                                        })
                                        sms = request.env['mail.message'].sudo().search(
                                            [("body", "=", body), ("message_type", "=", 'sms'),
                                             ("res_id", "=", user.partner_id.id)])
                                        if not sms:
                                            composer.action_send_sms()  # envoyer un sms de félicitation d'inscription
                                        if user.partner_id.phone:
                                            user.partner_id.phone = '0' + str(user.partner_id.phone.replace(' ', ''))[
                                                                          -9:]
                                else:
                                    if not user.partner_id.bolt:
                                        if user.partner_id.phone:
                                            phone = str(user.partner_id.phone.replace(' ', ''))[-9:]
                                            phone = '+33' + ' ' + phone[0:1] + ' ' + phone[1:3] + ' ' + phone[
                                                                                                        3:5] + ' ' + phone[
                                                                                                                     5:7] + ' ' + phone[
                                                                                                                                  7:]
                                            user.partner_id.phone = phone
                                        url = 'https://bit.ly/3CZ2HtS'
                                        body = "MCM ACADEMY. Afin d'accéder à notre formation vous devez vous inscrire à l'examen auprès de la CMA de votre région via le lien suivant:%s" % (
                                             url)
                                        if body:
                                            composer = request.env['sms.composer'].with_context(
                                                default_res_model='res.partner',
                                                default_res_id=user.partner_id.id,
                                                default_composition_mode='comment',
                                            ).sudo().create({
                                                'body': body,
                                                'mass_keep_log': True,
                                                'mass_force_send': False,
                                                'use_active_domain': False,
                                            })
                                            sms = request.env['mail.message'].sudo().search(
                                                [("body", "=", body), ("message_type", "=", 'sms'),
                                                 ("res_id", "=", user.partner_id.id)])
                                            if not sms:

                                                composer.action_send_sms()  # we send sms to client contains link to register in cma.
                                            if user.partner_id.phone:
                                                user.partner_id.phone = '0' + str(user.partner_id.phone.replace(' ', ''))[
                                                                              -9:]

                                        mail_compose_message = request.env['mail.compose.message']
                                        mail_compose_message.fetch_sendinblue_template()
                                        template_id = False
                                        template_id = request.env['mail.template'].sudo().search(
                                            [('subject', "=", "Inscription examen chambre des métiers"),
                                             ('model_id', "=", 'res.partner')],
                                            limit=1)  # we send email to client contains link to register in cma. we get the mail template from sendinblue
                                        if not template_id:
                                            template_id = request.env['mail.template'].sudo().search(
                                                [('name', "=", "MCM INSCRIPTION EXAMEN CMA"),
                                                 ('model_id', "=", 'res.partner')],
                                                limit=1)
                                        if template_id:
                                            message = request.env['mail.message'].sudo().search(
                                                [('subject', "=", "Inscription examen chambre des métiers"),
                                                 ('model', "=", 'res.partner'), ('res_id', "=", user.partner_id.id)],
                                                limit=1)
                                            if not message:  # check if we have already sent the email
                                                user.partner_id.with_context(force_send=True).message_post_with_template(
                                                    template_id.id,
                                                    composition_mode='comment',
                                                )  # send the email to clien
                                """changer step à validé dans espace client """
                                user.partner_id.step = 'finish'
                                session = request.env['partner.sessions'].search([('client_id', '=', user.partner_id.id),
                                                                               (
                                                                                   'session_id', '=', module_id.session_id.id)])
                                if not session:
                                    new_history = request.env['partner.sessions'].sudo().create({
                                        'client_id': user.partner_id.id,
                                        'session_id': module_id.session_id.id,
                                        'module_id': module_id.id,
                                        'company_id': 1,
                                    })

                        else:
                            if 'digimoov' in str(training_id):
                                vals = {
                                    'description': 'CPF: id module edof %s non trouvé' % (training_id),
                                    'name': 'CPF : ID module edof non trouvé ',
                                    'team_id': request.env['helpdesk.team'].sudo().search(
                                        [('name', 'like', 'Client'), ('company_id', "=", 2)],
                                        limit=1).id,
                                }
                                description = 'CPF: id module edof ' + str(training_id) + ' non trouvé'
                                ticket = request.env['helpdesk.ticket'].sudo().search([("description", "=", description)])
                                if not ticket:
                                    new_ticket = request.env['helpdesk.ticket'].sudo().create(
                                        vals)
                            else:
                                vals = {
                                    'partner_email': '',
                                    'partner_id': False,
                                    'description': 'CPF: id module edof %s non trouvé' % (training_id),
                                    'name': 'CPF : ID module edof non trouvé ',
                                    'team_id': request.env['helpdesk.team'].sudo().search(
                                        [('name', "like", _('Client')), ('company_id', "=", 1)],
                                        limit=1).id,
                                }
                                description = 'CPF: id module edof ' + str(training_id) + ' non trouvé'
                                ticket = request.env['helpdesk.ticket'].sudo().search([('description', 'ilike', description)])
                                if not ticket:
                                    new_ticket = request.env['helpdesk.ticket'].sudo().create(
                                        vals)
        return True
    
    """Mettre à jour statut cpf apres chaque update sur edof """
    @http.route(['/update_cpf_state'], type='json', auth="public", methods=['POST'])
    def update_cpf_statut(self, **kw):
        request.uid = odoo.SUPERUSER_ID
        dossier = json.loads(request.httprequest.data)
        event = request.httprequest.headers.get('X-Wedof-Event')
        externalId = dossier['externalId']
        email = dossier['attendee']['email']
        email = email.replace("%", ".")  # remplacer % par .
        email = email.replace(" ", "")  # supprimer les espaces envoyés en paramètre email
        email = str(email).lower()  # recupérer l'email en miniscule pour éviter la création des deux comptes
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
        tel = ""
        if "phoneNumber" in dossier['attendee']:
            tel = dossier['attendee']['phoneNumber']

        code_postal = ""
        if "zipCode" in dossier['attendee']['address']:
            code_postal = dossier['attendee']['address']['zipCode']

        ville = ""
        if "city" in dossier['attendee']['address']:
            ville = dossier['attendee']['address']['city']
        residence = ""
        if "residence" in dossier['attendee']['address']:
            residence = dossier['attendee']['address']['residence']
        nom = ""
        if 'firstName' in dossier['attendee']['firstName']:
            nom = dossier['attendee']['firstName']
            nom = unidecode(nom)

        prenom = ""
        if "lastName" in dossier['attendee']['lastName']:
            prenom = dossier['attendee']['lastName']
            prenom = unidecode(prenom)
        diplome = dossier['trainingActionInfo']['title']
        product_id=""

        if state == "validated":
            print('validate', email, dossier['attendee']['lastName'], dossier['attendee']['firstName'])
            return self.cpf_validate(training_id, email, residence, num_voie, nom_voie, voie, street, tel, code_postal, ville,
                              diplome, dossier['attendee']['lastName'], dossier['attendee']['firstName'],
                              dossier['externalId'], lastupd)
        else:
            users = request.env['res.users'].sudo().search(
                [('login', "=", email)])  # search user with same email sended
            user = False
            if users and len(users) > 1:
                user = users[1]
                print('userss', users)
                for utilisateur in users:
                    if utilisateur.partner_id.id_edof and utilisateur.partner_id.date_examen_edof and utilisateur.partner_id.session_ville_id:  # if more than user ,check between them wich user is come from edof
                        user = utilisateur
                        print('if userssss', user.partner_id.email)
            else:
                user = users
            if user:  # if user finded
                print('webhooooookk if__________________user', user.partner_id.statut_cpf, user.partner_id.email)
                user.partner_id.mode_de_financement = 'cpf'  # update field mode de financement to cpf
                user.partner_id.funding_type = 'cpf'  # update field funding type to cpfprint('partner',partner.numero_cpf,user.login)
                print(user.partner_id.date_cpf)
                """chercher le produit sur odoo selon id edof de formation"""
                product_ids = request.env['product.template'].sudo().search(
                    [])
                for product_id in product_ids:
                    if product_id.id_edof and product_id.id_edof in training_id:
                        _logger.info("id_edof %s" % str(product_id))
                        print("product id validate digi", product_id.id_edof)
                        if product_id:
                            user.partner_id.id_edof = product_id.id_edof
                            if state == "inTraining":
                                print('intraining', email)
                                user.partner_id.statut_cpf = "in_training"
                                user.partner_id.numero_cpf = externalId
                                user.partner_id.date_cpf = lastupd
                                user.partner_id.diplome = diplome


                            if state == "terminated":
                                print('terminated', email)
                                user.partner_id.statut_cpf = "out_training"
                                user.partner_id.numero_cpf = externalId
                                user.partner_id.diplome = diplome
                                user.partner_id.date_cpf = lastupd

                            if state == "serviceDoneDeclared":
                                print('serviceDoneDeclared', email)
                                user.partner_id.statut_cpf = "service_declared"
                                user.partner_id.numero_cpf = externalId
                                user.partner_id.date_cpf = lastupd
                                user.partner_id.diplome = diplome


                            if state == "serviceDoneValidated":
                                print('serviceDoneValidated', email)

                                user.partner_id.statut_cpf = "service_validated"
                                user.partner_id.numero_cpf = externalId
                                user.partner_id.date_cpf = lastupd
                                user.partner_id.diplome = diplome

                            if state == "canceledByAttendee" or state == "canceledByAttendeeNotRealized" or state == "canceledByOrganism" or state == "refusedByAttendee" or state == "refusedByOrganism" or state == "rejectedWithoutTitulaireSuite" or state == "rejected":
                                if user.partner_id.numero_cpf == externalId:
                                    """Vérifier si le dossier en formation donc statut de dossier est abandonné si non annulé"""
                                    if user.partner_id.statut_cpf == "intraining":
                                        user.partner_id.statut = "abandon"
                                        if user.partner_id.mcm_session_id and user.partner_id.module_id:
                                            vals = {
                                                'partner_id': user.partner_id.id,
                                                'statut': 'abandon',
                                                'session_id': user.partner_id.mcm_session_id.id,
                                                'module_id': user.partner_id.module_id.id,
                                            }

                                            session_wizard = request.env[
                                                'res.partner.session.wizard'].sudo().create(
                                                vals)
                                            session_wizard.action_modify_partner()
                                    elif user.partner_id.statut_cpf != "canceled":
                                        user.partner_id.statut = "canceled"
                                        if user.partner_id.mcm_session_id and user.partner_id.module_id:
                                            vals = {
                                                'partner_id': user.partner_id.id,
                                                'statut': 'canceled',
                                                'session_id': user.partner_id.mcm_session_id.id,
                                                'module_id': user.partner_id.module_id.id,
                                            }

                                            session_wizard = request.env[
                                                'res.partner.session.wizard'].sudo().create(
                                                vals)
                                            session_wizard.action_modify_partner()
                                    user.partner_id.statut_cpf = "canceled"
                                    user.partner_id.date_cpf = lastupd
                                    user.partner_id.diplome = diplome


                            if state == "terminated":
                                print('terminated', email)
                                user.partner_id.statut_cpf = "out_training"
                                user.partner_id.numero_cpf = externalId
                                user.partner_id.diplome = diplome
                                user.partner_id.date_cpf = lastupd

        return True
