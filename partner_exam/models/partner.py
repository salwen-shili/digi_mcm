# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime, date

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class IrSequence(models.Model):
    _inherit = "ir.sequence"

    alphabet = fields.Char(string="Alphabet Evalbox")
    suffix_number = fields.Char(string="Suffix Evalbox")


class resComapny(models.Model):
    _inherit = "res.partner"

    note_exam = fields.Char("Note d'examen blanc")
    note_exam_id = fields.One2many('info.examen', 'partner_id')
    note_exam_mcm_id = fields.One2many('info.examen', 'partner_id')
    note_exam_count = fields.Integer(compute="compute_notes_exams_count")
    this_is_technical_field = fields.Boolean(readonly=True, default=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    report = fields.Boolean(default=False, help="Cocher ce bouton si vous voulez changer la session de ce client!")
    # Add fields pour la justification dans l'interface client en cas de report
    justification = fields.Boolean(string="Justification")
    paiement = fields.Boolean(string="Paiement")
    attachment_ids = fields.Many2many('ir.attachment', string="Attachment", required=True)
    autre_raison = fields.Text(string="Autre Raison")
    # Fields CERFA
    num_departement = fields.Char(string="N° du département en France")
    nom_marital = fields.Char(string="Nom marital")
    other_cases = fields.Char(string="Nom de l'Etat pour les autres cas")
    age = fields.Char()
    nom_evalbox = fields.Char(string="Nom Evalbox")
    prenom_evalbox = fields.Char(string="Prénom Evalbox")
    code_evalbox = fields.Char()

    def compute_notes_exams_count(self):
        for record in self:
            record.note_exam_count = self.env['info.examen'].search_count(
                [('partner_id', 'child_of', self.id)])

    def get_notes_history(self):
        self.ensure_one()
        return {
            "name": self.name,
            "view_type": "form",
            "view_mode": "tree,form",
            "res_model": "info.examen",
            "type": "ir.actions.act_window",
            "domain": [("partner_id", "child_of", self.id)],
            'context': {'default_note_exam_id': self.note_exam_id.ids},
        }

    def write(self, values):
        """ Update this function to add new line in list of sessions
        if the field mcm_session_id changed based on report boolean field
        if report=True ===> user can edit session in partner view"""
        session = super(resComapny, self).write(values)
        if 'mcm_session_id' in values and self.report is not False:
            if self.env['partner.sessions'].search_count([('client_id', 'child_of', self.id)]) > 0:
                # Update data in old session if sum of sessions lines > 0
                self.env['partner.sessions'].search([('client_id', 'child_of', self.id)], limit=1,
                                                    order='id desc').sudo().update({
                    'client_id': self.id,
                    # 'session_id': self.mcm_session_id.id,
                    'company_id': self.company_id.id,
                    'justification': self.justification,
                    'paiement': self.paiement,
                    'attachment_ids': self.attachment_ids,
                    'autre_raison': self.autre_raison})
                # Add new line in examen if mcm_session_id changed
                if self.justification is True:
                    self.env['info.examen'].search([], limit=1, order='id desc').sudo().create({
                        'partner_id': self.id,
                        'session_id': self.mcm_session_id.id,
                        'module_id': self.module_id.id,
                        'date_exam': self.mcm_session_id.date_exam,
                        'epreuve_a': 0,
                        'epreuve_b': 0,
                        'presence': 'absence_justifiee',
                        'ville_id': self.mcm_session_id.session_ville_id.id, })
            # Create new line in historic sessions
            sessions = self.env['partner.sessions'].search(
                [('client_id', '=', self.id), ('session_id', '=', self.mcm_session_id.id)])
            if not sessions:
                sessions.sudo().create({
                    'client_id': self.id,
                    'session_id': self.mcm_session_id.id,
                    'module_id': self.module_id.id,
                })
            # Reset fields
            self.report = False
            self.justification = False
            self.paiement = False
            self.attachment_ids = None
            self.autre_raison = None
        """Si mode de financement changé sur la fiche client sera changé sur info examen"""
        if 'mode_de_financement' in values:
            info_exam = self.env['info.examen'].sudo().search([('partner_id', '=', self.id)])
            if info_exam:
                info_exam.mode_de_financement = dict(self._fields['mode_de_financement'].selection).get(
                    self.mode_de_financement)
        """ Calculer âge pour faire le filtrage avec âge dans la fiche client en utilisant relativedelta"""
        if 'birthday' in values:
            dt = self.birthday
            today = date.today()
            rd = relativedelta(today, dt).years
            self.age = rd  # Affectation de l'age au champ age dans res.partner
            _logger.info('rec.age date of birth-------------11111111111111111111-------- %s', self.age)
        return session

    @api.model
    def create(self, vals):
        if vals['company_id'] == 2:  # company DIGIMOOV
            # prefix = "A"
            vals['prenom_evalbox'] = self.env['ir.sequence'].next_by_code(
                'res.partner') or '/'  # Affectation: Generate a sequence number to prenom_evalbox field

            ir_sequence = self.env['ir.sequence'].search([('name', '=', "Res Partner Evalbox")],
                                                         limit=1)  # Search in ir.sequence with name of the record
            print("ir_sequence", ir_sequence)  # Print
            if ir_sequence.number_next_actual == 100000:  # Condition if next number in ir.sequence == 1001 because we need max 1000
                # For one letter exemple: A:1-99999, B:1-99999
                vals['prenom_evalbox'] = ir_sequence.number_next_actual  # Update number_next_actual to 1
                ir_sequence.number_next_actual = int('00001')
                print("Hello //", ir_sequence.number_next_actual)
                vals['prenom_evalbox'] = ir_sequence.number_next_actual

                char = ir_sequence.alphabet
                print("char///", char)
                if chr(ord(char) + 1) == "[":  # refaire boucle apres "Z" ==> "[" : le champ alphabet sera égale à "A"
                    ir_sequence.alphabet = "A"
                    char = ir_sequence.alphabet
                    vals['nom_evalbox'] = char
                else:
                    char = chr(ord(char) + 1)
                    vals['nom_evalbox'] = char
            else:
                print("else ////")
                char = ir_sequence.alphabet
                ir_sequence.alphabet = char
                vals['nom_evalbox'] = ir_sequence.alphabet
                #ir_sequence.number_next_actual = int('00001')
                vals['prenom_evalbox'] = ir_sequence.number_next_actual
                vals['code_evalbox'] = str(vals['nom_evalbox']) + str(vals['prenom_evalbox'])
        return super(resComapny, self).create(vals)
