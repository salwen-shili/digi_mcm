import logging
import hashlib
from odoo import api, fields, models, _
from odoo.tools.safe_eval import safe_eval
_logger = logging.getLogger(__name__)

EMAIL_PATTERN = '([^ ,;<@]+@[^> ,;]+)'
replacement_of_key = [('id', 'list_id')]
DATE_CONVERSION = ['date_created', 'last_sub_date', 'last_unsub_date', 'campaign_last_sent']


class MassMailingList(models.Model):
    _inherit = "mailing.list" #v13

    def _compute_contact_nbr(self):
        #v13
        self.env.cr.execute('''
            select
                list_id, count(*)
            from
                mailing_contact_list_rel r
                left join mailing_contact c on (r.contact_id=c.id)
                left join mail_blacklist bl on (LOWER(substring(c.email, %s)) = bl.email and bl.active)
            where
                list_id in %s AND
                COALESCE(r.opt_out,FALSE) = FALSE
                AND c.is_email_valid = TRUE
                AND c.email IS NOT NULL
            group by
                list_id
        ''', [EMAIL_PATTERN, tuple(self.ids)])
        data = dict(self.env.cr.fetchall())
        for mailing_list in self:
            mailing_list.contact_nbr = data.get(mailing_list.id, 0)

    contact_nbr = fields.Integer(compute="_compute_contact_nbr", string='Number of Contacts')


class sendinblueLists(models.Model):
    _name = "sendinblue.lists"
    _inherits = {'mailing.list': 'odoo_list_id'} #v13
    _description = "sendinblue Audience"

    def _compute_contact_total_nbr(self):
        #v13
        self.env.cr.execute('''
            select
                list_id, count(*)
            from
                mailing_contact_list_rel r
                left join mailing_contact c on (r.contact_id=c.id)
                left join mail_blacklist bl on (LOWER(substring(c.email, %s)) = bl.email and bl.active)
            where
                list_id in %s
                AND c.email IS NOT NULL
            group by
                list_id
        ''', [EMAIL_PATTERN, tuple(self.odoo_list_id.ids)])
        data = dict(self.env.cr.fetchall())
        for mailing_list in self:
            mailing_list.contact_total_nbr = data.get(mailing_list.odoo_list_id.id, 0)


    color = fields.Integer('Color Index', default=0)
    partner_id = fields.Many2one('res.partner', string="Contact", ondelete='restrict')
    list_id = fields.Char("SendINBlue Audience ID", copy=False, readonly=True)
    totalsubscribers = fields.Integer('Total Subscribers', default=0)
    totalblacklisted = fields.Integer('Total Blacklisted', default=0)
    folder_id = fields.Many2one('sendinblue.folder','Folder')
    date_created = fields.Datetime("Creation Date", readonly=True)
    odoo_list_id = fields.Many2one('mailing.list',required=True, string='Odoo Mailing List',ondelete="cascade") #v13
    contact_total_nbr = fields.Integer(compute="_compute_contact_total_nbr", string='Number of Total Contacts')
    account_id = fields.Many2one("sendinblue.accounts", string="Account", required=True)
    last_create_update_date = fields.Datetime("Last Create Update")
    write_date = fields.Datetime('Update on', index=True, readonly=True)
    member_since_last_changed = fields.Datetime("Fetch Member Since Last Change", copy=False)

    @api.model
    def create(self, vals):
        if vals.get('name',False):
            odoo_list_id = self.env['mailing.list'].search([('name', '=', vals.get('name'))],limit=1)
            if not odoo_list_id:
                odoo_list_id = self.env['mailing.list'].create({'is_public':True,'name':vals.get('name')}) #v13
            vals.update({'odoo_list_id':odoo_list_id.id})
        return super(sendinblueLists, self).create(vals)

    # @api.multi
    def write(self, vals):
        res = super(sendinblueLists, self).write(vals)
        sendblue_vals = {}
        if vals.get('name',False):
            for record in self:
                record.odoo_list_id.write({'name':vals.get('name')})
        if not self._context.get('no_update',False):
            for rec in self.filtered(lambda x: x.list_id):
                if 'name' in vals:
                    sendblue_vals.update({'name':rec.name})
                if 'folder_id' in vals:
                    sendblue_vals.update({'name': rec.name,'folderId': int(rec.folder_id.sendinblue_id)})
                if sendblue_vals:
                    rec.update_in_sendinblue(sendblue_vals)
        return res


    def action_view_recipients(self):
        action = self.env.ref('mass_mailing.action_view_mass_mailing_contacts').read()[0]
        action['domain'] = [('list_ids', 'in', self.odoo_list_id.ids)]
        ctx = {'default_list_ids': [self.odoo_list_id.id]}
        if self.env.context.get('show_total', False):
            action['context'] = ctx
        if self.env.context.get('show_black', False):
            ctx.update({'search_default_black_contact': 1})
            action['context'] = ctx
        return action

    def create_queue_for_export_list_contacts(self):
        queue_process_obj = self.env['sendinblue.queue.process']
        for rec in self:
            prepared_vals = {'list_id': rec.id,
                             'operation': 'pending_to_export_contact',
                             'account_id': rec.account_id.id,
                             }
            queue_process_id = queue_process_obj.create(prepared_vals)
        return True


    # @api.multi
    def export_in_sendinblue(self):
        for sb_list in self:
            if sb_list.folder_id and not sb_list.folder_id.sendinblue_id:
                sb_list.folder_id.export_folder_sendinblue()
            prepared_vals =  {'name':self.name,'folderId':int(self.folder_id.sendinblue_id)}
            response = sb_list.account_id._send_request('contacts/lists', prepared_vals, method='POST')
            sb_list.list_id = response.get('id')
            if sb_list.contact_ids:
                # sb_list.create_queue_for_export_list_contacts()
                queue_ids = sb_list.create_queue_for_export_list_contacts()
                queue_ids.sendinblue_process_queue()
        return True

    # @api.multi
    def update_in_sendinblue(self, vals={}):
        self.ensure_one()
        self.account_id._send_request('contacts/lists/%s' % self.list_id, vals, method='PUT')
        self.write({'last_create_update_date': fields.Datetime.now()})
        return True

    # @api.multi
    def create_or_update_list(self, values_dict, account=False):
        list_vals = {}
        sendinblue_folder_obj = self.env['sendinblue.folder']
        list_id = values_dict.get('id')
        totalsubscribers = values_dict.pop('totalSubscribers')
        totalblacklisted = values_dict.pop('totalBlacklisted')
        folderid = values_dict.pop('folderId')
        # createdAt = values_dict.get('createdAt',False) and values_dict.pop('createdAt') or False
        # dynamicList = values_dict.pop('dynamicList',False) and values_dict.pop('dynamicList') or False
        folder_id = sendinblue_folder_obj.search([('sendinblue_id','=',folderid),('account_id','=',account.id)],limit=1)
        if not folder_id and account:
            account.import_folders()
            folder_id = sendinblue_folder_obj.search([('sendinblue_id', '=', folderid),('account_id','=',account.id)], limit=1)

        existing_list = self.search([('list_id', '=', list_id)])
        # for old_key, new_key in replacement_of_key:
        #     values_dict[new_key] = values_dict.pop(old_key)
        # for item in DATE_CONVERSION:
        #     if values_dict.get(item, False) == '':
        #         values_dict[item] = False
        #     if values_dict.get(item, False):
        #         values_dict[item] = account.covert_date(values_dict.get(item))
        # values_dict.update({'account_id': account.id,'totalsubscribers':totalsubscribers,'totalblacklisted':totalblacklisted,'folder_id':folder_id.id})
        list_vals.update({'name':values_dict.get('name',' '),'list_id':list_id,'account_id': account.id,'totalsubscribers':totalsubscribers,'totalblacklisted':totalblacklisted,'folder_id':folder_id.id})
        if not existing_list:
            existing_list = self.create(list_vals)
        else:
            list_vals.update({'list_id': list_id})
            existing_list.with_context(no_update=True).write(list_vals)
        existing_list.create_queue_for_fetch_member()
        existing_list.write({'last_create_update_date': fields.Datetime.now()})
        return True

    # @api.multi
    def import_lists(self, account=False):
        if not account:
            raise Warning("SendinBlue Account not defined to import lists")
        offset = 0
        limit = 10
        while True:
            prepared_vals = {'limit': limit, 'offset': offset}
            response = account._send_request('contacts/lists', {}, method='GET', params=prepared_vals)
            if len(response.get('lists', [])) == 0:
                break
            for rec_dict in response.get('lists', []):
                self.create_or_update_list(rec_dict, account=account)
                self._cr.commit()
            offset = offset + 10
        account.fetch_merge_fields()
        return True

    # @api.one
    def refresh_list(self):
        for rec in self:
            if not rec.account_id:
                raise Warning("SendinBlue Account not defined to Refresh list")
            response = rec.account_id._send_request('contacts/lists/%s' % rec.list_id, {})
            rec.create_or_update_list(response, account=rec.account_id)
        for folder in self.mapped('folder_id'):
            folder.refresh_folder()
        return True

    def _prepare_vals_for_to_create_partner(self, vals):
        merge_field_vals = vals.get('attributes')
        prepared_vals = {}
        for custom_field in self.account_id.merge_field_ids:
            if custom_field.field_id and custom_field.name in ['FIRSTNAME', 'LASTNAME']:
                prepared_vals.update({custom_field.field_id.name: merge_field_vals.get(custom_field.name)})
            if custom_field.name in ['FIRSTNAME', 'LASTNAME'] and not prepared_vals.get('name', False):
                prepared_vals.update({'name': "%s %s" % (merge_field_vals.get('FIRSTNAME',''), merge_field_vals.get('LASTNAME',''))})
            elif custom_field.field_id:
                prepared_vals.update({custom_field.field_id.name: merge_field_vals.get(custom_field.name)})
        return prepared_vals

    def process_fetch_member_queue(self, pending_record):
        if not pending_record.pending_res_data:
            return True
        members_data = safe_eval(pending_record.pending_res_data)
        mail_blacklist_obj = self.env['mail.blacklist']
        mailing_contact_obj = self.env['mailing.contact']
        count = 0
        # member_count = 0
        while members_data:
            for member in members_data[:100]:
                if not member.get('email', False):
                    continue
                attributes = member.get('attributes')
                update_partner_required = True
                contact_id = mailing_contact_obj.search([('email', '=', member.get('email'))])
                if attributes.get('LASTNAME', '') or attributes.get('FIRSTNAME', ''):
                    name = "%s %s" % (attributes.get('LASTNAME', ''), attributes.get('FIRSTNAME', ''))
                else:
                    name = member.get('email',' ')
                emailBlacklisted = member.get('emailBlacklisted')
                blacklisted_mail = mail_blacklist_obj.search([('email','ilike',member.get('email'))])
                prepared_vals_for_create_partner = self._prepare_vals_for_to_create_partner(member)
                prepared_vals_for_create_partner.update({'sendinblue_id': member.get('id')})
                if blacklisted_mail and emailBlacklisted:
                    blacklisted_mail.active = 'True'
                elif blacklisted_mail and not emailBlacklisted:
                    blacklisted_mail.active = 'False'
                elif not blacklisted_mail and emailBlacklisted:
                    mail_blacklist_obj.create({'email':member.get('email'),'active':True})
                if not contact_id:
                    if not self.account_id.auto_create_member:
                        continue
                    self.update_partner_detail(name, member.get('email'), prepared_vals_for_create_partner)
                    update_partner_required = False
                    contact_id = mailing_contact_obj.create(
                        {'name': name,
                         'email': member.get('email'),
                         'is_blacklisted':emailBlacklisted,
                         'sendinblue_id':member.get('id',False)})
                if contact_id:
                    md5_email = hashlib.md5(member.get('email').encode('utf-8')).hexdigest()
                    if update_partner_required:
                        self.update_partner_detail(name, member.get('email'), prepared_vals_for_create_partner)
                    vals = {'list_id': self.odoo_list_id.id, 'contact_id': contact_id.id,
                            'sendinblue_id': member.get('id'), 'sendinblue_md5_email': md5_email}
                    existing_define_list = contact_id.subscription_list_ids.filtered(
                        lambda x: x.list_id.id == self.odoo_list_id.id)
                    # vals.update({'opt_out': True}) if member.get('emailBlacklisted',False) else vals.update({'opt_out': False})
                    # if existing_define_list:
                    #     existing_define_list.write(vals)
                    # else:
                    if not existing_define_list:
                        contact_id.subscription_list_ids.create(vals)
                    # member_count += 1
                    # _logger.info("## Member Count : %s" % (member_count))
            del members_data[:100]
            count += 100
            pending_record.write({'pending_res_data': members_data})
            self._cr.commit()
            _logger.info("## SendinBlue Process Fetch Members For %s : CURRENTLY PROCESSED RECORD COUNT : %s" % (pending_record.name, count))
        return True

    # @api.one
    def create_queue_for_fetch_member(self):
        queue_process_obj = self.env['sendinblue.queue.process']
        queue_process_ids = queue_process_obj
        exist_queue = queue_process_obj.search([('list_id','=',self.id),('state','=','in_queue')])
        if exist_queue:
            queue_process_ids += exist_queue
            return queue_process_ids
        if not self.account_id:
            raise Warning("SendinBlue Account not defined to Fetch Member list")
        res_data = []
        prepared_vals = {}
        limit = 500
        offset = 0
        if self.member_since_last_changed:
            prepared_vals.update({'since_last_changed': self.member_since_last_changed.strftime("%Y-%m-%dT%H:%M:%S+00:00")})
        while True:
            prepared_vals.update({'limit': limit, 'offset': offset})
            response = self.account_id._send_request('contacts/lists/%s/contacts' % self.list_id, {}, params=prepared_vals)
            if len(response.get('contacts')) == 0:
                break
            if isinstance(response.get('contacts'), dict):
                members_data = [response.get('contacts')]
            else:
                members_data = response.get('contacts')
            res_data += members_data
            queue_process_ids += queue_process_obj.create(
                                {
                                  'response_data': res_data,
                                  'list_id': self.id,
                                  'operation': 'fetch_member',
                                  'account_id': self.account_id.id,
                                }
            )
            offset = offset + 500
        self.write({'member_since_last_changed': fields.Datetime.now()})
        return queue_process_ids

    # @api.multi
    def update_partner_detail(self, name, email, partner_detail):
        query = """
                        SELECT id 
                          FROM res_partner
                        WHERE LOWER(substring(email, '([^ ,;<@]+@[^> ,;]+)')) = LOWER(substring('{}', '([^ ,;<@]+@[^> ,;]+)'))""".format(
            email)
        self._cr.execute(query)
        partner_id = self._cr.fetchone()
        partner_id = partner_id[0] if partner_id else False
        if partner_id:
            partner_id = self.env['res.partner'].browse(partner_id)
            if partner_detail:
                partner_id.with_context(no_update=True).write(partner_detail)
        else:
            if self.account_id.auto_create_member and self.account_id.auto_create_partner:
                partner_detail.update({
                    'email': email,
                    'is_company': False,
                    'type': 'contact',
                })
                self.env['res.partner'].create(partner_detail)
        return True

    # @api.multi
    def fetch_members(self):
        'called when click on fetch member button from list from view'
        for record in self:
            record.create_queue_for_fetch_member()

    @api.model
    def fetch_member_cron(self):
        'called using cron'
        for record in self.search([]):
            if record.account_id and record.account_id.auto_refresh_member:
                record.create_queue_for_fetch_member()
        return True

    # @api.multi
    def unlink(self):
    #     for record in self.filtered(lambda x: x.list_id):
    #         record.account_id._send_request('contacts/lists/%s' % record.list_id, {}, method='DELETE')
        self.mapped('odoo_list_id').unlink()
        return super(sendinblueLists, self).unlink()
