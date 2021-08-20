from odoo import api, fields, models, _

REPLACEMENT_OF_KEY = [('id', 'template_id')]
DATE_CONVERSION = ['createdAt', 'modifiedAt']


class SendinblueTemplates(models.Model):
    _name = "sendinblue.templates"
    _description = "Templates"

    name = fields.Char("Name", required=True, help="The name of the template.")
    template_id = fields.Char("Template ID", copy=False)
    subject = fields.Char("Subject")
    sb_sender_id = fields.Many2one('sendinblue.senders','Sender')
    sender_name = fields.Char("Sender Name")
    sender_email = fields.Char("Sender Email")
    testsent = fields.Char("Test Sent")
    createdAt = fields.Datetime("Created On")
    modifiedAt = fields.Datetime("Edited On")
    active = fields.Boolean("Active", default=True)
    to_field = fields.Char("To Field")
    htmlcontent  = fields.Html('Html Content')
    tag = fields.Char("Tag")
    account_id = fields.Many2one("sendinblue.accounts", string="Account", required=True, ondelete='cascade')

    #@api.multi
    def create_or_update_template(self, values_dict, account=False):
        sender_obj = self.env['sendinblue.senders']
        odoo_sender_id = sender_obj
        template_id = values_dict.get('id')
        existing_list = self.search([('template_id', '=', template_id)])
        for old_key, new_key in REPLACEMENT_OF_KEY:
            values_dict[new_key] = values_dict.pop(old_key)
        for item in DATE_CONVERSION:
            if values_dict.get(item, False) == '':
                values_dict[item] = False
            if values_dict.get(item, False):
                values_dict[item] = account.covert_date(values_dict.get(item))
        if values_dict.get('sender',{}):
            odoo_sender_id = sender_obj.search([('account_id','=',account.id),('sendinblue_id','=',values_dict.get('sender').get('id'))])
            if not odoo_sender_id:
                account.import_senders()
                odoo_sender_id = sender_obj.search([('account_id', '=', account.id), ('sendinblue_id', '=', values_dict.get('sender').get('id'))])
        # Added for v13
        for pop_field in ['replyTo', 'toField', 'sender']:
            values_dict.pop(pop_field)
        values_dict.update({
                            'account_id': account.id,
                            'active':values_dict.pop('isActive'),
                            'sb_sender_id':odoo_sender_id.id,
                            'testsent' : values_dict.pop('testSent'),
                            'htmlcontent' : values_dict.pop('htmlContent')
                            })
        if not existing_list:
            existing_list = self.create(values_dict)
        else:
            existing_list.write(values_dict)
        return True

    #@api.multi
    def import_templates(self, account=False):
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
            self.create_or_update_template(template_dict, account=account)
        return True