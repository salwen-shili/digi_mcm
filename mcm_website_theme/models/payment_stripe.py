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

    """Heriter la methode qui fait le payment intent sur stipe et ajouter la partie de creation d'abonnement"""
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
                result=self.create_stripe_subsription()
                # return result
            else :
                """Si non si un payement de la totalité de montant """
                print("else ")
                result = super(PaymentStripeAcquirer, self).stripe_s2s_do_transaction(**kwargs)
        return result

    """creer un abonnement stripe avec api """
    def create_stripe_subsription(self):
        if not self.payment_token_id.stripe_payment_method:
            # old token before using sca, need to fetch data from the api
            self.payment_token_id._stripe_sca_migrate_customer()
        data = {
          'customer': self.payment_token_id.acquirer_ref,
          'items[0][price]': '{{RECURRING_PRICE_ID}}',
          'add_invoice_items[0][price]': '{{PRICE_ID}}'
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
        if not self.env.context.get('off_session'):
            charge_params.update(setup_future_usage='off_session', off_session=False)
        _logger.info('_create_stripe_subsription: Sending values to stripe, values:\n%s',
                     pprint.pformat(charge_params))

        res = self.acquirer_id._stripe_request('subscriptions', charge_params)
        if res.get('charges') and res.get('charges').get('total_count'):
            res = res.get('charges').get('data')[0]

        _logger.info('_create_stripe_subsription: Values received:\n%s', pprint.pformat(res))
        return res

