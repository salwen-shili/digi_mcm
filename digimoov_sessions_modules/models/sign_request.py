# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, _, api, http
from odoo.exceptions import UserError
from werkzeug.urls import url_join
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, formataddr

class InheritSignRequest(models.Model):
    _inherit = "sign.request"

    def send_signature_accesses(self, subject=None, message=None):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for signer in self:
            if not signer.partner_id or not signer.partner_id.email:
                continue
            if not signer.create_uid.email:
                continue
            tpl = self.env.ref('sign.sign_template_mail_request')
            if signer.partner_id.lang:
                tpl = tpl.with_context(lang=signer.partner_id.lang)
            body = tpl.render({
                'record': signer,
                'link': url_join(base_url, "sign/document/mail/%(request_id)s/%(access_token)s" % {'request_id': signer.sign_request_id.id, 'access_token': signer.access_token}),
                'subject': subject,
                'body': message if message != '<p><br></p>' else False,
            }, engine='ir.qweb', minimal_qcontext=True)

            if not signer.signer_email:
                raise UserError(_("Please configure the signer's email address"))
            self.env['sign.request']._message_send_mail(
                body, 'mail.mail_notification_light',
                {'record_name': signer.sign_request_id.reference},
                {'model_description': 'signature', 'company': signer.create_uid.company_id},
                {'email_from': "examen@digimoov.fr",
                 'author_id': "Service examen DIGIMOOV",
                 'email_to': formataddr((signer.partner_id.name, signer.partner_id.email)),
                 'subject': subject},
                force_send=True
            )

    def action_sent(self, subject=None, message=None):
        # Send accesses by email
        self.write({'state': 'sent'})
        for sign_request in self:
            ignored_partners = []
            for request_item in sign_request.request_item_ids:
                if request_item.state != 'draft':
                    ignored_partners.append(request_item.partner_id.id)
            included_request_items = sign_request.request_item_ids.filtered(lambda r: not r.partner_id or r.partner_id.id not in ignored_partners)

            if sign_request.send_signature_accesses(subject, message, ignored_partners=ignored_partners):
                Log = http.request.env['sign.log'].sudo()
                vals = Log._prepare_vals_from_request(sign_request)
                vals['action'] = 'create'
                vals = Log._update_vals_with_http_request(vals)
                Log.create(vals)
                followers = sign_request.message_follower_ids.mapped('partner_id')
                followers -= sign_request.create_uid.partner_id
                followers -= sign_request.request_item_ids.mapped('partner_id')
                if followers:
                    sign_request.send_follower_accesses(followers, subject, message)
                included_request_items.action_sent()
            else:
                sign_request.action_draft()

# class SignRequest(models.Model):
#     _inherit = "sign.request"
#
#     company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
#
#     def action_resend(self):
#         user = self.env.user
#         user.company_id = self.env.company.id
#         self.action_draft()
#         subject = _("%s vous a envoyé un document à remplir et à signer") % (self.company_id.name)
#         self.action_sent(subject=subject)
#
# class SignSendRequest(models.TransientModel):
#     _inherit = 'sign.send.request'
#
#     @api.model
#     def default_get(self, fields):
#         user = self.env.user
#         user.company_id = self.env.company.id
#         res = super(SignSendRequest, self).default_get(fields)
#         res['subject'] =  _("%s vous a envoyé un document à remplir et à signer") % (self.env.company.name)
#         return res