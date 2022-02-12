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
        for rec in self:
            rec.quizz_corrected = True
            rec.partner_id.note_exam = str(rec.quizz_score)
            if rec.quizz_score < 40 :
                print('email echec')
            else:
                print('email success')