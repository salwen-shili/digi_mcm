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

class WebhookInvoiceController(http.Controller):
    """Créer une facture apres l'evennement "à facturer" sur edof"""
    @http.route(['/facturer_cpf'], type='http', auth="public", methods=['POST'])
    def facturer_cpf(self, **kw):
        companies = self.env['res.company'].sudo().search([])
        if companies:
            for company in companies:
                api_key = company.wedof_api_key
                headers = {
                    'accept': 'application/json',
                    'Content-Type': 'application/json',
                    'X-API-KEY': api_key,
                }
            dossier = json.loads(request.httprequest.data)
            event = request.httprequest.headers.get('X-Wedof-Event')
            _logger.info("webhoooooooooook facturer %s" % str(dossier))
            _logger.info("header %s" % str(event))
            externalId = dossier['externalId']
            amountCGU = dossier['amountCGU']
            bill_num=""
            print("CGU", amountCGU)
            email = dossier['attendee']['email']
            email = email.replace("%", ".")  # remplacer % par .
            email = email.replace(" ", "")  # supprimer les espaces envoyés en paramètre email
            email = str(
                email).lower()  # recupérer l'email en miniscule pour éviter la création des deux comptes
            print('dossier', dossier)
            idform = dossier['trainingActionInfo']['externalId']
            training_id = ""
            if "_" in idform:
                idforma = idform.split("_", 1)
                if idforma:
                    training_id = idforma[1]
            state = dossier['state']
            print('training', training_id)
            user = request.env['res.partner'].sudo().search([('numero_cpf', "=", externalId)])
            """Récupérer la date  et le montant d'acompte sur cpf via api wedof  """
            date_acompte=""
            params_ = (
                ('order', 'desc'),
                ('type', 'deposit'),
                ('state', 'issued'),
                ('registrationFolderId', externalId),
                ('sort', 'lastUpdate'),
                ('limit', '1000')
            )

            response_paiement = requests.get('https://www.wedof.fr/api/payments/', headers=headers,
                                             params=params_)
            paiements = response_paiement.json()
            """Récupérer le paiement selon numero de dossier et type de paiement acompte  """
            for paiement in paiements:
                external = paiement['externalId']
                _logger.info("paiement %s" % str(dossier))
                acompte_amount=paiement['amount']
                """Changer format date"""
                if 'transactionDate' in paiement:
                    transaction_date = paiement['transactionDate']
                    trdate = datetime.strptime(transaction_date, '%Y-%m-%dT%H:%M:%S.%fz')
                    newformat = "%d/%m/%Y"
                    trdateform = trdate.strftime(newformat)
                    date_acompte = datetime.strptime(trdateform, "%d/%m/%Y")
                    print("paiement", externalId, date_acompte)
                product_id = ""
                if 'digimoov' in str(training_id):
    
                    product_id = request.env['product.product'].sudo().search(
                        [('id_edof', "=", str(training_id)), ('company_id', "=", 2)], limit=1)
                else:
                    print('if digi ', product_id)
                    product_id = request.env['product.product'].sudo().search(
                        [('id_edof', "=", str(training_id)), ('company_id', "=", 1)], limit=1)
    
                if user and product_id and product_id.company_id.id == 2 and user.id_edof and user.date_examen_edof and user.session_ville_id:
    
                    module_id = request.env['mcmacademy.module'].sudo().search(
                        [('company_id', "=", 2), ('session_ville_id', "=", user.session_ville_id.id),
                         ('date_exam', "=", user.date_examen_edof), ('product_id', "=", product_id.id),
                         ('session_id.number_places_available', '>', 0)], limit=1)
                    print('before if modulee', module_id)
                    if module_id:
                        print('if modulee', module_id)
                        product_id = request.env['product.product'].sudo().search(
                            [('product_tmpl_id', '=', module_id.product_id.id)])
                        request.env.user.company_id = 2
                        """chercher facture avec numero de dossier si n'existe pas on crée une facture"""
                        invoice = request.env['account.move'].sudo().search(
                            [('numero_cpf', "=", externalId),
                             ('state', "=", 'posted'),
                             ('partner_id', "=", user.id)], limit=1)
                        print('invoice', invoice.name)
                        if invoice :
                            invoice.module_id = user.module_id
                            num=invoice.name
                            bill_num=num.replace('FA', '')
                            bill_num = bill_num.replace('-', '')
                        if not invoice:
                            _logger.info('invoice digi %s' % str(invoice.name))
                            print('if  not invoice digi ')
                            so = request.env['sale.order'].sudo().create({
                                'partner_id': user.id,
                                'company_id': 2,
                            })
                            so.module_id = user.module_id
                            so.session_id = user.session_id
                            """Créer une ligne de vente avec le montant CGU récupéré depuis cpf"""
                            so_line = request.env['sale.order.line'].sudo().create({
                                'name': product_id.name,
                                'product_id': product_id.id,
                                'product_uom_qty': 1,
                                'product_uom': product_id.uom_id.id,
                                'price_unit': amountCGU,
                                'order_id': so.id,
                                'tax_id': product_id.taxes_id,
                                'company_id': 2,
                            })
                            # prix de la formation dans le devis
                            amount_before_instalment = so.amount_total
                            # so.amount_total = so.amount_total * 0.25
                            for line in so.order_line:
                                line.price_unit = so.amount_total
                            so.action_confirm()
                            ref = False
                            # Creation de la Facture Cpf
                            # Si la facture est de type CPF :  On parse le pourcentage qui est 25 %
                            # methode_payment prend la valeur CPF pour savoir bien qui est une facture CPF qui prend la valeur 25 % par default
    
                            if so.amount_total > 0 and so.order_line:
                                moves = so._create_invoices(final=True)
                                for move in moves:
                                    move.type_facture = 'interne'
                                    # move.cpf_acompte_invoice= True
                                    # move.cpf_invoice =True
                                    move.methodes_payment = 'cpf'
                                    move.numero_cpf = externalId
                                    move.pourcentage_acompte = 25
                                    move.module_id = so.module_id
                                    move.session_id = so.session_id
                                    for line in move.invoice_line_ids:
                                        print('line', line.price_unit)
                                        line.price_unit = amountCGU
                                        print('line', line.price_unit)
                                    """Calculer l'acompte 25% du montant total de la formation """
    
                                    acompte = (product_id.lst_price * move.pourcentage_acompte) / 100
                                    
                                    print('acompte', acompte, product_id.lst_price, move.amount_paye)
                                    if so.pricelist_id.code:
                                        move.pricelist_id = amountCGU
                                    move.company_id = so.company_id
                                    move.price_unit = amountCGU  # changé avec montant CGU
                                    # move.cpf_acompte_invoice=True
                                    # move.cpf_invoice = True
                                    move.methodes_payment = 'cpf'
                                    move.post()
                                    """Extraire les chiffres du nom de la facture"""
                                    num = move.name
                                    bill_num = num.replace('FA', '')
                                    bill_num = bill_num.replace('-', '')
                                    journal_id = move.journal_id.id
                                    acquirer = request.env['payment.acquirer'].sudo().search(
                                        [('name', "=", _('stripe')), ('company_id', '=', 1)], limit=1)
                                    if acquirer:
                                        journal_id = acquirer.journal_id.id
                                    """Effectuer  un payement de 25% de montant total de la formation pour digimoov"""
                                    payment_method = request.env['account.payment.method'].sudo().search(
                                        [('code', 'ilike', 'electronic')])
                                    payment = request.env['account.payment'].sudo().create(
                                        {'payment_type': 'inbound',
                                         'payment_method_id': payment_method.id,
                                         'partner_type': 'customer',
                                         'partner_id': move.partner_id.id,
                                         'amount': acompte_amount,
                                         'currency_id': move.currency_id.id,
                                         'payment_date': date_acompte,
                                         'journal_id': journal_id,
                                         'communication': False,
                                         'payment_token_id': False,
                                         'invoice_ids': [(6, 0, move.ids)],
                                         })
                                    print("paiement", payment)
    
                                    payment.post()
                                    move.cpf_acompte_amount = acompte_amount
                                    ref = move.name
    
                            so.action_cancel()
                            so.unlink()
                elif user and product_id and product_id.company_id.id == 1 and user.id_edof and user.date_examen_edof and user.session_ville_id:
                    """Pour mcm creation de facture sans passer un paiement de 25%"""
                    module_id = request.env['mcmacademy.module'].sudo().search(
                        [('company_id', "=", 1), ('session_ville_id', "=", user.session_ville_id.id),
                         ('date_exam', "=", user.date_examen_edof), ('product_id', "=", product_id.id),
                         ('session_id.number_places_available', '>', 0)], limit=1)
                    print('before if modulee', module_id)
                    if module_id:
                        print('if modulee', module_id)
                        product_id = request.env['product.product'].sudo().search(
                            [('product_tmpl_id', '=', module_id.product_id.id)])
                        request.env.user.company_id = 1
                        """chercher facture avec numero de dossier si n'existe pas on crée une facture"""
                        invoice = request.env['account.move'].sudo().search(
                            [('numero_cpf', "=", externalId),
                             ('state', "=", 'posted'),
                             ('partner_id', "=", user.id)], limit=1)
                        if invoice:
                            num = invoice.name
                            bill_num = num.replace('FA', '')
                            bill_num = bill_num.replace('-', '')
                        print('invoice', invoice.name)
                        if not invoice:
                            _logger.info('invoice %s'%str(invoice.name))
    
                            print('if  not invoice digi ')
                            so = request.env['sale.order'].sudo().create({
                                'partner_id': user.id,
                                'company_id': 1,
                            })
                            so.module_id = user.module_id
                            so.session_id = user.session_id
                            """Créer une ligne de vente avec le montant CGU récupéré depuis cpf"""
                            so_line = request.env['sale.order.line'].sudo().create({
                                'name': product_id.name,
                                'product_id': product_id.id,
                                'product_uom_qty': 1,
                                'product_uom': product_id.uom_id.id,
                                'price_unit': amountCGU,
                                'order_id': so.id,
                                'tax_id': product_id.taxes_id,
                                'company_id': 1,
                            })
                            # prix de la formation dans le devis
                            amount_before_instalment = so.amount_total
                            # so.amount_total = so.amount_total * 0.25
                            for line in so.order_line:
                                line.price_unit = so.amount_total
                            so.action_confirm()
                            ref = False
                            # Creation de la Facture Cpf
                            # Si la facture est de type CPF :  On parse le pourcentage qui est 25 %
                            # methode_payment prend la valeur CPF pour savoir bien qui est une facture CPF qui prend la valeur 25 % par default
    
                            if so.amount_total > 0 and so.order_line:
                                moves = so._create_invoices(final=True)
                                for move in moves:
                                    move.type_facture = 'interne'
                                    # move.cpf_acompte_invoice= True
                                    # move.cpf_invoice =True
                                    move.methodes_payment = 'cpf'
                                    move.numero_cpf = externalId
                                    move.pourcentage_acompte = 25
                                    move.module_id = so.module_id
                                    move.session_id = so.session_id
                                    for line in move.invoice_line_ids:
                                        print('line', line.price_unit)
                                        line.price_unit = amountCGU
                                        print('line', line.price_unit)
                                    """Calculer l'es 'acompte 25% du montant total de la formation """
                                    acompte = (product_id.lst_price * move.pourcentage_acompte) / 100
                                    move.cpf_acompte_amount = acompte
                                    print('acompte', acompte, product_id.lst_price)
                                    if so.pricelist_id.code:
                                        move.pricelist_id = amountCGU
                                    move.company_id = so.company_id
                                    move.price_unit = amountCGU  # changé avec montant CGU
                                    # move.cpf_acompte_invoice=True
                                    # move.cpf_invoice = True
                                    move.methodes_payment = 'cpf'
                                    move.post()
                                    num = move.name
                                    bill_num = num.replace('FA', '')
                                    bill_num = bill_num.replace('-', '')
                                    ref = move.name
    
                            so.action_cancel()
                            so.unlink()
            """Facturer le dossier cpf par l'api en utilisant la référence de la facture odoo """
            if bill_num.isdigit():
                _logger.info("bill num %s" % bill_num)
                data='{"billNumber":"' + bill_num + '"}'
                facturer_dossier=requests.post('https://www.wedof.fr/api/registrationFolders/'+ externalId +'/billing',headers=headers,data=data)
                content = json.loads(facturer_dossier.content)
                _logger.info("post facture %s" %str(content))
                if str(facturer_dossier.status_code) == "200":
                    _logger.info("post success facture %s" % str(facturer_dossier.status_code))

                
        return True

    """Ajouter date d'acompte reçu sur la fiche client apres l'evennement "a reçu un acompte" sur edof"""
    @http.route(['/acompte_cpf'], type='http', auth="public", methods=['POST'])
    def acompte_cpf(self, **kw):
        _logger.info("webhooooooook rest amount")
        dossier = json.loads(request.httprequest.data)
        event = request.httprequest.headers.get('X-Wedof-Event')
        _logger.info("webhoooooooooook acompte %s" % str(dossier))
        _logger.info("header %s" % str(event))
        external = dossier['externalId']
        companies = self.env['res.company'].sudo().search([])
        if companies:
            for company in companies:
                api_key = company.wedof_api_key
                params_ = (
                    ('order', 'desc'),
                    ('type', 'deposit'),
                    ('state','issued'),
                    ('registrationFolderId', external),
                    ('sort', 'lastUpdate'),
                    ('limit', '1000')
                )
                headers = {
                    'accept': 'application/json',
                    'Content-Type': 'application/json',
                    'X-API-KEY': api_key,
                }

                response_paiement = requests.get('https://www.wedof.fr/api/payments/', headers=headers,
                                                 params=params_)
                paiements = response_paiement.json()
                print("dossier", dossier)
                """Récupérer le paiement selon numero de dossier et type de paiement acompte  """
                for paiement in paiements:
                    externalId = paiement['externalId']
                    """Changer format date"""
                    if 'transactionDate' in paiement:
                        transaction_date = paiement['transactionDate']
                        trdate = datetime.strptime(transaction_date, '%Y-%m-%dT%H:%M:%S.%fz')
                        newformat = "%d/%m/%Y"
                        trdateform = trdate.strftime(newformat)
                        trans_date = datetime.strptime(trdateform, "%d/%m/%Y")
                        print("paiement", externalId, trans_date, external)
                        """Chercher la fiche client correspondante et affecter la date d'acompte"""
                        partner = request.env['res.partner'].sudo().search([("numero_cpf", "=", external)], limit=1)
                        print("partner", partner.acompte_date)
                        if partner:
                            partner.acompte_date = trans_date
                            print("partner", partner.acompte_date)
        return True



    """Payer le montant restant  sur la facture apres l'evenement 'payé' sur edof"""
    @http.route(['/rest_amount_cpf'], type='http', auth="public", methods=['POST'])
    def rest_amount_invoice(self):
        _logger.info("webhooooooook rest amount")
        dossier = json.loads(request.httprequest.data)
        event = request.httprequest.headers.get('X-Wedof-Event')
        _logger.info("webhoooooooooook restamount %s" % str(dossier))
        _logger.info("header %s" % str(event))
        external = dossier['externalId']
        companies = self.env['res.company'].sudo().search([])
        if companies:
            for company in companies:
                api_key = company.wedof_api_key
                headers = {
                    'accept': 'application/json',
                    'Content-Type': 'application/json',
                    'X-API-KEY': api_key,
                }
                params_ = (
                    ('order', 'desc'),
                    ('type', 'bill'),
                    ('state', 'issued'),
                    ('registrationFolderId', external),
                    ('sort', 'lastUpdate'),
                    ('limit', '1000')
                )

                response_paiement = requests.get('https://www.wedof.fr/api/payments/', headers=headers,
                                                 params=params_)
                paiements = response_paiement.json()
                """Récupérer le paiement selon numero de dossier et type de paiement acompte  """
                for paiement in paiements:
                    """Changer format date"""
                    date_paiement = ""
                    amount = paiement['amount']
                    if 'transactionDate' in paiement and paiement['transactionDate']:
                        transaction_date = paiement['transactionDate']
                        trdate = datetime.strptime(transaction_date, '%Y-%m-%dT%H:%M:%S.%fz')
                        newformat = "%d/%m/%Y"
                        trdateform = trdate.strftime(newformat)
                        date_paiement = datetime.strptime(trdateform, "%d/%m/%Y")
                        print("paiement", external, date_paiement)
                    """chercher la facture par numero cpf"""
                    move =request.env['account.move'].sudo().search([('numero_cpf',"=",external)],limit=1)
                    if move and move.invoice_payment_state != "paid":
                        journal_id = move.journal_id.id
                        acquirer = request.env['payment.acquirer'].sudo().search(
                            [('name', "=", _('stripe')), ('company_id', '=', 1)], limit=1)
                        if acquirer:
                            journal_id = acquirer.journal_id.id
                        """Effectuer  un payement de montant restant  de la formation pour digimoov"""
                        payment_method = request.env['account.payment.method'].sudo().search(
                            [('code', 'ilike', 'electronic')])
                        payment = request.env['account.payment'].sudo().create(
                            {'payment_type': 'inbound',
                             'payment_method_id': payment_method.id,
                             'partner_type': 'customer',
                             'partner_id': move.partner_id.id,
                             'amount': move.amount_residual,
                             'currency_id': move.currency_id.id,
                             'payment_date': date_paiement,
                             'journal_id': journal_id,
                             'communication': False,
                             'payment_token_id': False,
                             'invoice_ids': [(6, 0, move.ids)],
                             })
                        print("paiement", payment)

                        payment.post()

        return True


        

