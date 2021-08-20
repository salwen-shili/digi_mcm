from odoo import api, fields, models, _


class MassMailingContactListRel(models.Model):
    _inherit = 'mailing.contact.subscription' #v13

    @api.depends('list_id')
    def _compute_sendinblue_list_id(self):
        sendinblue_list_obj = self.env['sendinblue.lists']
        for record in self:
            list_id = sendinblue_list_obj.search([('odoo_list_id', '=', record.list_id.id)], limit=1)
            record.sendinblue_list_id = list_id.id

    sendinblue_id = fields.Char("SendinBlue ID", readonly=1, copy=False)
    sendinblue_list_id = fields.Many2one('sendinblue.lists', compute="_compute_sendinblue_list_id", string="sendinblue List", store=True)
    sendinblue_md5_email = fields.Char("MD5 Email", readonly=1, copy=False)
    related_partner_id = fields.Many2one('res.partner', related='contact_id.related_partner_id', string='Related Customer', readonly=True, store=True)

    def unlink(self):
        for record in self:
            if record.contact_id.sendinblue_id and record.sendinblue_list_id and record.sendinblue_list_id.list_id:
                account = record.list_id and record.list_id.sendinblue_list_id and record.list_id.sendinblue_list_id.account_id or False
                list_ids = list(map(int, record.sendinblue_list_id.list_id))
                prepared_vals = {"unlinkListIds": list_ids}
                response = account._send_request('contacts/%s' % (record.contact_id.sendinblue_id and int(record.contact_id.sendinblue_id) or record.contact_id.email), prepared_vals, method='PUT')
        return super(MassMailingContactListRel, self).unlink()