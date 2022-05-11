# -*- coding: utf-8 -*-

from odoo import models, fields, api


class search(models.Model):
    _inherit = 'res.partner'

    sessions_count = fields.Integer(compute='compute_sessions_count')
    historic_sessions_ids = fields.One2many('partner.sessions', 'client_id', 'Historique des sessions')

    def compute_sessions_count(self):
        for record in self:
            record.sessions_count = self.env['partner.sessions'].search_count(
                [('client_id', 'child_of', self.id)])

    def get_sessions_history(self):
        self.ensure_one()
        return {
            "name": self.name,
            "view_type": "form",
            "view_mode": "tree,form",
            "res_model": "partner.sessions",
            "type": "ir.actions.act_window",
            "domain": [("client_id", "child_of", self.id)],
            "context": self.env.context,
        }

    def write(self, vals):
        """ Ajouter la partie statistique de 360 dans l'interface de l'historique de session """
        sessions = super(search, self).write(vals)
        last_session_line = self.env['partner.sessions'].search(
            [('client_id', '=', self.id), ('session_id', '=', self.mcm_session_id.id)], limit=1)
        if 'temps_minute' in vals or 'date_creation' in vals or 'reactions' in vals or 'averageScore' in vals or 'last_login' in vals or 'mode_de_financement' in vals or 'etat_financement_cpf_cb' in vals or 'numero_cpf' in vals:
            last_session_line.totalTimeSpentInMinutes = self.temps_minute
            last_session_line.date_creation = self.date_creation
            last_session_line.reactions = self.reactions
            last_session_line.average_score = self.averageScore
            last_session_line.last_login = self.last_login
            last_session_line.folder_number_cpf = self.numero_cpf
            last_session_line.funding_method = dict(self._fields['mode_de_financement'].selection).get(
                    self.mode_de_financement)
            last_session_line.stat_funding = dict(self._fields['etat_financement_cpf_cb'].selection).get(
                    self.etat_financement_cpf_cb)
            print("self.historic_sessions_ids.totalTimeSpentInMinutes", last_session_line.totalTimeSpentInMinutes)
        return sessions
