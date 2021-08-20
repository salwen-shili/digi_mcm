import logging
from odoo import fields, api, models, _
from odoo.tools.safe_eval import safe_eval
_logger = logging.getLogger(__name__)


class SendINblueQueueProcess(models.Model):
    _name = "sendinblue.queue.process"
    _order = 'id desc'
    _description = 'SendinBlue Queue Process'

    _get_queue_state = [('in_queue', 'In Queue'),('done', 'Done')]

    name = fields.Char('Name', required=1, default=lambda self: _('New'))
    create_date = fields.Datetime("Create Date")
    account_id = fields.Many2one("sendinblue.accounts", string="Account", ondelete='cascade')
    operation = fields.Selection([('pending_to_export_contact', 'Export Contacts'),
                                  ('fetch_member', 'Fetch Member SendinBlue'),
                                  ('campaign_activity_report', 'Campaign and Activity Report')], string="Operation")
    list_id = fields.Many2one("sendinblue.lists", string="SendinBlue List", ondelete='cascade', copy=False)
    processed_contact_ids = fields.Many2many('mailing.contact', 'mailing_contact_sendinblue_queue_rel','queue_id', 'contact_id', string='Processed Contacts') #v13
    campaign_id = fields.Many2one("mailing.mailing", string="Campaign", ondelete='cascade', copy=False) #v13
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user, copy=False)
    state = fields.Selection(_get_queue_state, default='in_queue', string='State', readonly=True)
    response_data = fields.Text('Response Data', copy=False, readonly=True)
    pending_res_data = fields.Text('Pending Response Data', copy=False, readonly=True)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            if 'company_id' in vals:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code(
                    'sendinblue.queue.process') or _('New')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('sendinblue.queue.process') or _('New')
        if vals.get('response_data'):
            vals.update({'pending_res_data': vals.get('response_data')})
        return super(SendINblueQueueProcess, self).create(vals)

    #@api.multi
    def sendinblue_create_queue(self):

        """Called using cron job for fetch infomation of campian and email activity"""
        if not self.env['sendinblue.accounts'].search([]):
            return True
        _logger.info('--------Stared cron for fetch email activity------------')
        mass_malling_obj = self.env['mailing.mailing'] #v13
        mass_malling_ids = mass_malling_obj.search([('state', 'in', ['in_queue','done', 'sending']), ('sendinblue_id', '!=', False)])
        exist_ids = self.search([('state','in',['in_queue']),('campaign_id','in',mass_malling_ids.ids)])
        mass_malling_ids -= exist_ids.mapped('campaign_id') or mass_malling_obj
        for record in mass_malling_ids:
            record.create_queue_for_fetch_email_activity()
        self._cr.commit()
        _logger.info('--------End cron for fetch email activity------------')
        return True

    #@api.multi
    def process_pending_to_export_contact(self):
        export_contact_list = self or self.search([('operation','=','pending_to_export_contact'),('state', 'in', ['in_queue']),('list_id', '!=', False)])
        for rec in export_contact_list:
            rec.contact_ids.action_export_to_sendinblue()
        return True

    #@api.multi
    def process_fetch_member(self):
        queue_records = self or self.search([('operation','=','fetch_member'),('state', 'in', ['in_queue']), ('list_id', '!=', False)])
        for rec in queue_records:
            _logger.info('--------Processing Queue {}------------'.format(rec.name))
            rec.list_id.process_fetch_member_queue(rec)
            rec.write({'state':'done'})
            _logger.info('--------End Process Queue {}------------'.format(rec.name))
        return True

    def process_campaign_activity_report(self):
        _logger.info('--------End Fetch Email Activity------------')
        queue_records = self or self.search([('operation','=','campaign_activity_report'),('state', 'in', ['in_queue']), ('campaign_id', '!=', False)])
        for rec in queue_records:
            for campaign in rec.campaign_id:
                campaign.fetch_campaign()
                _logger.info('--------Queue Id {} campaign {} ------------'.format(rec.id, campaign.id))
            self._cr.commit()
            for contact_list in rec.campaign_id.contact_list_ids:
                remaining_contacts = contact_list.contact_ids
                remaining_contacts -= rec.processed_contact_ids
                for contact in remaining_contacts:
                    contact.fetch_email_statistics(rec.account_id)
                    rec.write({'processed_contact_ids': [(4, contact.id)]})
                    self._cr.commit()
                    _logger.info('--------Queue Id {} contact id {} ------------'.format(rec.id, contact.id))
            rec.write({'state': 'done'})
            self._cr.commit()
        _logger.info('--------End Fetch Email Activity------------')
        return True

    @api.model
    def sendinblue_process_queue(self):
        if not self.env['sendinblue.accounts'].search([]):
            return True
        _logger.info('--------Start Cron for process queue------------')
        all_queue = self.search([('state', 'in', ['in_queue'])])
        for in_queue in all_queue:
            if hasattr(in_queue, 'process_%s' % in_queue.operation):
                res = getattr(in_queue, 'process_%s' % in_queue.operation)()
        _logger.info('--------End Cron for process queue------------')
        return True