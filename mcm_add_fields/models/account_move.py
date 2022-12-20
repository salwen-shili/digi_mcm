# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Ce programme a été modifié par seifeddinne le 22/03/2021
# Modification du process de la facturation
# Modification de l'aperçu de la facturation
# celon le champs methodes_payments : cpf /carte_bleu
# on oublie pas qu on travaille avec la notion de multi_compagnie :
# compagnie_id.id ==1 c est MCM_Academy
# compagnie_id.id ==2 c est Digimoov

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError
from _datetime import datetime, date
import requests
from requests.structures import CaseInsensitiveDict
from datetime import datetime, timedelta, date
import re
import json
from odoo import _
import locale
from dateutil.relativedelta import relativedelta
from unidecode import unidecode
import logging
import pyshorteners
_logger = logging.getLogger(__name__)



class AccountMove(models.Model):
    _inherit = "account.move"
    # Déclaration des fields
    # On a ajouté ces champs :
    # restamount / acompte_invoice /pourcentage_acompte /methodes_payment
    mcm_paid_amount = fields.Monetary(string='Montant payé', compute='_get_mcm_paid_amount', store=True)
    acompte_invoice = fields.Boolean(default=False)
    cpf_solde_invoice = fields.Boolean(default=False)
    cpf_acompte_invoice = fields.Boolean(default=False)
    amount_residual = fields.Monetary(string='Montant due', compute='_get_mcm_paid_amount', store=True)
    amount = fields.Monetary(string='Montant', compute='_compute_payments_widget_to_reconcile_info', store=True)
    amount_paye = fields.Monetary(string='Montant payé', store=True, readonly=True)
    restamount = fields.Monetary(string='Reste à payé ', compute='_compute_change_amount', store=True, readonly=True)
    module_id = fields.Many2one('mcmacademy.module', 'Module',track_visibility='always') #track visibility of module
    session_id = fields.Many2one('mcmacademy.session', 'Session',track_visibility='always') #track visibility of session
    pricelist_id = fields.Many2one('product.pricelist', 'Liste de prix')
    methodes_payment = fields.Selection(selection=[('cpf', 'CPF'), ('cartebleu', 'Carte bleue')],
                                        String='Méthode de payment')
    cpf_acompte_amount = fields.Monetary("Montant d'acompte")
    pourcentage_acompte = fields.Integer(string="Pourcentage d'acompte", compute='_compute_change_amount', store=True,
                                         readonly=False)
    billed_cpf=fields.Boolean("Facturé sur CPF",track_visibility='always')

    def write(self, vals_list):
        #ajouter la facture à l'historique de session
        rslt = super(AccountMove, self).write(vals_list)
        if  'session_id' in vals_list:

            session_id = vals_list['session_id']
            session = self.env['partner.sessions'].search([('client_id', '=', self.partner_id.id),
                                                              ('session_id', '=', session_id)],limit=1)
            if session:

                    session.sudo().write({
                        'invoice_id': self.id
                    })


        return rslt

    
    @api.depends('amount_total', 'amount_residual')
    def _get_mcm_paid_amount(self):
        for rec in self:
            payments = self.env['account.payment'].search(
                ['|', '&', ('communication', "=", rec.name), ('state', "=", 'posted'),
                 ('communication', 'like', rec.invoice_origin)])
            paid_amount = 0.0
            for payment in payments:
                paid_amount += payment.amount
            rec.mcm_paid_amount = paid_amount

    # Fonction qui calcule le reste à payé ,le montant de la formation et le pourcentage de l'acompte lhors de la modification de l'acompte
    # On traite les cas celon deux critere en_interne ou par site web
    # On calcule le montant total untaxed , le montant_paye , le restamount
    # le montant residual doit avoir le rest du montant
    # amount_residual_signed c'est pour l'avoir il prend le reste a paye
    # amount_total_signed c est aussi por l'avoir il prend le reste à payer
    # on a deux valeurs: site web ou inte rne
    # Si la méthode de payment est cpf et le champs   methode_payment == CPF alors :
    # La vue de la facture change elle affiche l'acompte qui prend sa valeur default 25 %
    # Et on peux la changer en pourcentage qu' on veux tout en calculant le montant payée et le reste à payer correctement
    # Si non si la méthode de payment est par carte bleu et le champs methode_payment== 'cartebleu' : l'acompte ne  s'affiche pas et la facture prend la somme de la formation
    # On oublie pas qu on travaille avec la notion de multi_compagnie :
    # Compagnie_id.id ==1 c est MCM_Academy (Pour les factures MCM on élimine la partie acompte carrément )
    # Compagnie_id.id ==2 c est Digimoov (Présence de la partie acompte pour les factures CPF qui prend par défaut 25 % pour le nouveau process et peux etre modifiable par la suite )
    # Reste à déclarer qu on a daysDiff ce champ  joue le role d'un répère axiale du temps avec lequel on sépare les deux process de travail pour la génération des factures
    # La process de la facturation avec deux facture pour chacque client qui a été mis avant on applique pour eux un pourcentage_acompte== 0
    # Les nouveau factures CPF avec le nouveau process prennent automatique 25 % modifiable par la suite en cas de besoin
    # company_id.id == 1 ça indique qu' on travaille avec la compagnie  MCM_academy
    # company_id.id == 2 ça indique qu' on travaille avec la compagnie  Digimoov
    @api.depends('invoice_line_ids.price_subtotal', 'pourcentage_acompte', 'methodes_payment', 'company_id')
    def _compute_change_amount(self):
        date_precis = date(2021, 4, 28)

        for rec in self:
            amount_untaxed_initiale = rec.amount_untaxed
            invoice_date = rec.invoice_date
            daysDiff = 0
            rec.pourcentage_acompte = 0
            rec.restamount = rec.amount_residual
            rec.amount_paye = rec.amount_total - rec.amount_residual
            if date_precis and rec.invoice_date:
                daysDiff = ((date_precis) - rec.invoice_date).days
                if (rec.methodes_payment == 'cpf' and daysDiff >= 0):
                    rec.pourcentage_acompte = 0
                    rec.amount_paye = (rec.amount_untaxed * rec.pourcentage_acompte) / 100
                    rec.restamount = amount_untaxed_initiale - rec.amount_paye
                    # rec.amount_untaxed =  rec.amount_paye
                    # rec.amount_residual = rec.restamount
                    rec.amount_residual_signed = rec.restamount
                    rec.amount_total_signed = rec.restamount
                elif (rec.methodes_payment == 'cpf' and daysDiff < 0 and rec.company_id.id == 2):
                    if (rec.pourcentage_acompte == 25 and rec.company_id.id == 2):
                        rec.pourcentage_acompte = 25
                        rec.amount_paye = (rec.amount_untaxed * rec.pourcentage_acompte) / 100
                        rec.restamount = amount_untaxed_initiale - rec.amount_paye
                        # rec.amount_untaxed =  rec.amount_paye
                        # rec.amount_residual = rec.restamount
                        rec.amount_residual_signed = rec.restamount
                        rec.amount_total_signed = rec.restamount
                    elif (rec.pourcentage_acompte == 5 and rec.company_id.id == 2):
                        rec.pourcentage_acompte = 5
                        rec.amount_paye = (rec.amount_untaxed * rec.pourcentage_acompte) / 100
                        rec.restamount = amount_untaxed_initiale - rec.amount_paye
                        # rec.amount_untaxed =  rec.amount_paye
                        # rec.amount_residual = rec.restamount
                        rec.amount_residual_signed = rec.restamount
                        rec.amount_total_signed = rec.restamount
                    else:
                        rec.pourcentage_acompte = 25
                        rec.amount_paye = (rec.amount_untaxed * rec.pourcentage_acompte) / 100
                        rec.restamount = amount_untaxed_initiale - rec.amount_paye
                        # rec.amount_untaxed =  rec.amount_paye
                        # rec.amount_residual = rec.restamount
                        rec.amount_residual_signed = rec.restamount
                        rec.amount_total_signed = rec.restamount

            # elif (rec.methode_payment == 'cartebleu'):
            #     # rec.pourcentage_acompte = 0
            #     # amount_untaxed = rec.invoice_line_ids.price_subtotal
            #     print("testmontant web")
            #     print(rec.invoice_line_ids.price_subtotal)
            #     print(rec.amount_untaxed)

    # @api.model
    # def write (self, vals):
    #     residual_amounts_list = super(AccountMove, self).create(vals)
    #     for rec in self :
    #     #     rec.amount_residual = rec.restamount
    #         print("hhhh")
    #     return residual_amounts_list

    # Annulation de l'acompte
    def delete_invoice(self):
        moves = self.env['account.payment'].search([])
        for move in moves:
            move.name = '/'
            move.line_ids.unlink()
            move.sudo().unlink()

    """Créer une facture suite à l'evennement à facturer sur cpf"""
    def create_invoice(self):
        companies = self.env['res.company'].sudo().search([])
        if companies:
            for company in companies:
                api_key = company.wedof_api_key
                params_wedof = (
                    ('order', 'desc'),
                    ('type', 'all'),
                    ('state', 'all'),
                    ('billingState', 'toBill'),
                    ('certificationState', 'all'),
                    ('sort', 'lastUpdate'),
                    ('limit', '100'),

                )
                headers = {
                    'accept': 'application/json',
                    'Content-Type': 'application/json',
                    'X-API-KEY': api_key,
                }
                response = requests.get('https://www.wedof.fr/api/registrationFolders/', headers=headers,
                                        params=params_wedof)
                registrations = response.json()
                for dossier in registrations:
                    lastUpdate=dossier['lastUpdate']
                    updatedate = datetime.strptime(lastUpdate, '%Y-%m-%dT%H:%M:%S.%fz')
                    newformat = "%d/%m/%Y"
                    updatedateform = updatedate.strftime(newformat)
                    update_date_last = datetime.strptime(updatedateform, "%d/%m/%Y")
                    _logger.info("last update %s" %str(update_date_last))

                    externalId = dossier['externalId']
                    amountCGU = dossier['amountCGU']
                    amount_ht=dossier['amountHt']
                    print("CGU", amountCGU,dossier)
                    bill_num=""
                    bill=False
                    email = dossier['attendee']['email']
                    email = email.replace("%", ".")  # remplacer % par .
                    email = email.replace(" ", "")  # supprimer les espaces envoyés en paramètre email
                    email = str(
                        email).lower()  # recupérer l'email en miniscule pour éviter la création des deux comptes
                    print('dossier', dossier)
                    idform = dossier['trainingActionInfo']['externalId']
                    _logger.info('dossier %s' % str(dossier))
                    training_id = ""
                    if "_" in idform:
                        idforma = idform.split("_", 1)
                        if idforma:
                            training_id = idforma[1]
                    state = dossier['state']
                    _logger.info('training %s'%str(training_id) )

                    user = self.env['res.partner'].sudo().search([('numero_cpf', "=", externalId)],limit=1)

                    product_id = ""
                    if 'digimoov' in str(training_id):
                        product_id = self.env['product.product'].sudo().search(
                            [('id_edof', "=", str(training_id)), ('company_id', "=", 2)], limit=1)
                        _logger.info('if digi %s' %str(product_id))
                        _logger.info('edof %s' % str(user.id_edof))
                        _logger.info('date %s' % str(user.date_examen_edof))
                        _logger.info('ville %s' % str(user.session_ville_id))

                    else:
                        print('if digi ', product_id)
                        product_id = self.env['product.product'].sudo().search(
                            [('id_edof', "=", str(training_id)), ('company_id', "=", 1)], limit=1)
                        _logger.info('if not digi %s' %str(product_id))
                        _logger.info('edof %s' %str(user.id_edof))
                        _logger.info('date %s' %str(user.date_examen_edof))
                        _logger.info('ville %s' %str(user.session_ville_id))



                    if user and product_id and product_id.company_id.id == 2 and user.id_edof and user.date_examen_edof and user.session_ville_id:
                        _logger.info("userrrr******** %s" %user.numero_cpf)
                        module_id = self.env['mcmacademy.module'].sudo().search(
                            [('company_id', "=", 2), ('session_ville_id', "=", user.session_ville_id.id),
                             ('date_exam', "=", user.date_examen_edof), ('product_id', "=", product_id.id)
                              ], limit=1)
                        _logger.info('before if modulee %s' %str(module_id.name))
                        if module_id:
                            _logger.info('if modulee %s'%str( module_id))
                            product_id = self.env['product.product'].sudo().search(
                                [('product_tmpl_id', '=', module_id.product_id.id)])
                            self.env.user.company_id = 2
                            """chercher facture avec numero de dossier si n'existe pas on crée une facture"""
                            invoice = self.env['account.move'].sudo().search(
                                [('numero_cpf', "=", externalId),
                                 ('state', "=", 'posted'),
                                 ('partner_id', "=", user.id)], limit=1)
                            print('invoice', invoice.name,invoice.invoice_payments_widget)
                            if invoice :
                                # invoice.button_draft()
                                # for line in invoice.invoice_line_ids:
                                #     print('line invoiice ', line.price_unit,invoice.name)
                                #     line.price_unit = amountCGU
                                # invoice.post()
                                #
                                # invoice.amount_paye = (product_id.lst_price * invoice.pourcentage_acompte) / 100

                                # invoice.cpf_acompte_amount = (product_id.lst_price * invoice.pourcentage_acompte) / 100
                                # print("invvvvv",invoice.cpf_acompte_amount)
                                # payment = self.env['account.payment'].sudo().search([('invoice_ids',"in",invoice.id),
                                #                                                      ('amount',"=",acompte_amount)])
                                # print("helloooo",payment)
                                # if not payment:
                                #     invoice.cpf_acompte_amount = acompte_amount
                                #     """Effectuer  un payement de 25% de montant total de la formation pour digimoov"""
                                #     journal_id = invoice.journal_id.id
                                #
                                #     payment_method = self.env['account.payment.method'].sudo().search(
                                #         [('code', 'ilike', 'electronic')])
                                #     payment = self.env['account.payment'].sudo().create(
                                #         {'payment_type': 'inbound',
                                #          'payment_method_id': payment_method.id,
                                #          'partner_type': 'customer',
                                #          'partner_id': invoice.partner_id.id,
                                #          'amount': acompte_amount,
                                #          'currency_id': invoice.currency_id.id,
                                #          'journal_id': journal_id,
                                #          'communication': False,
                                #          'payment_token_id': False,
                                #          'payment_date': date_acompte,
                                #          'invoice_ids': [(6, 0, invoice.ids)],
                                #          })
                                #     print("paiement", payment)
                                #
                                #     payment.post()
                                num = invoice.name
                                invoice.module_id=user.module_id
                                _logger.info('if invoice******** %s ' % str(invoice.module_id.name))
                                _logger.info('if invoice******** %s ' % str(invoice.name))
                                bill_num = num.replace('FA', '')
                                bill_num = bill_num.replace('-', '')
                                bill=invoice
                            if not invoice:
                                _logger.info('if  not invoice digi %s')
                                so = self.env['sale.order'].sudo().create({
                                    'partner_id': user.id,
                                    'company_id': 2,
                                })
                                so.module_id = user.module_id
                                _logger.info("SO module id %s "% str(so.module_id.name) )
                                so.session_id = user.mcm_session_id
                                """Créer une ligne de vente avec le montant CGU récupéré depuis cpf"""
                                so_line = self.env['sale.order.line'].sudo().create({
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
                                            line.price_unit = amountCGU
                                            print('line', line.price_unit)


                                        print('acompte', move.acompte_invoice, product_id.lst_price,move.amount_paye)
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
                                        bill=move


                                        journal_id = move.journal_id.id
                                        acquirer = self.env['payment.acquirer'].sudo().search(
                                            [('name', "=", _('stripe')), ('company_id', '=', 1)], limit=1)
                                        if acquirer:
                                            journal_id = acquirer.journal_id.id
                                        """ si acompte versé sur cpf effectuer  un payement de 25% de montant total de la formation pour digimoov"""
                                        params_ = (
                                            ('order', 'desc'),
                                            ('type', 'deposit'),
                                            ('state', 'issued'),
                                            ('registrationFolderId', externalId),
                                            ('sort', 'lastUpdate'),
                                            ('limit', '1000')
                                        )

                                        response_paiement = requests.get('https://www.wedof.fr/api/payments/',
                                                                         headers=headers,
                                                                         params=params_)
                                        paiements = response_paiement.json()
                                        """Récupérer le paiement selon numero de dossier et type de paiement acompte  """
                                        for paiement in paiements:
                                            """Changer format date"""
                                            date_acompte = ""
                                            acompte_amount = paiement['amount']
                                            _logger.info("paiement %s" % str(paiement))

                                            if 'transactionDate' in paiement:
                                                transaction_date = paiement['transactionDate']
                                                trdate = datetime.strptime(transaction_date, '%Y-%m-%dT%H:%M:%S.%fz')
                                                newformat = "%d/%m/%Y"
                                                trdateform = trdate.strftime(newformat)
                                                date_acompte = datetime.strptime(trdateform, "%d/%m/%Y")
                                                _logger.info("paiement acompte %s" % str(acompte_amount))

                                                payment_method = self.env['account.payment.method'].sudo().search(
                                                    [('code', 'ilike', 'electronic')])
                                                payment = self.env['account.payment'].sudo().create(
                                                    {'payment_type': 'inbound',
                                                     'payment_method_id': payment_method.id,
                                                     'partner_type': 'customer',
                                                     'partner_id': move.partner_id.id,
                                                     'amount': acompte_amount,
                                                     'currency_id': move.currency_id.id,
                                                     'journal_id': journal_id,
                                                     'communication': False,
                                                     'payment_token_id': False,
                                                     'payment_date': date_acompte,
                                                     'invoice_ids': [(6, 0, move.ids)],
                                                     })
                                                _logger.info("paiement %s"%str(payment))
                                                _logger.info('if not invoice %s ' % str(move.name))

                                                payment.post()
                                                """Ajouter la facture à l'hiistorique de session"""
                                                session = self.env['partner.sessions'].search(
                                                    [('client_id', '=', move.partner_id.id),
                                                     ('session_id', '=', move.session_id.id)])
                                                if session:
                                                    history = self.env['partner.sessions'].sudo().write({
                                                        'invoice_id': move.id,
                                                    })
                                                move.cpf_acompte_amount = acompte_amount

                                        ref = move.name

                                so.action_cancel()
                                so.unlink()

                    elif user  and product_id and product_id.company_id.id == 1 and user.id_edof and user.date_examen_edof and user.session_ville_id:
                        module_id = self.env['mcmacademy.module'].sudo().search(
                            [('company_id', "=", 1), ('session_ville_id', "=", user.session_ville_id.id),
                             ('date_exam', "=", user.date_examen_edof), ('product_id', "=", product_id.id)
                             ], limit=1)
                        print('before if modulee', module_id)
                        if module_id:
                            _logger.info('if modulee %s' %str(module_id))
                            product_id = self.env['product.product'].sudo().search(
                                [('product_tmpl_id', '=', module_id.product_id.id)])
                            self.env.user.company_id = 1
                            """chercher facture avec numero de dossier si n'existe pas on crée une facture"""
                            invoice = self.env['account.move'].sudo().search(
                                [('numero_cpf', "=", externalId),
                                 ('state', "=", 'posted'),
                                 ('partner_id', "=", user.id)], limit=1)
                            print('invoice', invoice.name)
                            if invoice :
                                num = invoice.name
                                bill_num = num.replace('FA', '')
                                bill_num = bill_num.replace('-', '')
                            if not invoice:
                                print('if  not invoice digi ')
                                so = self.env['sale.order'].sudo().create({
                                    'partner_id': user.id,
                                    'company_id': 1,
                                })
                                so.module_id = user.module_id
                                so.session_id = user.mcm_session_id
                                """Créer une ligne de vente avec le montant CGU récupéré depuis cpf"""
                                so_line = self.env['sale.order.line'].sudo().create({
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
                                        """Calculer les acompte 25% du montant total de la formation """
                                        acompte = (product_id.lst_price * move.pourcentage_acompte) / 100
                                        move.cpf_acompte_amount=acompte
                                        print('acompte', acompte, product_id.lst_price)
                                        if so.pricelist_id.code:
                                            move.pricelist_id = amountCGU
                                        move.company_id = so.company_id
                                        move.price_unit = amountCGU  # changé avec montant CGU
                                        # move.cpf_acompte_invoice=True
                                        # move.cpf_invoice = True
                                        move.methodes_payment = 'cpf'
                                        move.post()
                                        """Ajouter la facture à l'hiistorique de session"""
                                        session = self.env['partner.sessions'].search(
                                            [('client_id', '=', move.partner_id.id),
                                             ('session_id', '=', move.session_id.id)])
                                        if session:
                                            history = self.env['partner.sessions'].sudo().write({
                                                'invoice_id': move.id,
                                            })
                                        num = move.name
                                        bill_num = num.replace('FA', '')
                                        bill_num=bill_num.replace('-','')
                                        ref = move.name
                                so.action_cancel()
                                so.unlink()

                    """Facturer le dossier cpf par l'api en utilisant la référence de la facture odoo """
                    _logger.info("billig state %s " %str(dossier['billingState']))
                    _logger.info("billig state %s " % str(bill_num.isdigit()))
                    if bill_num.isdigit() and dossier['billingState'] =="toBill" and not bill.billed_cpf:
                        _logger.info("bill num %s" %bill_num)
                        data = '{"billNumber":"' + bill_num + '"}'
                        facturer_dossier = requests.post(
                            'https://www.wedof.fr/api/registrationFolders/' + externalId + '/billing', headers=headers,
                            data=data)
                        content = json.loads(facturer_dossier.content)
                        _logger.info("post facture %s" % str(content))
                        if str(facturer_dossier.status_code) == "200":
                            _logger.info("post success facture %s" % str(facturer_dossier.status_code))
                            if bill:
                                bill.billed_cpf=True


    def get_acompte(self):
        companies = self.env['res.company'].sudo().search([])
        if companies:
            for company in companies:
                api_key = company.wedof_api_key
                params_wedof = (
                    ('order', 'desc'),
                    ('type', 'all'),
                    ('state', 'all'),
                    ('billingState', 'depositPaid'),
                    ('certificationState', 'all'),
                    ('sort', 'lastUpdate'),
                    ('limit', '1000')
                )

                headers = {
                    'accept': 'application/json',
                    'Content-Type': 'application/json',
                    'X-API-KEY': api_key,
                }
                """Récupérer à partir de wedof la liste des dossiers   ayant statut de facture acompte déposé  """
                response = requests.get('https://www.wedof.fr/api/registrationFolders/', headers=headers,
                                        params=params_wedof)
                registrations = response.json()

                for dossier in registrations:
                    _logger.info("dossier %s"% str(dossier))

                    external = dossier['externalId']
                    params_ = (
                        ('order', 'desc'),
                        ('type', 'deposit'),
                        ('state','issued'),
                        ('registrationFolderId', external),
                        ('sort', 'lastUpdate'),
                        ('limit', '1000')
                    )

                    response_paiement = requests.get('https://www.wedof.fr/api/payments/', headers=headers,
                                          params=params_ )
                    paiements=response_paiement.json()
                    """Récupérer le paiement selon numero de dossier et type de paiement acompte  """
                    for paiement in paiements:
                        externalId = paiement['externalId']
                        _logger.info("paiement %s" % str(dossier))

                        """Changer format date"""
                        if 'transactionDate' in paiement and paiement['transactionDate']:
                            transaction_date=paiement['transactionDate']
                            trdate = datetime.strptime(transaction_date, '%Y-%m-%dT%H:%M:%S.%fz')
                            newformat = "%d/%m/%Y"
                            trdateform = trdate.strftime(newformat)
                            trans_date = datetime.strptime(trdateform, "%d/%m/%Y")
                            print("paiement", externalId,trans_date,external)
                            """Chercher la fiche client correspondante et affecter la date d'acompte"""
                            partner=self.env['res.partner'].sudo().search([("numero_cpf","=",external)],limit=1)
                            print("partner", partner.acompte_date)
                            if partner:
                                _logger.info("if partner paiement %s" % str(partner.acompte_date))
                                partner.acompte_date=trans_date
                                print("partner",partner.acompte_date)

    """Payer le montant restant  sur la facture pour les anciens factures """
    def rest_amount_invoice(self):
        companies = self.env['res.company'].sudo().search([])
        if companies:
            for company in companies:
                api_key = company.wedof_api_key
                params_wedof = (
                    ('order', 'desc'),
                    ('type', 'all'),
                    ('state', 'all'),
                    ('billingState', 'paid'),
                    ('certificationState', 'all'),
                    ('sort', 'lastUpdate'),
                    ('limit', '1000')
                )
                headers = {
                    'accept': 'application/json',
                    'Content-Type': 'application/json',
                    'X-API-KEY': api_key,
                }
                response = requests.get('https://www.wedof.fr/api/registrationFolders/', headers=headers,
                                        params=params_wedof)
                registrations = response.json()
                for dossier in registrations:

                    external = dossier['externalId']
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
                    """Récupérer le paiement selon numero de dossier et type de paiement facture  """
                    for paiement in paiements:
                        """Changer format date"""
                        date_paiement = ""
                        amount = paiement['amount']
                        print('amount paiement',amount)
                        if 'transactionDate' in paiement and paiement['transactionDate']:
                            transaction_date = paiement['transactionDate']
                            trdate = datetime.strptime(transaction_date, '%Y-%m-%dT%H:%M:%S.%fz')
                            newformat = "%d/%m/%Y"
                            trdateform = trdate.strftime(newformat)
                            date_paiement = datetime.strptime(trdateform, "%d/%m/%Y")
                            print("paiement", external, date_paiement)
                        """chercher la facture par numero cpf"""
                        move =self.env['account.move'].sudo().search([('numero_cpf',"=",external),
                                                                      ("methodes_payment","=","cpf")],limit=1)
                        if move and move.invoice_payment_state != "paid":
                            journal_id = move.journal_id.id
                            acquirer = self.env['payment.acquirer'].sudo().search(
                                [('name', "=", _('stripe')), ('company_id', '=', 1)], limit=1)
                            if acquirer:
                                journal_id = acquirer.journal_id.id
                            """Effectuer  un payement de montant restant  de la formation pour digimoov"""
                            payment_method = self.env['account.payment.method'].sudo().search(
                                [('code', 'ilike', 'electronic')])
                            payment = self.env['account.payment'].sudo().create(
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

    """Modifier les anicennes factures cpf avec les informations récupéré à partir de wedof """
    def invoice_update(self):
        companies = self.env['res.company'].sudo().search([('id',"=",2)])
        if companies:
                api_key = companies.wedof_api_key
                params_wedof = (
                    ('order', 'desc'),
                    ('type', 'all'),
                    ('state', 'all'),
                    ('billingState', 'paid'),
                    ('certificationState', 'all'),
                    ('sort', 'lastUpdate'),
                    ('since','2022-01-03'),
                    ('limit', '1000')
                )

                headers = {
                    'accept': 'application/json',
                    'Content-Type': 'application/json',
                    'X-API-KEY': api_key,
                }
                """Récupérer à partir de wedof la liste des dossiers   ayant statut de facture acompte déposé  """
                # response = requests.get('https://www.wedof.fr/api/registrationFolders/', headers=headers,
                #                         params=params_wedof)
                # registrations = response.json()
                params_ = (
                    ('order', 'desc'),
                    ('type', 'bill'),
                    ('state', 'issued'),
                    ('limit', '1000'),
                    ('since','2022-01-03')
                )

                response_paiement = requests.get('https://www.wedof.fr/api/payments/', headers=headers,
                                                 params=params_)
                paiements = response_paiement.json()
                """Récupérer le paiement selon numero de dossier et type de paiement 'facture'  """
                for paiement in paiements:
                    externalId = paiement['registrationFolder']['externalId']
                    """Changer format date"""
                    if 'transactionDate' in paiement and paiement['transactionDate']:
                        transaction_date = str(paiement['transactionDate'])
                        print(transaction_date)
                        trdate = datetime.strptime(transaction_date, '%Y-%m-%dT%H:%M:%S.%fz')
                        newformat = "%d/%m/%Y"
                        trdateform = trdate.strftime(newformat)
                        trans_date = datetime.strptime(trdateform, "%d/%m/%Y")
                        _logger.info("externalId %s" % str(externalId))
                        invoices=self.env['account.move'].sudo().search([("numero_cpf","=",externalId),
                                                                         ("methodes_payment","=","cpf"),
                                                                         ("invoice_payment_state","!=","paid")])
                        for invoice in invoices :
                            _logger.info("invoice %s" %str(invoice.name))
                            journal_id = invoice.journal_id.id
                            acquirer =self.env['payment.acquirer'].sudo().search(
                                [('name', "=", _('stripe')), ('company_id', '=', 1)], limit=1)
                            if acquirer:
                                journal_id = acquirer.journal_id.id
                            """Effectuer  un payement de montant restant  de la formation pour digimoov"""
                            payment_method = self.env['account.payment.method'].sudo().search(
                                [('code', 'ilike', 'electronic')])
                            payment = self.env['account.payment'].sudo().create(
                                {'payment_type': 'inbound',
                                 'payment_method_id': payment_method.id,
                                 'partner_type': 'customer',
                                 'partner_id': invoice.partner_id.id,
                                 'amount': invoice.amount_residual,
                                 'currency_id': invoice.currency_id.id,
                                 'payment_date': trans_date if trans_date else date.today(),
                                 'journal_id': journal_id,
                                 'communication': False,
                                 'payment_token_id': False,
                                 'invoice_ids': [(6, 0, invoice.ids)],
                                 })
                            payment.post()

    def remplir_session(self):
        invoices = self.env['account.move'].sudo().search([("methodes_payment", "=", 'cpf'),
                                                           ("session_id", "=", False)])
        for invoice in invoices:
            if invoice.partner_id.mcm_session_id:
                _logger.info("remplir invoice %s" %invoice.partner_id.mcm_session_id)
                invoice.session_id=invoice.partner_id.mcm_session_id
                
    def remplir_billed_cpf(self):
        companies = self.env['res.company'].sudo().search([])
        if companies:
            for company in companies:
                api_key = company.wedof_api_key
                params_wedof = (
                    ('order', 'desc'),
                    ('type', 'all'),
                    ('state', 'all'),
                    ('billingState', 'billed'),
                    ('sort', 'lastUpdate'),
                    ('since', '2022-10-01'),
                    ('limit', '1000')
                )

                headers = {
                    'accept': 'application/json',
                    'Content-Type': 'application/json',
                    'X-API-KEY': api_key,
                }
                """Récupérer à partir de wedof la liste des dossiers   ayant statut de facture acompte déposé  """
                response = requests.get('https://www.wedof.fr/api/registrationFolders/', headers=headers,
                                        params=params_wedof)
                registrations = response.json()
                params_ = (
                    ('order', 'desc'),
                    ('type', 'bill'),
                    ('state', 'issued'),
                    ('limit', '1000'),
                    ('since', '2022-01-03')
                )

                # response_paiement = requests.get('https://www.wedof.fr/api/payments/', headers=headers,
                #                                  params=params_)
                # paiements = response_paiement.json()

                for register in registrations:
                    externalId = register['externalId']
                    billidd=register['billNumber']
                    billid=""
                    if billidd:
                        """get last 4 number of invoice"""
                        billid = billidd[-5:]

                        """Changer format date"""
                        # if 'transactionDate' in paiement and paiement['transactionDate']:
                        #     transaction_date = str(paiement['transactionDate'])
                        #     print(transaction_date)
                        #     trdate = datetime.strptime(transaction_date, '%Y-%m-%dT%H:%M:%S.%fz')
                        #     newformat = "%d/%m/%Y"
                        #     trdateform = trdate.strftime(newformat)
                        #     trans_date = datetime.strptime(trdateform, "%d/%m/%Y")
                    _logger.info("externalId %s" % str(externalId))
                    _logger.info("billid %s" % str(billid))
                    invoices = self.env['account.move'].sudo().search([("numero_cpf", "=", externalId),
                                                                       ("methodes_payment", "=", "cpf"),])
                    if invoices:
                         for invoice in invoices:
                            _logger.info("invoice %s" % str(invoice.name))
                            invoice_name=invoice.name
                            invoice_ref=invoice_name[-5:]
                            if billid==invoice_ref:
                                _logger.info("if bill %s" % str(invoice_ref))
                                invoice.billed_cpf=True

    def create_invoice_bolt(self):
        emails = [
            'frankinam@hotmail.fr',
            'tiemokodiomande42@gmail.com',
            'krmkd@hotmail.com',
            'hurkus61@gmail.com',
            'theophiledongue2@yahoo.fr',
            'dawod1996.22@yahoo.com',
            'aberrak.06@gmail.com',
            'rankinam@hotmail.fr',
            'bretagnegirone@gmail.com',
            'dj.arbouze@yahoo.fr',
            'kadriidjassa199@gmail.com',
            'theophiledongue2@yahoo.fr',
            'borhencharkaoui@outlook.fr',
            'soufien.awaida@gmail.com'

        ]
        for email in emails:
            user = self.env['res.users'].sudo().search([("login", "=", email)],limit=1)
            if user:
                _logger.info("partner %s" % str(user.name))
                sale_order = self.env['sale.order'].sudo().search([('partner_id', "=", user.partner_id.id),
                                                                   ('module_id.product_id.default_code', "=",
                                                                    "vtc_bolt")])
                _logger.info("sale order %s" % str(sale_order.name))
            else:
                _logger.info('create new partner')
                user = self.env['res.users'].with_context(no_reset_password=True
                                                          ).sudo().create({
                    'name': str(email),
                    'login': str(email),
                    'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])],
                    'email': email,
                    'notification_type': 'inbox',
                    'website_id': 1,
                    'company_ids': [1],
                    'company_id': 1,

                })
                user.company_id = 1
                user.partner_id.company_id = 1
                user.partner_id.bolt = True


            if user:
                message = self.env["mail.message"].create(
                    {
                        "subject": "Client bolt de stripe",
                        "message_type": "comment",
                        "model": "res.partner",
                        "res_id": user.partner_id.id,
                        "partner_ids": [(4, user.partner_id.id)],
                        "body": "<p>Ancien client BOLT provient de stripe pour garder les factures</p>",
                    }
                )

                session_ville = self.env['session.ville'].sudo().search([('name_ville', "=", "Hauts-de-France")])
                date_time_str = '28/06/2022'
                date_time_obj = datetime.strptime(date_time_str, "%d/%m/%Y")
                product_id = self.env['product.template'].sudo().search(
                    [('default_code', "=", "vtc_bolt"), ('company_id', "=", 1)], limit=1)
                if session_ville and product_id:
                    module_id = self.env['mcmacademy.module'].sudo().search(
                        [('company_id', "=", 1),
                         ('session_ville_id', "=", session_ville.id),
                         ('date_exam', "=", date_time_obj),
                         ('product_id', "=", product_id.id)
                         ], limit=1)
                    _logger.info('before if modulee %s' % str(module_id))
                    if module_id:
                        _logger.info('if modulee %s' % str(module_id))
                        user.partner_id.module_id = module_id
                        user.partner_id.mcm_session_id = module_id.session_id
                        product_id = self.env['product.product'].sudo().search(
                            [('product_tmpl_id', '=', module_id.product_id.id)])
                        list = []
                        for client in module_id.session_id.client_ids:  # get list of existing clients ids
                            list.append(client.id)
                        list.append(user.partner_id.id)  # append partner to the list
                        module_id.session_id.write(
                            {'client_ids': [(6, 0, list)]})  # update the list of clients
                        invoice = self.env['account.move'].sudo().search(
                            [('module_id', "=", module_id.id),
                             ('state', "=", 'posted'),
                             ('partner_id', "=", user.partner_id.id)], limit=1)
                        print('invoice', invoice)
                        if not invoice:
                            print('if  not invoice mcm')
                            so = self.env['sale.order'].sudo().create({
                                'partner_id': user.partner_id.id,
                                'company_id': 1,
                            })
                            self.env['sale.order.line'].sudo().create({
                                'name': product_id.name,
                                'product_id': product_id.id,
                                'product_uom_qty': 1,
                                'product_uom': product_id.uom_id.id,
                                'price_unit': product_id.list_price,
                                'order_id': so.id,
                                'tax_id': product_id.taxes_id,
                                'company_id': 1
                            })
                            # Enreggistrement des valeurs de la facture
                            # Parser le pourcentage d'acompte
                            # Creation de la facture étape Finale
                            # Facture comptabilisée
                            so.action_confirm()
                            so.module_id = module_id
                            so.session_id = module_id.session_id
                            moves = so._create_invoices(final=True)
                            for move in moves:
                                move.type_facture = 'interne'
                                move.module_id = so.module_id
                                # move.cpf_acompte_invoice=True
                                # move.cpf_invoice =True
                                move.methodes_payment = 'cartebleu'
                                move.session_id = so.session_id
                                move.company_id = so.company_id
                                move.website_id = 1
                                for line in move.invoice_line_ids:
                                    if line.account_id != line.product_id.property_account_income_id and line.product_id.property_account_income_id:
                                        line.account_id = line.product_id.property_account_income_id
                                 move.post()
                            so.action_cancel()
                            so.unlink()

    def create_invoice_billed(self):
        companies = self.env['res.company'].sudo().search([])
        if companies:
            for company in companies:
                api_key = company.wedof_api_key

                params_wedof = (
                    ('order', 'desc'),
                    ('type', 'all'),
                    ('state', 'all'),
                    ('billingState', 'billed'),
                    ('certificationState', 'all'),
                    ('sort', 'lastUpdate'),
                    ('limit', '150'),
    

                )
                headers = {
                    'accept': 'application/json',
                    'Content-Type': 'application/json',
                    'X-API-KEY': api_key,
                }
                response = requests.get('https://www.wedof.fr/api/registrationFolders/', headers=headers,
                                        params=params_wedof)
                registrations = response.json()
                for dossier in registrations:
                    billnumero = dossier['billNumber']
                    billnumero = billnumero[:6] + "-" + billnumero[6:]
                    billnumero = "FA" + billnumero
                    _logger.info("bill num %s" % str(billnumero))
                    billedDate = dossier['history']['billedDate']
                    date_to_compare_str = "2022-12-07"
                    date_to_compare = datetime.strptime(date_to_compare_str, '%Y-%m-%d')
                    date_to_compare = date_to_compare.date()
                    updatedate = datetime.strptime(billedDate, '%Y-%m-%dT%H:%M:%S.%fz')
                    dateform = updatedate.date()
                    _logger.info("last update %s" % str(date_to_compare))
                    date_invoice_str = "07/12/2022"
                    date_to_invoice = datetime.strptime(date_invoice_str, '%d/%m/%Y')
                    if dateform == date_to_compare:
                        _logger.info("if date")
                        externalId = dossier['externalId']
                        amountCGU = dossier['amountCGU']
                        amount_ht = dossier['amountHt']
                        print("CGU", amountCGU, dossier)
                        bill_num = ""
                        bill = False
                        email = dossier['attendee']['email']
                        email = email.replace("%", ".")  # remplacer % par .
                        email = email.replace(" ", "")  # supprimer les espaces envoyés en paramètre email
                        email = str(
                            email).lower()  # recupérer l'email en miniscule pour éviter la création des deux comptes
                        print('dossier', dossier)
                        idform = dossier['trainingActionInfo']['externalId']
                        _logger.info('dossier %s' % str(dossier))
                        training_id = ""
                        if "_" in idform:
                            idforma = idform.split("_", 1)
                            if idforma:
                                training_id = idforma[1]
                        state = dossier['state']
                        _logger.info('training %s' % str(training_id))

                        user = self.env['res.partner'].sudo().search([('numero_cpf', "=", externalId)], limit=1)

                        product_id = ""
                        if 'digimoov' in str(training_id):
                            product_id = self.env['product.product'].sudo().search(
                                [('id_edof', "=", str(training_id)), ('company_id', "=", 2)], limit=1)
                            _logger.info('if digi %s' % str(product_id))
                            _logger.info('edof %s' % str(user.id_edof))
                            _logger.info('date %s' % str(user.date_examen_edof))
                            _logger.info('ville %s' % str(user.session_ville_id))

                        else:
                            print('if digi ', product_id)
                            product_id = self.env['product.product'].sudo().search(
                                [('id_edof', "=", str(training_id)), ('company_id', "=", 1)], limit=1)
                            _logger.info('if not digi %s' % str(product_id))
                            _logger.info('edof %s' % str(user.id_edof))
                            _logger.info('date %s' % str(user.date_examen_edof))
                            _logger.info('ville %s' % str(user.session_ville_id))

                        if user and product_id and product_id.company_id.id == 2 and user.id_edof and user.date_examen_edof and user.session_ville_id:
                            _logger.info("userrrr******** %s" % user.numero_cpf)
                            module_id = self.env['mcmacademy.module'].sudo().search(
                                [('company_id', "=", 2), ('session_ville_id', "=", user.session_ville_id.id),
                                 ('date_exam', "=", user.date_examen_edof), ('product_id', "=", product_id.id)
                                 ], limit=1)
                            _logger.info('before if modulee %s' % str(module_id.name))
                            if module_id:
                                _logger.info('if modulee %s' % str(module_id))
                                product_id = self.env['product.product'].sudo().search(
                                    [('product_tmpl_id', '=', module_id.product_id.id)])
                                self.env.user.company_id = 2
                                """chercher facture avec numero de dossier si n'existe pas on crée une facture"""
                                invoice = self.env['account.move'].sudo().search(
                                    [('numero_cpf', "=", externalId),
                                     ('state', "=", 'posted'),
                                     ('partner_id', "=", user.id)], limit=1)
                                #print('invoice', invoice.name, invoice.invoice_payments_widget)
                                if invoice:
                                    num = invoice.name
                                    invoice.module_id = user.module_id
                                    invoice.billed_cpf=True
                                    invoice.invoice_date=date_to_invoice
                                    _logger.info('if invoice******** %s ' % str(invoice.module_id.name))
                                    _logger.info('if invoice******** %s ' % str(invoice.name))
                                    bill_num = num.replace('FA', '')
                                    bill_num = bill_num.replace('-', '')
                                    bill = invoice

                                if not invoice:
                                    _logger.info('if  not invoice digi %s')
                                    so = self.env['sale.order'].sudo().create({
                                        'partner_id': user.id,
                                        'company_id': 2,
                                    })
                                    so.module_id = user.module_id
                                    _logger.info("SO module id %s " % str(so.module_id.name))
                                    so.session_id = user.mcm_session_id
                                    """Créer une ligne de vente avec le montant CGU récupéré depuis cpf"""
                                    so_line = self.env['sale.order.line'].sudo().create({
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
                                                line.price_unit = amountCGU
                                                print('line', line.price_unit)

                                            print('acompte', move.acompte_invoice, product_id.lst_price,
                                                  move.amount_paye)
                                            if so.pricelist_id.code:
                                                move.pricelist_id = amountCGU
                                            move.company_id = so.company_id
                                            move.price_unit = amountCGU  # changé avec montant CGU
                                            # move.cpf_acompte_invoice=True
                                            # move.cpf_invoice = True
                                            move.methodes_payment = 'cpf'
                                            move.sudo().write({'name': billnumero})
                                            move.invoice_date=date_to_invoice
                                            move.billed_cpf=True
                                            _logger.info("name invoice %s" % str(move.name))
                                            move.post()
                                            num = move.name
                                            bill_num = num.replace('FA', '')
                                            bill_num = bill_num.replace('-', '')
                                            bill = move

                                            journal_id = move.journal_id.id
                                            acquirer = self.env['payment.acquirer'].sudo().search(
                                                [('name', "=", _('stripe')), ('company_id', '=', 1)], limit=1)
                                            if acquirer:
                                                journal_id = acquirer.journal_id.id
                                            """ si acompte versé sur cpf effectuer  un payement de 25% de montant total de la formation pour digimoov"""
                                            params_ = (
                                                ('order', 'desc'),
                                                ('type', 'deposit'),
                                                ('state', 'issued'),
                                                ('registrationFolderId', externalId),
                                                ('sort', 'lastUpdate'),
                                                ('limit', '1000')
                                            )

                                            response_paiement = requests.get('https://www.wedof.fr/api/payments/',
                                                                             headers=headers,
                                                                             params=params_)
                                            paiements = response_paiement.json()
                                            """Récupérer le paiement selon numero de dossier et type de paiement acompte  """
                                            for paiement in paiements:
                                                """Changer format date"""
                                                date_acompte = ""
                                                acompte_amount = paiement['amount']
                                                _logger.info("paiement %s" % str(paiement))

                                                if 'transactionDate' in paiement:
                                                    transaction_date = paiement['transactionDate']
                                                    trdate = datetime.strptime(transaction_date,
                                                                               '%Y-%m-%dT%H:%M:%S.%fz')
                                                    newformat = "%d/%m/%Y"
                                                    trdateform = trdate.strftime(newformat)
                                                    date_acompte = datetime.strptime(trdateform, "%d/%m/%Y")
                                                    _logger.info("paiement acompte %s" % str(acompte_amount))

                                                    payment_method = self.env['account.payment.method'].sudo().search(
                                                        [('code', 'ilike', 'electronic')])
                                                    payment = self.env['account.payment'].sudo().create(
                                                        {'payment_type': 'inbound',
                                                         'payment_method_id': payment_method.id,
                                                         'partner_type': 'customer',
                                                         'partner_id': move.partner_id.id,
                                                         'amount': acompte_amount,
                                                         'currency_id': move.currency_id.id,
                                                         'journal_id': journal_id,
                                                         'communication': False,
                                                         'payment_token_id': False,
                                                         'payment_date': date_acompte,
                                                         'invoice_ids': [(6, 0, move.ids)],
                                                         })
                                                    _logger.info("paiement %s" % str(payment))
                                                    _logger.info('if not invoice %s ' % str(move.name))

                                                    payment.post()
                                                    """Ajouter la facture à l'hiistorique de session"""
                                                    session = self.env['partner.sessions'].search(
                                                        [('client_id', '=', move.partner_id.id),
                                                         ('session_id', '=', move.session_id.id)])
                                                    if session:
                                                        history = self.env['partner.sessions'].sudo().write({
                                                            'invoice_id': move.id,
                                                        })
                                                    move.cpf_acompte_amount = acompte_amount

                                            ref = move.name

                                    so.action_cancel()
                                    so.unlink()

                    #     elif user  and product_id and product_id.company_id.id == 1 and user.id_edof and user.date_examen_edof and user.session_ville_id:
                    #         module_id = self.env['mcmacademy.module'].sudo().search(
                    #             [('company_id', "=", 1), ('session_ville_id', "=", user.session_ville_id.id),
                    #              ('date_exam', "=", user.date_examen_edof), ('product_id', "=", product_id.id),
                    #              ('session_id.number_places_available', '>', 0)], limit=1)
                    #         print('before if modulee', module_id)
                    #         if module_id:
                    #             _logger.info('if modulee %s' %str(module_id))
                    #             product_id = self.env['product.product'].sudo().search(
                    #                 [('product_tmpl_id', '=', module_id.product_id.id)])
                    #             self.env.user.company_id = 1
                    #             """chercher facture avec numero de dossier si n'existe pas on crée une facture"""
                    #             invoice = self.env['account.move'].sudo().search(
                    #                 [('numero_cpf', "=", externalId),
                    #                  ('state', "=", 'posted'),
                    #                  ('partner_id', "=", user.id)], limit=1)
                    #             print('invoice', invoice.name)
                    #             if invoice :
                    #                 num = invoice.name
                    #                 bill_num = num.replace('FA', '')
                    #                 bill_num = bill_num.replace('-', '')
                    #             if not invoice:
                    #                 print('if  not invoice digi ')
                    #                 so = self.env['sale.order'].sudo().create({
                    #                     'partner_id': user.id,
                    #                     'company_id': 1,
                    #                 })
                    #                 so.module_id = user.module_id
                    #                 so.session_id = user.mcm_session_id
                    #                 """Créer une ligne de vente avec le montant CGU récupéré depuis cpf"""
                    #                 so_line = self.env['sale.order.line'].sudo().create({
                    #                     'name': product_id.name,
                    #                     'product_id': product_id.id,
                    #                     'product_uom_qty': 1,
                    #                     'product_uom': product_id.uom_id.id,
                    #                     'price_unit': amountCGU,
                    #                     'order_id': so.id,
                    #                     'tax_id': product_id.taxes_id,
                    #                     'company_id': 1,
                    #                 })
                    #                 # prix de la formation dans le devis
                    #                 amount_before_instalment = so.amount_total
                    #                 # so.amount_total = so.amount_total * 0.25
                    #                 for line in so.order_line:
                    #                     line.price_unit = so.amount_total
                    #                 so.action_confirm()
                    #                 ref = False
                    #                 # Creation de la Facture Cpf
                    #                 # Si la facture est de type CPF :  On parse le pourcentage qui est 25 %
                    #                 # methode_payment prend la valeur CPF pour savoir bien qui est une facture CPF qui prend la valeur 25 % par default
                    #
                    #                 if so.amount_total > 0 and so.order_line:
                    #                     moves = so._create_invoices(final=True)
                    #                     for move in moves:
                    #                         move.type_facture = 'interne'
                    #                         # move.cpf_acompte_invoice= True
                    #                         # move.cpf_invoice =True
                    #                         move.methodes_payment = 'cpf'
                    #                         move.numero_cpf = externalId
                    #                         move.pourcentage_acompte = 25
                    #                         move.module_id = so.module_id
                    #                         move.session_id = so.session_id
                    #                         for line in move.invoice_line_ids:
                    #                             print('line', line.price_unit)
                    #                             line.price_unit = amountCGU
                    #                             print('line', line.price_unit)
                    #                         """Calculer les acompte 25% du montant total de la formation """
                    #                         acompte = (product_id.lst_price * move.pourcentage_acompte) / 100
                    #                         move.cpf_acompte_amount=acompte
                    #                         print('acompte', acompte, product_id.lst_price)
                    #                         if so.pricelist_id.code:
                    #                             move.pricelist_id = amountCGU
                    #                         move.company_id = so.company_id
                    #                         move.price_unit = amountCGU  # changé avec montant CGU
                    #                         # move.cpf_acompte_invoice=True
                    #                         # move.cpf_invoice = True
                    #                         move.methodes_payment = 'cpf'
                    #                         move.post()
                    #                         """Ajouter la facture à l'hiistorique de session"""
                    #                         session = self.env['partner.sessions'].search(
                    #                             [('client_id', '=', move.partner_id.id),
                    #                              ('session_id', '=', move.session_id.id)])
                    #                         if session:
                    #                             history = self.env['partner.sessions'].sudo().write({
                    #                                 'invoice_id': move.id,
                    #                             })
                    #                         num = move.name
                    #                         bill_num = num.replace('FA', '')
                    #                         bill_num=bill_num.replace('-','')
                    #                         ref = move.name
                    #                 so.action_cancel()
                    #                 so.unlink()















