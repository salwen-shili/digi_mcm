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


class MailMessageInherit(models.AbstractModel):
    _inherit = 'mail.message'

    def redirect_client_response(self):
        # an automated action to personalize email_from,reply_to and redirect response of clients when creating a new mail message
        for record in self :
            _logger.info("redirect_client_response : %s %s" % (str(record.model), str(record.res_id)))
            if record.model and record.model in ["sale.order", "helpdesk.ticket", "account.move", "documents.document"] and record.message_type in ['email','comment','snailmail']: #check if mail message model in ["sale.order", "helpdesk.ticket", "account.move", "documents.document"]
                if record.res_id:
                    search_record = self.env[str(record.model)].sudo().search([('id', "=", record.res_id)],
                                                                              limit=1) #search record using new message model and res_id
                    _logger.info("redirect_client_response search_record: %s" % (str(search_record)))
                    if search_record:
                        if search_record.partner_id.id == record.author_id.id:
                            record.model = "res.partner" #update new message model to res partner
                            record.res_id = search_record.partner_id.id #update new message res_id to id of partner
            if '<' in record.reply_to and '>' in record.reply_to:
                catchall_mail = re.search('<(.*)>', record.reply_to)
                catchall_mail = catchall_mail.group(1)
                if catchall_mail:
                    catchall_mail = str(catchall_mail)
                    user_sudo = self.env['res.users'].sudo().search([('partner_id', "=", int(record.author_id))],
                                                                    limit=1)
                    if record.res_id : #check res_id of record
                        records = self.env[record.model].browse([record.res_id])
                        _logger.info('user_sudo : %s' % str(user_sudo))
                        if records:
                            if hasattr(records, 'company_id'):
                                user_signature = self.env['res.user.signature'].sudo().search(
                                    [('user_id', "=", user_sudo.id), ('company_id', "=", records.company_id.id)],
                                    limit=1)
                                if user_signature and user_signature.reply_to:  # verify if 'reply_to' in the sender's user's signature elready filled
                                    _logger.info('catchall_mail : %s' % str(catchall_mail))
                                    _logger.info('user_signature.reply_to : %s' % str(user_signature.reply_to))
                                    new_reply_to = record.reply_to.replace(catchall_mail, user_signature.reply_to)
                                    _logger.info('new_reply_to : %s' % str(record.reply_to))
                                    record.reply_to = new_reply_to  # change mail message's default reply_to by the reply_to of the user signature
            author = record.author_id
            email = record.email_from
            company_id = record.company_id
            if company_id and author:  # check company of active record(sale order,helpdesk ticket,partner...etc)
                user =  self.env['res.users'].sudo().search(
                    [('partner_id', "=", author.id)],limit=1)
                if user :
                    user_signature = self.env['res.user.signature'].sudo().search(
                        [('user_id', "=", user.id), ('company_id', "=", company_id.id)],
                        limit=1)  # check if the mail sender has a email from related to the company already checked before
                    if user_signature and user_signature.email_from and user.partner_id.email in email:
                        record.email_from = tools.formataddr(
                            (user.partner_id.name or u"False",
                             user_signature.email_from or u"False"))  # change the sender mail
                        if record.author_id:
                            if not record.author_id.partner_share and record.message_type in ['email', 'comment',
                                                                                              'snailmail']:
                                body = self.env.ref('mail_smtp_imap_by_company.mail_bounce_footer').render({
                                    'message_company': record.company_id,
                                }, engine='ir.qweb')
                                _logger.info('mail message redirect_client_response body %s' % (str(body)))
                                record.body += body.decode("utf-8")
    
