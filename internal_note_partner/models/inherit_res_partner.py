from odoo import api, fields, models


class InheritResPartner(models.Model):
    _inherit = "res.partner"

    composer_ids = fields.Many2one('mail.message', string='Composer')
    last_internal_log = fields.Char(compute="_compute_get_last_internal_log", string="Commentaire Interne")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    def _compute_get_last_internal_log(self):
        for record in self:
            last_line = record.env['mail.message'].sudo().search([('record_name', '=', record.name), ('subtype_id', '=', 'Note'), ('message_type', 'in', ['comment', 'notification'])], limit=1)
            record.last_internal_log = last_line.body

    def get_mail_history(self):
        self.ensure_one()
        return {
            "name": self.name,
            "view_type": "form",
            "view_mode": "tree,form",
            "res_model": "mail.message",
            "type": "ir.actions.act_window",
            "domain": [("record_name", "=", self.name), ('message_type', 'in', ['comment', 'notification']), ('subtype_id', '=', 'Note')],
        }
