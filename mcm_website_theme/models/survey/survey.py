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
            if rec.score < 40 :
                print('envoi mail echec')
            else:
                print("envoi mail sucess")

