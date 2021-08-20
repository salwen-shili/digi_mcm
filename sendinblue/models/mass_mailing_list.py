from odoo import api, fields, models, _


class MassMailingList(models.Model):
    _inherit = "mailing.list" #v13

    # @api.one
    def _compute_sendinblue_list_id(self):
        sendinblue_list_obj = self.env['sendinblue.lists']
        for record in self:
            list_id = sendinblue_list_obj.search([('odoo_list_id', '=', record.id)],limit=1)
            if list_id:
                record.sendinblue_list_id = list_id.id
            else:
                record.sendinblue_list_id = False

    sendinblue_list_id = fields.Many2one('sendinblue.lists', compute='_compute_sendinblue_list_id',
                                        string="Associated sendinblue List")
