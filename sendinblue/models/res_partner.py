from odoo import fields, models, api

def _partner_split_name(partner_name):
    return [' '.join(partner_name.split()[:-1]), ' '.join(partner_name.split()[-1:])]

class ResPartner(models.Model):
    _inherit = 'res.partner'

    sendinblue_id = fields.Char('Sendinblue Id')
    #v13
    subscription_list_ids = fields.One2many('mailing.contact.subscription',
        'related_partner_id', string='Subscription Information', domain=[('sendinblue_list_id','!=',False)])

    #@api.multi
    def get_mailing_partner(self, email):
        #v13
        query = """
                        SELECT id 
                          FROM mailing_contact
                        WHERE LOWER(substring(email, '([^ ,;<@]+@[^> ,;]+)')) = LOWER(substring('{}', '([^ ,;<@]+@[^> ,;]+)'))""".format(email)
        self._cr.execute(query)
        return self._cr.fetchone()

    @api.model
    def create(self, vals):
        res = super(ResPartner, self).create(vals)
        if vals.get('email', False):
            mailing_contact = self.env['mailing.contact'] #v13
            partner_record = self.get_mailing_partner(vals.get('email'))
            if partner_record:
                mailing_contact.browse(partner_record[0]).related_partner_id = res.id
        return res

    #@api.multi
    def get_sendinblue_accounts(self):
        sendinblue_list_ids = self.mapped('subscription_list_ids').mapped('sendinblue_list_id')
        account_ids = sendinblue_list_ids.mapped('account_id')
        return account_ids

    #@api.multi
    def update_partner_in_sendinblue(self, vals):
        """Called while changing partner field value which is defined in merge field in send in blue account screen."""
        partner_field_ids = ['name', 'email']
        mailing_contact = self.env['mailing.contact'] #v13
        req_attributes = {}
        for record in self:
            body_param = {}
            if vals.get('name',False):
                req_attributes.update({'FIRSTNAME': _partner_split_name(vals.get('name'))[0], 'LASTNAME': _partner_split_name(vals.get('name'))[1]})
            if vals.get('email',False):
                body_email = vals.get('email',False) and vals.get('email').lower() or record.email and record.email.lower() or ''
                body_param.update({'email':body_email})
                req_attributes.update({'email':vals.get('email',False) or record.email})
                partner_record = self.get_mailing_partner(vals.get('email'))
                if partner_record:
                    mailing_contact.browse(partner_record[0]).related_partner_id = record.id
                else:
                    partner_record = self.get_mailing_partner(record.email)
                    if partner_record:
                        mailing_contact.browse(partner_record[0]).write({'related_partner_id': False})
            account_ids = self.get_sendinblue_accounts()
            for account in account_ids:
                if account.auto_create_partner:
                    sb_list_ids = record.subscription_list_ids.mapped('sendinblue_list_id').filtered(lambda x: x.account_id == account)
                    sb_list_ids = sb_list_ids.mapped('list_id')
                    list_ids = list(map(int, sb_list_ids))
                    body_param.update({'listIds': list(map(int, list_ids))})
                    merge_fields = account.mapped('merge_field_ids').filtered(lambda x: x.field_id)
                    partner_field_ids += merge_fields.mapped('field_id').mapped('name')
                    if any([o_field in vals for o_field in partner_field_ids]):
                        for m_field in merge_fields:
                            if hasattr(record, m_field.field_id.name):
                                value = getattr(record, m_field.field_id.name)
                                req_attributes.update({m_field.name: vals.get(m_field.field_id.name,False) or value})
                        body_param.update({'attributes': req_attributes})
                        account._send_request('contacts/%s' % (record.sendinblue_id and int(record.sendinblue_id) or vals.get('email',False) or record.email), body_param, method='PUT')
        return True

    #@api.multi
    def write(self, vals):
        res = super(ResPartner, self).write(vals)
        if not self._context.get('no_update',False):
            self.update_partner_in_sendinblue(vals)
        return res
