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

class WebhookController(http.Controller):
    """valider les dossier cpf pour digimoov  apres la creation par webhook"""
    @http.route(['/validate_cpf_digi'], type='json', auth="public", methods=['POST'])
    def validate_cpf_digi(self, **kw):
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
    def validate_cpf_digi(self, **kw):
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
        if str(event) == "registrationFolder.created":
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
        user = request.env['res.users'].sudo().search([('login', "=", email)])
        exist = True
        if not user:
            if tel:
                user = request.env["res.users"].sudo().search(
                    [("phone", "=", str(tel))], limit=1)
                if not user:
                    phone_number = str(tel).replace(' ', '')
                    if '+33' not in str(phone_number):  # check if edof api send the number of client with +33
                        phone = phone_number[0:2]
                        if str(phone) == '33' and ' ' not in str(
                                tel):  # check if edof api send the number of client in this format (number_format: 33xxxxxxx)
                            phone = '+' + str(tel)
                            user = request.env["res.users"].sudo().search([("phone", "=", phone)], limit=1)
                            if not user:
                                phone = phone[0:3] + ' ' + phone[3:4] + ' ' + phone[4:6] + ' ' + phone[
                                                                                                 6:8] + ' ' + phone[
                                                                                                              8:10] + ' ' + phone[
                                                                                                                            10:]
                                user = request.env["res.users"].sudo().search([("phone", "=", phone)], limit=1)
                            if not user:
                                phone = '0' + str(phone[4:])
                                user = request.env["res.users"].sudo().search(
                                    ['|', ("phone", "=", phone), ("phone", "=", phone.replace(' ', ''))], limit=1)
                        phone = phone_number[0:2]
                        if str(phone) == '33' and ' ' in str(
                                tel):  # check if edof api send the number of client in this format (number_format: 33 x xx xx xx)
                            phone = '+' + str(tel)
                            user = request.env["res.users"].sudo().search(
                                ['|', ("phone", "=", phone), ("phone", "=", phone.replace(' ', ''))], limit=1)
                            if not user:
                                phone = '0' + str(phone[4:])
                                user = request.env["res.users"].sudo().search(
                                    ['|', ("phone", "=", phone), ("phone", "=", phone.replace(' ', ''))], limit=1)
                        phone = phone_number[0:2]
                        if str(phone) in ['06', '07'] and ' ' not in str(
                                tel):  # check if edof api send the number of client in this format (number_format: 07xxxxxx)
                            user = request.env["res.users"].sudo().search(
                                ['|', ("phone", "=", str(tel)), ("phone", "=", str('+33' + tel.replace(' ', '')[-9:]))],
                                limit=1)
                            if not user:
                                phone = phone[0:2] + ' ' + phone[2:4] + ' ' + phone[4:6] + ' ' + phone[
                                                                                                 6:8] + ' ' + phone[8:]
                                user = request.env["res.users"].sudo().search([("phone", "=", phone)], limit=1)
                            if not user:
                                phone = '0' + str(phone[4:])
                                user = request.env["res.users"].sudo().search(
                                    ['|', ("phone", "=", phone), ("phone", "=", phone.replace(' ', ''))], limit=1)
                        phone = phone_number[0:2]
                        if str(phone) in ['06', '07'] and ' ' in str(
                                tel):  # check if edof api send the number of client in this format (number_format: 07 xx xx xx)
                            user = request.env["res.users"].sudo().search(
                                ['|', ("phone", "=", str(tel)), str(tel).replace(' ', '')], limit=1)
                            if not user:
                                phone_number = str(tel[1:])
                                user = request.env["res.users"].sudo().search(
                                    ['|', ("phone", "=", str('+33' + phone_number)),
                                     ("phone", "=", ('+33' + phone_number.replace(' ', '')))], limit=1)
                    else:  # check if edof api send the number of client with+33
                        if ' ' not in str(tel):
                            phone = str(tel)
                            phone = phone[0:3] + ' ' + phone[3:4] + ' ' + phone[4:6] + ' ' + phone[6:8] + ' ' + phone[
                                                                                                                8:10] + ' ' + phone[
                                                                                                                              10:]
                            user = request.env["res.users"].sudo().search(
                                [("phone", "=", phone)], limit=1)
                        if not user:
                            user = request.env["res.users"].sudo().search(
                                [("phone", "=", str(phone_number).replace(' ', ''))], limit=1)
                            if not user:
                                phone = str(phone_number)
                                phone = phone[3:]
                                phone = '0' + str(phone)
                                user = request.env["res.users"].sudo().search(
                                    [("phone", "like", phone.replace(' ', ''))], limit=1)
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
        # user = request.env['res.users'].sudo().search([('login', "=", email)])
        if user:
            client = request.env['res.partner'].sudo().search(
                [('id', '=', user.partner_id.id)])
            if client:
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
                client.zip = code_postal
                client.city = ville
                client.diplome = diplome  # attestation capacitév ....
                client.date_cpf = lastupd
                client.name = str(prenom) + " " + str(nom)
                module_id = False
                product_id = False
                if "digimoov" in str(module):
                    user.write({'company_ids': [1, 2], 'company_id': 2})
                    product_id = request.env['product.template'].sudo().search(
                        [('id_edof', "=", str(module)), ('company_id', "=", 2)], limit=1)
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
                            for line in so.order_line:
                                line.price_unit = so.amount_total
                else:
                    user.write({'company_ids': [(4, 2)], 'company_id': 1})
                    product_id = request.env['product.template'].sudo().search(
                        [('id_edof', "=", str(module)), ('company_id', "=", 1)], limit=1)
                    print("product id validate mcm", product_id.id_edof)
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