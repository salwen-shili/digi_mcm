# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models,_,api



class SignRequest(models.Model):
    _inherit = "sign.request"

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    def action_resend(self):
        user = self.env.user
        user.company_id = self.env.company.id
        self.action_draft()
        subject = _("%s vous a envoyé un document à remplir et à signer") % (self.company_id.name)
        self.action_sent(subject=subject)

class SignSendRequest(models.TransientModel):
    _inherit = 'sign.send.request'

    @api.model
    def default_get(self, fields):
        user = self.env.user
        user.company_id = self.env.company.id
        res = super(SignSendRequest, self).default_get(fields)
        res['subject'] =  _("%s vous a envoyé un document à remplir et à signer") % (self.env.company.name)
        return res