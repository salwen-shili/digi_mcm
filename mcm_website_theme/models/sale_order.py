# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    instalment_number = fields.Integer("Tranches", compute='get_instalment_number')
    amount_to_pay = fields.Monetary('Montant à Payer', compute='compute_amount_to_pay')
    instalment = fields.Boolean(default=False)
    conditions = fields.Boolean(default=False)
    failures = fields.Boolean(default=False)
    accompagnement = fields.Boolean(default=False)
    # Add fields of questionnaire in the sale order. These fields will be deleted next.
    besoins_particuliers = fields.Selection([('Oui', 'Oui'), ('Non', 'Non')])
    type_besoins = fields.Text()
    raison_choix = fields.Selection([
        ('En chômage', 'Je suis en chômage et je suis en recherche d\'emploi'),
        ('Monter sa propre entreprise', 'Je veux monter ma propre entreprise et être indépendant'),
        ('Passionné par le métier', 'Je suis passionné par le métier de chauffeur'),
        ('En reconversion professionnelle', 'Je suis en reconversion professionnelle pour être chauffeur'),
        ('Mettre à jour ses connaissances', 'Pour mettre à jour mes connaissances et compétences du métier'),
        ('Arrondir ses fins du mois', 'Pour arrondir mes fins du mois')])
    support_formation = fields.Selection([
        ('Vidéos préenregistrées', 'En visualisant des vidéos préenregistrées '),
        ('Documents en ligne', 'En lisant des documents PDF en ligne'),
        ('En mode audio', 'En écoutant les cours en mode audio'),
        ('Alternance entre tous ces modes', 'En alternant entre tous ces modes d’apprentissage')])
    availability = fields.Selection([
        ('Le matin', 'Le matin'),
        ("L'après-midi", "L'après-midi"),
        ('Le soir', 'Le soir'),
        ('Le week-end', 'Le week-end'),
        ('Peu importe', 'Peu importe'),
        ('Je ne souhaite pas être coaché', 'Je ne souhaite pas être coaché'),
    ])
    attentes = fields.Text()

    @api.depends('amount_total', 'pricelist_id')
    def get_instalment_number(self):
        for rec in self:
            for line in rec.order_line:
                if line.product_id.instalment_number:
                    rec.instalment_number = line.product_id.instalment_number

    @api.depends('amount_total', 'instalment_number')
    def compute_amount_to_pay(self):
        for rec in self:
            rec.amount_to_pay = rec.amount_total / rec.instalment_number

    def sale_action_sent(self):
        return self.write({'state': 'sent'})

    def write(self, values):

        order = super(SaleOrder, self).write(values)
        subtype_id = self.env['ir.model.data'].xmlid_to_res_id('mt_note')
        if 'signed_by' in values and 'signed_on' in values and 'signature' in values and self.state != 'cancel' and self.state != 'draft' and self.company_id.id == 1:
            message = self.env['mail.message'].sudo().create({
                'subject': 'Contrat signé',
                'model': 'res.partner',
                'res_id': self.partner_id.id,
                'message_type': 'notification',
                'subtype_id': subtype_id,
                'body': 'Contrat signé par ' + str(values['signed_by']),
            })
            _logger.info(self.partner_id.module_id.name)
            _logger.info(self.partner_id.module_id.id)
            for order in self:
                _logger.info("step for order in self: ")
                _logger.info(order.partner_id.step)
                _logger.info(self.partner_id.module_id.name)

                order.partner_id.step = 'finish'
            if not self.partner_id.renounce_request:

                if self.partner_id.phone:
                    phone = str(self.partner_id.phone.replace(' ', ''))[-9:]
                    phone = '+33' + ' ' + phone[0:1] + ' ' + phone[1:3] + ' ' + phone[
                                                                                3:5] + ' ' + phone[
                                                                                             5:7] + ' ' + phone[
                                                                                                          7:]
                    self.partner_id.phone = phone
                url = 'https://www.mcm-academy.fr/my'
                body = "Chere(e) %s félicitation pour votre inscription, votre formation commence dans 14 jours. Si vous souhaitez commencer dès maintenant cliquez sur le lien suivant : %s" % (
                    self.partner_id.name, url)
                if body:
                    composer = self.env['sms.composer'].with_context(
                        default_res_model='res.partner',
                        default_res_ids=self.partner_id.id,
                        default_composition_mode='mass',
                    ).sudo().create({
                        'body': body,
                        'mass_keep_log': True,
                        'mass_force_send': True,
                    })
                    composer.action_send_sms()
                    if self.partner_id.phone:
                        self.partner_id.phone = '0' + str(self.partner_id.phone.replace(' ', ''))[
                                                      -9:]
            else:
                if not self.partner_id.bolt:
                    if self.partner_id.phone:
                        phone = str(self.partner_id.phone.replace(' ', ''))[-9:]
                        phone = '+33' + ' ' + phone[0:1] + ' ' + phone[1:3] + ' ' + phone[
                                                                                    3:5] + ' ' + phone[
                                                                                                 5:7] + ' ' + phone[
                                                                                                              7:]
                        self.partner_id.phone = phone
                    url = 'https://bit.ly/3CZ2HtS'
                    body = "MCM ACADEMY. Afin d'accéder à notre formation vous devez vous inscrire à l'examen auprès de la CMA de votre région via le lien suivant : %s" % (
                        url)
                    if body:
                        composer = self.env['sms.composer'].with_context(
                            default_res_model='res.partner',
                            default_res_id=self.partner_id.id,
                            default_composition_mode='comment',
                        ).sudo().create({
                            'body': body,
                            'mass_keep_log': True,
                            'mass_force_send': False,
                            'use_active_domain': False,
                        })
                        composer.action_send_sms()  # we send sms to client contains link to register in cma.
                        if self.partner_id.phone:
                            self.partner_id.phone = '0' + str(self.partner_id.phone.replace(' ', ''))[
                                                          -9:]
                    mail_compose_message = self.env['mail.compose.message']
                    mail_compose_message.fetch_sendinblue_template()
                    template_id = False
                    if self.partner_id.module_id.name == "Formation Taxi Solo" \
                            or self.partner_id.module_id.name == "Formation VTC Solo" \
                            or self.partner_id.module_id.name == "Repassage formation VTC" \
                            or self.partner_id.module_id.name == "Formation à distance VMDTR" \
                            or self.partner_id.module_id.name == "Repassage formation TAXI":
                        _logger.info(" soloooooooooooooo solo test")

                        template_id = self.env['mail.template'].sudo().search(
                            [('subject', "=", "Inscription examen chambre des métiers"),
                             ('model_id', "=", 'res.partner')],
                            limit=1)  # we send email to client contains link to register in cma. we get the mail template from sendinblue
                        if not template_id:
                            template_id = self.env['mail.template'].sudo().search(
                                [('name', "=", "MCM INSCRIPTION EXAMEN CMA 2023"),
                                 ('model_id', "=", 'res.partner')],
                                limit=1)
                        if template_id:
                            message = self.env['mail.message'].sudo().search(
                                [('subject', "=", "Inscription examen chambre des métiers"),
                                 ('model', "=", 'res.partner'), ('res_id', "=", self.partner_id.id)],
                                limit=1)
                            if not message:  # check if we have already sent the email
                                self.partner_id.with_context(force_send=True).message_post_with_template(
                                    template_id.id,
                                    composition_mode='comment',
                                )  # send the email to client
                            _logger.info("maillllllllll sen solooo t")

                    elif self.partner_id.module_id.name == "Formation passerelle Taxi" or \
                            self.partner_id.module_id.name == "Formation passerelle VTC" \
                            or self.partner_id.module_id.name == "Formation Taxi Premium" or \
                            self.partner_id.module_id.name == "Formation VTC Premium":
                        _logger.info("PremiumPremiumPremiumPremium")
                        _logger.info(self.partner_id.module_id.name)
                        _logger.info(self.partner_id.module_id.id)

                        template_id = self.env['mail.template'].sudo().search(
                            [('subject', "=", "Inscription examen chambre des métiers:PREMIUM"),
                             ('model_id', "=", 'res.partner')],
                            limit=1)  # we send email to client contains link to register in cma. we get the mail template from sendinblue
                        if not template_id:
                            template_id = self.env['mail.template'].sudo().search(
                                [('name', "=", "MCM INSCRIPTION EXAMEN CMA 2023 : PREMIUM"),
                                 ('model_id', "=", 'res.partner')],
                                limit=1)
                        if template_id:
                            message = self.env['mail.message'].sudo().search(
                                [('subject', "=",  "Inscription examen chambre des métiers:PREMIUM"),
                                 ('model', "=", 'res.partner'), ('res_id', "=", self.partner_id.id)],
                                limit=1)
                            if not message:  # check if we have already sent the email
                                self.partner_id.with_context(force_send=True).message_post_with_template(
                                    template_id.id,
                                    composition_mode='comment',
                                )  # send the email to client
                            _logger.info("maillllllllll premuinimmmmm")

        return order
