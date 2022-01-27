from datetime import date

from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class InheritResPartner(models.Model):
    _inherit = "res.partner"

    composer_ids = fields.Many2one('mail.message', string='Composer')
    last_internal_log = fields.Char(compute="_compute_get_last_internal_log", string="Commentaire Interne")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    presence = fields.Char(readonly=True, store=True)
    resultat = fields.Char(readonly=True, store=True)
    nombre_de_passage = fields.Char(readonly=True, store=True)
    date_exam = fields.Date(related="mcm_session_id.date_exam", string="Date d'examen")
    is_recu = fields.Boolean(default=False)
    is_ajourne = fields.Boolean(default=False)
    is_present = fields.Boolean(default=False)
    is_Absent = fields.Boolean(default=False)
    is_absence_justifiee = fields.Boolean(default=False)

    @api.onchange('note_exam_id')
    def update_boolean_values_partner(self):
        for rec in self.env['res.partner'].search([('statut', "=", 'won')], order='id DESC', limit=500):
            if rec.resultat == 'Admis(e)':
                rec.is_recu = True
            if rec.resultat == 'Ajourné(e)':
                rec.is_ajourne = True
            if rec.presence == 'Présent(e)':
                rec.is_present = True
            if rec.presence == 'Absent(e)':
                rec.is_Absent = True
            if rec.presence == 'Absence justifiée':
                rec.is_absence_justifiee = True

    def _get_last_presence_resultat_values(self):
        """ Function to get presence and resultat values of last session in tree partner view"""
        for rec in self.env['res.partner'].sudo().search(
                [('create_date', '<', date.today()), ('mcm_session_id', '!=', None), ('id', '=', self.id)]):
            last_line = rec.env['info.examen'].sudo().search(
                [('partner_id', "=", rec.id), ('date_exam', '<', date.today())], limit=1, order="id desc")
            if len(rec.note_exam_id):
                _logger.info('-------Cron Partner presence and resultat------- %s',
                             rec.note_exam_id.partner_id.display_name)
                for line in last_line:
                    if line.presence == 'present':
                        rec.presence = "Présent(e)"
                    if line.presence == 'Absent':
                        rec.presence = "Absent(e)"
                    if line.presence == 'absence_justifiee':
                        rec.presence = "Absence justifiée"
                    elif not line.presence:
                        rec.presence = "_______"
                # Remplir le champ resultat par valeur de dernier examen
                for resultat in last_line:
                    if resultat.resultat == 'ajourne':
                        rec.resultat = "Ajourné(e)"
                    if resultat.resultat == 'recu':
                        rec.resultat = "Admis(e)"
                    elif not resultat.resultat:
                        rec.resultat = "_______"

    def _compute_get_last_internal_log(self):
        for record in self:
            last_line = record.env['mail.message'].sudo().search(
                [('record_name', '=', record.name), ('subtype_id', '=', 'Note'),
                 ('message_type', 'in', ['comment', 'notification'])], limit=1)
            record.last_internal_log = last_line.body

    def get_comments_history(self):
        self.ensure_one()
        return {
            'name': self.name,
            'view_type': "form",
            'view_mode': "tree,form",
            'res_model': "mail.message",
            'type': "ir.actions.act_window",
            'domain': [("record_name", "=", self.name), ('message_type', 'in', ['comment', 'notification']),
                       ('subtype_id', '=', 'Note')],
            'context': "{'create': False, 'edit':False}"
        }

    def write(self, values):
        """ Mettre à jour presence & resultat fields pour chaque mise à jour"""
        val = super(InheritResPartner, self).write(values)
        if 'note_exam_id' in values:
            self._get_last_presence_resultat_values()
        return val
