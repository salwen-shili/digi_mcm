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

    def write(self, vals):
        record = super(Survey, self).write(vals)
        # Si le test de français est terminé
        # on change le statut de l'apprenant dans le lead vers "encours de correction"
        if 'state' in vals:
            if vals['state'] == 'done' and self.survey_id.title == 'Examen blanc Français':
                partner = self.env['res.partner'].sudo().search([("id", "=", self.partner_id.id)])
                if partner:
                    self.partner_id.changestage("En cours de correction - Examen Blanc", partner)
                    mail_compose_message = self.env['mail.compose.message']
                    mail_compose_message.fetch_sendinblue_template()
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
        return record
 