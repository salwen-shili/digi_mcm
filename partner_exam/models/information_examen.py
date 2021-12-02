# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.tools import datetime, base64
from odoo.exceptions import ValidationError, _logger
import requests
from requests.structures import CaseInsensitiveDict
from datetime import datetime, timedelta, date
import logging

_logger = logging.getLogger(__name__)


class NoteExamen(models.Model):
    _name = "info.examen"
    _rec_name = 'partner_id'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Les Notes et les informations des examens"

    partner_id = fields.Many2one('res.partner', string="Client")
    epreuve_a = fields.Float(string="Epreuve A(QCM):", track_visibility='always', group_operator='avg')
    epreuve_b = fields.Float(string="Epreuve B(QRO)", track_visibility='always', default=1, group_operator='avg')
    moyenne_generale = fields.Float(string="Moyenne Générale", track_visibility='always', store=True, group_operator='avg')
    mention = fields.Selection(selection=[
        ('recu', 'reçu'),
        ('ajourne', 'ajourné')],
        string="Mention", default=False)
    resultat = fields.Selection(selection=[
        ('recu', 'Reçu'),
        ('ajourne', 'Ajourné')], string="Résultat")
    date_exam = fields.Date(string="Date Examen", track_visibility='always')
    active = fields.Boolean('Active', default=True)
    module_ids = fields.One2many('mcmacademy.module', 'info_examen_id')
    date_today = fields.Date(string="Date d'envoi de relevée de note: ", default=datetime.today())
    company_id = fields.Many2one(
        'res.company', string='Company', change_default=True,
        default=lambda self: self.env.company,
        required=False, readonly=False)
    nombre_de_passage = fields.Selection(selection=[
        ('premier', 'premier'),
        ('deuxieme', 'deuxième'),
        ('troisieme', 'troisième')],
        string="Nombre De Passage", default="premier")

    presence = fields.Selection(selection=[
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
    sorti_formation =fields.Boolean(string="Sorti de formation")

    @api.onchange('epreuve_a', 'epreuve_b', 'presence')
    def _compute_moyenne_generale(self):
        """ This function used to auto display some result
        like the "Moyenne Generale" & "Mention" & "Resultat" """
        for rec in self:
            rec.moyenne_generale = (rec.epreuve_a + rec.epreuve_b) / 2
            if rec.epreuve_a >= 10 and rec.epreuve_b >= 8 and rec.moyenne_generale >= 12:
                rec.moyenne_generale = rec.moyenne_generale
                rec.mention = 'recu'
                rec.resultat = 'recu'
                rec.sudo().write({'session_id': self.partner_id.mcm_session_id,
                                  'date_exam': self.partner_id.mcm_session_id.date_exam,
                                  'presence': 'present',
                                  'ville_id': self.partner_id.mcm_session_id.session_ville_id.id})
            else:
                # reset your fields
                rec.epreuve_a = rec.epreuve_a
                rec.epreuve_b = rec.epreuve_b
                rec.mention = 'ajourne'
                rec.resultat = 'ajourne'
                if rec.epreuve_a >= 1 and rec.epreuve_a < 21:
                    rec.presence = 'present'
                elif rec.epreuve_a < 1 and rec.epreuve_b < 1:
                    rec.presence = 'Absent'
                if rec.epreuve_b >= 1 and rec.epreuve_b < 21:
                    rec.presence = 'present'
                elif rec.epreuve_a < 1 and rec.epreuve_b < 1:
                    rec.presence = 'Absent'

    @api.onchange("résultat")
    def etat_de_client_apres_examen(self):
        """Fonction pour mettre le champs etat
        automatique depend de champ resultat,
        pour l'utilisé dans la template de "Atestation de suivi de formation" """
        for rec in self:
            if rec.resultat == 'recu':
                rec.etat = "avec succès"
            if not rec.resultat == "recu":
                rec.etat = "sans succès"

    @api.model
    def create(self, vals):
        resultat = super(NoteExamen, self).create(vals)
        resultat._compute_moyenne_generale()
        resultat.mise_ajour_mode_financement()
        return resultat

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

    """ Mettre à jour le champ mode de financement selon la facture """
    def mise_ajour_mode_financement(self):
        for client in self:
            facture = self.env['account.move'].sudo().search([('partner_id', '=', client.partner_id.id),
                                                              ('state', "=", "posted"), ], limit=1)
            _logger.info('facture %s', client.partner_id.email)
            _logger.info('facture %s', facture.methodes_payment)
            if facture:
                client.mode_de_financement = facture.methodes_payment

    """utiliser api wedof pour changer etat de dossier sur edof selon la presence le jour d'examen"""
    def change_etat_wedof(self):
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
            'X-API-KEY': '026514d6bc7d880515a27eae4947bccef4fbbf03',
        }
        params_wedof = (
            ('order', 'asc'),
            ('type', 'all'),
            ('state', 'inTraining'),
            ('billingState', 'all'),
            ('certificationState', 'all'),
            ('sort', 'lastUpdate'),
            ('limit', '1000')
        )
        data1 = '{}'
        data = '{\n "absenceDuration": 0,\n "forceMajeureAbsence": false,\n "trainingDuration": 0\n}'
        response = requests.get('https://www.wedof.fr/api/registrationFolders', headers=headers,
                                params=params_wedof)
        registrations = response.json()
        for dossier in registrations:
            _logger.info('lengh api get %s' % str(len(registrations)))
            externalId = dossier['externalId']
            email = dossier['attendee']['email']
            info_exam = self.env['info.examen'].sudo().search([('partner_id.numero_cpf', "=", str(externalId)),
                                                               ('presence', "=", "present")], limit=1)

            if info_exam:
                _logger.info('apprenant existant %s' % info_exam.partner_id.numero_cpf)
                response1 = requests.post('https://www.wedof.fr/api/registrationFolders/' + externalId + '/terminate',
                                          headers=headers, data=data1)
                response = requests.post('https://www.wedof.fr/api/registrationFolders/' + externalId + '/serviceDone',
                                         headers=headers, data=data)
                
                info_exam.sorti_formation=True
                _logger.info('terminate %s' % str(response1.status_code))
                _logger.info('service done %s' % str(response.status_code))

    """utiliser api wedof pour changer etat de dossier sur edof selon l'absence le jour d'examen"""
    def change_etat_wedof_absent(self):
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
            'X-API-KEY': '026514d6bc7d880515a27eae4947bccef4fbbf03',
        }
        params_wedof = (
            ('order', 'asc'),
            ('type', 'all'),
            ('state', 'inTraining'),
            ('billingState', 'all'),
            ('certificationState', 'all'),
            ('sort', 'lastUpdate'),
            ('limit', '1000')
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
            info_exam = self.env['info.examen'].sudo().search([('partner_id.numero_cpf', "=", str(externalId)),
                                                               ('presence', "=", "Absent"),
                                                               ('partner_id.temps_minute', '>=', 60)], limit=1)
            if info_exam:
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
                    info_exam.sorti_formation=True

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
        if 'partner_id' in values or 'epreuve_a' in values:
            session_one = self.env['partner.sessions'].search_count(
                [('client_id', '=', self.partner_id.id), ('paiement', '!=', True)])
            if session_one == 1:
                self.nombre_de_passage = "premier"
            session_two = self.env['partner.sessions'].search_count(
                [('client_id', '=', self.partner_id.id), ('paiement', '!=', True)])
            if session_two == 2:
                self.nombre_de_passage = "deuxieme"
            session_three = self.env['partner.sessions'].search_count(
                [('client_id', '=', self.partner_id.id), ('paiement', '!=', True)])
            if session_three == 3:
                self.nombre_de_passage = "troisieme"
            session_four = self.env['partner.sessions'].search_count(
                [('client_id', '=', self.partner_id.id), ('paiement', '!=', True)])
            if session_four == 4:
                self.nombre_de_passage = "premier"
            session_five = self.env['partner.sessions'].search_count(
                [('client_id', '=', self.partner_id.id), ('paiement', '!=', True)])
            if session_five == 5:
                self.nombre_de_passage = "deuxieme"
            session_six = self.env['partner.sessions'].search_count(
                [('client_id', '=', self.partner_id.id), ('paiement', '!=', True)])
            if session_six == 6:
                self.nombre_de_passage = "troisieme"
        return res
