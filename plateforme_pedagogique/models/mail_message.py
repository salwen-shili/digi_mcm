from odoo import models, fields, api,SUPERUSER_ID
from odoo.exceptions import ValidationError
from unidecode import unidecode
import logging
import pyshorteners
_logger = logging.getLogger(__name__)


class Message(models.Model):
    _inherit = 'mail.mail'


    def write(self, vals):
        res = super(Message, self).write(vals)
        if 'state' in vals:
            print('state', vals)
            # if vals['state'] == "outgoing":
            #     print('outgoing', vals)
            #     for partner_id in self.recipient_ids:
            #         email=partner_id.email
            #         if "#" in email :
            #             new_email=email.replace('#digimoov','')
            #             partner_id.email = new_email
            if vals['state']=="sent":
                print('write',vals)
                for partner_id in self.recipient_ids:
                    if "#" in partner_id.second_email:
                        partner_id.email=partner_id.second_email

        return res

    def create(self, values):
        res = super(Message, self).create(values)
        print("create ", values)
        if 'recipient_ids' in values:
            for recipient_ids in values['recipient_ids']:
                print('iffffff',recipient_ids)
                for recipient_id in recipient_ids:
                    partner=self.env['res.partner'].sudo().search([('id',"=",recipient_id)])
                    if partner and "#" in partner.email :
                            email=partner.email
                            print('reciep', partner.email )
                            new_email = email.replace('#digimoov', '')
                            partner.email = new_email
        if 'state' in values:
            print('state', values)
            # if vals['state'] == "outgoing":
            #     print('outgoing', values)
            #     for partner_id in self.recipient_ids:
            #         email=partner_id.email
            #         if "#" in email :
            #             new_email=email.replace('#digimoov','')
            #             partner_id.email = new_email
            # if vals['state']=="sent":
            #     print('write',values)
            #     for partner_id in self.recipient_ids:
            #         if "#" in partner_id.second_email:
            #             partner_id.email=partner_id.second_email

        return res