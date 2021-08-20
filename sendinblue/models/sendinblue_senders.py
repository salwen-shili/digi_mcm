from odoo import fields,api,models

class SendINBlueSenders(models.Model):
    _name = 'sendinblue.senders'
    _description = "Sendinblue Senders"

    sendinblue_id = fields.Char('SendINBlue ID')
    name = fields.Char('Name')
    email = fields.Char('Email')
    active = fields.Boolean('Active')
    account_id = fields.Many2one('sendinblue.accounts',string='Account')

    def action_export_senders_sendinblue(self):
        def prepare_data(rec):
            return {
                'email' : rec.email,
                'name' : rec.name
            }
        for record in self.filtered(lambda x : not x.sendinblue_id and x.account_id):
            vals = prepare_data(record)
            res = record.account_id._send_request('senders', vals, method='POST')
            record.write({'sendinblue_id':res.get('id')})
        for record in self.filtered(lambda x : x.sendinblue_id and x.account_id):
            vals = prepare_data(record)
            res = record.account_id._send_request('senders/{}.'.format(record.sendinblue_id), vals, params={'senderId':record.sendinblue_id}, method='PUT')





