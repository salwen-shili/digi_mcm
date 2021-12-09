# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
import logging
_logger = logging.getLogger(__name__)


class resPartnerSessions(models.Model):
    _name = "partner.sessions"
    _rec_name = 'session_id'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Historique sessions"

    client_id = fields.Many2one('res.partner', 'Client')
    session_id = fields.Many2one('mcmacademy.session', 'Session', track_visibility='always')
    theoretic = fields.Selection(selection=[
        ('adjourned', 'Ajourné'),
        ('admitted', 'Admis'),
    ], string='Théorique')
    practical = fields.Selection(selection=[
        ('adjourned', 'Ajourné'),
        ('admitted', 'Admis'),
    ], string='Pratique')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    # Add new field pour la justification de report
    justification = fields.Boolean(string="Absence justifié", track_visibility='always')
    paiement = fields.Boolean(string="Changement de ville", track_visibility='always')
    attachment_ids = fields.Many2many('ir.attachment', string="Attachment", required=True)
    autre_raison = fields.Text(track_visibility='always')
    date_exam = fields.Date(related="session_id.date_exam")

    def remove_double_session_same_session(self):
        """ Add this function to remove duplicate
        sessions in partner interface"""
        _logger.info('----------Double sessions in historic sessions-----------')
        sessions = self.env['partner.sessions'].search([])
        duplicate_sessions = []
        for partner_sessions in sessions:
            if partner_sessions.session_id.id and partner_sessions.id not in duplicate_sessions:
                duplicates = self.env['partner.sessions'].search(
                    [('client_id', '=', partner_sessions.client_id.id), ('id', '!=', partner_sessions.id),
                     ('session_id', '=', partner_sessions.session_id.id)])
                for dup in duplicates:
                    duplicate_sessions.append(dup.id)
                    print("duplicate_sessions", duplicate_sessions)
        self.browse(duplicate_sessions).unlink()
