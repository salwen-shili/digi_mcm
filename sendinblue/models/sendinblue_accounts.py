# -*- coding: utf-8 -*-
import json
import time
import requests
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, Warning


class SendinblueAccounts(models.Model):
    _name = "sendinblue.accounts"
    _description = "Sendinblue Accounts"

    name = fields.Char("Name", required=True, copy=False, help="Name of your Sendinblue account")

    # Authentication
    api_key = fields.Char('API Key', required=True, copy=False)
    auto_refresh_member = fields.Boolean("Auto Sync Member?", copy=False, default=True)
    auto_create_member = fields.Boolean("Auto Create Member?", copy=False, default=True)
    auto_create_partner = fields.Boolean("Auto Create Customer?", copy=False, default=False)
    list_ids = fields.One2many('sendinblue.lists', 'account_id', string="Lists/Audience", copy=False)
    campaign_ids = fields.One2many('mailing.mailing', 'sendinblue_account_id', string="Campaigns", copy=False)#v13
    merge_field_ids = fields.One2many("sendinblue.merge.fields", 'account_id', string="Merge Fields", ondelete='cascade', copy=False)
    folder_ids = fields.One2many("sendinblue.folder", 'account_id', string="Folders", copy=False)
    active = fields.Boolean('Active',default=True)

    _sql_constraints = [
        ('api_keys_uniq', 'unique(api_key)', 'API keys must be unique per sendinblue Account!'),
    ]

    @api.model
    def _send_request(self, request_url, request_data, params=False, method='GET'):
        if not self.api_key:
            raise ValidationError(_("sendinblue API key is not found!"))

        api_key = self.api_key
        headers = {
            'accept': "application/json",
            'Content-Type': 'application/json',
            'api-key': api_key
        }
        data = json.dumps(request_data)
        api_url = "https://api.sendinblue.com/v3/{url}".format(url=request_url)
        try:
            req = requests.request(method, api_url, auth=('apikey', api_key), headers=headers, params=params, data=data)
            req.raise_for_status()
            response_text = req.text
        except requests.HTTPError as e:
            raise Warning("%s" % req.text)
        response = json.loads(response_text) if response_text else {}
        return response

    #@api.multi
    def get_refresh_member_action(self):
        action = self.env.ref('base.ir_cron_act').read()[0]
        refresh_member_cron = self.env.ref('sendinblue.fetch_member_sendinblue')
        if refresh_member_cron:
            action['views'] = [(False, 'form')]
            action['res_id'] = refresh_member_cron.id
        else:
            raise ValidationError(_("Scheduled action isn't found! Please upgrade app to get it back!"))
        return action

    def covert_date(self, value):
        before_date = value[:19]
        coverted_date = time.strptime(before_date, "%Y-%m-%dT%H:%M:%S")
        final_date = time.strftime("%Y-%m-%d %H:%M:%S", coverted_date)
        return final_date

    #@api.multi
    def import_lists(self):
        sendinblue_lists = self.env['sendinblue.lists']
        for account in self:
            sendinblue_lists.import_lists(account)
        return True

    #@api.multi
    def import_folders(self):
        sendinblue_folder = self.env['sendinblue.folder']
        for account in self:
            sendinblue_folder.import_folders(account)
        return True

    #@api.multi
    def import_templates(self):
        sendinblue_templates = self.env['sendinblue.templates']
        for account in self:
            sendinblue_templates.import_templates(account)
        return True

    #@api.multi
    def import_campaigns(self):
        mass_mailing_obj = self.env['mailing.mailing'] #v13
        for account in self:
            mass_mailing_obj.import_campaigns(account)
        return True

    # @api.one
    def test_connection(self):
        response = self._send_request('contacts/lists', {})
        if response:
            raise Warning("Test Connection Succeeded")
        return True

    # @api.one
    def fetch_merge_fields(self):
        sendinblue_merge_field_obj = self.env['sendinblue.merge.fields']
        if not self.api_key:
            raise Warning("SendInBlue Account not defined to Fetch Merge Field")
        merge_field_list = []
        prepared_vals = {}
        response = self._send_request('contacts/attributes', {}, method='GET')
        if isinstance(response.get('attributes'), dict):
            merge_field_list = [response.get('attributes')]
        else:
            merge_field_list += response.get('attributes')
        for merge_field in merge_field_list:
            merge_field_id = sendinblue_merge_field_obj.search(
                [('name', '=', merge_field.get('name')), ('account_id', '=', self.id)])
            # merge_field.update({'account_id': self.id})
            vals = {
                'name':merge_field.get('name',''),
                'category':merge_field.get('category',''),
                'account_id': self.id,
                'type': merge_field.get('type', ''),
            }
            if not merge_field_id:
                sendinblue_merge_field_obj.create(vals)
            if merge_field_id:
                merge_field_id.write(vals)
        return merge_field_list

    def import_senders(self):
        if not self.api_key:
            raise Warning("SendInBlue Account not defined to Fetch Merge Field")
        response = self._send_request('senders', {}, method='GET')
        senders_obj = self.env['sendinblue.senders']
        for res in response.get('senders',[]):
            sb_id = res.pop('id')
            exist = senders_obj.search([('sendinblue_id', '=', sb_id), ('account_id', '=', self.id)])
            if exist:
                exist.write(res)
            else:
                res.update({'sendinblue_id':sb_id,'account_id':self.id})
                senders_obj.create(res)
        return True

    def refresh_folder(self):
        for rec in self:
            rec.refresh_folder()
        return True
    
    def unlink(self):
        for rec in self:
            queue_ids = self.env['sendinblue.queue.process'].search([('account_id','=',rec.id),('state','=','in_queue')])
            queue_ids.unlink()
        return super(SendinblueAccounts, self).unlink()

