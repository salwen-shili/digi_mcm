from odoo import models, fields, api, SUPERUSER_ID
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError, AccessError
from odoo.osv import osv
from odoo import _
import json
import base64
import time
from datetime import datetime
import requests
import logging
_logger = logging.getLogger(__name__)

class AirCall(models.Model):
    _name = 'call.detail'
    _rec_name = 'call_contact'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Call/Details'

    call_id = fields.Char(string="Air Call Id", required=False, )
    call_direction = fields.Char(string="AirCall Direction", required=False, )
    call_status = fields.Char(string="Status", required=False, )
    call_recording = fields.Char(string="Recording_url", required=False, )
    call_contact = fields.Many2one(comodel_name="res.partner", string="Contact", required=False, )
    user_id = fields.Many2one(comodel_name="res.users", string="Task Assigned To",
                              required=False, )
    phone_number = fields.Char(string="Phone Number", required=False, )
    user_name = fields.Char(string="User Name", required=False)
    company_name = fields.Char(string="Company Name", required=False)
    digits = fields.Char(string="Company Number", required=False)
    call_date = fields.Datetime(string="Call Date", required=False, )
    is_imp_tag = fields.Boolean(string="is aircall tag")
    air_call_tag = fields.Many2many(comodel_name="res.partner.category", relation="call_tags_relation", column1="call_tag_id", column2="call_id", string="Tags", )
    notes = fields.Text(strng="Notes", required=False)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    def write(self,values):
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
        if self.phone_number and not self.call_contact:
            odoo_contact = self.env["res.users"].sudo().search(
                [("phone", "=", str(self.phone_number))], limit=1)
            if not odoo_contact:
                phone_number = str(self.phone_number).replace(' ', '')
                if '+33' not in str(phone_number):  # check if aircall api send the number of client with +33
                    phone = phone_number[0:2]
                    if str(phone) == '33' and ' ' not in str(self.phone_number):  # check if aircall api send the number of client in this format (number_format: 33xxxxxxx)
                        phone = '+' + str(self.phone_number)
                        odoo_contact = self.env["res.users"].sudo().search([("phone", "=", phone)], limit=1)
                        if not odoo_contact:
                            phone = phone[0:3] + ' ' + phone[3:4] + ' ' + phone[4:6] + ' ' + phone[6:8] + ' ' + phone[
                                                                                                                8:10] + ' ' + phone[
                                                                                                                              10:]
                            odoo_contact = self.env["res.users"].sudo().search([("phone", "=", phone)], limit=1)
                    phone = phone_number[0:2]
                    if str(phone) == '33' and ' ' in str(self.phone_number):  # check if aircall api send the number of client in this format (number_format: 33 x xx xx xx)
                        phone = '+' + str(self.phone_number)
                        odoo_contact = self.env["res.users"].sudo().search(
                            ['|', ("phone", "=", phone), ("phone", "=", phone.replace(' ', ''))], limit=1)
                    phone = phone_number[0:2]
                    if str(phone) in ['06', '07'] and ' ' not in str(self.phone_number):  # check if aircall api send the number of client in this format (number_format: 07xxxxxx)
                        odoo_contact = self.env["res.users"].sudo().search(
                            [("phone", "=", str(self.phone_number))], limit=1)
                        print('odoo_contact5 :', odoo_contact.partner_id.name)
                        if not odoo_contact:
                            phone = phone[0:2] + ' ' + phone[2:4] + ' ' + phone[4:6] + ' ' + phone[6:8] + ' ' + phone[
                                                                                                                8:]
                            odoo_contact = self.env["res.users"].sudo().search([("phone", "=", phone)], limit=1)
                    phone = phone_number[0:2]
                    if str(phone) in ['06', '07'] and ' ' in str(self.phone_number):  # check if aircall api send the number of client in this format (number_format: 07 xx xx xx)
                        odoo_contact = self.env["res.users"].sudo().search(
                            ['|', ("phone", "=", str(self.phone_number)),
                             str(self.phone_number).replace(' ', '')], limit=1)
                else:  # check if aircall api send the number of client with+33
                    if ' ' not in str(self.phone_number):
                        phone = str(self.phone_number)
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
            if not odoo_contact :
                res_users = self.env["res.users"]
                odoo_contact = res_users.find_user_with_phone(self.phone_number)
                _logger.info('odoo contact1 : %s' % str(odoo_contact))
            if odoo_contact :
                self = self.with_user(SUPERUSER_ID)
                self.sudo().write({"call_contact": odoo_contact.partner_id.id})
        








