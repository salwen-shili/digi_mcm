# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class sendinblueSegments(models.Model):
    _name = "sendinblue.folder"
    _description = "Sendinblue Folder"

    #@api.multi
    def _compute_sb_list_ids(self):
        for record in self:
            sb_list_ids = self.env['sendinblue.lists'].search([('folder_id','=',record.id)])
            record.sb_list_count = len(sb_list_ids)

    name = fields.Char("Name", required=True, copy=False, help="Name of your Sendinblue Folder")
    account_id = fields.Many2one("sendinblue.accounts", string="Account", required=True)
    sendinblue_id = fields.Char("SendinBlue Folder ID", readonly=True, copy=False)
    totalsubscribers = fields.Integer('Total Subscribers', default=0,readonly=True)
    totalblacklisted = fields.Integer('Total Blacklisted', default=0,readonly=True)
    uniquesubscribers = fields.Integer('Unique Subscribers', default=0,readonly=True)
    sb_list_count = fields.Integer(string='Delivery Orders', compute='_compute_sb_list_ids')

    def action_view_sb_lists(self):
        self.ensure_one()
        action = self.env.ref('sendinblue.action_sendinblue_lists').read()[0]
        sb_list_ids = self.env['sendinblue.lists'].search([('folder_id', '=', self.id)])
        if len(sb_list_ids) > 1:
            action['domain'] = [('id', 'in', sb_list_ids.ids)]
        elif sb_list_ids:
            action['views'] = [(self.env.ref('sendinblue.view_sendinblue_lists_form').id, 'form')]
            action['res_id'] = sb_list_ids.id
        return action

    #@api.multi
    def import_folders(self, account=False):
        if not account:
            raise Warning("sendinblue Account not defined to import Folders")
        response = account._send_request('contacts/folders', {}, method='GET')
        for folder in response.get('folders'):
            self.create_or_update_folder(folder, account=account)
        return True

    #@api.multi
    def refresh_folder(self):
        # self.export_folder_sendinblue()
        res = self.account_id._send_request('contacts/folders/{}'.format(self.sendinblue_id), {}, method='GET')
        rec = self.create_or_update_folder(res)
        return True

    #@api.multi
    def export_folder_sendinblue(self):
        if not self.account_id:
            raise Warning("sendinblue Account not defined to export Folders")
        if self.sendinblue_id:
            self.account_id._send_request('contacts/folders/{}'.format(self.sendinblue_id), {'name': self.name}, method='PUT')
        else:
            response = self.account_id._send_request('contacts/folders', {'name':self.name}, method='POST')
            self.sendinblue_id = response.get('id')
        return True

    #@api.multi
    def create_or_update_folder(self, values_dict, account=False):
        sendinblue_id = values_dict.pop('id')
        folder_name = values_dict.get('name')
        existing_list = self.search([('sendinblue_id', '=', sendinblue_id)])
        values_dict.update({
                            'account_id': account and account.id or self.account_id.id,
                            'name': folder_name,
                            'totalsubscribers': values_dict.pop('totalSubscribers'),
                            'totalblacklisted': values_dict.pop('totalBlacklisted'),
                            'uniquesubscribers': values_dict.pop('uniqueSubscribers'),
                            'sendinblue_id': sendinblue_id
        })
        if not existing_list:
            existing_list = self.create(values_dict)
        else:
            existing_list.write(values_dict)
        return existing_list