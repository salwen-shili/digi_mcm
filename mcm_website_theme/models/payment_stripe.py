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

import logging
_logger = logging.getLogger(__name__)
# The following currencies are integer only, see https://stripe.com/docs/currencies#zero-decimal
INT_CURRENCIES = [
    u'BIF', u'XAF', u'XPF', u'CLP', u'KMF', u'DJF', u'GNF', u'JPY', u'MGA', u'PYG', u'RWF', u'KRW',
    u'VUV', u'VND', u'XOF'
]
class PaymentStripeAcquirer(models.Model):
    _inherit = "payment.transaction"


    def _stripe_create_payment_intent(self, acquirer_ref=None, email=None):
        print("je suis la ")
        _logger.info("je suis laaaaaaaaaaaa ---------- %s" % str(self))

        result = super(PaymentStripeAcquirer, self)._stripe_create_payment_intent(acquirer_ref, email)
        return result

    """Heriter la methode qui fait le payment intent sur stripe et ajouter la partie de creation d'abonnement"""
    def stripe_s2s_do_transaction(self, **kwargs):
        for rec in self :
            print("stripe_s2s_do_transaction",rec.reference)
            reference =rec.reference
            data = reference.split("-")
            sale = self.env['sale.order'].sudo().search([('name', 'ilike', data[0])])
            print('sale ', sale)
            if sale and sale.instalment and sale.company_id.id==2:
                """Si le devis est trouvé avec la condition de payement sur plusieurs fois
                on appelle la methode de creation d'abonnement stripe """
                print("instalment")
                self.ensure_one()
                res=self.create_stripe_subsription(sale)
                result=self._stripe_s2s_validate_tree_subscription(res)
                print('*************resultvalidate',result)
                return result
            else :
                """Si non si un payement de la totalité de montant """
                print("else ")
                result = super(PaymentStripeAcquirer, self).stripe_s2s_do_transaction(**kwargs)
        return result

    """creer un abonnement stripe avec api """
    def create_stripe_subsription(self,sale):
        if not self.payment_token_id.stripe_payment_method:
            # old token before using sca, need to fetch data from the api
            self.payment_token_id._stripe_sca_migrate_customer()
        """trouver le produit sur stripe pour créer un abonnement  """
        nom_produit=sale.module_id.name
        print('name product', nom_produit)
        data = self.acquirer_id._stripe_request('products', method="GET")
        products = data.get('data', [])
        RECURRING_PRICE_ID=""
        for prod in products:
            name=prod['name']
            id =prod['id']
            print('produuuuuuuuuuuuuuuuuct',prod)
            print("name",name)
            if name.lower() == nom_produit.lower():
                data = self.acquirer_id._stripe_request('prices', method="GET")
                prices = data.get('data', [])
                print('if namee pricesss ', prices)
                for price in prices:
                    if price['product']== id and price['type']=="recurring":
                        RECURRING_PRICE_ID=price['id']
                        print('price recurring', price)


        if RECURRING_PRICE_ID=="":
            print('pas de produit recurent')
        else :
            subscription_data = {
              'customer': self.payment_token_id.acquirer_ref,
              'items[0][price]': RECURRING_PRICE_ID,
              'default_payment_method': self.payment_token_id.stripe_payment_method

            }

            charge_params = {
                'amount': int(self.amount if self.currency_id.name in INT_CURRENCIES else float_round(self.amount * 100, 2)),
                'currency': self.currency_id.name.lower(),
                'off_session': True,
                'confirm': True,
                'payment_method': self.payment_token_id.stripe_payment_method,
                'customer': self.payment_token_id.acquirer_ref,
                "description": self.reference,
            }
            # if not self.env.context.get('off_session'):
            #     subscription_data.update(setup_future_usage='off_session', off_session=False)
            _logger.info('_create_stripe_subsription: Sending values to stripe, values:\n%s',
                         pprint.pformat(subscription_data))

            res = self.acquirer_id._stripe_request('subscriptions', subscription_data)
            if res.get('charges') and res.get('charges').get('total_count'):
                res = res.get('charges').get('data')[0]

            _logger.info('_create_stripe_subsription: Values received:\n%s', pprint.pformat(res))
            return res

    def _stripe_s2s_validate_tree(self, tree):

        result = super(PaymentStripeAcquirer, self)._stripe_s2s_validate_tree(tree)

        status = tree.get('status')
        tx_id = tree.get('id')
        tx_secret = tree.get("client_secret")
        print('treeeeee',status,tx_id,tx_secret)
        return result


    def _stripe_s2s_validate_tree_subscription(self, tree):
        self.ensure_one()
        if self.state not in ("draft", "pending"):
            _logger.info('Stripe: trying to validate an already validated tx (ref %s)', self.reference)
            return True

        status = tree.get('status')
        tx_id = tree.get('id')
        tx_secret = tree.get("client_secret")
        vals = {
            "date": fields.datetime.now(),
            "acquirer_reference": tx_id,
            "stripe_payment_intent": tx_id,
            "stripe_payment_intent_secret": tx_secret
        }
        if status == 'active':
            self.write(vals)
            self._set_transaction_done()
            self.execute_callback()
            if self.type == 'form_save':
                s2s_data = {
                    'customer': tree.get('customer'),
                    'payment_method': tree.get('default_payment_method'),
                    # 'card': tree.get('default_payment_method').get('card'),
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
            return False
        else:
            error = tree.get("failure_message") or tree.get('error', {}).get('message')
            self._set_transaction_error(error)
            return False

