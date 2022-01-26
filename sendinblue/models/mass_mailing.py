import logging
from odoo.tools.safe_eval import safe_eval
from odoo import api, fields, models, tools, _
from odoo.exceptions import Warning, ValidationError, UserError
from email.utils import formataddr, parseaddr
import dateutil
from pytz import timezone

_logger = logging.getLogger(__name__)

REPLACEMENT_OF_KEY = [('id', 'sendinblue_id'), ('create_time', 'create_date'), ('send_time', 'sent_date'),
                      ('type', 'sendinblue_champ_type')]
DATE_CONVERSION = ['createdAt','scheduledAt']
UNWANTED_DATA = ['_links', 'created_by', 'edited_by', 'thumbnail']


class MassMailing(models.Model):
    _inherit = "mailing.mailing" #v13


    createdAt = fields.Datetime("Created on", readonly=True, index=True)
    sentAt = fields.Datetime("Sent on", readonly=True, index=True)
    sendinblue_template_id = fields.Many2one('sendinblue.templates', "SendinBlue Template", copy=False)
    sendinblue_id = fields.Char("SendinBlue ID", copy=False)
    sendinblue_champ_type = fields.Selection(
        [('classic', 'Classic'), ('plaintext', 'Plain Text'), ('absplit', 'AB Split'), ('rss', 'RSS'),
         ('variate', 'Variate')],
        default='classic', string="Type")
    sb_sender_id = fields.Many2one('sendinblue.senders','Sender Emails',copy=False)
    sendinblue_account_id = fields.Many2one('sendinblue.accounts', string="SendinBlue Account")
    sendinblue_body_html = fields.Html('SendinBlue Body', related='sendinblue_template_id.htmlcontent',store=True)

    @api.onchange('sb_sender_id')
    def _onchange_sb_sender_id(self):
        for rec in self:
            if rec.sb_sender_id:
                rec.email_from = formataddr((rec.sb_sender_id.name, rec.sb_sender_id.email))
                rec.reply_to = formataddr((rec.sb_sender_id.name, rec.sb_sender_id.email))

    @api.onchange('sendinblue_template_id')
    def _onchange_sendinblue_template_id(self):
        for rec in self:
            if rec.sendinblue_template_id:
                rec.sb_sender_id = rec.sendinblue_template_id and rec.sendinblue_template_id.sb_sender_id or False
                rec.email_from = formataddr((rec.sb_sender_id.name, rec.sb_sender_id.email))
                rec.reply_to = formataddr((rec.sb_sender_id.name, rec.sb_sender_id.email))
                rec.sendinblue_account_id = rec.sendinblue_template_id.account_id and rec.sendinblue_template_id.account_id.id or False

    # @api.multi
    def create_queue_for_fetch_email_activity(self):
        self.ensure_one()
        queue_process_obj = self.env['sendinblue.queue.process']
        queue_process_ids = queue_process_obj
        account = self.sendinblue_template_id.account_id or self.sendinblue_account_id or False
        if not account:
                raise UserError(_("SendinBlue account isn't found on available template. Please import/reimport SendinBlue template first!"))
        exist_ids = queue_process_obj.search([('state','in',['in_queue']),('campaign_id', '=', self.id), ('account_id','=',account.id), ('operation', '=', 'campaign_activity_report')])
        if exist_ids:
            queue_process_ids += exist_ids
        else:
            prepared_vals = {'campaign_id': self.id,
                             'operation': 'campaign_activity_report',
                             'account_id': account and account.id or False,
                             }
            queue_process_ids += queue_process_obj.create(prepared_vals)
        return queue_process_ids

    # @api.multi
    def create_or_update_campaigns(self, values_dict, account=False):
        fetch_needed = False
        odoo_list_ids = self.env['mailing.list'] #v13
        send_list_obj = self.env['sendinblue.lists']
        sendinblue_id = values_dict.get('id')
        recipients_dict = values_dict.get('recipients')
        list_ids = recipients_dict.get('lists')
        if list_ids:
            odoo_list_ids = send_list_obj.search([('list_id', 'in', list_ids)]).mapped('odoo_list_id')
        status = values_dict.get('status')
        subject_line = values_dict.get('subject')
        try:
            email_from = formataddr((values_dict.get('sender').get('email'), values_dict.get('replyTo')))
        except Exception as e:
            email_from = self.env['mail.message']._get_default_from()
        for item in DATE_CONVERSION:
            if values_dict.get(item, False) == '':
                values_dict[item] = False
            if values_dict.get(item, False):
                values_dict[item] = account.covert_date(values_dict.get(item))
        prepared_vals = {
            'createdAt': values_dict.get('createdAt') or False,
            'sentAt': values_dict.get('scheduledAt') or False, #maybe unuseble field
            'sent_date': values_dict.get('scheduledAt') or False,
            'subject': subject_line or values_dict.get('name',' '),
            'sendinblue_id': sendinblue_id,
            'mailing_model_id': self.env.ref('mass_mailing.model_mailing_list').id,
            'contact_list_ids': [(6, 0, odoo_list_ids.ids)],
            'sendinblue_champ_type': values_dict.get('type'),
            'email_from': email_from,
            'reply_to': email_from,
            'sendinblue_account_id': account and account.id or False,
        }
        if status in ['draft']:
            prepared_vals.update({'state': 'draft'})
        elif status == 'queued':
            prepared_vals.update({'state': 'in_queue'})
            fetch_needed = True
        # elif status == 'sending':
        #     prepared_vals.update({'state': 'sending'})
        elif status == 'sent':
            if not self.state == 'done':
                fetch_needed = True
            prepared_vals.update({'state': 'done'})
        # for item in DATE_CONVERSION:
        #     if prepared_vals.get(item, False) == '':
        #         prepared_vals[item] = False
        #     if prepared_vals.get(item, False):
        #         prepared_vals[item] = account.covert_date(prepared_vals.get(item))
        existing_list = self.search([('sendinblue_id', '=', sendinblue_id)])
        if not existing_list:
            existing_list = self.create(prepared_vals)
            self.env.cr.execute("""
                           UPDATE
                           mailing_mailing
                           SET create_date = '%s'
                           WHERE id = %s
                           """ % (prepared_vals.get('createdAt'), existing_list.id))
        else:
            existing_list.write(prepared_vals)
        existing_list._onchange_model_and_list()
        existing_list.body_html = False
        if fetch_needed:
            existing_list.create_queue_for_fetch_email_activity()
        return True

    # @api.multi
    def fetch_campaign(self):
        self.ensure_one()
        if not self.sendinblue_id:
            return True
        account = self.sendinblue_template_id.account_id or self.sendinblue_account_id or False
        response = account._send_request('emailCampaigns/%s' % self.sendinblue_id, {})
        self.create_or_update_campaigns(response, account=account)
        return True

    # @api.multi
    def import_campaigns(self, account=False):
        if not account:
            raise Warning("sendinblue Account not defined to import Campaigns")
        count = 1000
        offset = 0
        campaigns_list = []
        while True:
            prepared_vals = {'limit': count, 'offset': offset}
            response = account._send_request('emailCampaigns', {}, params=prepared_vals)
            if len(response.get('campaigns',[])) == 0:
                break
            if isinstance(response.get('campaigns'), dict):
                campaigns_list += [response.get('campaigns')]
            campaigns_list += response.get('campaigns')
            offset = offset + 1000
        for campaigns_dict in campaigns_list:
            self.create_or_update_campaigns(campaigns_dict, account=account)
        return True

    @api.model
    def _prepare_vals_for_exportIN_sb(self):
        self.ensure_one()
        from_name, from_email = parseaddr(self.email_from)
        reply_to_name, reply_to_email = parseaddr(self.reply_to)
        for sb_list in self.contact_list_ids.mapped('sendinblue_list_id'):
            if not sb_list.list_id:
                sb_list.export_in_sendinblue()
        settings_dict = {
                            'subject': self.name,
                            'sender': {'name': from_name,'email':from_email,},
                            'name': self.name,
                            'from_name': from_name,
                            'replyTo': reply_to_email,
                            # 'templateId': int(self.sendinblue_template_id.template_id),
                            'recipients' : {'listIds' : list(map(int,self.contact_list_ids.mapped('sendinblue_list_id').mapped('list_id')))},
                            'htmlContent' : self.sendinblue_body_html  #comment becuase got warning we can not set html content with template id
        }
        return settings_dict

    # @api.one
    def export_to_sendinblue(self, account=False):
        if self.sendinblue_id:
            return True
        if not account:
            raise Warning("sendinblue Account not defined in selected Template.")
        prepared_vals = self._prepare_vals_for_exportIN_sb()
        response = account._send_request('emailCampaigns', prepared_vals, method='POST')
        if response.get('id', False):
            self.write({'sendinblue_id': response['id']})
        else:
            ValidationError(_("sendinblue Identification wasn't received. Please try again!"))
        self._cr.commit()
        return True

    # @api.one
    def send_now_sendinblue(self, account=False):
        if not account:
            raise Warning("sendinblue Account not defined in selected Template.")
        response = account._send_request('emailCampaigns/{}/sendNow'.format(self.sendinblue_id), {}, method='POST')
        return True

    #@api.multi
    def send_test_mail_sendinblue(self, test_emails):
        self.ensure_one()
        self.export_to_sendinblue(self.sendinblue_template_id.account_id)
        prepared_vals = {'emailTo': [test_emails]}
        response = self.sendinblue_template_id.account_id._send_request('emailCampaigns/%s/sendTest' % self.sendinblue_id,
                                                                       prepared_vals, method='POST')
        return True

    #@api.multi
    def schedule_sendinblue_champaign(self, schedule_date):
        self.ensure_one()
        self.export_to_sendinblue(self.sendinblue_template_id.account_id)
        prepared_vals = {'scheduledAt': schedule_date.strftime('%Y-%m-%dT%H:%M:%S.%f')}
        response = self.sendinblue_template_id.account_id._send_request('emailCampaigns/%s' % self.sendinblue_id,prepared_vals, method='PUT')
        return True

    #@api.multi
    def cancel_mass_mailing(self):
        res = super(MassMailing, self).cancel_mass_mailing()
        if self.sendinblue_id and self.sendinblue_template_id:
            prepared_vals = {'status': 'suspended'}
            self.sendinblue_template_id.account_id._send_request('emailCampaigns/%s/status' % self.sendinblue_id,prepared_vals, method='PUT')
        return res

    #@api.multi
    def action_put_in_queue(self):
        res = super(MassMailing, self).action_put_in_queue()
        for record in self.filtered(lambda x: x.sendinblue_template_id):
            if len(record.contact_list_ids) > 1:
                raise ValidationError(_("Multiple list is not allowed while going with sendinblue!"))
            if record.contact_list_ids.filtered(lambda x: not x.sendinblue_list_id):
                raise ValidationError(_("Please provide sendinblue list as you selected sendinblue Template!"))
            record.export_to_sendinblue(record.sendinblue_template_id.account_id)
            if record.sendinblue_id:
                record.send_now_sendinblue(record.sendinblue_template_id.account_id)
                record.fetch_campaign()
        return res

    @api.model
    def _process_mass_mailing_queue(self):
        mass_mailings = self.search(
            [('state', 'in', ('in_queue', 'sending')), '|', ('schedule_date', '<', fields.Datetime.now()),
             ('schedule_date', '=', False)])
        for mass_mailing in mass_mailings:
            user = mass_mailing.write_uid or self.env.user
            mass_mailing = mass_mailing.with_context(**user.sudo(user).context_get())
            if mass_mailing.sendinblue_id:
                mass_mailing.fetch_campaign()
                continue
            if len(mass_mailing._get_remaining_recipients()) > 0:
                mass_mailing.state = 'sending'
                mass_mailing.action_send_mail()
            else:
                mass_mailing.write({'state': 'done', 'sent_date': fields.Datetime.now()})

    #@api.multi
    def unlink(self):
        for rec in self:
            rec.mailing_trace_ids.unlink()
            if rec.state not in ['sending','done'] and rec.sendinblue_id and rec.sendinblue_template_id:
                rec.sendinblue_template_id.account_id._send_request('emailCampaigns/%s' % rec.sendinblue_id, {},method='DELETE')
        return super(MassMailing, self).unlink()