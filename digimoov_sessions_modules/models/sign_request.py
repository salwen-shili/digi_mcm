# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models,_



class SignRequest(models.Model):
    _inherit = "sign.request"

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    def action_resend(self):
        self.action_draft()
        subject = _("%s vous a envoyé un document à remplir et à signer") % (self.company_id.name)
        self.action_sent(subject=subject)
