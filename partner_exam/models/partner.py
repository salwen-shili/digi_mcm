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
    justification = fields.Boolean(string="Absence justifié")
    paiement = fields.Boolean(string="Paiement")
    attachment_ids = fields.Many2many('ir.attachment', string="Attachment", required=True)
    autre_raison = fields.Text(string="Autre Raison")
    # Fields CERFA
    num_departement = fields.Char(string="N° du département en France")
    nom_marital = fields.Char(string="Nom marital")
    other_cases = fields.Char(string="Nom de l'Etat pour les autres cas")
    age = fields.Char()
    nom_evalbox = fields.Char(string="Nom Evalbox")
    prenom_evalbox = fields.Char(string="Prénom Evalbox", track_visibility='always')
    code_evalbox = fields.Char()
    zip = fields.Char(change_default=True)

    def print_report_name_partner(self):
        """ La fonction sera utilisée dans les noms de rapport en format PDF de l'interface de contact."""
        self.ensure_one()
        return '- %s - %s - %s' % (
            self.display_name, self.mcm_session_id.session_ville_id.display_name,
            self.mcm_session_id.date_exam.strftime(
                '%d/%m/%Y'))

    def _get_report_base_filename(self):
        self.ensure_one()
        return '%s %s' % (self.type_name, self.name)

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
                    self.is_ajourne = True
                    self.is_recu = False
                    self.is_Absent = False
                    self.is_absence_justifiee = True
                    self.env['info.examen'].search([], limit=1, order='id desc').sudo().create({
                        'partner_id': self.id,
                        'session_id': self.mcm_session_id.id,
                        'module_id': self.module_id.id,
                        'date_exam': self.mcm_session_id.date_exam,
                        'company_id': self.mcm_session_id.company_id.id,
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
            info_exam = self.env['info.examen'].sudo().search(
                [('partner_id', '=', self.id), ('date_exam', '=', self.mcm_session_id.date_exam)])
            if info_exam:
                info_exam.mode_de_financement = dict(self._fields['mode_de_financement'].selection).get(
                    self.mode_de_financement)
        """ Calculer âge pour faire le filtrage avec âge dans la fiche client en utilisant relativedelta"""
        if 'birthday' in values or 'mcm_session_id' in values:
            dt = self.birthday
            date_exam = self.mcm_session_id.date_exam
            rd = relativedelta(date_exam, dt).years
            months = relativedelta(date_exam, dt).months
            jours = relativedelta(date_exam, dt).months
            self.age = str(rd) + "ans" + " " + str(months) + "mois" + " " + str(
                jours) + "jours"  # Affectation de l'age au champ age dans res.partner (année + mois)
        if self.company_id.id == 2:  # If company = Digimoov
            eval_name_actuel = self.nom_evalbox[1:0] if self.nom_evalbox else ''
            eval_name = str(self.mcm_session_id.session_ville_id.name_ville[
                            0:3]).upper() + "-" + eval_name_actuel if self.mcm_session_id.session_ville_id.name_ville else ''
            # Affectation: Generate a sequence number to prenom_evalbox field
            self.env['ir.sequence'].next_by_code('res.partner') or '/'
            # Search in ir.sequence with name of the record
            ir_sequence = self.env['ir.sequence'].search([('name', '=', "Res Partner Evalbox")],
                                                         limit=1)
            # Condition if next number in ir.sequence == 1001 because we need max 100000
            if ir_sequence.number_next_actual == 100000:
                # For one letter example: A:1-99999, B:1-99999
                # self.prenom_evalbox = ir_sequence.number_next_actual  # Update number_next_actual to 1
                ir_sequence.number_next_actual = int('00001')  # Initialisation de 1
                self.prenom_evalbox = ir_sequence.number_next_actual
                self.nom_evalbox = eval_name
                # To concatenate (combine) multiple fields
                self.code_evalbox = str(self.nom_evalbox) + str(self.prenom_evalbox)
                _logger.info(
                    "Create function €€€€€ if res.mcm_session_id €€€€€€ %s" % str(self.code_evalbox))
            elif 'mcm_session_id' in values and self.code_evalbox is False and self.state == 'en_formation':
                self.nom_evalbox = eval_name
                # Update code evalbox and # To concatenate (combine) multiple fields
                self.code_evalbox = eval_name + str(self.prenom_evalbox)
                _logger.info("Self nom evalbox §§§§§ if mcm_session_id §§§§§ %s" % str(self.nom_evalbox))
                _logger.info("Self prénom evalbox §§§§§ if mcm_session_id §§§§§ %s" % str(self.prenom_evalbox))
            # else:
            #     self.code_evalbox = str(self.nom_evalbox) + str(self.prenom_evalbox)
            #     _logger.info("Self Code evalbox ##### else ##### %s" % str(self.code_evalbox))
        return session

    @api.model
    def create(self, vals):
        """ Lors de la création d'une nouvelle fiche client le nom evalbox sera rempli par
        un alphabet et prénom evalbox par séquence des nombres puis ça sera concaténé dans le champ evalbox"""
        res = super(resComapny, self).create(vals)
        if res.company_id.id == 2:
            res.prenom_evalbox = self.env['ir.sequence'].next_by_code(
                'res.partner') or '/'  # Affectation: Generate a sequence number to prenom_evalbox field
            ir_sequence = self.env['ir.sequence'].search([('name', '=', "Res Partner Evalbox")],
                                                         limit=1)  # Search in ir.sequence with name of the record
            if ir_sequence.number_next_actual == 100000:  # Condition if next number in ir.sequence == 1001 because we need max 1000
                # For one letter example: A:1-99999, B:1-99999
                res.prenom_evalbox = ir_sequence.number_next_actual  # Update number_next_actual to 1
                ir_sequence.number_next_actual = int('00001')  # Initialisation de 1
                res.prenom_evalbox = ir_sequence.number_next_actual

                char = ir_sequence.alphabet  # Global variable char to get alphabet from the search in sequence class
                _logger.info(
                    "ir_sequence.number_next_actual evalbox ##### if (create function)##### %s" % str(self.char))
                if chr(ord(char) + 1) == "[":  # refaire boucle apres "Z" ==> "[" : le champ alphabet sera égale à "A"
                    ir_sequence.alphabet = "A"
                    char = ir_sequence.alphabet
                    res.nom_evalbox = char
                    if res.mcm_session_id:
                        res.nom_evalbox = str(res.mcm_session_id.session_ville_id.name_ville[0:3]).upper() + "-" + char
                        res.code_evalbox = str(res.nom_evalbox) + str(
                            res.prenom_evalbox)  # To concatenate (combine) multiple fields
                        _logger.info(
                            "Create function €€€€€ if res.mcm_session_id €€€€€€ %s" % str(
                                res.code_evalbox))
                    else:
                        res.code_evalbox = str(res.nom_evalbox) + str(
                            res.prenom_evalbox)  # To concatenate (combine) multiple fields
                        _logger.info(
                            "Create function %%%%% else res.mcm_session_id %%%%%% %s" % str(
                                res.code_evalbox))
                else:
                    char = chr(ord(char) + 1)
                    res.nom_evalbox = char
                    _logger.info("else %% create" % str(res.nom_evalbox))
                    if res.mcm_session_id:
                        res.nom_evalbox = str(res.mcm_session_id.session_ville_id.name_ville[0:3]).upper() + "-" + char
                        res.code_evalbox = str(res.nom_evalbox) + str(
                            res.prenom_evalbox)  # To concatenate (combine) multiple fields
                        _logger.info("code_evalbox µµµ       create       µµµ %s" % str(res.code_evalbox))
                    else:
                        res.code_evalbox = str(res.nom_evalbox) + str(
                            res.prenom_evalbox)  # To concatenate (combine) multiple fields
                        _logger.info("else code_evalbox ££££       else      ££££ %s" % str(res.code_evalbox))

            else:  # If number_next_actual != 100000
                char = ir_sequence.alphabet
                # ir_sequence.alphabet = char
                res.nom_evalbox = char  # Get alphabet from ir.sequence class
                res.prenom_evalbox = ir_sequence.number_next_actual
                _logger.info("else prenom_evalbox +++++++++      else      ++++++++ %s" % str(res.prenom_evalbox))
                if res.mcm_session_id:
                    res.nom_evalbox = str(res.mcm_session_id.session_ville_id.name_ville[0:3]).upper() + "-" + char
                    res.code_evalbox = str(res.nom_evalbox) + str(
                        res.prenom_evalbox)  # To concatenate (combine) multiple fields
                    _logger.info("IF code_evalbox ££££       IF      ££££ %s" % str(res.code_evalbox))
                else:
                    res.code_evalbox = str(
                        res.nom_evalbox) + str(
                        res.prenom_evalbox)  # To concatenate (combine) multiple fields
                    _logger.info("else not session_id evalbox ££££       else      ££££ %s" % str(res.code_evalbox))
        return res
