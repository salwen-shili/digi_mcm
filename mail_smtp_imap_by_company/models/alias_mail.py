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
import base64
import datetime
import dateutil
import email
import hashlib
import hmac
import lxml
import logging
import pytz
import re
import socket
import time
import threading

from collections import namedtuple
from email.message import Message
from email.utils import formataddr
from lxml import etree
from werkzeug import url_encode
from werkzeug import urls
from odoo.tools import remove_accents
from odoo import _, api, exceptions, fields, models, tools, registry, SUPERUSER_ID
from odoo.osv import expression

from odoo.tools import pycompat, ustr
from odoo.tools.misc import clean_context, split_every
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)

class MailThreadInherit(models.AbstractModel):

    _inherit = 'mail.thread'

    @api.model
    def message_route(self, message, message_dict, model=None, thread_id=None, custom_values=None):
        if not isinstance(message, Message):
            raise TypeError('message must be an email.message.Message at this point')
        catchall_alias = self.env['ir.config_parameter'].sudo().get_param("mail.catchall.alias")
        bounce_alias = self.env['ir.config_parameter'].sudo().get_param("mail.bounce.alias") #get no reply boucing alias from config parameter created on ovh mailing
        bounce_domain = self.env['ir.config_parameter'].sudo().get_param("mail.catchall.domain") #get no reply boucing alias from config parameter created on ovh mailing
        fallback_model = model

        # get email.message.Message variables for future processing
        local_hostname = socket.gethostname()
        message_id = message_dict['message_id']

        # compute references to find if message is a reply to an existing thread
        thread_references = message_dict['references'] or message_dict['in_reply_to']
        msg_references = [ref for ref in tools.mail_header_msgid_re.findall(thread_references) if 'reply_to' not in ref]
        mail_messages = self.env['mail.message'].sudo().search([('message_id', 'in', msg_references)], limit=1,
                                                               order='id desc, message_id')
        _logger.info('message_route mail_messages : %s' %(str(mail_messages)))
        is_a_reply = bool(mail_messages)
        reply_model, reply_thread_id = mail_messages.model, mail_messages.res_id

        # author and recipients
        email_from = message_dict['email_from']
        email_from_localpart = (tools.email_split(email_from) or [''])[0].split('@', 1)[0].lower()
        email_to = message_dict['to']
        email_to_localpart = (tools.email_split(email_to) or [''])[0].split('@', 1)[0].lower()
        _logger.info('mail smtp imap by company : Routing mail from %s to %s with Message-Id %s: direct write to catchall, bounce',
                     message_dict['email_from'], message_dict['to'], str(message_dict))
        # Delivered-To is a safe bet in most modern MTAs, but we have to fallback on To + Cc values
        # for all the odd MTAs out there, as there is no standard header for the envelope's `rcpt_to` value.
        rcpt_tos_localparts = [e.split('@')[0].lower() for e in tools.email_split(message_dict['recipients'])]
        email_to_alias_domain_list = [e.split('@')[1].lower() for e in tools.email_split(message_dict['recipients'])]

        # 0. Handle bounce: verify whether this is a bounced email and use it to collect bounce data and update notifications for customers
        #    Bounce regex: typical form of bounce is bounce_alias+128-crm.lead-34@domain
        #       group(1) = the mail ID; group(2) = the model (if any); group(3) = the record ID 
        #    Bounce message (not alias)
        #       See http://datatracker.ietf.org/doc/rfc3462/?include_text=1
        #        As all MTA does not respect this RFC (googlemail is one of them),
        #       we also need to verify if the message come from "mailer-daemon"
        #    If not a bounce: reset bounce information
        bounced = False
        if bounce_alias and bounce_alias in email_to_localpart: #check if email_to ( reply to ) contains no reply ( bounce_alias)
            bounce_re = re.compile("%s\+(\d+)-?([\w.]+)?-?(\d+)?" % re.escape(bounce_alias), re.UNICODE)
            bounce_match = bounce_re.search(email_to)
            company = 1
            if 'digimoov' in email_to:  # check if email_to contains digimoov
                company = 2
            elif 'mcm-academy' in email_to:
                company = 1
            message_company = self.env['res.company'].search([('id', "=", company)], limit=1)
            _logger.info('-----template_bounce message_company ------:  %s' % message_company)
            body = self.env.ref('mail_smtp_imap_by_company.mail_bounce_catchall_by_company').render({
                'message': message, 'message_company': message_company,
            }, engine='ir.qweb')
            company_bounce = "%s@%s" %(str(bounce_alias),str(message_company.alias_domain)) if message_company.alias_domain else "%s@%s" %(str(bounce_alias),str(bounce_domain)) # get no-reply ( bounce ) email from company and ir.config_parameter
            template_bounce = False
            if company == 2 :
                template_bounce = self.env['mail.template'].sudo().search(
                    [('name', "=", "Bounced mail - Digimoov"),('model_id.model',"=",'res.partner')], limit=1)
            else:
                template_bounce = self.env['mail.template'].sudo().search(
                    [('name', "=", "Bounced Mail - MCM Academy"), ('model_id.model', "=", 'res.partner')], limit=1)
            if template_bounce:
                self._routing_create_bounce_email(email_from, template_bounce.body_html, message, reply_to=str(company_bounce)) # send automatic bounce mail to client using default function of odoo _routing_create_bounce_email
                bounced = True
            else:
                self._routing_create_bounce_email(email_from, body, message, reply_to=str(company_bounce))
                bounced = True
            if bounce_match:
                company = 1
                if 'digimoov' in email_to: #check if email_to contains digimoov
                    company = 2
                elif 'mcm-academy' in email_to:
                    company = 1
                message_company = self.env['res.company'].search([('id', "=", company)], limit=1)
                # body = self.env.ref('mail_smtp_imap_by_company.mail_bounce_catchall_by_company').render({
                #     'message': message, 'message_company': message_company,
                # }, engine='ir.qweb')

                if company == 2:
                    template_bounce = self.env['mail.template'].sudo().search(
                        [('name', "=", "Bounced mail - Digimoov"), ('model_id.model', "=", 'res.partner')], limit=1)
                    _logger.info('-----template_bounce Digimoov ------:  %s' % template_bounce)
                    _logger.info('-----template_bounce.body_html Digimoov ------:  %s' % template_bounce.body_html)
                else:
                    template_bounce = self.env['mail.template'].sudo().search(
                        [('name', "=", "Bounced Mail - MCM Academy"), ('model_id.model', "=", 'res.partner')], limit=1)
                    _logger.info('-----template_bounce MCM ------:  %s' % company_bounce)
                if not bounced :
                    if template_bounce:
                        self._routing_create_bounce_email(email_from, template_bounce.body_html, message, reply_to=str(
                            company_bounce))  # send automatic bounce mail to client using default function of odoo _routing_create_bounce_email
                    else:
                        self._routing_create_bounce_email(email_from, body, message, reply_to=str(company_bounce))
                return []
        if message.get_content_type() == 'multipart/report' or email_from_localpart == 'mailer-daemon' and not bounced:
            _logger.info('multipart/report')
            self._routing_handle_bounce(message, message_dict)
            return []
        if not bounced :
            self._routing_reset_bounce(message, message_dict)

        # 1. Handle reply
        #    if destination = alias with different model -> consider it is a forward and not a reply
        #    if destination = alias with same model -> check contact settings as they still apply
        if reply_model and reply_thread_id:
            other_alias = self.env['mail.alias'].search([
                '&',
                ('alias_name', '!=', False),
                ('alias_name', '=', email_to_localpart)
            ])
            if other_alias and other_alias.alias_model_id.model != reply_model:
                is_a_reply = False
        if is_a_reply:
            dest_aliases = self.env['mail.alias'].search([('alias_name', 'in', rcpt_tos_localparts)], limit=1)
            user_id = self._mail_find_user_for_gateway(email_from, alias=dest_aliases).id or self._uid
            route = self._routing_check_route(
                message, message_dict,
                (reply_model, reply_thread_id, custom_values, user_id, dest_aliases),
                raise_exception=False)
            if route:
                _logger.info('message_route route : %s' %(str(route)))
                _logger.info(
                    'Routing mail from %s to %s with Message-Id %s: direct reply to msg: model: %s, thread_id: %s, custom_values: %s, uid: %s',
                    email_from, email_to, message_id, reply_model, reply_thread_id, custom_values, self._uid)
                reply_message = self.env['mail.message'].sudo().search([('message_id', "=", str(message_id))], limit=1,
                                                               order='id desc, message_id')
                if reply_message :
                    _logger.info("message_route reply_message : %s" %(str(reply_message)))
                return [route]
            elif route is False:
                return []

        # 2. Handle new incoming email by checking aliases and applying their settings
        if rcpt_tos_localparts:
            # no route found for a matching reference (or reply), so parent is invalid
            message_dict.pop('parent_id', None)
            # check it does not directly contact catchall
            if catchall_alias and catchall_alias in email_to_localpart:
                _logger.info('Routing mail from %s to %s with Message-Id %s: direct write to catchall, bounce',
                            email_from, email_to, message_id)
                _logger.info('multipart/report')
                _logger.info('multipart/report1 %s' % (str(email_to)))
                #company = 1
                if 'digimoov' in email_to: #check if email_to contains digimoov
                    #company = 2
                    template_bounce = self.env['mail.template'].sudo().search(
                        [('name', "=", "Bounced mail - Digimoov"), ('model_id.model', "=", 'res.partner')], limit=1)
                    _logger.info('-----template_bounce Digimoov ------:  %s' % template_bounce)
                    _logger.info('-----template_bounce.body_html Digimoov ------:  %s' % template_bounce.body_html)
                if 'mcm-academy' in email_to: #check if email_to contains Mcm-academy
                    #company = 1
                    template_bounce = self.env['mail.template'].sudo().search(
                        [('name', "=", "Bounced Mail - MCM Academy"), ('model_id.model', "=", 'res.partner')], limit=1)
                    _logger.info('-----template_bounce MCM ------:  %s' % template_bounce)
                _logger.info('multipart/report1 %s' % (str(email_to)))
                message_company = self.env['res.company'].search([('id', "=", company)], limit=1)
                body = self.env.ref('mail_smtp_imap_by_company.mail_bounce_catchall_by_company').render({
                    'message': message, 'message_company': message_company,
                }, engine='ir.qweb')
                _logger.info('reply to :  %s' % (str(self.env.company.email)))


                if not bounced:
                    _logger.info('reply to1 :  %s' % (str(message_company.email)))
                    self._routing_create_bounce_email(email_from, template_bounce.body_html, message, reply_to=message_company.email)
                return []
            alias_domain_id = self.env['alias.mail'].search([('domain_name', 'in', email_to_alias_domain_list)])
            dest_aliases = False
            if alias_domain_id:
                dest_aliases = self.env['mail.alias'].search(
                    [('alias_domain', 'in', alias_domain_id.ids), ('alias_name', 'in', rcpt_tos_localparts)])

            if dest_aliases:
                routes = []
                for alias in dest_aliases:
                    user_id = self._mail_find_user_for_gateway(email_from, alias=alias).id or self._uid
                    route = (
                    alias.alias_model_id.model, alias.alias_force_thread_id, safe_eval(alias.alias_defaults), user_id,
                    alias)
                    route = self._routing_check_route(message, message_dict, route, raise_exception=True)
                    if route:
                        _logger.info(
                            'Routing mail from %s to %s with Message-Id %s: direct alias match: %r',
                            email_from, email_to, message_id, route)
                        routes.append(route)
                return routes

        # 3. Fallback to the provided parameters, if they work
        if fallback_model:
            # no route found for a matching reference (or reply), so parent is invalid
            message_dict.pop('parent_id', None)
            user_id = self._mail_find_user_for_gateway(email_from).id or self._uid
            route = self._routing_check_route(
                message, message_dict,
                (fallback_model, thread_id, custom_values, user_id, None),
                raise_exception=True)
            if route:
                _logger.info(
                    'Routing mail from %s to %s with Message-Id %s: fallback to model:%s, thread_id:%s, custom_values:%s, uid:%s',
                    email_from, email_to, message_id, fallback_model, thread_id, custom_values, user_id)
                return [route]

        # logger info if no routes found and if no bounce occured
        _logger.info(
            'No possible route found for incoming message from %s to %s (Message-Id %s:). '
            'Create an appropriate mail.alias or force the destination model.' %
            (email_from, email_to, message_id)
        )

    def _routing_create_bounce_email(self, email_from, body_html, message, **mail_values):
        bounce_to = tools.decode_message_header(message, 'Return-Path') or email_from
        _logger.info('_routing_create_bounce_email bounce_to : %s' % (str(bounce_to)))
        bounce_mail_values = {
            'body_html': body_html,
            'subject': 'Re: %s' % message.get('subject'),
            'email_to': bounce_to,
            'auto_delete': True,
        }
        bounce_from = self.env['ir.mail_server']._get_default_bounce_address()
        _logger.info('_routing_create_bounce_email bounce_from : %s' % (str(bounce_from)))
        if bounce_from:
            bounce_mail_values['email_from'] = 'MAILER-DAEMON <%s>' % bounce_from
        _logger.info('_routing_create_bounce_email mail_values : %s' % (str(mail_values)))
        bounce_mail_values.update(mail_values)
        self.env['mail.mail'].create(bounce_mail_values).send()

class AliasMail(models.Model):
    _name = 'alias.mail'
    _rec_name = 'domain_name'

    domain_name = fields.Char(string="Domain Name")
    company_id = fields.Many2one('res.company', string="Company")

class Alias(models.Model):
    _inherit = "mail.alias"

    alias_domain = fields.Many2one('alias.mail',default=lambda self: self.env["alias.mail"].sudo().search([('company_id','=',self.env.user.company_id.id)],limit=1))
#     name = fields.Char(related='alias_domain.domain_name', store=True)

    _sql_constraints = [
        ('alias_unique', 'Check(1=1)', "Unfortunately this email alias is already used, please choose a unique one !"),
    ]

    @api.model
    def _clean_and_make_unique(self, name, alias_ids=False):
        # when an alias name appears to already be an email, we keep the local part only
        name = remove_accents(name).lower().split('@')[0]
        name = re.sub(r'[^\w+.]+', '-', name)
        return name

    def name_get(self):
        """Return the mail alias display alias_name, including the implicit
           mail catchall domain if exists from config otherwise "New Alias".
           e.g. `jobs@mail.odoo.com` or `jobs` or 'New Alias'
        """
        res = []
        for record in self:
            if record.alias_name and record.alias_domain:
                res.append((record['id'], "%s@%s" % (record.alias_name, record.alias_domain.domain_name)))
            elif record.alias_name:
                res.append((record['id'], "%s" % (record.alias_name)))
            else:
                res.append((record['id'], _("Inactive Alias")))
        return res

# class Team(models.Model):
#     _inherit = "crm.team"
#     
#     alias_domain = fields.Many2one('alias.mail')
#     name = fields.Char(store=True)
# 
# class Project(models.Model):
#     _inherit = "project.project"
#     
#     alias_domain = fields.Many2one('alias.mail')
#     name = fields.Char(store=True)
# 
class AccountJournal(models.Model):
    _inherit = "account.journal"

    alias_domain = fields.Many2one('alias.mail',related='alias_id.alias_domain')
#     name = fields.Char(store=True)

    @api.model
    def create(self, vals):
        res = super(AccountJournal, self).create(vals)
        if 'alias_domain' in vals:
            if vals.get('alias_domain'):
                res.alias_id.sudo().write({'alias_domain':vals.get('alias_domain')})
                del(vals['alias_domain'])
            else:
                alias = self.env["alias.mail"].sudo().search([('company_id','=',self.env.user.company_id.id)],limit=1)
                if alias:
                    res.alias_id.sudo().write({'alias_domain':alias.id})
        return res

    def write(self, vals):
        for journal in self:
            if 'alias_domain' in vals:
                journal.alias_id.sudo().write({'alias_domain':vals.get('alias_domain')})
                if vals.get('alias_domain'):
                    del(vals['alias_domain'])
        return super(AccountJournal, self).write(vals)
# 
# class Job(models.Model):
#     _inherit = "hr.job"
#     
#     alias_domain = fields.Many2one('alias.mail')
#     name = fields.Char(store=True)

