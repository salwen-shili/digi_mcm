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

    @api.onchange('resultat', 'partner_id')
    def update_boolean_values(self):
        for rec in self.env['info.examen'].search([], order='id DESC'):
            if rec.resultat == 'recu':
                rec.is_recu = True
                print("rec.is_recu", rec.is_recu)
            if rec.resultat == 'ajourne':
                rec.is_ajourne = True
            if rec.presence == 'present':
                rec.is_present = True
            if rec.presence == 'Absent':
                rec.is_Absent = True
            if rec.presence == 'absence_justifiee':
                rec.is_absence_justifiee = True

    @api.onchange('partner_id', 'epreuve_a', 'epreuve_b', 'presence')
    def compute_moyenne_generale(self):
        """ This function used to auto display some result
        like the "Moyenne Generale" & "Mention" & "Resultat" """
        for rec in self:
            rec.moyenne_generale = (rec.epreuve_a + rec.epreuve_b) / 2
            if rec.epreuve_a >= 10 and rec.epreuve_b >= 8 and rec.moyenne_generale >= 12 and rec.partner_id:
                rec.moyenne_generale = rec.moyenne_generale
                rec.mention = 'recu'
                rec.resultat = 'recu'
                self.session_id = self.partner_id.mcm_session_id
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
                if 1 <= rec.epreuve_a < 21 or 1 <= rec.epreuve_b < 21 and not last_line.justification and rec.partner_id:
                    self.session_id = self.partner_id.mcm_session_id
                    self.date_exam = self.partner_id.mcm_session_id.date_exam
                    self.presence = 'present'
                    self.ville_id = self.partner_id.mcm_session_id.session_ville_id.id
                    self.partner_id.presence = "Présent(e)"
                    self.partner_id.resultat = "Ajourné(e)"
                elif rec.epreuve_a < 1 and rec.epreuve_b < 1 and not last_line.justification and rec.partner_id:
                    self.session_id = self.partner_id.mcm_session_id
                    self.date_exam = self.partner_id.mcm_session_id.date_exam
                    self.presence = 'Absent'
                    self.ville_id = self.partner_id.mcm_session_id.session_ville_id.id
                    self.partner_id.update({'presence': "Absent(e)"})
                    self.partner_id.resultat = "Ajourné(e)"
                elif rec.epreuve_a < 1 and rec.epreuve_b < 1 and last_line.justification is True and rec.partner_id:
                    self.session_id = last_line.session_id
                    self.date_exam = last_line.session_id.date_exam
                    self.presence = 'absence_justifiee'
                    self.ville_id = last_line.session_id.session_ville_id.id
                    self.partner_id.update({'presence': "Absence justifiée"})
                    self.partner_id.resultat = "Ajourné(e)"

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
        resultat.compute_moyenne_generale()
        resultat.mise_ajour_mode_financement()
        if 'partner_id' in vals:
            if 'presence' == 'present':
                self.partner_id.presence = "Présent(e)"
            if 'presence' == 'Absent':
                self.partner_id.presence = "Absent(e)"
            if 'presence' == 'absence_justifiee':
                self.partner_id.presence = "Absence justifiée"
            elif not 'presence':
                self.partner_id.presence = "_______"
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
                client.mode_de_financement = dict(facture._fields['methodes_payment'].selection).get(
                    facture.methodes_payment)
                print("client.mode_de_financement", client.mode_de_financement)

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
        if 'partner_id' in values or 'epreuve_a' in values:
            session_count = self.env['partner.sessions'].search_count(
                [('client_id', '=', self.partner_id.id), ('paiement', '!=', True)])
            if session_count == 1:
                self.nombre_de_passage = "premier"
                self.partner_id.nombre_de_passage = "Premier"
                print(self.partner_id.nombre_de_passage)
            if session_count == 2:
                self.nombre_de_passage = "deuxieme"
                self.partner_id.nombre_de_passage = "Deuxième"
            if session_count == 3:
                self.nombre_de_passage = "troisieme"
                self.partner_id.nombre_de_passage = "Troisième"
            if session_count == 4:
                self.nombre_de_passage = "premier"
                self.partner_id.nombre_de_passage = "Premier"
            if session_count == 5:
                self.nombre_de_passage = "deuxieme"
                self.partner_id.nombre_de_passage = "Deuxième"
            if session_count == 6:
                self.nombre_de_passage = "troisieme"
                self.partner_id.nombre_de_passage = "Troisième"
        return res
