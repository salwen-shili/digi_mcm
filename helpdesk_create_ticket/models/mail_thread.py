# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import _, api, exceptions, fields, models, tools, registry, SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def message_notify(self, *,
                       partner_ids=False, parent_id=False, model=False, res_id=False,
                       author_id=None, email_from=None, body='', subject=False, **kwargs):
        """ Shortcut allowing to notify partners of messages that shouldn't be
        displayed on a document. It pushes notifications on inbox or by email depending
        on the user configuration, like other notifications. """
        if self:
            self.ensure_one()
        # split message additional values from notify additional values
        print('custom call message_notify : %s ,%s, %s, %s' % (self._name, res_id, subject, kwargs))
        msg_kwargs = dict((key, val) for key, val in kwargs.items() if key in self.env['mail.message']._fields)
        notif_kwargs = dict((key, val) for key, val in kwargs.items() if key not in msg_kwargs)

        author_info = self._message_compute_author(author_id, email_from, raise_exception=True)
        author_id, email_from = author_info['author_id'], author_info['email_from']

        if not partner_ids:
            _logger.warning('Message notify called without recipient_ids, skipping')
            return self.env['mail.message']

        if not (model and res_id):  # both value should be set or none should be set (record)
            model = False
            res_id = False

        MailThread = self.env['mail.thread']
        values = {
            'parent_id': parent_id,
            'model': self._name if self else False,
            'res_id': self.id if self else False,
            'message_type': 'user_notification',
            'subject': subject,
            'body': body,
            'author_id': author_id,
            'email_from': email_from,
            'partner_ids': partner_ids,
            'subtype_id': self.env['ir.model.data'].xmlid_to_res_id('mail.mt_note'),
            'record_name': False,
            'reply_to': MailThread._notify_get_reply_to(default=email_from, records=None)[False],
            'message_id': tools.generate_tracking_message_id('message-notify'),
        }
        values.update(msg_kwargs)

        new_message = MailThread._message_create(values)
        if new_message.model in ['helpdesk.ticket',
                                 'sale.order'] and new_message.message_type == 'user_notification':  # check if odoo send mail of assignment for helpdesk and sale order models
            return new_message  # don't send mail of assignment for new tickets and new sale orders
        else:
            MailThread._notify_thread(new_message, values, **notif_kwargs)
        return new_message

    @api.model
    def _notify_prepare_template_context(self, message, msg_vals, model_description=False, mail_auto_delete=True):
        # compute send user and its related signature
        signature = ''
        user = self.env.user
        author = message.env['res.partner'].browse(msg_vals.get('author_id')) if msg_vals else message.author_id
        model = msg_vals.get('model') if msg_vals else message.model
        add_sign = msg_vals.get('add_sign') if msg_vals else message.add_sign
        subtype_id = msg_vals.get('subtype_id') if msg_vals else message.subtype_id.id
        message_id = message.id
        record_name = msg_vals.get('record_name') if msg_vals else message.record_name
        author_user = user if user.partner_id == author else author.user_ids[0] if author and author.user_ids else False
        # trying to use user (self.env.user) instead of browing user_ids if he is the author will give a sudo user,
        # improving access performances and cache usage.
        if author_user:
            user = author_user
            if add_sign:
                signature = user.signature
        else:
            if add_sign:
                signature = "<p>-- <br/>%s</p>" % author.name

        company = self.company_id.sudo() if self and 'company_id' in self else user.company_id
        if company.website:
            website_url = 'http://%s' % company.website if not company.website.lower().startswith(
                ('http:', 'https:')) else company.website
        else:
            website_url = False

        # Retrieve the language in which the template was rendered, in order to render the custom
        # layout in the same language.
        lang = self.env.context.get('lang')
        if {'default_template_id', 'default_model', 'default_res_id'} <= self.env.context.keys():
            template = self.env['mail.template'].browse(self.env.context['default_template_id'])
            if template and template.lang:
                lang = template._render_template(template.lang, self.env.context['default_model'],
                                                 self.env.context['default_res_id'])

        if not model_description and model:
            model_description = self.env['ir.model'].with_context(lang=lang)._get(model).display_name

        tracking = []
        if msg_vals.get('tracking_value_ids', True) if msg_vals else bool(self):  # could be tracking
            for tracking_value in self.env['mail.tracking.value'].sudo().search([('mail_message_id', '=', message.id)]):
                groups = tracking_value.field_groups
                if not groups or self.env.is_superuser() or self.user_has_groups(groups):
                    tracking.append((tracking_value.field_desc,
                                     tracking_value.get_old_display_value()[0],
                                     tracking_value.get_new_display_value()[0]))

        is_discussion = subtype_id == self.env['ir.model.data'].xmlid_to_res_id('mail.mt_comment')
        company_id = self.company_id.sudo() if self and 'company_id' in self else False
        if company_id:  # check company of active record(sale order,helpdesk ticket,partner...etc)
            user_signature = self.env['res.user.signature'].sudo().search(
                [('user_id', "=", user.id), ('company_id', "=", company_id.id)],
                limit=1)  # check if the mail sender has a signature related to the company already checked before
            if user_signature and user_signature.signature:
                signature = user_signature.signature  # change the signature of mail if user signature related to the company founded
        return {
            'message': message,
            'signature': signature,
            'website_url': website_url,
            'company': company,
            'model_description': model_description,
            'record': self,
            'record_name': record_name,
            'tracking_values': tracking,
            'is_discussion': is_discussion,
            'subtype': message.subtype_id,
            'lang': lang,
        }

    def _message_compute_author(self, author_id=None, email_from=None, raise_exception=True):
        """ Tool method computing author information for messages. Purpose is
        to ensure maximum coherence between author / current user / email_from
        when sending emails. """
        res = super(MailThread, self)._message_compute_author(author_id, email_from,
                                                              raise_exception)  # inherit function of compute author of email ( email sender )
        author = res['author_id']
        email = res['email_from']
        user = self.env.user
        company_id = self.company_id.sudo() if self and 'company_id' in self else False
        if company_id:  # check company of active record(sale order,helpdesk ticket,partner...etc)
            user_signature = self.env['res.user.signature'].sudo().search(
                [('user_id', "=", user.id), ('company_id', "=", company_id.id)],
                limit=1)  # check if the mail sender has a email from related to the company already checked before
            if user_signature and user_signature.email_from and user.partner_id.email in email:
                res['email_from'] = tools.formataddr(
                    (user.partner_id.name or u"False", user_signature.email_from or u"False"))  # change the sender mail
        return res
