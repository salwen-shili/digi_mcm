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
    
    def remove_double_session_same_session(self):
        """ Add this function to remove duplicate
        sessions in partner interface"""
        duplicate_sessions = []
        for partner_sessions in self:
            if partner_sessions.session_id.id and partner_sessions.id not in duplicate_sessions:
                duplicates = self.env['partner.sessions'].search([('client_id', '=', partner_sessions.client_id.id), ('id', '!=', partner_sessions.id), ('session_id', '=', partner_sessions.session_id.id)])
                print(duplicates)
                for dup in duplicates:
                    print("dup", dup)
                    duplicate_sessions.append(dup.id)
                    print("duplicate_contacts", duplicate_sessions)
        self.browse(duplicate_sessions).unlink()