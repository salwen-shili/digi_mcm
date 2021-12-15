from odoo import api, fields, models


class InheritResPartner(models.Model):
    _inherit = "res.partner"

    composer_ids = fields.Many2one('mail.message', string='Composer')
    last_internal_log = fields.Char(compute="_compute_get_last_internal_log", string="Commentaire Interne")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    presence = fields.Char(readonly=True, compute="_compute_get_last_presence_values")
    resultat = fields.Char(readonly=True, compute="_compute_get_last_resultat_values")
    date_exam = fields.Date(related="mcm_session_id.date_exam", string="Date d'examen")

    def _compute_get_last_presence_values(self):
        """ Function to get presence value of last session in tree partner view"""
        for rec in self:
            last_line = rec.env['info.examen'].sudo().search([('partner_id', "=", rec.id)], limit=1, order="id desc")
            if last_line.presence:
                rec.presence = str(last_line.presence).title()
            else:
                rec.presence == '_______'

    def _compute_get_last_resultat_values(self):
        """ Function to get result value of last session in tree partner view"""
        for rec in self:
            last_line = rec.env['info.examen'].sudo().search([('partner_id', "=", rec.id)], limit=1, order="id desc")
            if last_line.resultat:
                rec.resultat = str(last_line.resultat).title()
            else:
                rec.resultat == '_______'

    def _compute_get_last_internal_log(self):
        for record in self:
            last_line = record.env['mail.message'].sudo().search([('record_name', '=', record.name), ('subtype_id', '=', 'Note'), ('message_type', 'in', ['comment', 'notification'])], limit=1)
            record.last_internal_log = last_line.body

    def get_comments_history(self):
        self.ensure_one()
        return {
            'name': self.name,
            'view_type': "form",
            'view_mode': "tree,form",
            'res_model': "mail.message",
            'type': "ir.actions.act_window",
            'domain': [("record_name", "=", self.name), ('message_type', 'in', ['comment', 'notification']), ('subtype_id', '=', 'Note')],
            'context': "{'create': False, 'edit':False}"
        }
