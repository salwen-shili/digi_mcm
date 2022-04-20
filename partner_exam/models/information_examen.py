# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.tools import datetime, base64
from odoo.exceptions import ValidationError, _logger
import requests
from requests.structures import CaseInsensitiveDict
from datetime import datetime, timedelta, date
import logging
import json

_logger = logging.getLogger(__name__)


class NoteExamen(models.Model):
    _name = "info.examen"
    _rec_name = 'partner_id'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Les Notes et les informations des examens"

    partner_id = fields.Many2one('res.partner', string="Client")
    epreuve_a = fields.Float(string="Epreuve A(QCM):", track_visibility='always', group_operator='avg')
    epreuve_b = fields.Float(string="Epreuve B(QRO)", track_visibility='always', default=1, group_operator='avg')
    moyenne_generale = fields.Float(string="Moyenne Générale", track_visibility='always', store=True,
                                    group_operator='avg')
    mention = fields.Selection([
        ('recu', 'Reçu'),
        ('ajourne', 'Ajourné')],
        string="Mention", default=False)
    resultat = fields.Selection([
        ('recu', 'Reçu'),
        ('ajourne', 'Ajourné')], string="Résultat")
    date_exam = fields.Date(string="Date Examen", track_visibility='always')
    active = fields.Boolean('Active', default=True)
    company_id = fields.Many2one(
        'res.company', string='Company', change_default=True,
        default=lambda self: self.env.company,
        required=False, readonly=False)
    nombre_de_passage = fields.Selection(selection=[
        ('premier', 'Premier'),
        ('deuxieme', 'Deuxième'),
        ('troisieme', 'Troisième')],
        string="Nombre De Passage", default="premier")

    presence = fields.Selection([
        ('present', 'Présent'),
        ('Absent', 'Absent'),
        ('absence_justifiee', 'Absence justifiée')],
        string="Présence", default='present')
    # Ajout le champ etat qui sera invisible dans l'interface "notes & examen"
    # Utilisation de ce champ pour une information dans le fichier xml de "attestation de suivi de formation
    etat = fields.Char(compute="etat_de_client_apres_examen")
    mode_de_financement = fields.Char(string="Mode de financement")
    session_id = fields.Many2one('mcmacademy.session')
    # For automation action conditions use.
    this_is_exam_technical_field = fields.Boolean(readonly=True, default=True)
    temps_minute = fields.Integer(related="partner_id.temps_minute")
    sorti_formation = fields.Boolean(string="Sorti de formation")
    is_recu = fields.Boolean(default=False)
    is_ajourne = fields.Boolean(default=False)
    is_present = fields.Boolean(default=False)
    is_Absent = fields.Boolean(default=False)
    is_absence_justifiee = fields.Boolean(default=False)
    phone = fields.Char(related="partner_id.phone")
    mobile = fields.Char(compute="_compute_phone_value_to_mobile", store=True)
    module_id = fields.Many2one("mcmacademy.module")
    # Champ Mcm-academy
    epreuve_theorique = fields.Selection([
        ('reussi', 'Réussi(e)'),
        ('ajourne', 'Ajourné(e)')], string="Epreuve théorique")

    epreuve_pratique = fields.Selection([
        ('reussi', 'Réussi(e)'),
        ('ajourne', 'Ajourné(e)')], string="Epreuve pratique")

    state_theorique = fields.Selection([
        ('reussi', 'Réussi(e)'),
        ('ajourne', 'Ajourné(e)')], string="Statut théorique")

    state_pratique = fields.Selection([
        ('reussi', 'Réussi(e)'),
        ('ajourne', 'Ajourné(e)')], string="Statut pratique")

    presence_mcm = fields.Selection([
        ('present', 'Présent'),
        ('Absent', 'Absent'),
        ('absence_justifiee', 'Absence justifiée')],
        string="Présence")

    @api.depends('partner_id.phone')
    def _compute_phone_value_to_mobile(self):
        for rec in self.env['info.examen'].search([]):
            if rec.phone is not None:
                print("alloo phone", rec.phone)
                rec.mobile = rec.phone
                print("alloo mobile", rec.mobile)

    @api.onchange('resultat', 'partner_id', 'presence')
    def update_boolean_values(self):
        for rec in self:
            if rec.resultat == 'recu':
                rec.is_recu = True
                rec.is_ajourne = False
            if rec.resultat == 'ajourne' and rec.presence == 'present':
                rec.is_ajourne = True
                rec.is_recu = False
                rec.is_Absent = True
                rec.is_absence_justifiee = False
            if rec.resultat == 'ajourne' and rec.presence == 'absence_justifiee':
                rec.is_ajourne = True
                rec.is_recu = False
                rec.is_Absent = False
                rec.is_absence_justifiee = True
            if rec.presence == 'present':
                rec.is_present = True
                rec.is_Absent = False
                rec.is_absence_justifiee = False
            if rec.presence == 'Absent' and rec.resultat == 'ajourne':
                rec.is_Absent = True
                rec.is_ajourne = True
                rec.is_present = False
                rec.is_recu = False
                rec.is_absence_justifiee = False
            # if rec.presence == 'absence_justifiee':
            #     rec.is_absence_justifiee = True
            #     rec.is_recu = False
            #     rec.is_Absent = False

    def _calcul_ancien_client(self):
        """ Suit aux changements pour les notes des examens;
        en va lancer cette fonction une fois pour changer les anciennes notes existantes telle que moyenne générale/200"""
        for line in self.env['info.examen'].sudo().search([]):
            if line.date_exam:
                if line.epreuve_a > 0 or line.epreuve_b > 0:
                    qcm = line.epreuve_a * 5
                    line.epreuve_a = qcm
                    qro = line.epreuve_b * 5
                    line.epreuve_b = qro
                    line.moyenne_generale = (line.epreuve_a + line.epreuve_b)

    @api.onchange('partner_id', 'epreuve_a', 'epreuve_b', 'presence', 'nombre_de_passage')
    def compute_moyenne_generale(self):
        """ This function used to auto display some result
        like the "Moyenne Generale" & "Mention" & "Resultat" """
        for rec in self:
            session_count = rec.env['partner.sessions'].search_count(
                [('client_id', '=', rec.partner_id.id), ('paiement', '!=', True)])
            rec.moyenne_generale = (rec.epreuve_a + rec.epreuve_b)
            if rec.epreuve_a >= 50 and rec.epreuve_b >= 40 and rec.moyenne_generale >= 120 and rec.partner_id:
                rec.moyenne_generale = rec.moyenne_generale
                rec.mention = 'recu'
                rec.resultat = 'recu'
                # self.partner_id = self.partner_id.id
                self.session_id = self.partner_id.mcm_session_id
                self.module_id = self.partner_id.module_id.id
                self.date_exam = self.partner_id.mcm_session_id.date_exam
                self.presence = 'present'
                self.ville_id = self.partner_id.mcm_session_id.session_ville_id.id
                self.partner_id.presence = "Présent(e)"
                self.partner_id.resultat = "Admis(e)"

            else:
                # reset your fields
                rec.epreuve_a = rec.epreuve_a
                rec.epreuve_b = rec.epreuve_b
                rec.mention = 'ajourne'
                rec.resultat = 'ajourne'
                rec.partner_id.resultat = "Ajourné(e)"

                last_line = self.env['partner.sessions'].search(
                    [('client_id', '=', rec.partner_id.id), ('date_exam', '<', date.today())], limit=1,
                    order='id desc')
                if 1 <= rec.epreuve_a < 201 or 1 <= rec.epreuve_b < 201 and not last_line.justification and rec.partner_id:
                    self.session_id = self.partner_id.mcm_session_id
                    self.module_id = self.partner_id.module_id.id
                    self.date_exam = self.partner_id.mcm_session_id.date_exam
                    self.presence = 'present'
                    self.ville_id = self.partner_id.mcm_session_id.session_ville_id.id
                    self.partner_id.presence = "Présent(e)"
                    self.partner_id.resultat = "Ajourné(e)"
                elif rec.epreuve_a < 1 and rec.epreuve_b < 1 and not last_line.justification and rec.partner_id:
                    self.session_id = self.partner_id.mcm_session_id
                    self.module_id = self.partner_id.module_id.id
                    self.date_exam = self.partner_id.mcm_session_id.date_exam
                    self.presence = 'Absent'
                    self.ville_id = self.partner_id.mcm_session_id.session_ville_id.id
                    self.partner_id.update({'presence': "Absent(e)"})
                    self.partner_id.resultat = "Ajourné(e)"
                elif rec.epreuve_a < 1 and rec.epreuve_b < 1 and last_line.justification is True and rec.partner_id:
                    self.session_id = last_line.session_id
                    self.module_id = last_line.client_id.module_id.id
                    self.date_exam = last_line.session_id.date_exam
                    self.presence = 'absence_justifiee'
                    self.ville_id = last_line.session_id.session_ville_id.id
                    self.partner_id.update({'presence': "Absence justifiée"})
                    self.partner_id.resultat = "Ajourné(e)"

    @api.onchange("résultat", "epreuve_theorique", "epreuve_pratique")
    def etat_de_client_apres_examen(self):
        """Fonction pour mettre le champs etat
        automatique depend de champ resultat,
        pour l'utilisé dans la template de "Atestation de suivi de formation" """
        for rec in self:
            if rec.resultat == 'recu':
                rec.etat = "avec succès"
            if not rec.resultat == "recu":
                rec.etat = "sans succès"
        # Ajouter une condition si company == MCM-ACADEMY et selon state téthorique == reussi
        # donc state pratique sera automatiquement Réussi(e)
        if self.company_id.id == 1:
            if self.epreuve_theorique:
                if self.epreuve_theorique == 'reussi':
                    self.state_theorique = 'reussi'  # Affectation automatique
                else:  # si epreuve_theorique == Ajournée
                    self.state_theorique = 'ajourne'
            if self.epreuve_pratique:
                if self.epreuve_pratique == 'reussi':
                    self.state_pratique = 'reussi'
                else:  # si epreuve pratique == Ajournée
                    self.state_pratique = 'ajourne'

    def _clear_duplicates_exams(self):
        """ Cron Delete exams duplications based on id and date_exam """
        duplicates_exams = []
        for partner_exam in self.env['info.examen'].search([], order='id DESC'):
            _logger.info("Delete exams duplications based on date_exam.")
            if partner_exam.date_exam and partner_exam.id not in duplicates_exams:
                duplicates = self.search([('id', '!=', partner_exam.id), ('date_exam', '=', partner_exam.date_exam),
                                          ('partner_id', '=', partner_exam.partner_id.id)])
                for dup in duplicates:
                    duplicates_exams.append(dup.id)
        self.browse(duplicates_exams).unlink()

    """ Mettre à jour le champ mode de financement selon la fiche client """

    def mise_ajour_mode_financement(self):
        for client in self:
            partner = self.env['res.partner'].sudo().search([('id', '=', client.partner_id.id),
                                                             ], limit=1)
            _logger.info('fiche %s', partner.email)
            _logger.info('fiche %s', partner.mode_de_financement)
            if partner:
                client.mode_de_financement = dict(partner._fields['mode_de_financement'].selection).get(
                    partner.mode_de_financement)
                print("client.mode_de_financement", client.mode_de_financement)

    def mise_ajour_mode_financement_ir_cron(self):
        for client in self.env['info.examen'].sudo().search([]):
            partner = self.env['res.partner'].sudo().search([('id', '=', client.partner_id.id),
                                                             ], limit=1)
            _logger.info('fiche  %s', partner.email)
            _logger.info('fiche %s', partner.mode_de_financement)
            if partner:
                client.mode_de_financement = dict(partner._fields['mode_de_financement'].selection).get(
                    partner.mode_de_financement)
                print("client.mode_de_financement", client.mode_de_financement)

    """utiliser api wedof pour changer etat de dossier sur edof selon la presence le jour d'examen"""

    def change_etat_wedof(self):
        company = self.env['res.company'].sudo().search([('id', "=", 2)])
        api_key = ""
        if company:
            api_key = company.wedof_api_key
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
            'X-API-KEY': api_key,
        }
        params_wedof = (
            ('order', 'desc'),
            ('state', 'inTraining'),
            ('sort', 'lastUpdate'),
            ('limit', '100'),
        )
        data1 = '{}'
        data = '{\n "absenceDuration": 0,\n "forceMajeureAbsence": false,\n "trainingDuration": 0\n}'
        response = requests.get('https://www.wedof.fr/api/registrationFolders', headers=headers,
                                params=params_wedof)
        registrations = response.json()
        for dossier in registrations:
            _logger.info('lengh api get %s' % str(len(registrations)))

            externalId = dossier['externalId']
            print('externalId', externalId)
            email = dossier['attendee']['email']
            lastupdatestr = str(dossier['lastUpdate'])
            lastupdate = datetime.strptime(lastupdatestr, '%Y-%m-%dT%H:%M:%S.%fz')
            newformat = "%d/%m/%Y %H:%M:%S"
            lastupdateform = lastupdate.strftime(newformat)
            lastupd = datetime.strptime(lastupdateform, "%d/%m/%Y %H:%M:%S")
            idform = dossier['trainingActionInfo']['externalId']
            training_id = ""
            if "_" in idform:
                idforma = idform.split("_", 1)
                if idforma:
                    training_id = idforma[1]
            info_exam = self.env['info.examen'].sudo().search([('partner_id.numero_cpf', "=", str(externalId)),
                                                               ('presence', "=", "present")], limit=1)

            if info_exam:
                product_id = self.env['product.template'].sudo().search(
                    [('id_edof', "=", str(training_id))], limit=1)
                _logger.info('apprenant existant %s' % info_exam.partner_id.numero_cpf)
                response1 = requests.post('https://www.wedof.fr/api/registrationFolders/' + externalId + '/terminate',
                                          headers=headers, data=data1)
                response = requests.post('https://www.wedof.fr/api/registrationFolders/' + externalId + '/serviceDone',
                                         headers=headers, data=data)

                _logger.info('terminate %s' % str(response1.status_code))
                _logger.info('service done %s' % str(response.status_code))
                if response.status_code == 200:
                    """si statut est changé sur wedof on change statut_cpf sur fiche client """
                    _logger.info('if service done %s' % info_exam.partner_id.numero_cpf)
                    info_exam.partner_id.statut_cpf = "service_declared"
                    info_exam.sorti_formation = True
                    info_exam.partner_id.date_cpf = lastupd
                    if product_id:
                        info_exam.partner_id.id_edof = product_id.id_edof

    """utiliser api wedof pour changer etat de dossier sur edof selon l'absence le jour d'examen"""

    def change_etat_wedof_absent(self):
        company = self.env['res.company'].sudo().search([('id', "=", 2)])
        api_key = ""
        if company:
            api_key = company.wedof_api_key
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
            'X-API-KEY': api_key,
        }

        params_wedof = (
            ('order', 'desc'),
            ('state', 'inTraining'),
            ('sort', 'lastUpdate'),
            ('limit', '100'),
        )
        param_360 = (
            ('company', '56f5520e11d423f46884d593'),
            ('apiKey', 'cnkcbrhHKyfzKLx4zI7Ub2P5'),
            ('deleted', 'false')
        )
        data1 = '{}'
        data = '{\n "absenceDuration": 0,\n "forceMajeureAbsence": false,\n "trainingDuration": 0\n}'
        response_wedof = requests.get('https://www.wedof.fr/api/registrationFolders', headers=headers,
                                      params=params_wedof)
        registrations = response_wedof.json()
        for dossier in registrations:
            _logger.info('lengh api get %s' % str(len(registrations)))
            externalId = dossier['externalId']
            email = dossier['attendee']['email']
            lastupdatestr = str(dossier['lastUpdate'])
            lastupdate = datetime.strptime(lastupdatestr, '%Y-%m-%dT%H:%M:%S.%fz')
            newformat = "%d/%m/%Y %H:%M:%S"
            lastupdateform = lastupdate.strftime(newformat)
            lastupd = datetime.strptime(lastupdateform, "%d/%m/%Y %H:%M:%S")
            idform = dossier['trainingActionInfo']['externalId']
            training_id = ""
            if "_" in idform:
                idforma = idform.split("_", 1)
                if idforma:
                    training_id = idforma[1]
            info_exam = self.env['info.examen'].sudo().search([('partner_id.numero_cpf', "=", str(externalId)),
                                                               ('presence', "=", "Absent"),
                                                               ('partner_id.temps_minute', '>=', 60)], limit=1)
            if info_exam:
                product_id = self.env['product.template'].sudo().search(
                    [('id_edof', "=", str(training_id))], limit=1)
                existe = False
                """Chercher l'apprenant absent sur la plateforme"""
                response_plateforme = requests.get('https://app.360learning.com/api/v1/users', params=param_360)
                users = response_plateforme.json()
                for user in users:
                    user_mail = user['mail']
                    if user_mail == info_exam.partner_id.email:
                        existe = True
                        _logger.info("partner in 360 %s" % info_exam.partner_id.email)
                """si l'apprenant n'existe pas sur la plateforme on fait sortir de formation"""
                if existe == False:
                    _logger.info('non existant %s' % info_exam.partner_id.email)
                    _logger.info('apprenant existant %s' % info_exam.partner_id.numero_cpf)
                    response1 = requests.post(
                        'https://www.wedof.fr/api/registrationFolders/' + externalId + '/terminate',
                        headers=headers, data=data1)
                    response = requests.post(
                        'https://www.wedof.fr/api/registrationFolders/' + externalId + '/serviceDone',
                        headers=headers, data=data)
                    _logger.info('terminate %s' % str(response1.status_code))
                    _logger.info('service done %s' % str(response.status_code))
                    if response.status_code == 200:
                        """si statut est changé sur wedof on change statut_cpf sur fiche client """
                        _logger.info('if service done %s' % info_exam.partner_id.numero_cpf)
                        info_exam.partner_id.statut_cpf = "service_declared"
                        info_exam.sorti_formation = True
                        info_exam.partner_id.date_cpf = lastupd
                        if product_id:
                            info_exam.partner_id.id_edof = product_id.id_edof

    def update_session_examen(self):
        """ Mettre à jour le champ session selon condition de date examen = date examen de la session dans la fiche client"""
        for examen in self:
            session = self.env['res.partner'].sudo().search([('id', '=', examen.partner_id.id)], limit=1)
            if session and examen.date_exam:
                if examen.date_exam == examen.partner_id.mcm_session_id.date_exam:
                    examen.session_id = examen.partner_id.mcm_session_id

    def write(self, values):
        res = super(NoteExamen, self).write(values)
        # Add condition based on checkbox field paiement != True
        # to put auto value in "nombre de passage" based on sum of historic sessions
        if 'partner_id' in values:
            self.update_boolean_values()
        return res

    def create(self, values):
        res = super(NoteExamen, self).create(values)
        res.compute_moyenne_generale()
        res.mise_ajour_mode_financement()
        if 'partner_id' in values:
            """ Une affectation simple de champ presence lors 
            de la creation d'un examen avec une absence justifiée automatiquement """
            if 'presence' == 'present':
                self.partner_id.presence = "Présent(e)"
            if 'presence' == 'Absent':
                self.partner_id.presence = "Absent(e)"
            if 'presence' == 'absence_justifiee':
                self.partner_id.presence = "Absence justifiée"
            elif not 'presence':
                self.partner_id.presence = "_______"
        """ Génère automatiquement le nombre de passages en fonction des conditions, 
        si un pack (Pro, SOLO, repassage...) est égal à "examen" ou s'il y a une justification valide.  
        Après avoir vérifié la dernière ligne des notes d'examen si le numéro de passage == "premier'". 
        ainsi la ligne suivante sera déplacée comme la seconde... 
        Dans le cas contraire, le nombre de passage sera à nouveau le premier. """
        if res.partner_id.note_exam_id:
            if res.partner_id.module_id.product_id.default_code == 'examen' or res.partner_id.justification == 'absence_justifiee':
                info_exam = self.env['info.examen'].sudo().search(
                    [('partner_id', '=', res.partner_id.id), ('id', "!=", res.id)], order="id desc", limit=1)
                if info_exam:
                    if info_exam.nombre_de_passage == 'premier':
                        res.nombre_de_passage = 'deuxieme'
                    elif info_exam.nombre_de_passage == 'deuxieme':
                        res.nombre_de_passage = 'troisieme'
                    elif info_exam.nombre_de_passage == 'troisieme':
                        res.nombre_de_passage = 'premier'
                else:
                    res.nombre_de_passage = 'premier'
            else:
                res.nombre_de_passage = 'premier'
        return res
