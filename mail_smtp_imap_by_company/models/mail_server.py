# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2016-Today Geminate Consultancy Services (<http://geminatecs.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import _, api, fields, models
from odoo import tools
from odoo.addons.base.models.ir_mail_server import MailDeliveryException
import logging

_logger = logging.getLogger(__name__)


class IrMailServer(models.Model):
    _inherit = "ir.mail_server"

    default_company = fields.Many2one('res.company', string="Company")

class MailMail(models.Model):
    _inherit = "mail.mail"

    def send(self, auto_commit=False, raise_exception=False):
        for server_id, batch_ids in self._split_by_server():
            #geminatecs
            smtp_session = None
            #active_company_id = self.env['res.users'].browse(self._context.get('uid') or self.env.user).company_id
            active_company_id = self.env.company
            company_server_id = self.env['ir.mail_server'].search([('default_company', '=', active_company_id.id)])
            server_id = company_server_id and company_server_id.id or server_id
            #geminatecs
            try:
                smtp_session = self.env['ir.mail_server'].connect(mail_server_id=server_id)
            except Exception as exc:
                if raise_exception:
                    # To be consistent and backward compatible with mail_mail.send() raised
                    # exceptions, it is encapsulated into an Odoo MailDeliveryException
                    raise MailDeliveryException(_('Unable to connect to SMTP Server'), exc)
                else:
                    batch = self.browse(batch_ids)
                    batch.write({'state': 'exception', 'failure_reason': exc})
                    batch._postprocess_sent_message(success_pids=[], failure_type="SMTP")
            else:
                self.browse(batch_ids)._send(
                    auto_commit=auto_commit,
                    raise_exception=raise_exception,
                    smtp_session=smtp_session)
                _logger.info(
                    'Sent batch %s emails via mail server ID #%s',
                    len(batch_ids), server_id)
            finally:
                if smtp_session:
                    smtp_session.quit()

class FetchmailServer(models.Model):
    _inherit = 'fetchmail.server'

    default_company = fields.Many2one('res.company', string="Company")

class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def _message_add_suggested_recipient(self, result, partner=None, email=None, reason=''):
        """ Called by _message_get_suggested_recipients, to add a suggested
            recipient in the result dictionary. The form is :
                partner_id, partner_name<partner_email> or partner_name, reason """
        self.ensure_one()
        if email and not partner:
            # get partner info from email
            partner_info = self._message_partner_info_from_emails([email])[0]
            if partner_info.get('partner_id'):
                partner = self.env['res.partner'].sudo().browse([partner_info['partner_id']])[0]
        if partner : #check if partner
            if email and email in [val[1] for val in result[self.ids[0]]]:  # already existing email -> skip
                return result
            if partner and partner in self.message_partner_ids:  # recipient already in the followers -> skip
                return result
            if partner and partner.id in [val[0] for val in result[self.ids[0]]]:  # already existing partner ID -> skip
                return result
            if partner and partner.email:  # complete profile: id, name <email>
                result[self.ids[0]].append((partner.id, '%s<%s>' % (partner.name, partner.email), reason))
            elif partner:  # incomplete profile: id, name
                result[self.ids[0]].append((partner.id, '%s' % (partner.name), reason))
            else:  # unknown partner, we are probably managing an email address
                result[self.ids[0]].append((False, email, reason))
        return result
    # @api.model
    # def _message_route_process(self, message, message_dict, routes):
    #     self = self.with_context(attachments_mime_plainxml=True) # import XML attachments as text
    #     # postpone setting message_dict.partner_ids after message_post, to avoid double notifications
    #     original_partner_ids = message_dict.pop('partner_ids', [])
    #     thread_id = False
    #
    #     for model, thread_id, custom_values, user_id, alias in routes or ():
    #         subtype_id = False
    #         Model = self.env[model].with_context(mail_create_nosubscribe=True, mail_create_nolog=True)
    #         if not (thread_id and hasattr(Model, 'message_update') or hasattr(Model, 'message_new')):
    #             raise ValueError(
    #                 "Undeliverable mail with Message-Id %s, model %s does not accept incoming emails" %
    #                 (message_dict['message_id'], model)
    #             )
    #
    #         # disabled subscriptions during message_new/update to avoid having the system user running the
    #         # email gateway become a follower of all inbound messages
    #         ModelCtx = Model.with_user(user_id).sudo()
    #         if thread_id and hasattr(ModelCtx, 'message_update'):
    #             thread = ModelCtx.browse(thread_id)
    #             thread.message_update(message_dict)
    #         else:
    #             # if a new thread is created, parent is irrelevant
    #             message_dict.pop('parent_id', None)
    #             thread = ModelCtx.message_new(message_dict, custom_values)
    #             #geminatecs
    #             print('thread:',thread)
    #             print('custom_values: ',custom_values)
    #             thread.sudo().write({'company_id': alias and alias.alias_domain.company_id.id or self.env.company.id})
    #             #geminatecs
    #
    #             thread_id = thread.id
    #             subtype_id = thread._creation_subtype().id
    #
    #         # replies to internal message are considered as notes, but parent message
    #         # author is added in recipients to ensure he is notified of a private answer
    #         parent_message = False
    #         if message_dict.get('parent_id'):
    #             parent_message = self.env['mail.message'].sudo().browse(message_dict['parent_id'])
    #         partner_ids = []
    #         if not subtype_id:
    #             if message_dict.pop('internal', False):
    #                 subtype_id = self.env['ir.model.data'].xmlid_to_res_id('mail.mt_note')
    #                 if parent_message and parent_message.author_id:
    #                     partner_ids = [parent_message.author_id.id]
    #             else:
    #                 subtype_id = self.env['ir.model.data'].xmlid_to_res_id('mail.mt_comment')
    #
    #         post_params = dict(subtype_id=subtype_id, partner_ids=partner_ids, **message_dict)
    #         # remove computational values not stored on mail.message and avoid warnings when creating it
    #         for x in ('from', 'to', 'cc', 'recipients', 'references', 'in_reply_to', 'bounced_email', 'bounced_message', 'bounced_msg_id', 'bounced_partner'):
    #             post_params.pop(x, None)
    #         new_msg = False
    #         if thread._name == 'mail.thread':  # message with parent_id not linked to record
    #             new_msg = thread.message_notify(**post_params)
    #         else:
    #             new_msg = thread.message_post(**post_params)
    #
    #         if new_msg and original_partner_ids:
    #             # postponed after message_post, because this is an external message and we don't want to create
    #             # duplicate emails due to notifications
    #             new_msg.write({'partner_ids': original_partner_ids})
    #     return thread_id
