import re
import dateutil
from odoo import api, fields, models, _
from pytz import timezone

EMAIL_PATTERN = '([^ ,;<@]+@[^> ,;]+)'


def _partner_split_name(partner_name):
    return [' '.join(partner_name.split()[:-1]), ' '.join(partner_name.split()[-1:])]


class massMailingContact(models.Model):
    _inherit = "mailing.contact"

    #@api.multi
    def get_partner_for_sb(self, email):
        query = """
                SELECT id 
                  FROM res_partner
                WHERE LOWER(substring(email, '([^ ,;<@]+@[^> ,;]+)')) = LOWER(substring('{}', '([^ ,;<@]+@[^> ,;]+)'))""".format(email)
        self._cr.execute(query)
        return self._cr.fetchone() or False

    @api.model
    def create(self, vals):
        res = super(massMailingContact, self).create(vals)
        if vals.get('email', False):
            partner_record = self.get_partner_for_sb(vals.get('email'))
            res.related_partner_id = partner_record
        return res

    #@api.multi
    def write(self, vals):
        if vals.get('email', False) and not self._context.get('do_not_update', False):
            partner_record = self.get_partner_for_sb(vals.get('email'))
            vals.update({'related_partner_id': partner_record})
        res = super(massMailingContact, self).write(vals)
        return res

    @api.depends('subscription_list_ids', 'subscription_list_ids.sendinblue_id', 'subscription_list_ids.list_id')
    def _get_sendinblue_pending_for_export(self):
        available_sendinblue_lists = self.env['sendinblue.lists'].search([])
        lists = available_sendinblue_lists.mapped('odoo_list_id').ids
        for record in self:
            if record.subscription_list_ids.filtered(lambda x: x.list_id.id in lists and not x.sendinblue_id):
                record.sendinblue_pending_for_export = True
            else:
                record.sendinblue_pending_for_export = False

    @api.depends('email')
    def _compute_related_partner_id(self):
        for record in self:
            query = """
            SELECT id 
              FROM res_partner
            WHERE LOWER(substring(email, '([^ ,;<@]+@[^> ,;]+)')) = LOWER(substring('{}', '([^ ,;<@]+@[^> ,;]+)'))""".format(record.email)
            self._cr.execute(query)
            partner_record = self._cr.fetchone()
            if partner_record:
                record.related_partner_id = partner_record[0]
            else:
                record.related_partner_id = False

    @api.depends('email')
    def _compute_is_email_valid(self):
        for record in self:
            record.is_email_valid = re.match(EMAIL_PATTERN, record.email or '')

    sendinblue_id = fields.Char('SendinBlue ID')
    sendinblue_pending_for_export = fields.Boolean(compute="_get_sendinblue_pending_for_export", string="Pending For Export", store=True)
    related_partner_id = fields.Many2one('res.partner', 'Related Customer', help='Display related customer by matching Email address.')
    is_email_valid = fields.Boolean(compute='_compute_is_email_valid', store=True)

    def _sendinblue_prepare_vals_for_merge_fields(self, account_id):
        self.ensure_one()
        merge_fields_vals = {}
        partner_id = self.related_partner_id
        for custom_field in account_id.merge_field_ids:
            if custom_field.name == 'FIRSTNAME':
                first_name = _partner_split_name(self.name)[0] if _partner_split_name(self.name)[0] else _partner_split_name(self.name)[1]
                merge_fields_vals.update({custom_field.name: first_name})
                if custom_field.field_id:
                    merge_fields_vals.update({custom_field.name: getattr(partner_id or self, custom_field.field_id.name) if custom_field.field_id and hasattr(partner_id or self, custom_field.field_id.name) else first_name})
            elif custom_field.name == 'LASTNAME':
                last_name = _partner_split_name(self.name)[1] if _partner_split_name(self.name)[0] else _partner_split_name(self.name)[0]
                merge_fields_vals.update({custom_field.name: last_name})
                if custom_field.field_id:
                    merge_fields_vals.update({custom_field.name: getattr(partner_id or self, custom_field.field_id.name) if custom_field.field_id and hasattr(partner_id or self, custom_field.field_id.name) else last_name})
            else:
                value = getattr(partner_id or self, custom_field.field_id.name) if custom_field.field_id and hasattr(partner_id or self, custom_field.field_id.name) else ''
                merge_fields_vals.update({custom_field.name: value or ''})
        return merge_fields_vals

    #@api.multi
    def action_export_to_sendinblue(self):
        """
        Export contact and update in sendinblue
        :return:
        """
        exported_contacts = self.env['mailing.contact'] #v13
        for record in self:
            if record.sendinblue_id:
                record.action_update_to_sendinblue()
                continue
            account_ids = record.subscription_list_ids.mapped('list_id').mapped('sendinblue_list_id').mapped('account_id')
            for ex_account in account_ids:
                sb_list_ids = record.subscription_list_ids.mapped('sendinblue_list_id').filtered(lambda x : x.account_id == ex_account)
                sb_list_ids = sb_list_ids.mapped('list_id')
                merge_fields_vals = record._sendinblue_prepare_vals_for_merge_fields(ex_account)
                list_ids = list(map(int, sb_list_ids))
                prepared_vals = {"email": record.email.lower(),
                                 "listIds": list_ids,
                                 'attributes': merge_fields_vals}
                response = ex_account._send_request('contacts', prepared_vals, method='POST')
                if response.get('id', False):
                    record.write({'sendinblue_id': response.get('id', False),'sendinblue_pending_for_export' : True})
                    exported_contacts += record
        return exported_contacts

    #@api.multi
    def action_update_to_sendinblue(self):
        updated_contacts = self.env['mailing.contact'] #v13
        for record in self:
            account_ids = record.subscription_list_ids.mapped('list_id').mapped('sendinblue_list_id').mapped('account_id')
            for ex_account in account_ids:
                sb_list_ids = record.subscription_list_ids.mapped('sendinblue_list_id').filtered(lambda x : x.account_id == ex_account)
                sb_list_ids = sb_list_ids.mapped('list_id')
                list_ids = list(map(int, sb_list_ids))
                merge_fields_vals = record._sendinblue_prepare_vals_for_merge_fields(ex_account)
                prepared_vals = {"email": record.email.lower(),
                                 "listIds": list_ids,
                                 'attributes': merge_fields_vals}
                response = ex_account._send_request('contacts/%s' % (record.email), prepared_vals, method='PUT')
                updated_contacts += record
        return updated_contacts

    def _prepare_statistics_vals(self, res, contact):
        mass_malling_obj = self.env['mailing.mailing'] #v13
        vals = {}
        mass_malling_id = False
        if res.get('messagesSent', False):
            for sent_dict in res.get('messagesSent', []):
                mass_malling_id = mass_malling_obj.search([('sendinblue_id', '=', sent_dict.get('campaignId'))],
                                                          limit=1)
                event_datetime = dateutil.parser.parse(sent_dict.get('eventTime'))
                event_date = event_datetime.astimezone(timezone('UTC')).strftime('%Y-%m-%d %H:%M:%S')
                vals.update({'sent': event_date, 'scheduled': event_date, 'bounced': False})
                self._create_statistics_record(mass_malling_id,contact,vals)
        if res.get('hardBounces', False) or res.get('softBounces', False):
            bounces_records = res.get('hardBounces', []) + res.get('softBounces', [])
            for sent_dict in bounces_records:
                mass_malling_id = mass_malling_obj.search([('sendinblue_id', '=', sent_dict.get('campaignId'))],
                                                          limit=1)
                event_datetime = dateutil.parser.parse(sent_dict.get('eventTime'))
                event_date = event_datetime.astimezone(timezone('UTC')).strftime('%Y-%m-%d %H:%M:%S')
                vals.update({'bounced': event_date, 'sent': event_date, 'scheduled': event_date})
                self._create_statistics_record(mass_malling_id, contact, vals)
        if res.get('opened', False):
            for sent_dict in res.get('opened', []):
                mass_malling_id = mass_malling_obj.search([('sendinblue_id', '=', sent_dict.get('campaignId'))],
                                                          limit=1)
                event_datetime = dateutil.parser.parse(sent_dict.get('eventTime'))
                event_date = event_datetime.astimezone(timezone('UTC')).strftime('%Y-%m-%d %H:%M:%S')
                vals.update({'opened': event_date})
                self._create_statistics_record(mass_malling_id, contact, vals)
        if res.get('clicked', False):
            # for sent_dict in res.get('clicked', []):
            for sent_dict_links in res.get('clicked', []):
                for sent_dict in sent_dict_links.get('links', []):
                    mass_malling_id = mass_malling_obj.search([('sendinblue_id', '=', sent_dict.get('campaignId'))],limit=1)
                    if not mass_malling_id:
                        continue
                    event_datetime = dateutil.parser.parse(sent_dict.get('eventTime'))
                    event_date = event_datetime.astimezone(timezone('UTC')).strftime('%Y-%m-%d %H:%M:%S')
                    vals.update({'clicked': event_date})
                    self._create_statistics_record(mass_malling_id, contact, vals)

        return True

    def _create_statistics_record(self, mass_malling_id, contact, vals):
        stat_obj = self.env['mailing.trace']
        if mass_malling_id:
            exist = self.env['mailing.trace'].search([('mass_mailing_id','=',mass_malling_id.id),('email','=',contact.email)])
            if exist:
                exist.write(vals)
            else:
                res_id = self.env[mass_malling_id.mailing_model_real].search_read([('email', '=', contact.email)], ['email'], limit=1)
                res_id = res_id and res_id[0]['id'] or False
                vals.update({
                    'model': mass_malling_id.mailing_model_real,
                    'res_id': res_id,
                    'mass_mailing_id': mass_malling_id.id,
                    'email': contact.email,
                })
                stat_obj.create(vals)
        return True

    #@api.multi
    def fetch_email_statistics(self,account):
        """
        Use to fetch statistics vals from sendinblue by contact
        :param account: sendinblue account
        :return: current record
        """
        for rec in self:
            res = account._send_request('contacts/{}/campaignStats'.format(rec.email.lower()), {}, method='GET')
            self._prepare_statistics_vals(res, rec)
        return self