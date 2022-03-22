# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.tools.float_utils import float_round
import requests
from requests.exceptions import HTTPError
from werkzeug import urls
from collections import namedtuple
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.addons.payment_stripe.controllers.main import StripeController
import pprint
import psycopg2
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)
# The following currencies are integer only, see https://stripe.com/docs/currencies#zero-decimal
INT_CURRENCIES = [
    u'BIF', u'XAF', u'XPF', u'CLP', u'KMF', u'DJF', u'GNF', u'JPY', u'MGA', u'PYG', u'RWF', u'KRW',
    u'VUV', u'VND', u'XOF'
]
class PaymentStripeAcquirer(models.Model):
    _inherit = "payment.transaction"
    stripe_sub_reference = fields.Char("Reference d'abonnement")
    """Heriter la methode qui fait le payment intent sur stripe et ajouter la partie de creation d'abonnement"""
    def stripe_s2s_do_transaction(self, **kwargs):
        for rec in self :
            print("stripe_s2s_do_transaction",rec.reference)
            reference =rec.reference
            data = reference.split("-")
            sale = self.env['sale.order'].sudo().search([('name', 'ilike', data[0])])
            print('sale ', sale)
            if sale and sale.instalment:
                """Si le devis est trouvé avec la condition de payement sur plusieurs fois
                on appelle la methode de creation d'abonnement stripe """
                print("instalment")
                res=self.create_stripe_subsription(sale)
                '''il faut verifier si  un abonnement est créé ou non '''
                print('res subscription ', res)
                if res :
                    """si l'abonnement est créé on valide la transaction et on fait la mise à jour des informations"""
                    result=self._stripe_s2s_validate_tree_subscription(res)
                    print('*************resultvalidate',result)
                    return result
                else :
                    """on cas d'erreur on met à jour l'etat de transaction comme erreur"""
                    print('erreuur')
                    msg="Abonnement stripe non effectué "
                    self._set_transaction_error(msg)
                    return False
            else :
                """Si non si un payement de la totalité de montant on garde le paiement Intent """
                print("else ")
                result = super(PaymentStripeAcquirer, self).stripe_s2s_do_transaction(**kwargs)
                return result
    """creer un abonnement stripe avec api """
    def create_stripe_subsription(self,sale):
        if not self.payment_token_id.stripe_payment_method:
            # old token before using sca, need to fetch data from the api
            self.payment_token_id._stripe_sca_migrate_customer()
        """trouver le produit recurent sur stripe pour créer un abonnement  """
        nom_produit=sale.module_id.product_id.name
        id_produit=sale.module_id.product_id.id_stripe
        """vérifier la valeur de instalment number 
        et créer la date d'annulation d'abonnement """
        instalment_number = (sale.instalment_number)
        print('name product instalment', nom_produit, instalment_number)
        today=date.today()
        canceled=str(today+ relativedelta(months=instalment_number)+ timedelta(days=1))
        date_canceled= int(datetime.strptime(canceled, "%Y-%m-%d").timestamp())
        params = (('limit', '100'),)
        url = "products/%s" % (id_produit)
        data = self.acquirer_id._stripe_request(url, method="GET")
        prod = data.get('data', [])
        print('product',date_canceled)
        RECURRING_PRICE_ID=False
        data = self.acquirer_id._stripe_request('prices',data=params, method="GET")
        prices = data.get('data', [])
        print('if namee pricesss ', prices)
        for price in prices:
            if price['product']== id_produit and price['type']=="recurring":
                RECURRING_PRICE_ID=price['id']
                print('price recurring', price)
        if RECURRING_PRICE_ID:
            """Si le produit recurent est trouvé on lance l'api pour créer un abonnement"""
            subscription_data = {
                'customer': self.payment_token_id.acquirer_ref,
                'items[0][price]': RECURRING_PRICE_ID,
                'default_payment_method': self.payment_token_id.stripe_payment_method,
                'cancel_at':date_canceled
            }
            _logger.info('_create_stripe_subsription: Sending values to stripe, values:\n%s',
                         pprint.pformat(subscription_data))
            """créer un abonnement sur stripe"""
            res = self.acquirer_id._stripe_request('subscriptions', subscription_data)
            if res.get('id'):
                _logger.info('_create_stripe_subsription: Values received:\n%s', pprint.pformat(res))
                return res
            else:
                """si l'abonnement n'est pas créé on affiche erreur de paiement """
                print('pas dabonnement')
                stripe_error = res.get("failure_message") or res.get('error', {}).get('message')
                _logger.error('Stripe: invalid reply received from stripe API, looks like '
                              'the transaction failed. (error: %s)', stripe_error or 'n/a')
                error_msg = _("We're sorry to report that the transaction has failed.")
                if stripe_error:
                    error_msg += " " + (_("Stripe gave us the following info about the problem: '%s'") %
                                        stripe_error)
                raise ValidationError(error_msg)
            return False
        else :
            """si le produit est non trouvé, un message d'erreur sera affiché,la transaction passe à l'etat "error"
                        et un ticket sera créé pour service client et comptabilité  """
            print('pas de produit recurent')
            error = data.get("failure_message") or data.get('error', {}).get('message')
            self._set_transaction_error(error)
            vals = {
                'description': 'Erreur de paiement stripe %s %s' % (sale.partner_id.name, sale.name),
                'name': 'Tentative de paiement',
                'team_id': self.env['helpdesk.team'].sudo().search(
                    [('name', 'like', 'Comptabilité')],
                    limit=1).id,
            }
            description = "Erreur de paiement stripe " + str(sale.partner_id.name) + " " + str(sale.name)
            ticket = self.env['helpdesk.ticket'].sudo().search([("description", "=", description),
                                                                ("team_id.name", 'like', 'Comptabilité')])
            if not ticket:
                new_ticket = self.env['helpdesk.ticket'].sudo().create(
                    vals)
            vals_client = {
                'description': 'Erreur de paiement stripe %s %s' % (sale.partner_id.name, sale.name),
                'name': 'Tentative de paiement',
                'team_id': self.env['helpdesk.team'].sudo().search(
                    [('name', 'like', 'Client')],
                    limit=1).id,
            }
            description_client = "Erreur de paiement stripe " + str(sale.partner_id.name) + " " + str(sale.name)
            ticket = self.env['helpdesk.ticket'].sudo().search([("description", "=", description_client),
                                                                ("team_id.name", 'like', 'Client')])
            if not ticket:
                new_ticket = self.env['helpdesk.ticket'].sudo().create(
                    vals_client)
            return False
    def _stripe_s2s_validate_tree_subscription(self, tree):
        self.ensure_one()
        if self.state not in ("draft", "pending"):
            _logger.info('Stripe: trying to validate an already validated tx (ref %s)', self.reference)
            return True
        latest_invoice=tree.get('latest_invoice')
        print('latest invoice', latest_invoice,tree)
        tx_id = tree.get('id')
        subscription_id=tree.get('id')
        """recuperer le  paiement de cet abonnement pour recuperer les information de 1ere transaction"""
        params = (('limit', '100'),)
        paiement_intent = self.acquirer_id._stripe_request("payment_intents", data=params, method="GET")
        data_paiement = paiement_intent.get('data', [])
        paiement_intent_id=""
        tx_secret=""
        card=""
        status=""
        for pay in data_paiement:
            invoice = pay.get('invoice')
            print("invoice",invoice)
            if invoice==latest_invoice:
                print('paiement***************', pay.get('id'))
                paiement_intent_id=pay.get('id')
                tx_secret=pay.get('client_secret')
                payment_method=pay.get('payment_method_options',[])
                card=payment_method.get('card',[])
                status=pay.get('status')
        vals = {
            "date": fields.datetime.now(),
            "acquirer_reference": tx_id,
            "stripe_payment_intent": paiement_intent_id,
            "stripe_payment_intent_secret": tx_secret,
            "stripe_sub_reference":subscription_id
        }
        if status == 'succeeded':
            self.write(vals)
            self._set_transaction_done()
            self.execute_callback()
            if self.type == 'form_save':
                s2s_data = {
                    'customer': tree.get('customer'),
                    'payment_method': tree.get('default_payment_method'),
                    'card': card,
                    'acquirer_id': self.acquirer_id.id,
                    'partner_id': self.partner_id.id
                }
                token = self.acquirer_id.stripe_s2s_form_process(s2s_data)
                self.payment_token_id = token.id
            if self.payment_token_id:
                self.payment_token_id.verified = True
            return True
        if status in ('processing', 'requires_action'):
            self.write(vals)
            self._set_transaction_pending()
            return True
        if status == 'requires_payment_method':
            self._set_transaction_cancel()
            self.acquirer_id._stripe_request('payment_intents/%s/cancel' % self.stripe_payment_intent)
            return False
        else:
            error = tree.get("failure_message") or tree.get('error', {}).get('message')
            self._set_transaction_error(error)
            return False
    

