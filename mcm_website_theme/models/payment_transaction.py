# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import time
from odoo import api, fields, models, _, SUPERUSER_ID
import logging
import requests
_logger = logging.getLogger(__name__)
import pyshorteners
class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"
    # """Créer une facture lorsque l'etat de transaction sera done"""
    # def write(self, vals):
    #     result = super(PaymentTransaction, self).write(vals)
    #     if 'state' in vals:
    #         if vals['state'] == "done":
    #             self._reconcile_after_transaction_done()
    #     return result
    def _set_transaction_done(self):
        transaction = super(PaymentTransaction, self)._set_transaction_done()
        if self.reference:
            data = self.reference.split("-")
            sale = self.env['sale.order'].sudo().search([('name', 'ilike', data[0])])
            _logger.info("_set_transaction_done %s and state_of_transaction %s and sale is : %s" %(str(self.stripe_payment_intent),str(self.state),str(sale.name)))
            if (self.stripe_payment_intent and self.state == 'done' and sale):
                Session = self.env['mcm.session']
                sale.partner_id.mcm_session_id = sale.session_id
                sale.partner_id.module_id = sale.module_id
                sale.partner_id.sudo().write({'statut': 'won'})
                sale.partner_id.mode_de_financement = 'particulier'
                for order in sale.order_line:
                    session = Session.sudo().search([('product_id', '=', order.product_id.product_tmpl_id.id)])
                    if session:
                        sale.partner_id.session_id = session
                if sale.env.su:
                    # sending mail in sudo was meant for it being sent from superuser
                    sale = sale.with_user(SUPERUSER_ID)
                template_id = sale._find_mail_template(force_confirmation_template=True)
                _logger.info('_set_transaction_done _find_mail_template %s and sale : %s' % (str(template_id),str(sale)))
                if template_id and sale:
                    sale.with_context(force_send=True).message_post_with_template(template_id,
                                                                                  composition_mode='comment',
                                                                                  email_layout_xmlid="portal_contract.mcm_mail_notification_paynow_online"
                                                                                 )
                if sale:
                    test=sale.get_portal_url(report_type='pdf', download=True)

    # Ce programme a été modifié par seifeddinne le 31/05/2021
    # ajout du champs methode_payment qui stock la valeur carte bleu si le payment et par carte bleu

    def _reconcile_after_transaction_done(self):
        transaction=super(PaymentTransaction,self)._reconcile_after_transaction_done()
        return transaction

    def _check_amount_and_confirm_order(self):
        self.ensure_one()
        for order in self.sale_order_ids.filtered(lambda so: so.state in ('draft', 'sent')):
            if order.instalment :
                if float_compare(self.amount*order.instalment_number, order.amount_total, 2) == 0:
                    order.with_context(send_email=True).action_confirm()
            else :
                if float_compare(self.amount, order.amount_total, 2) == 0:
                    order.with_context(send_email=True).action_confirm()
                else:
                    _logger.warning(
                        '<%s> transaction AMOUNT MISMATCH for order %s (ID %s): expected %r, got %r',
                        self.acquirer_id.provider,order.name, order.id,
                        order.amount_total, self.amount,
                    )
                    order.message_post(
                        subject=_("Amount Mismatch (%s)") % self.acquirer_id.provider,
                        body=_("The order was not confirmed despite response from the acquirer (%s): order total is %r but acquirer replied with %r.") % (
                            self.acquirer_id.provider,
                            order.amount_total,
                            self.amount,
                        )
                    )
    def _invoice_sale_orders(self):
        res = super(PaymentTransaction, self)._invoice_sale_orders()
        template = self.env['mail.template'].sudo().search([('model', '=', 'account.move')])
        for trans in self.filtered(lambda t: t.sale_order_ids):
            if trans.invoice_ids :
                for sale in trans.sale_order_ids :
                    sale.partner_id.mcm_session_id = sale.session_id
                    sale.partner_id.module_id = sale.module_id
                    sale.partner_id.sudo().write({'statut': 'won'})
                    sale.partner_id.mode_de_financement = 'particulier'
                    for invoice in trans.invoice_ids :
                        invoice.type_facture='web'
                        invoice.methodes_payment = 'cartebleu'
                        invoice.stripe_sub_reference=self.stripe_sub_reference # s'il sagit d'un paiement sur plusieur fois recupérer l'id d'abonnement sur stripe
                        invoice.module_id=sale.module_id
                        invoice.session_id=sale.session_id
                        sale.partner_id.mcm_session_id = sale.session_id
                        sale.partner_id.module_id = sale.module_id
                        if sale.pricelist_id.code:
                            invoice.pricelist_id=sale.pricelist_id
                        invoice.company_id=sale.company_id
                        for move in invoice.with_user(SUPERUSER_ID):
                            move.message_post_with_template(int(template),
                                                               composition_mode='comment',
                                                               email_layout_xmlid="portal_contract.mcm_mail_notification_paynow_online"
                                                              )
                    sale.action_cancel()
                    sale.sale_action_sent()

                    if sale.partner_id.renounce_request == False:
                        """Envoyer sms pour renoncer au droit de rétractation """
                        url = '%smy' % str(sale.partner_id.company_id.website)
                        short_url = pyshorteners.Shortener()
                        short_url = short_url.tinyurl.short(
                            url)  # convert the url to be short using pyshorteners library
                        sms_body_ = "Afin d'intégrer notre plateforme de formation de suite, veuillez renoncer à votre droit de rétractation sur votre espace client %s" % (
                            short_url) # content of sms

                        sale.partner_id.send_sms(sms_body_, sale.partner_id)
        return res

        # _logger.info("***************after transaction done")
        # invoices = self.mapped('invoice_ids')
        # template = self.env['mail.template'].sudo().search([('model', '=', 'account.move')])
        # if self.reference:
        #     data = self.reference.split("-")
        #     sale = self.env['sale.order'].sudo().search([('name', 'ilike', data[0])])
        #     _logger.info("_reconcile_after_transaction_done state %s and state_of_transaction %s and sale is : %s" % (str(self.stripe_payment_intent), str(self.state), str(sale)))
        #     if (self.stripe_payment_intent and self.state == 'done' and sale):
        #         sale.action_confirm()
        #         sale.partner_id.mcm_session_id=sale.session_id
        #         sale.partner_id.module_id=sale.module_id
        #         sale.partner_id.sudo().write({'statut': 'won'})
        #         sale.partner_id.mode_de_financement ='particulier'
        #         moves = sale._create_invoices(final=False)
        #         _logger.info("_reconcile_after_transaction_done moves %s" %str(moves))
        #         for move in moves:
        #             move.type_facture='web'
        #             move.methodes_payment = 'cartebleu'
        #             move.stripe_sub_reference=self.stripe_sub_reference # s'il sagit d'un paiement sur plusieur fois recupérer l'id d'abonnement sur stripe
        #             move.module_id=sale.module_id
        #             move.session_id=sale.session_id
        #             sale.partner_id.mcm_session_id = sale.session_id
        #             sale.partner_id.module_id = sale.module_id
        #             if sale.pricelist_id.code:
        #                 move.pricelist_id=sale.pricelist_id
        #             move.company_id=sale.company_id
        #             move.action_post()
        #         sale.action_cancel()
        #         sale.sale_action_sent()

                # for move in moves.with_user(SUPERUSER_ID):
                #     move.message_post_with_template(int(template),
                #                                        composition_mode='comment',
                #                                        email_layout_xmlid="portal_contract.mcm_mail_notification_paynow_online"
                #                                       )
                
                # if sale.partner_id.renounce_request == False:
                #     """Envoyer sms pour renoncer au droit de rétractation """
                #     url = '%smy' % str(sale.partner_id.company_id.website)
                #     short_url = pyshorteners.Shortener()
                #     short_url = short_url.tinyurl.short(
                #         url)  # convert the url to be short using pyshorteners library
                #     sms_body_ = "Afin d'intégrer notre plateforme de formation de suite, veuillez renoncer à votre droit de rétractation sur votre espace client %s" % (
                #         short_url) # content of sms
                # 
                #     sale.partner_id.send_sms(sms_body_, sale.partner_id)
