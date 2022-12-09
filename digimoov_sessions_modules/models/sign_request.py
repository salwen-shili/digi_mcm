# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
import time
import logging

from odoo import fields, models, _, api, http
from odoo.exceptions import UserError
from werkzeug.urls import url_join
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, formataddr

_logger = logging.getLogger(__name__)


class InheritSignRequest(models.Model):
    _inherit = "sign.request"

    def send_completed_document(self):
        """ Inherit this function to change name of file Activity logs to Détails"""
        self.ensure_one()
        if len(self.request_item_ids) <= 0 or self.state != 'signed':
            return False

        if not self.completed_document:
            self.generate_completed_document()

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        attachment = self.env['ir.attachment'].create({
            'name': "%s.pdf" % self.reference,
            'datas': self.completed_document,
            'type': 'binary',
            'res_model': self._name,
            'res_id': self.id,
        })
        report_action = self.env.ref('sign.action_sign_request_print_logs')
        # print the report with the public user in a sudoed env
        # public user because we don't want groups to pollute the result
        # (e.g. if the current user has the group Sign Manager,
        # some private information will be sent to *all* signers)
        # sudoed env because we have checked access higher up the stack
        public_user = self.env.ref('base.public_user', raise_if_not_found=False)
        if not public_user:
            # public user was deleted, fallback to avoid crash (info may leak)
            public_user = self.env.user
        pdf_content, __ = report_action.with_user(public_user).sudo().render_qweb_pdf(self.id)
        attachment_log = self.env['ir.attachment'].create({
            'name': "Détails - %s.pdf" % time.strftime('%Y-%m-%d - %H:%M:%S'),
            'datas': base64.b64encode(pdf_content),
            'type': 'binary',
            'res_model': self._name,
            'res_id': self.id,
        })
        # add code to get contact with email examen@digimoov.fr
        service_examen = self.env['res.partner'].sudo().search(
            [('email', '=', 'examen@digimoov.fr'), ('company_id', "=", 2),
             ('display_name', '=', "Service examen DIGIMOOV")],
            limit=1)
        for signer in self.request_item_ids:
            if not signer.signer_email:
                continue

            tpl = self.env.ref('sign.sign_template_mail_completed')
            body = tpl.render({
                'record': self,
                'link': url_join(base_url, 'sign/document/%s/%s' % (self.id, signer.access_token)),
                'subject': '%s signed' % self.reference,
                'body': False,
            }, engine='ir.qweb', minimal_qcontext=True)

            if not self.create_uid.email:
                raise UserError(_("Please configure the sender's email address"))
            if not signer.signer_email:
                raise UserError(_("Please configure the signer's email address"))
            if signer.signer_email != "examen@digimoov.fr":
                self.env['sign.request'].sudo()._message_send_mail(
                    body, 'mail.mail_notification_light',
                    {'record_name': self.reference},
                    {'model_description': 'signature', 'company': self.create_uid.company_id},
                    {'email_from': service_examen.email,
                     'author_id': service_examen.id,
                     'email_to': formataddr((signer.partner_id.name, signer.signer_email)),
                     'subject': _('%s has been signed') % self.reference,
                     'attachment_ids': [(4, attachment.id), (4, attachment_log.id)]},
                    force_send=True
                )
            else:
                self.env['sign.request'].sudo()._message_send_mail(
                    body, 'mail.mail_notification_light',
                    {'record_name': self.reference},
                    {'model_description': 'signature', 'company': self.create_uid.company_id},
                    {'email_from': formataddr((self.create_uid.name, self.create_uid.email)),
                     'author_id': self.create_uid.partner_id.id,
                     'email_to': formataddr((signer.partner_id.name, signer.signer_email)),
                     'subject': _('%s has been signed') % self.reference,
                     'attachment_ids': [(4, attachment.id), (4, attachment_log.id)]},
                    force_send=True
                )

        tpl = self.env.ref('sign.sign_template_mail_completed')
        body = tpl.render({
            'record': self,
            'link': url_join(base_url, 'sign/document/%s/%s' % (self.id, self.access_token)),
            'subject': '%s signed' % self.reference,
            'body': '',
        }, engine='ir.qweb', minimal_qcontext=True)

        for follower in self.mapped('message_follower_ids.partner_id') - self.request_item_ids.mapped('partner_id'):
            if not follower.email:
                continue
            if not self.create_uid.email:
                raise UserError(_("Please configure the sender's email address"))
            if follower.email != "examen@digimoov.fr":
                self.env['sign.request'].sudo()._message_send_mail(
                    body, 'mail.mail_notification_light',
                    {'record_name': self.reference},
                    {'model_description': 'signature', 'company': self.create_uid.company_id},
                    {'email_from': service_examen.email,
                     'author_id': service_examen.id,
                     'email_to': formataddr((follower.name, follower.email)),
                     'subject': _('%s has been signed') % self.reference}
                )
            else:
                self.env['sign.request'].sudo()._message_send_mail(
                    body, 'mail.mail_notification_light',
                    {'record_name': self.reference},
                    {'model_description': 'signature', 'company': self.create_uid.company_id},
                    {'email_from': formataddr((self.create_uid.name, self.create_uid.email)),
                     'author_id': self.create_uid.partner_id.id,
                     'email_to': formataddr((follower.name, follower.email)),
                     'subject': _('%s has been signed') % self.reference}
                )

        return True


class InheritMcmacademySession(models.Model):
    _inherit = "mcmacademy.session"

    def send_cerfa_to_sign(self):
        """ 1- Génèrer un rapport cerfa
            2- Ajouter template dans module signature"""

        partner = self.env['res.partner'].sudo().search(
            [('email', '=', 'tmejri@digimoov.fr')], limit=1)
        if partner:
            # Attach report to the Bank statement
            content, content_type = self.env.ref('partner_exam.report_cerfa').render_qweb_pdf(
                partner.id)
            cerfa = self.env['ir.attachment'].create({
                'name': "Takwa cerfa 2022 Test 1",
                'type': 'binary',
                'datas': base64.encodestring(content),
                'res_model': partner._name,
                'res_id': partner.id
            })
            _logger.info('----send_cerfa_to_sign ---- %s' % cerfa)

            template = self.env['sign.template'].create({
                'name': "Cerfa Test with signature 2",
                'redirect_url': str("https://form.jotform.com/222334146537352"),
                'attachment_id': cerfa.id,
                'datas': cerfa.datas,
                'sign_item_ids': False
            })
            _logger.info('----Create_template_to_sign ---- %s' % template)
            sign_item_role_id = self.env['sign.item.role'].sudo().search(
                [('name', '=', "Client")], limit=1).id
            sign_item_type_id = self.env['sign.item.type'].sudo().search(
                [('name', '=', "Signature")], limit=1).id
            signature = self.env['sign.item'].create({
                'type_id': sign_item_type_id,
                'required': True,
                'responsible_id': sign_item_role_id,
                'template_id': template.id,
                'page': 3,
                'posX': float(0.210),
                'posY': float(0.609),
                'width': float(0.200),
                'height': float(0.050),
            })
            template.sudo().update({'sign_item_ids': signature.id})


class InheritSignRequestItem(models.Model):
    _inherit = "sign.request.item"

    def send_signature_accesses(self, subject=None, message=None):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for signer in self:
            body = {
                'record': signer,
                'link': url_join(base_url, "sign/document/mail/%(request_id)s/%(access_token)s" % {
                    'request_id': signer.sign_request_id.id, 'access_token': signer.access_token}),
                'subject': subject,
                'body': message if message != '<p><br></p>' else False,
            }
            # Call value from dict 'body'
            link = body['link']

            if not signer.partner_id or not signer.partner_id.email:
                continue
            if not signer.create_uid.email:
                continue
            # Template proces verbal
            if "Procès verbal" in str(self.sign_request_id.reference):
                report_proces_verbal = self.env.ref('__export__.mail_template_868_33f1ceea')
                # Remove '\n' from Template
                body_remove_n = report_proces_verbal.body_html.replace('\n', '')
                # Replace le code HTML link with body['link']
                body_replace_link = body_remove_n.replace('lien_signature', link)
                body = body_replace_link
            # Template Cerfa
            elif "CERFA" in str(self.sign_request_id.reference):
                report_cerfa = self.env.ref('__export__.mail_template_870_ed45b4c4')
                # Remove '\n' from Template
                body_remove_n = report_cerfa.body_html.replace('\n', '')
                # Replace le code HTML link with body['link']
                body_replace_link = body_remove_n.replace('lien_signature', link)
                body = body_replace_link
            # Template Digimoov - Rapport de session surveillant session examen
            elif "SESSION D’EXAMEN" in str(self.sign_request_id.reference):
                report_session_examen = self.env.ref('__export__.mail_template_819_233cd54e')
                # Remove '\n' from Template
                body_remove_n = report_session_examen.body_html.replace('\n', '')
                # Replace le code HTML link with body['link']
                body_replace_link = body_remove_n.replace('lien_signature', link)
                body = body_replace_link
            # Template génèrale
            elif "CERFA" not in str(self.sign_request_id.reference) and "Procès verbal" not in str(
                    self.sign_request_id.reference) and "SESSION D’EXAMEN" not in str(self.sign_request_id.reference):
                general_template = self.env.ref('__export__.mail_template_783_c1e659a3')
                # Remove '\n' from Template
                body_remove_n = general_template.body_html.replace('\n', '')
                # Replace le code HTML link with body['link']
                body_replace_link = body_remove_n.replace('lien_signature', link)
                body = body_replace_link
            if not signer.signer_email:
                raise UserError(_("Please configure the signer's email address"))
            # Search contact mail with examen@digimoov.fr
            if signer.partner_id.email != "examen@digimoov.fr":
                author_digimoov = self.env['res.partner'].sudo().search(
                    [('email', '=', 'examen@digimoov.fr'), ('company_id', "=", 2),
                     ('display_name', '=', "Service examen DIGIMOOV")],
                    limit=1)
                self.env['sign.request'].sudo()._message_send_mail(
                    body, 'mail.mail_notification_light',
                    {'record_name': signer.sign_request_id.reference},
                    {'model_description': 'signature', 'company': signer.create_uid.company_id},
                    {'email_from': author_digimoov.email,
                     'author_id': author_digimoov.id,
                     'email_to': formataddr((signer.partner_id.name, signer.partner_id.email)),
                     'subject': subject},
                    force_send=True
                )
            else:  # code de odoo
                if not signer.signer_email:
                    raise UserError(_("Please configure the signer's email address"))
                self.env['sign.request'].sudo()._message_send_mail(
                    body, 'mail.mail_notification_light',
                    {'record_name': signer.sign_request_id.reference},
                    {'model_description': 'signature', 'company': signer.create_uid.company_id},
                    {'email_from': formataddr((signer.create_uid.name, signer.create_uid.email)),
                     'author_id': signer.create_uid.partner_id.id,
                     'email_to': formataddr((signer.partner_id.name, signer.partner_id.email)),
                     'subject': subject},
                    force_send=True
                )

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
