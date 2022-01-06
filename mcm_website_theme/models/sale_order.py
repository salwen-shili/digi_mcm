# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    instalment_number = fields.Integer("Tranches", compute='get_instalment_number')
    amount_to_pay = fields.Monetary('Montant à Payer', compute='compute_amount_to_pay')
    instalment = fields.Boolean(default=False)
    conditions = fields.Boolean(default=False)
    failures = fields.Boolean(default=False)
    accompagnement = fields.Boolean(default=False)
    #Add fields of questionnaire in the sale order. These fields will be deleted next.
    besoins_particuliers = fields.Selection([('Oui','Oui'),('Non','Non')])
    type_besoins = fields.Text()
    raison_choix = fields.Selection([
        ('En chômage', 'Je suis en chômage et je suis en recherche d\'emploi'),
        ('Monter sa propre entreprise', 'Je veux monter ma propre entreprise et être indépendant'),
        ('Passionné par le métier', 'Je suis passionné par le métier de chauffeur'),
        ('En reconversion professionnelle','Je suis en reconversion professionnelle pour être chauffeur'),
        ('Mettre à jour ses connaissances','Pour mettre à jour mes connaissances et compétences du métier'),
        ('Arrondir ses fins du mois','Pour arrondir mes fins du mois')])
    support_formation = fields.Selection([
        ('Vidéos préenregistrées', 'En visualisant des vidéos préenregistrées '),
        ('Documents en ligne', 'En lisant des documents PDF en ligne'),
        ('En mode audio', 'En écoutant les cours en mode audio'),
        ('Alternance entre tous ces modes', 'En alternant entre tous ces modes d’apprentissage')])
    attentes = fields.Text()


    @ api.depends('amount_total', 'pricelist_id')
    def get_instalment_number(self):
        for rec in self:
            if (rec.amount_total >= 1000 and rec.company_id.id == 1):
                rec.instalment_number = 3
            elif (rec.amount_total < 1000 and rec.company_id.id == 1):
                rec.instalment_number = 1
            elif (rec.company_id.id == 2):
                default_code = False
                for line in rec.order_line:
                    default_code = line.product_id.default_code
                if default_code == 'basique':
                    rec.instalment_number = 1
                elif default_code == 'avancee':
                    rec.instalment_number = 2
                elif default_code == 'premium':
                    rec.instalment_number = 3
                else:
                    rec.instalment_number = 1
            else:
                rec.instalment_number = 1
            print('instalment number')
            print(rec.instalment_number)

    @api.depends('amount_total', 'instalment_number')
    def compute_amount_to_pay(self):
        for rec in self:
            rec.amount_to_pay = rec.amount_total / rec.instalment_number

    def sale_action_sent(self):
        return self.write({'state': 'sent'})

    def write(self, values):
        order=super(SaleOrder,self).write(values)
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
            for order in self:
                order.partner_id.step = 'finish'
            if not self.partner_id.renounce_request:
                if self.partner_id.phone:
                    phone = str(self.partner_id.phone.replace(' ', ''))[-9:]
                    phone = '+33' + ' ' + phone[0:1] + ' ' + phone[1:3] + ' ' + phone[
                                                                                3:5] + ' ' + phone[
                                                                                             5:7] + ' ' + phone[
                                                                                                          7:]
                    self.partner_id.phone = phone
                url = str(self.partner_id.get_base_url()) + '/my'
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
                if self.partner_id.phone:
                    phone = str(self.partner_id.phone.replace(' ', ''))[-9:]
                    phone = '+33' + ' ' + phone[0:1] + ' ' + phone[1:3] + ' ' + phone[
                                                                                3:5] + ' ' + phone[
                                                                                             5:7] + ' ' + phone[
                                                                                                          7:]
                    self.partner_id.phone = phone
                url = 'https://formation.mcm-academy.fr/register'
                body = "Chere(e) %s : félicitation pour votre inscription, vous avez été invité par MCM ACADEMY à commencer votre formation via ce lien : %s . vous devez créer un compte avec les mêmes identifiants que MCM ACADEMY" % (
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
        return order