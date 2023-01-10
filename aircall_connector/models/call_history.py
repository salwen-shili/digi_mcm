from odoo import models, fields, api, SUPERUSER_ID
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError, AccessError
from odoo.osv import osv
from odoo import _
import json
import base64
import time
from datetime import datetime, date
import requests
import logging
import odoo

_logger = logging.getLogger(__name__)


class AirCall(models.Model):
    _name = 'call.detail'
    _rec_name = 'call_contact'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Call/Details'

    call_id = fields.Char(string="Air Call Id", required=False, )
    call_direction = fields.Char(string="AirCall Direction", required=False, )
    call_status = fields.Char(string="Status", required=False, )
    call_recording = fields.Char(string="Recording_url", required=False, )
    call_contact = fields.Many2one(comodel_name="res.partner", string="Contact", required=False, )
    user_id = fields.Many2one(comodel_name="res.users", string="Task Assigned To",
                              required=False, )
    phone_number = fields.Char(string="Phone Number", required=False, )
    owner = fields.Char(string="Owner", required=False, )
    user_name = fields.Char(string="User Name", required=False)
    company_name = fields.Char(string="Company Name", required=False)
    digits = fields.Char(string="Company Number", required=False)
    call_date = fields.Datetime(string="Call Date", required=False, )
    is_imp_tag = fields.Boolean(string="is aircall tag")
    air_call_tag = fields.Many2many(comodel_name="res.partner.category", relation="call_tags_relation",
                                    column1="call_tag_id", column2="call_id", string="Tags", )
    notes = fields.Text(strng="Notes", required=False)
    call_duration = fields.Integer(strng="Duration", required=False)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)


    def create(self, values):

        res = super(AirCall, self).create(values)
        return res
    def write(self, values):
        res = super(AirCall, self).write(values)
        ax_api_id = self.env['ir.config_parameter'].sudo().get_param('aircall_connector.ax_api_id')
        is_tag = self.env['ir.config_parameter'].sudo().get_param('aircall_connector.is_tag')
        ax_api_token = self.env['ir.config_parameter'].sudo().get_param('aircall_connector.ax_api_token')
        if is_tag and 'is_imp_tag' in values and not values['is_imp_tag']:
            tag_ids = []
            auth = ax_api_id + ':' + ax_api_token
            encoded_auth = base64.b64encode(auth.encode()).decode()
            header = {
                'Content-Type': 'application/json',
                'Authorization': 'Basic :{}'.format(encoded_auth)
            }
            for tag in values['air_call_tag'][0][2]:

                odoo_tag = self.env['res.partner.category'].search([('id', '=', tag)])
                if not odoo_tag.call_tag_id:
                    data = {
                        "name": odoo_tag.name,
                        "color": odoo_tag.color if odoo_tag.color else "#00B388"
                    }

                    response = requests.post(
                        'https://api.aircall.io/v1/tags'.format(self.call_id),
                        data=json.dumps(data),
                        headers=header)

                    if response.status_code == 400:
                        raise ValidationError(json.loads(response.content)['troubleshoot'])

                    response = json.loads(response.content)
                    if response:
                        print(response)
                        odoo_tag.call_tag_id = response['tag']['id']
                        # self.env.cr.commit()

                tag_ids.append(odoo_tag.call_tag_id)

            if not self.user_id.ac_user_id:
                phone_num = []
                data = {
                    'tags': tag_ids
                }

                response = requests.post(
                    'https://api.aircall.io/v1/calls/{}/tags'.format(self.call_id),
                    data=json.dumps(data),
                    headers=header)

                if response.status_code == 400:
                    raise ValidationError(json.loads(response.content)[
                                              'troubleshoot'])

                if response.status_code == 201:
                    pass

        return res

    def action_find_user_using_phone(self):
        for record in self:
            _logger.info('phone _number : %s' % str(record.phone_number))
            if record.phone_number and not record.call_contact:
                odoo_contact = self.env["res.users"].sudo().search(
                    [("phone", "=", str(record.phone_number))], limit=1)
                if not odoo_contact:
                    phone_number = str(record.phone_number).replace(' ', '')
                    if '+33' not in str(phone_number):  # check if aircall api send the number of client with +33
                        phone = phone_number[0:2]
                        if str(phone) == '33' and ' ' not in str(
                                record.phone_number):  # check if aircall api send the number of client in this format (number_format: 33xxxxxxx)
                            phone = '+' + str(record.phone_number)
                            odoo_contact = self.env["res.users"].sudo().search([("phone", "=", phone)], limit=1)
                            if not odoo_contact:
                                phone = phone[0:3] + ' ' + phone[3:4] + ' ' + phone[4:6] + ' ' + phone[
                                                                                                 6:8] + ' ' + phone[
                                                                                                              8:10] + ' ' + phone[
                                                                                                                            10:]
                                odoo_contact = self.env["res.users"].sudo().search([("phone", "=", phone)], limit=1)
                        phone = phone_number[0:2]
                        if str(phone) == '33' and ' ' in str(
                                record.phone_number):  # check if aircall api send the number of client in this format (number_format: 33 x xx xx xx)
                            phone = '+' + str(record.phone_number)
                            odoo_contact = self.env["res.users"].sudo().search(
                                ['|', ("phone", "=", phone), ("phone", "=", phone.replace(' ', ''))], limit=1)
                        phone = phone_number[0:2]
                        if str(phone) in ['06', '07'] and ' ' not in str(
                                record.phone_number):  # check if aircall api send the number of client in this format (number_format: 07xxxxxx)
                            odoo_contact = self.env["res.users"].sudo().search(
                                [("phone", "=", str(record.phone_number))], limit=1)
                            print('odoo_contact5 :', odoo_contact.partner_id.name)
                            if not odoo_contact:
                                phone = phone[0:2] + ' ' + phone[2:4] + ' ' + phone[4:6] + ' ' + phone[
                                                                                                 6:8] + ' ' + phone[
                                                                                                              8:]
                                odoo_contact = self.env["res.users"].sudo().search([("phone", "=", phone)], limit=1)
                        phone = phone_number[0:2]
                        if str(phone) in ['06', '07'] and ' ' in str(
                                record.phone_number):  # check if aircall api send the number of client in this format (number_format: 07 xx xx xx)
                            odoo_contact = self.env["res.users"].sudo().search(
                                ['|', ("phone", "=", str(record.phone_number)),
                                 str(record.phone_number).replace(' ', '')], limit=1)
                    else:  # check if aircall api send the number of client with+33
                        if ' ' not in str(record.phone_number):
                            phone = str(record.phone_number)
                            phone = phone[0:3] + ' ' + phone[3:4] + ' ' + phone[4:6] + ' ' + phone[6:8] + ' ' + phone[
                                                                                                                8:10] + ' ' + phone[
                                                                                                                              10:]
                            odoo_contact = self.env["res.users"].sudo().search(
                                [("phone", "=", phone)], limit=1)
                        if not odoo_contact:
                            odoo_contact = self.env["res.users"].sudo().search(
                                [("phone", "=", str(phone_number).replace(' ', ''))], limit=1)
                            if not odoo_contact:
                                phone = str(phone_number)
                                phone = phone[3:]
                                phone = '0' + str(phone)
                                odoo_contact = self.env["res.users"].sudo().search(
                                    [("phone", "like", phone.replace(' ', ''))], limit=1)
                _logger.info('odoo contact : %s' % str(odoo_contact))
                if not odoo_contact:
                    res_users = self.env["res.users"]
                    odoo_contact = res_users.find_user_with_phone(record.phone_number)
                    _logger.info('odoo contact1 : %s' % str(odoo_contact))
                if odoo_contact:
                    record = record.with_user(SUPERUSER_ID)
                    record.sudo().write({"call_contact": odoo_contact.partner_id.id})

    def action_update_notes(self):
        self.uid = odoo.SUPERUSER_ID
        for record in self:
            if record.call_id and record.call_contact:
                ax_api_id = self.env['ir.config_parameter'].sudo().get_param('aircall_connector.ax_api_id')
                ax_api_token = self.env['ir.config_parameter'].sudo().get_param('aircall_connector.ax_api_token')
                if not ax_api_id or not ax_api_token:
                    raise osv.except_osv(_("Error!"), (_("Please add Api Id and Api Token from Aircall setting")))

                auth = ax_api_id + ':' + ax_api_token
                encoded_auth = base64.b64encode(auth.encode()).decode()
                header = {
                    'Content-Type': 'application/json',
                    'Authorization': 'Basic :{}'.format(encoded_auth)
                }
                call_response = requests.get(
                    'https://api.aircall.io/v1/calls/%s' % (str(record.call_id)),  # max api get calls is 50
                    headers=header,
                )
                if call_response.status_code == 400 or call_response.status_code == 404:
                    raise ValidationError('Error')
                else:
                    if call_response.status_code != 204:
                        if call_response.content:
                            calls = json.loads(call_response.content)
                            call = calls['call']
                            self.call_details(call, record)

    def call_details(self, call, record):
        if call:
            # Get calls of MCM ACADEMY using call number name from api response
            # Creating a non existant contact
            started_at = call['started_at']
            if started_at:
                started_at = str(datetime.fromtimestamp(started_at))
            ended_at = call['ended_at']
            if ended_at:
                ended_at = str(datetime.fromtimestamp(ended_at))
            user_name = ''
            if call['user']:
                user_name = str(call['user']['name'])
            else:
                user_name = ''
            comments = ''
            comment = False
            notes = ''
            # check if call has new comments
            for note in call['comments']:
                comments += str(note['content']) + '\n'
                comment = str(note['content'])
                notes += comment + '\n'
                subtype_id = self.env['ir.model.data'].xmlid_to_res_id('mail.mt_note')
                entrant_sortant = ''
                if (call['direction']) and call['direction'] == 'inbound':
                    entrant_sortant = 'Appel Entrant'
                if (call['direction']) and call['direction'] == 'outbound':
                    entrant_sortant = 'Appel Sortant'
                content = "<b>" + user_name + " " + entrant_sortant + " " + " " + started_at + " " + ended_at + "</b><br/>"
                message = False
                if record.call_contact and subtype_id:
                    message = self.env['mail.message'].sudo().search(
                        [('subtype_id', "=", subtype_id), ('model', "=", 'res.partner'),('date','=',date.today()),
                         ('res_id', '=', record.call_contact.id), ('body', "ilike", comment)])
                    _logger.info('aircall find message mcm %s : %s' % (
                        str(record.call_contact), (str(message))))
                    if not message:
                        subject = user_name + " " + started_at + " " + ended_at
                        message = self.env['mail.message'].sudo().search(
                            [('subtype_id', "=", subtype_id), ('model', "=", 'res.partner'),('date','=',date.today()),
                             ('res_id', '=', record.call_contact.id), ('subject', "=",
                                                                       subject)])  # add another condition of search message using subject ( the subject is concatenation between user name + start datetime of call + end datetime of call )
                        _logger.info('aircall find message mcm with subject %s : %s' % (
                            str(record.call_contact), (str(subject))))
                        if message:
                            _logger.info("aircall message found : %s" % (str(message.body)))
                            if str(note['content']) not in message.body:
                                message.sudo().write({
                                    'body': message.body + '\n' + str(note['content'])
                                })
                if not message and record.call_contact:
                    # Create new Note in view contact
                    _logger.info('create new note in view contact mcm %s : %s' % (
                        str(record.call_contact), (str(str(content) + str(note['content'])))))
                    message = self.env['mail.message'].sudo().create({
                        'subject': user_name + " " + started_at + " " + ended_at,
                        'model': 'res.partner',
                        'res_id': record.call_contact.id,
                        'message_type': 'notification',
                        'subtype_id': subtype_id,
                        'body': str(content) + str(note['content']),
                    })
                    if record.call_contact.statut == "indecis":
                        record.call_contact.changestage("Indécis appelé", record.call_contact)
                        lead = self.env['crm.lead'].sudo().search([('partner_id', "=", record.call_contact.id)])
                        if lead:
                            _logger.info('lead %s' % str(lead))
                            lead.conseiller = user_name
                        _logger.info('createeeeee note ********************************')
