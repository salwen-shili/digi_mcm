# -*- coding: utf-8 -*-

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    birthday = fields.Date('Date of Birth')
    
    question_signup = fields.Char('Comment avez vous découvert notre site')

class ResUsers(models.Model):
    _inherit = "res.users"
    
    def find_user_with_phone(self,tel):
        # this function searches for the user using the given telephone number.
        user = self.env["res.users"].sudo().search(
            [("phone", "=", str(tel))], limit=1)
        if not user:
            phone_number = str(tel).replace(' ', '')
            if '+33' not in str(phone_number):  # check if edof api send the number of client with +33
                phone = phone_number[0:2]
                if str(phone) == '33' and ' ' not in str(
                        tel):  # check if edof api send the number of client in this format (number_format: 33xxxxxxx)
                    phone = '+' + str(tel)
                    user = self.env["res.users"].sudo().search([("phone", "=", phone)], limit=1)
                    if not user:
                        phone = phone[0:3] + ' ' + phone[3:4] + ' ' + phone[4:6] + ' ' + phone[
                                                                                         6:8] + ' ' + phone[
                                                                                                      8:10] + ' ' + phone[
                                                                                                                    10:]
                        user = self.env["res.users"].sudo().search([("phone", "=", phone)], limit=1)
                    if not user:
                        phone = '0' + str(phone[4:])
                        user = self.env["res.users"].sudo().search(
                            ['|', ("phone", "=", phone), ("phone", "=", phone.replace(' ', ''))], limit=1)
                phone = phone_number[0:2]
                if str(phone) == '33' and ' ' in str(
                        tel):  # check if edof api send the number of client in this format (number_format: 33 x xx xx xx)
                    phone = '+' + str(tel)
                    user = self.env["res.users"].sudo().search(
                        ['|', ("phone", "=", phone), ("phone", "=", phone.replace(' ', ''))], limit=1)
                    if not user:
                        phone = '0' + str(phone[4:])
                        user = self.env["res.users"].sudo().search(
                            ['|', ("phone", "=", phone), ("phone", "=", phone.replace(' ', ''))], limit=1)
                phone = phone_number[0:2]
                if str(phone) in ['06', '07'] and ' ' not in str(
                        tel):  # check if edof api send the number of client in this format (number_format: 07xxxxxx)
                    user = self.env["res.users"].sudo().search(
                        ['|', ("phone", "=", str(tel)), ("phone", "=", str('+33' + tel.replace(' ', '')[-9:]))],
                        limit=1)
                    if not user:
                        phone = phone[0:2] + ' ' + phone[2:4] + ' ' + phone[4:6] + ' ' + phone[
                                                                                         6:8] + ' ' + phone[8:]
                        user = self.env["res.users"].sudo().search([("phone", "=", phone)], limit=1)
                    if not user:
                        phone = '0' + str(phone[4:])
                        user = self.env["res.users"].sudo().search(
                            ['|', ("phone", "=", phone), ("phone", "=", phone.replace(' ', ''))], limit=1)
                phone = phone_number[0:2]
                if str(phone) in ['06', '07'] and ' ' in str(
                        tel):  # check if edof api send the number of client in this format (number_format: 07 xx xx xx)
                    user = self.env["res.users"].sudo().search(
                        ['|', ("phone", "=", str(tel)), str(tel).replace(' ', '')], limit=1)
                    if not user:
                        phone_number = str(tel[1:])
                        user = self.env["res.users"].sudo().search(
                            ['|', ("phone", "=", str('+33' + phone_number)),
                             ("phone", "=", ('+33' + phone_number.replace(' ', '')))], limit=1)
            else:  # check if edof api send the number of client with+33
                if ' ' not in str(tel):
                    phone = str(tel)
                    phone = phone[0:3] + ' ' + phone[3:4] + ' ' + phone[4:6] + ' ' + phone[6:8] + ' ' + phone[
                                                                                                        8:10] + ' ' + phone[
                                                                                                                      10:]
                    user = self.env["res.users"].sudo().search(
                        [("phone", "=", phone)], limit=1)
                if not user:
                    user = self.env["res.users"].sudo().search(
                        [("phone", "=", str(phone_number).replace(' ', ''))], limit=1)
                    if not user:
                        phone = str(phone_number)
                        phone = phone[3:]
                        phone = '0' + str(phone)
                        user = self.env["res.users"].sudo().search(
                            [("phone", "like", phone.replace(' ', ''))], limit=1)
        if user :
            return user
        else:
            return False