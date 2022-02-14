# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time
from odoo import api, fields, models,_

import logging
_logger = logging.getLogger(__name__)

class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"

    quizz_corrected = fields.Boolean(default=False,string="Examen corrigé")
    def update_partner_exam_result(self):
        for record in self:
            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'survey.user_input.wizard',
                'target': 'new',
                'context': {
                    'default_survey_user_input_id': self.ids[0],
                    'default_partner_id': record.partner_id.id,
                    'default_score': record.quizz_score,
                },
            }


class SurveyUserInputWizard(models.TransientModel):
    _name = 'survey.user_input.wizard'
    _description = 'confirm corrected exam'

    survey_user_input_id = fields.Many2one('survey.user_input', string="Examen")
    partner_id=fields.Many2one('res.partner',string="Client")
    score = fields.Float('Score (%)')

    def action_validate_correction_exam(self):
        for rec in self:
            rec.survey_user_input_id.quizz_corrected = True
            rec.partner_id.note_exam  = str(rec.score)
            mail_compose_message = self.env['mail.compose.message']
            mail_compose_message.fetch_sendinblue_template()
            if rec.score < 40:
                template_id = self.env['mail.template'].sudo().search(
                    [('subject', "=", "Résultat examen blanc : Ajourné MCM ACADEMY X BOLT"),
                     ('model_id', "=", 'res.partner')], limit=1)
                if template_id:
                    message = self.env['mail.message'].sudo().search(
                        [('subject', "=", "Résultat examen blanc : Ajourné MCM ACADEMY X BOLT"),
                         ('model', "=", 'res.partner'), ('res_id', "=", self.env.user.partner_id.id)],
                        limit=1)
                    if not message:
                        partner.with_context(force_send=True).message_post_with_template(template_id.id,
                                                                                         composition_mode='comment',
                                                                                         )
            else:
                mail_compose_message = self.env['mail.compose.message']
                mail_compose_message.fetch_sendinblue_template()
                template_id = self.env['mail.template'].sudo().search(
                    [('subject', "=", "Inscription Examen VTC - MCM ACADEMY X BOLT"),
                     ('model_id', "=", 'res.partner')], limit=1)
                user = self.env['res.users'].sudo().search(
                    [('partner_id', "=", rec.partner_id.id)], limit=1)
                if template_id:
                    template_id.attachment_ids = False
                    if user:
                        template_id.attachment_ids = False
                        attachment = self.env['ir.attachment'].search(
                            [("name", "=", "certification.pdf"), ("create_uid", "=", user.id)],
                            limit=1)
                        if attachment:
                            template_id.sudo().write({'attachment_ids': [(6, 0, attachment.ids)]})
                    message = self.env['mail.message'].sudo().search(
                        [('subject', "=", "Inscription Examen VTC - MCM ACADEMY X BOLT"),
                         ('model', "=", 'res.partner'), ('res_id', "=", self.env.user.partner_id.id)],
                        limit=1)
                    if not message:
                        rec.partner_id.with_context(force_send=True).message_post_with_template(template_id.id,
                                                                                         composition_mode='comment',
                                                                                         )
                

