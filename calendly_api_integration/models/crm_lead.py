# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models,_
import calendar
from datetime import date,datetime


class CRM(models.Model):
    _inherit = "crm.lead"

    uuid=fields.Char('UUID')
    start_date=fields.Date('Date de début')
    end_date=fields.Date('Date de fin')
    type_evenement=fields.Char("Type d'évenement")
    partner_ids=fields.Many2many('res.partner','partner_crm_lead_rel', 'lead_id', 'partner_id', string='Stagiaires')
    invitees_limit=fields.Integer('Compteur Limit')
    invitees_active=fields.Integer('Compteur Invitees')
    start_time=fields.Char('heure de début')
    end_time=fields.Char('heure de fin')


    def check_date(self):
        for rec in self:
            if(rec.end_date < date.today()):
                stage = self.env["crm.stage"].search([("name", "like", _("Passé"))])
                if stage:
                    rec.stage_id = stage.id
            if (rec.start_date > date.today()):
                stage = self.env["crm.stage"].search([("name", "like", _("À venir"))])
                if stage:
                    rec.stage_id = stage.id
            if (rec.start_date == date.today()):
                stage = self.env["crm.stage"].search([("name", "like", _("Jour J"))])
                if stage:
                    rec.stage_id = stage.id