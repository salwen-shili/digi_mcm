# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class resPartnerSessions(models.Model):
    _name = "partner.sessions"
    _description = "historique sessions"

    client_id= fields.Many2one('res.partner','Client')
    session_id= fields.Many2one('mcmacademy.session','Session')
    theoretic = fields.Selection(selection=[
        ('adjourned', 'Ajourné'),
        ('admitted', 'Admis'),
    ], string='Théorique')
    practical = fields.Selection(selection=[
        ('adjourned', 'Ajourné'),
        ('admitted', 'Admis'),
    ], string='Pratique')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)