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
    def write(self, vals):
        record = super(Survey, self).write(vals)
        # Si le test de français est terminé
        # on change le statut de l'apprenant dans le lead vers "encours de correction"
        if 'state' in vals:
            if vals['state'] == 'done' and self.survey_id.title=='Examen blanc Français':
                partner =self.env['res.partner'].sudo().search([("id","=",self.partner_id.id)])
                if partner:
                    self.partner_id.change_stage_lead("En cours de correction - Examen Blanc", partner)
        return record 