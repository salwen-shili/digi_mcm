from odoo import fields,models,api,_
from odoo.exceptions import UserError

class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    def sb_create_or_update_template(self, values_dict, account=False):
        sender_obj = self.env['sendinblue.senders']
        odoo_sender_id = sender_obj
        template_id = values_dict.get('id')
        for model_name in ['res.partner','crm.lead']:
            existing_list = self.env['mail.template'].search([('sb_template_id', '=', template_id),('model_id', '=', model_name)])
            if values_dict.get('sender',{}):
                odoo_sender_id = sender_obj.search([('account_id','=',account.id),('sendinblue_id','=',values_dict.get('sender').get('id'))])
                if not odoo_sender_id:
                    account.import_senders()
                    odoo_sender_id = sender_obj.search([('account_id', '=', account.id), ('sendinblue_id', '=', values_dict.get('sender').get('id'))])
            body_html = self.env['mail.thread']._replace_local_links(values_dict.get('htmlContent'))
            vals = {
                'sb_sender_id': odoo_sender_id.id,
                'email_from': odoo_sender_id and '%s <%s>' % (odoo_sender_id.name, odoo_sender_id.email) or '',
                'body_html': body_html,
                'sb_template_id' : template_id,
                'name':values_dict.get('name',''),
                'subject': values_dict.get('subject'),
                'model_id':self.env['ir.model'].search([('model','=',model_name)],limit=1).id
            }
            if not existing_list:
                existing_list = self.env['mail.template'].create(vals)
            else:
                existing_list.write(vals)
        return True

    def sb_import_templates(self, account=False):
        if not account:
            raise Warning("Sendinblue Account not defined to import templates")
        count = 1000
        offset = 0
        template_list = []
        while True:
            prepared_vals = {'limit': count, 'offset': offset}
            response = account._send_request('smtp/templates', {}, params=prepared_vals)
            if len(response.get('templates',[])) == 0:
                break
            if isinstance(response.get('templates'), dict):
                template_list += [response.get('templates')]
            template_list += response.get('templates')
            offset = offset + 1000
        for template_dict in template_list:
            self.sb_create_or_update_template(template_dict, account=account)
        return True

    def fetch_sendinblue_template(self):
        sb_account = self.env['sendinblue.accounts'].search([],limit=1)
        for rec in self:
            res = rec.sb_import_templates(account=sb_account)
        return {'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_id': self.id,
                'res_model': self._name,
                'target': 'new',
                'context': self._context,
                }

    def action_send_mail(self):
        if self._context.get('default_model') and self._context.get('default_model') == 'res.partner':
            partner = self.env[self._context.get('default_model')].browse(self._context.get('default_res_id'))
            if partner and not partner.company_id:
                raise UserError(_("Please define a company on the contact."))
        res = super(MailComposeMessage, self).action_send_mail()
        return res