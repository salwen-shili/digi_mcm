# -*- coding: utf-8 -*-

from odoo import models, fields, api

class search(models.Model):
    _inherit = 'res.partner'

    sessions_count = fields.Integer(compute='compute_sessions_count')
    historic_sessions_ids=fields.One2many('partner.sessions','client_id','Historique des sessions')
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
