# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
#
from odoo import api, fields, models, _
import calendar
from datetime import date, datetime
import logging
_logger = logging.getLogger(__name__)
class Survey(models.Model):
    _inherit = 'survey.user_input'

    @api.model
    def create(self, vals):
        # if 'partner_id' in vals :
            print('vals', vals)
            partner_id=vals['partner_id']
            partner = self.env['res.partner'].sudo().search([("id", "=",partner_id)])
            if partner:
                partner.changestage("Bolt-Prospection", partner)
            return super(Survey, self).create(vals)
    def write(self, vals):
        record = super(Survey, self).write(vals)
        # Si le test "Examen blanc Français" est terminé
        # on change le statut de l'apprenant dans le crm vers "encours de correction"
        if 'state' in vals:
            if vals['state'] == 'done' and self.survey_id.title == 'Examen blanc Français':
                partner = self.env['res.partner'].sudo().search([("id", "=", self.partner_id.id)])
                if partner:
                    self.partner_id.changestage("En cours de correction - Examen Blanc", partner)
                    mail_compose_message = self.env['mail.compose.message']
                    mail_compose_message.fetch_sendinblue_template()
                    """chercher l'email si n'est pas trouvé dans la liste des emails envoyés  on l'envoi"""
                    template_id = self.env['mail.template'].sudo().search(
                        [('subject', "=", "Examen blanc : en cours de correction MCM ACADEMY X BOLT"),
                         ('model_id', "=", 'res.partner')], limit=1)
                    if template_id:
                        message = self.env['mail.message'].sudo().search(
                            [('subject', "=", "Examen blanc : en cours de correction MCM ACADEMY X BOLT"),
                             ('model', "=", 'res.partner'), ('res_id', "=", self.env.user.partner_id.id)],
                            limit=1)
                        if not message:
                            partner.with_context(force_send=True).message_post_with_template(template_id.id,
                                                                                             composition_mode='comment',
                                                                                             )
                    if partner.phone:
                        phone = str(partner.phone.replace(' ', ''))[-9:]
                        phone = '+33' + ' ' + phone[0:1] + ' ' + phone[1:3] + ' ' + phone[3:5] + ' ' + phone[
                                                                                                       5:7] + ' ' + phone[
                                                                                                                    7:]
                        partner.phone = phone
                    body = "Bonjour %s, merci d'avoir complété votre test d'entré, vous recevrez vos résultats dans un délai de 24h hors weekend.MCM ACADEMY" % (
                        partner.name)
                    if body:
                        sms = self.env['mail.message'].sudo().search(
                            [("body", "=", body), ("message_type", "=", 'sms'), ("res_id", "=", partner.id)])
                        if not sms:
                            composer = self.env['sms.composer'].with_context(
                                default_res_model='res.partner',
                                default_res_ids=partner.id,
                                default_composition_mode='mass',
                            ).sudo().create({
                                'body': body,
                                'mass_keep_log': True,
                                'mass_force_send': True,
                            })
                            composer.action_send_sms()  # envoyer un sms de reussite à l'examen
                        if partner.phone:
                            partner.phone = '0' + str(partner.phone.replace(' ', ''))[-9:]
        return record


class MassMailing(models.Model):
        _inherit = "mailing.mailing"
        
class MarketingCampaign(models.Model):
    _inherit = 'marketing.campaign'

 