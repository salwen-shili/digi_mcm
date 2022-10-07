# -*- coding: utf-8 -*-
import functools
import xmlrpc.client
import requests
from requests.structures import CaseInsensitiveDict
from datetime import datetime, timedelta, date
import re
import json
from odoo import _
import locale
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, SUPERUSER_ID
from odoo.exceptions import ValidationError
from unidecode import unidecode
import logging
import pyshorteners

_logger = logging.getLogger(__name__)


class partner(models.Model):
    _inherit = 'res.partner'

    # ajouter champs au modele partner par defaut res.partner ne sont pas des instructors

    apprenant = fields.Boolean("Apprenant sur 360")
    group_id = fields.Many2many('plateforme_pedagogique.groupe', string="Groupe")
    # champs pour recuperer les statistiques
    assignedPrograms = fields.Integer(string='Nombre de programmes attribués')

    last_login = fields.Char(string="Derniere Activité")
    # learner_achivement=fields.Char(string="Réalisations des apprenants")
    averageScore = fields.Integer(string="Score Moyen", readonly=True)
    totalTimeSpentInMinutes = fields.Char(string="temps passé en minutes", readonly=False)
    password360 = fields.Char()  # Champs pour stocker le mot de passe non crypté
    firstName = fields.Char()
    lastName = fields.Char()
    date_creation = fields.Char(string="Date d'inscription")
    messages = fields.Char(string='Messages Postés')
    # publications = fields.Char(string='Cours ou programmes publiés')
    total_time_visio_min = fields.Integer()
    total_time_visio_hour = fields.Char(default="0h0min")
    total_time_appels_min = fields.Integer()
    total_time_appels_hour = fields.Char(default="0h0min")
    total_time_min = fields.Integer()
    total_time_hours = fields.Char(default="0h0min")
    reactions = fields.Char()
    comments = fields.Char()
    renounce_request = fields.Boolean(
        "Renonciation au droit de rétractation conformément aux dispositions de l'article L.221-28 1°")
    toDeactivateAt = fields.Char("Date de suppression")
    passage_exam = fields.Boolean("Examen passé", default=False)
    stats_ids = fields.Many2one('plateforme_pedagogique.user_stats')
    second_email = fields.Char(string='Email secondaire', track_visibility='always')
    temps_minute = fields.Integer(string="Temps passé en minutes")  # Champs pour récuperer temps en minute par api360
    temps_update_minute = fields.Char()
    is_pole_emploi = fields.Boolean(
        string="Pole Emploi")  # champ pour distinguer le mode de financement cpf+pole emploi
    # Recuperation de l'état de facturation pour cpf de wedof et carte bleu de odoo
    etat_financement_cpf_cb = fields.Selection([('untreated', 'Non Traité'),
                                                ('validated', 'Validé'),
                                                ('accepted', 'Accepté'),
                                                ('in_training', 'En Formation'),
                                                ('out_training', 'Sortie de Formation'),
                                                ('service_declared', 'Service Fait Declaré'),
                                                ('service_validated', 'Service Fait Validé'),
                                                ('bill', 'Facturé'),
                                                ('canceled', 'Annulé'),
                                                ('paid', 'Payé'),
                                                ('not_paid', 'Non payées'),
                                                ('in_payment', 'En paiement')],
                                               string="Financement", default=False)
    is_not_paid = fields.Boolean(default=False)

    @api.onchange('total_time_visio_min', 'total_time_appels_min', 'temps_minute')
    def convert_minutes_to_hours(self):
        """ Convert Minutes To Hours And Minutes """
        if self.total_time_visio_min or self.total_time_appels_min or self.temps_minute:
            hours = self.total_time_visio_min // 60
            minutes = self.total_time_visio_min % 60
            self.total_time_visio_hour = str(hours) + "h" + str(minutes) + "min"
            # Calcul total time_appels_min
            hour = self.total_time_appels_min // 60
            min = self.total_time_appels_min % 60
            self.total_time_appels_hour = str(hour) + "h" + str(min) + "min"
            # add field for update temps plateforme
            hour_temps_minute = self.temps_minute // 60
            min_temps_minute = self.temps_minute % 60
            self.temps_update_minute = str(hour_temps_minute) + "h" + str(min_temps_minute) + "min"
            # Calcul total time visio + appels + plateforme
            self.total_time_min = int(self.total_time_visio_min) + int(self.total_time_appels_min) + int(
                self.temps_minute)
            tot_min = int(self.total_time_min) // 60
            tot_hour = int(self.total_time_min) % 60
            tot_two = str(tot_min) + "h" + str(tot_hour) + "min"
            self.total_time_hours = tot_two

    def write(self, vals):
        """Changer login d'apprenant au moment de changement d'email sur la fiche client"""
        if 'email' in vals and vals['email'] is not None:

            # Si email changé on change sur login
            users = self.env['res.users'].sudo().search([('partner_id', "=", self.id)])
            if users:
                for user in users:
                    _logger.info("loginn---------- %s" % str(user.login))
                    user.sudo().write({
                        'login': vals['email']
                    })
                    # print('if user',user)
        record = super(partner, self).write(vals)
        return record

    def convertir_date_inscription(self):
        """Convertir date d'inscription de string vers date avec une format %d/%m/%Y"""
        locale.setlocale(locale.LC_TIME, str(self.env.user.lang) + '.utf8')
        for rec in self.env['res.partner'].sudo().search([('statut', "=", "won")]):
            if rec.date_creation:
                new_date_format = datetime.strptime(str(rec.date_creation), "%d %B %Y").date().strftime('%d/%m/%Y')
                rec.date_creation = new_date_format

    # Recuperer les utilisateurs de 360learning
    def getusers(self):
        locale.setlocale(locale.LC_TIME, str(self.env.user.lang) + '.utf8')
        params = (
            ('company', '56f5520e11d423f46884d593'),
            ('apiKey', 'cnkcbrhHKyfzKLx4zI7Ub2P5'),
        )
        response = requests.get('https://app.360learning.com/api/v1/users', params=params)
        users = response.json()
        # Faire un parcours sur chaque user et extraire ses statistiques
        for user in users:
            iduser = user['_id']
            email = user['mail']
            _logger.info('user %s' % str(user))
            response_user = requests.get('https://app.360learning.com/api/v1/users/' + iduser, params=params)
            table_user = response_user.json()
            lastlogin = ""
            if 'lastLoginAt' in table_user:
                lastlogin = str(table_user['lastLoginAt'])
            _logger.info('user date supp %s' % table_user['lastLoginAt'])
            times = ''
            time = 0
            # Ecrire le temps récupéré de 360 sous forme d'heures et minutes
            if 'totalTimeSpentInMinutes' in table_user:
                time = int(table_user['totalTimeSpentInMinutes'])
                heure = time // 60
                minute = time % 60
                times = str(heure) + 'h' + str(minute) + 'min'
                _logger.info("heuurs %s" % str(times))
                _logger.info("user %s" % str(email))
                if (heure == 0):
                    times = str(minute) + 'min'
                    _logger.info("timers %s" % str(times))
                if (minute == 0):
                    _logger.info("minute 0 %s" % str(times))
                    times = '0min'
            average = ''

            # Vérifier l'existance de champ dans table_user
            if 'averageScore' in table_user:
                average = str(table_user['averageScore'])
                print(average)
            # Si lastlogin n'est pas vide on change le format de date sous forme "01 mars, 2021"
            if (len(lastlogin) > 0):
                date_split = lastlogin[0:19]
                date = datetime.strptime(date_split, "%Y-%m-%dT%H:%M:%S")
                new_format = '%d %B, %Y'
                new_format = '%d %B, %Y'
                last_login = str(date.strftime(new_format))
            message = "0"
            if ('messages' in table_user):
                message = table_user['messages']
            # publication = ''
            # if ('publications' in table_user):
            #     publication = table_user['publications']
            comment = "0"
            if ('comments' in table_user):
                comments = table_user['comments']
            reaction = "0"
            if ('reactions' in table_user):
                reaction = table_user['reactions']
            # Chercher par email le meme client pour lui affecter les stats de 360
            partners = self.env['res.partner'].sudo().search([('email', "=", email)])
            for partner in partners:
                if partners:
                    """get first value of lastLoginAt as date inscription"""
                    if not partner.date_creation and not partner.last_login:
                        partner.sudo().write({
                            'date_creation': last_login
                        })
                    partner.sudo().write({
                        'last_login': last_login,
                        'averageScore': average,
                        'comments': comment,
                        'reactions': reaction,
                        'messages': message,
                        'totalTimeSpentInMinutes': times,
                        'assignedPrograms': table_user['assignedPrograms'],
                        'toDeactivateAt': table_user['toDeactivateAt'],
                        'apprenant': True,
                        'temps_minute': time

                    })
                    print("partner", partner.name, partner.last_login)

    # Recuperer les statistique par session de 360learning
    def getstats_session(self):
        params = (
            ('company', '56f5520e11d423f46884d593'),
            ('apiKey', 'cnkcbrhHKyfzKLx4zI7Ub2P5'),
        )
        response = requests.get('https://app.360learning.com/api/v1/courses', params=params)
        sessions = response.json()
        # faire un parcours sur chaque user et extraie ses statistique
        for session in sessions:
            id = session['_id']
            re = requests.get('https://app.360learning.com/api/v1/courses/' + id + '/stats/youcefallahoum@gmail.com',
                              params=params)
            pogramstat = re.json()
            print("courses:", session['name'], '*******', pogramstat)

    # En cas de changement de statut de client cette methode est exécutée

    # def write(self, vals):
    #     if 'statut' in vals:
    #         # Si statut annulé on supprime i-One
    #         if vals['statut'] == 'canceled':
    #             self.supprimer_ione_manuelle()
    #     record = super(partner, self).write(vals)
    #     return record

    # Ajout automatique d' i-One sur 360learning
    def Ajouter_iOne_auto(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if "localhost" not in str(base_url) and "dev" not in str(base_url):
            # company=self.env['res.company'].sudo().search([('id',"=",2)])
            # api_key=""
            # if company:
            #     api_key=company.wedof_api_key
            for partner in self.env['res.partner'].sudo().search([('statut', "=", "won"),
                                                                  ('statut_cpf', "!=", "canceled")
                                                                  ]):
                # Pour chaque apprenant chercher son contrat
                sale_order = self.env['sale.order'].sudo().search([('partner_id', '=', partner.id),
                                                                   ('session_id', '=', partner.mcm_session_id.id),
                                                                   ('module_id', '=', partner.module_id.id),
                                                                   ('state', '=', 'sale'),
                                                                   ('session_id.date_exam', '>', date.today())
                                                                   ], limit=1, order="id desc")

                today = date.today()
                _logger.info('sale order %s ' % sale_order.name)
                # Récupérer les documents et vérifier si ils sont validés ou non
                documents = self.env['documents.document'].sudo().search([('partner_id', '=', partner.id)])
                document_valide = False
                count = 0
                for document in documents:
                    if (document.state == "validated"):
                        count = count + 1
                if (count == len(documents) and count != 0):
                    document_valide = True
                # Cas particulier on doit Vérifier si partner a choisi une formation et si ses documents sont validés
                if partner.mode_de_financement == "particulier":
                    if ((sale_order) and (document_valide)):
                        statut = partner.statut
                        # Vérifier si contrat signé ou non
                        if (sale_order.state == 'sale') and (sale_order.signature):

                            # Si demande de renonce est coché donc l'apprenant est ajouté sans attendre 14jours
                            if partner.renounce_request:
                                self.ajouter_iOne(partner)
                            # si non il doit attendre 14jours pour etre ajouté
                            if not partner.renounce_request and (
                                    sale_order.signed_on + timedelta(days=14)) <= datetime.today():
                                self.ajouter_iOne(partner)
                """cas de cpf on vérifie la validation des document , la case de renonciation et la date d'examen qui doit etre au futur """
                if partner.mode_de_financement == "cpf":
                    if document_valide and partner.mcm_session_id.date_exam and (
                            partner.mcm_session_id.date_exam > date.today()):
                        if partner.renounce_request:
                            self.ajouter_iOne(partner)
                        if not partner.renounce_request and partner.numero_cpf:
                            """chercher le dossier cpf sur wedof pour prendre la date d'ajout"""
                            headers = {
                                'accept': 'application/json',
                                'Content-Type': 'application/json',
                                'X-API-KEY': partner.company_id.wedof_api_key,
                            }
                            responsesession = requests.get(
                                'https://www.wedof.fr/api/registrationFolders/' + partner.numero_cpf, headers=headers)
                            dossier = responsesession.json()
                            _logger.info('session %s' % str(dossier))
                            dateDebutSession_str = ""
                            if "trainingActionInfo" in dossier:
                                dateDebutSession_str = dossier['trainingActionInfo']['sessionStartDate']
                                dateDebutSession = datetime.strptime(dateDebutSession_str, '%Y-%m-%dT%H:%M:%S.%fz')
                                if dateDebutSession <= datetime.today():
                                    self.ajouter_iOne(partner)

    # Ajouter ione manuellement
    def ajouter_iOne_manuelle(self, partner):
        _logger.info("++++++++++++Cron ajouter_iOne_manuelle++++++++++++++++++++++")
        product_name = partner.module_id.product_id.name
        sale_order = self.env['sale.order'].sudo().search([('partner_id', '=', partner.id),
                                                           ('session_id', '=', partner.mcm_session_id.id),
                                                           ('module_id', '=', partner.module_id.id),
                                                           ('state', '=', 'sale'),
                                                           ], limit=1, order="id desc")
        _logger.info("sale order %s" % sale_order)
        # Pour chaque apprenant chercher sa facture
        # facture = self.env['account.move'].sudo().search([('session_id', '=', self.mcm_session_id.id),
        #                                                   ('module_id', '=', self.module_id.id),
        #                                                   ('state', '=', 'posted')
        #                                                   ], order="invoice_date desc", limit=1)
        # date_facture = facture.invoice_date
        # Calculer date d'ajout apres 14jours de date facture
        # date_ajout = date_facture + timedelta(days=14)
        today = datetime.today()
        # Récupérer les documents et vérifier si ils sont validés ou non
        documents = self.env['documents.document'].sudo().search([('partner_id', '=', partner.id)])
        document_valide = False
        count = 0
        for document in documents:
            if (document.state == "validated"):
                count = count + 1
                print('valide')
        print('count', count, 'len', len(documents))
        if (count == len(documents) and count != 0):
            # _logger.info("++++++++++++Cron DOC VALIDER++++++++++++++++++++++")
            document_valide = True
        if partner.mode_de_financement == "particulier":
            if ((sale_order) and (document_valide)):
                # Vérifier si contrat signé ou non
                if (sale_order.state == 'sale') and (sale_order.signature):
                    # Si demande de renonce est coché donc l'apprenant est ajouté sans attendre 14jours
                    if (partner.renounce_request):
                        partner.ajouter_iOne(partner)
                    # si non il doit attendre 14jours pour etre ajouté
                    if not partner.renounce_request and (sale_order.signed_on + timedelta(days=14)) <= today:
                        self.ajouter_iOne(partner)
        """cas de cpf on vérifie la validation des document , la case de renonciation et la date d'examen qui doit etre au futur """
        if partner.mode_de_financement == "cpf":
            if (document_valide) and (partner.mcm_session_id.date_exam) and (
                    partner.mcm_session_id.date_exam > date.today()):
                if (partner.renounce_request):
                    self.ajouter_iOne(partner)
                if not (partner.renounce_request) and partner.numero_cpf:
                    """chercher le dossier cpf sur wedof pour prendre la date d'ajout"""
                    headers = {
                        'accept': 'application/json',
                        'Content-Type': 'application/json',
                        'X-API-KEY': partner.company_id.wedof_api_key,
                    }
                    responsesession = requests.get('https://www.wedof.fr/api/registrationFolders/' + partner.numero_cpf,
                                                   headers=headers)
                    dossier = responsesession.json()
                    dateDebutSession_str = ""
                    _logger.info('session %s' % str(dossier))
                    if "trainingActionInfo" in dossier:
                        dateDebutSession_str = dossier['trainingActionInfo']['sessionStartDate']
                        dateDebutSession = datetime.strptime(dateDebutSession_str, '%Y-%m-%dT%H:%M:%S.%fz')
                        if dateDebutSession <= datetime.today():
                            self.ajouter_iOne(partner)

    def ajouter_iOne_button(self):
        _logger.info("++++++++++++Cron ajouter_iOne_manuelle++++++++++++++++++++++")
        product_name = self.module_id.product_id.name
        sale_order = self.env['sale.order'].sudo().search([('partner_id', '=', self.id),
                                                           ('session_id', '=', self.mcm_session_id.id),
                                                           ('module_id', '=', self.module_id.id),
                                                           ('state', '=', 'sale'),
                                                           ], limit=1, order="id desc")
        _logger.info("sale order %s" % sale_order)
        # Pour chaque apprenant chercher sa facture
        # facture = self.env['account.move'].sudo().search([('session_id', '=', self.mcm_session_id.id),
        #                                                   ('module_id', '=', self.module_id.id),
        #                                                   ('state', '=', 'posted')
        #                                                   ], order="invoice_date desc", limit=1)
        # date_facture = facture.invoice_date
        # Calculer date d'ajout apres 14jours de date facture
        # date_ajout = date_facture + timedelta(days=14)
        today = datetime.today()
        # Récupérer les documents et vérifier si ils sont validés ou non
        documents = self.env['documents.document'].sudo().search([('partner_id', '=', self.id)])
        document_valide = False
        count = 0
        for document in documents:
            if (document.state == "validated"):
                count = count + 1
                print('valide')
        print('count', count, 'len', len(documents))
        if (count == len(documents) and count != 0):
            # _logger.info("++++++++++++Cron DOC VALIDER++++++++++++++++++++++")
            document_valide = True
        if self.mode_de_financement == "particulier":
            if ((sale_order) and (document_valide)):
                # Vérifier si contrat signé ou non
                if (sale_order.state == 'sale') and (sale_order.signature):
                    # Si demande de renonce est coché donc l'apprenant est ajouté sans attendre 14jours
                    if (self.renounce_request):
                        self.ajouter_iOne(self)
                    # si non il doit attendre 14jours pour etre ajouté
                    if not self.renounce_request and (sale_order.signed_on + timedelta(days=14)) <= today:
                        self.ajouter_iOne(self)
        """cas de cpf on vérifie la validation des document , la case de renonciation et la date d'examen qui doit etre au futur """
        if self.mode_de_financement == "cpf":
            if (document_valide) and (self.mcm_session_id.date_exam) and (
                    self.mcm_session_id.date_exam > date.today()):
                if (self.renounce_request):
                    self.ajouter_iOne(self)
                if not (self.renounce_request) and self.numero_cpf:
                    """chercher le dossier cpf sur wedof pour prendre la date d'ajout"""
                    headers = {
                        'accept': 'application/json',
                        'Content-Type': 'application/json',
                        'X-API-KEY': partner.company_id.wedof_api_key,
                    }
                    responsesession = requests.get('https://www.wedof.fr/api/registrationFolders/' + partner.numero_cpf,
                                                   headers=headers)
                    dossier = responsesession.json()
                    dateDebutSession_str = ""
                    _logger.info('session %s' % str(dossier))
                    if "trainingActionInfo" in dossier:
                        dateDebutSession_str = dossier['trainingActionInfo']['sessionStartDate']
                        dateDebutSession = datetime.strptime(dateDebutSession_str, '%Y-%m-%dT%H:%M:%S.%fz')
                        if dateDebutSession <= datetime.today():
                            self.ajouter_iOne(self)

    def ajouter_iOne(self, partner):
        new_email = ""
        # Remplacez les paramètres régionaux de l'heure par le paramètre de langue actuel
        # du compte dans odoo
        self.env.user.lang = 'fr_FR'
        locale.setlocale(locale.LC_TIME, str(self.env.user.lang) + '.utf8')
        company = str(partner.module_id.company_id.id)
        product_name = partner.module_id.product_id.name
        if (not (product_name)):
            product_name = ''
        if not (partner.phone):
            partner.phone = ''
        # Extraire firstName et lastName à partir du champs name
        self.diviser_nom(partner)

        new_format = '%d %B %Y'
        if (partner.mcm_session_id.date_exam) and (partner.mcm_session_id.session_ville_id.name_ville):
            ville = str(partner.mcm_session_id.session_ville_id.name_ville).upper()
            _logger.info('----ville %s' % ville)
            date_exam = partner.mcm_session_id.date_exam
            # Changer format de date et la mettre en majuscule
            datesession = str(date_exam.strftime(new_format).upper())
            date_session = unidecode(datesession)
            responce_api = False
            # Récuperer le mot de passe à partir de res.users
            user = self.env['res.users'].sudo().search([('partner_id', '=', partner.id)], limit=1)
            _logger.info('avant if login user %s' % user.login)
            _logger.info('avant if partner email %s' % partner.email)

            if user:
                id_Digimoov_bienvenue = '56f5520e11d423f46884d594'
                id_Digimoov_Examen_Attestation = '5f9af8dae5769d1a2c9d5047'
                params = (
                    ('company', '56f5520e11d423f46884d593'),
                    ('apiKey', 'cnkcbrhHKyfzKLx4zI7Ub2P5'),
                )
                company_id = '56f5520e11d423f46884d593'
                api_key = 'cnkcbrhHKyfzKLx4zI7Ub2P5'
                urluser = ' https://app.360learning.com/api/v1/users?company=' + company_id + '&apiKey=' + api_key
                url_groups = 'https://app.360learning.com/api/v1/groups'
                url_unsubscribeToEmailNotifications = ' https://app.360learning.com/api/v1/users/unsubscribeToEmailNotifications?company=' + company_id + '&apiKey=' + api_key
                headers = CaseInsensitiveDict()
                headers["Content-Type"] = "application/json"

                invit = False
                create = False
                # Si le mot de passe n'est pas récupérée au moment d'inscrit on invite l'apprennant
                # if user.password360==False:
                # data_user ='{"mail":"' + partner.email + '"}'
                # resp_invit = requests.post(urluser, headers=headers, data=data_user)
                # if(resp_invit.status_code == 200):
                #     invit=True
                # Si non si mot de passe récupéré on l'ajoute sur la plateforme avec le meme mot de passe
                if (user.password360) and (company == '2'):
                    partner.password360 = user.password360
                    # password = str(user.password360.encode('utf-8'))
                    email = partner.email
                    # Désactiver les notifications par email
                    data_email = json.dumps({
                        "usersEmails": [
                            partner.email
                        ]
                    })
                    resp_unsub_email = requests.put(url_unsubscribeToEmailNotifications, headers=headers,
                                                    data=data_email)
                    _logger.info('desactiver email %s' % str(resp_unsub_email))
                    # Ajouter i-One to table user

                    data_user = {"mail": partner.email,
                                 "password": partner.password360,
                                 "firstName": partner.firstName,
                                 "lastName": partner.lastName,
                                 "phone": partner.phone,
                                 "lang": "fr",
                                 "sendCredentials": "true"}
                    resp = requests.post(urluser, headers=headers, data=json.dumps(data_user))
                    _logger.info('data_user %s' % str(data_user))
                    respo = str(json.loads(resp.text))
                    responce_api = json.loads(resp.text)
                    _logger.info('response addd  %s' % respo)
                    if (resp.status_code == 200):
                        create = True
                data_group = {}
                # Si l'apprenant a été ajouté sur table user on l'affecte aux autres groupes
                if (create):
                    _logger.info('create %s' % user.login)
                    today = date.today()
                    new_format = '%d/%m/%Y'
                    # Changer format de date et la mettre en majuscule
                    date_ajout = today.strftime(new_format)
                    # partner.date_creation = date_ajout
                    """Remplir champs date_creation  """
                    # self._cr.execute(
                    #     """UPDATE res_partner SET date_creation = %s WHERE id=%s""", (date_ajout, partner.id,))
                    # self._cr.commit()
                    _logger.info('date_inscrit %s' % str(partner.date_creation))

                    # Affecter i-One to groupe digimoov-bienvenue
                    urlgroup_Bienvenue = ' https://app.360learning.com/api/v1/groups/' + id_Digimoov_bienvenue + '/users/' + partner.email + '?company=' + company_id + '&apiKey=' + api_key

                    respgroupe = requests.put(urlgroup_Bienvenue, headers=headers, data=data_group)
                    print('bienvenue ', respgroupe.status_code, partner.date_creation)
                    partner.apprenant = True
                    # Affecter i-One à un pack et session choisi
                    response_grps = requests.get(url_groups, params=params)
                    existe = False
                    groupes = response_grps.json()
                    # print(response_grps.json())
                    company = str(partner.module_id.company_id.id)
                    for groupe in groupes:
                        # Convertir le nom en majuscule
                        nom_groupe = str(groupe['name']).upper()
                        print('nom groupe', groupe)
                        id_groupe = groupe['_id']
                        # affecter à groupe digimoov
                        digimoov_examen_leger = "Digimoov - Attestation de capacité de transport de marchandises de moins de 3.5t (léger)"
                        digimoov_examen_lourd = "Digimoov - Attestation de capacité de transport de marchandises de plus de 3.5t (lourd)"

                        # Si la company est digimoov on ajoute i-One sur 360
                        if (company == '2'):
                            """vérifier si formation leger ou lourd"""
                            if (partner.module_id.product_id.default_code == "transport-routier"):
                                if (nom_groupe == digimoov_examen_lourd.upper()):
                                    id_Digimoov_Examen_Attestation = id_groupe
                                    urlsession = ' https://app.360learning.com/api/v1/groups/' + id_Digimoov_Examen_Attestation + '/users/' + partner.email + '?company=' + company_id + '&apiKey=' + api_key
                                    respsession = requests.put(urlsession, headers=headers, data=data_group)

                            else:
                                if (nom_groupe == digimoov_examen_leger.upper()):
                                    id_Digimoov_Examen_Attestation = id_groupe
                                    urlsession = ' https://app.360learning.com/api/v1/groups/' + id_Digimoov_Examen_Attestation + '/users/' + partner.email + '?company=' + company_id + '&apiKey=' + api_key
                                    respsession = requests.put(urlsession, headers=headers, data=data_group)

                                # Affecter à un pack solo
                            packsolo = "Digimoov - Pack Solo"
                            if (("solo" in product_name) and (nom_groupe == packsolo.upper())):
                                print(partner.module_id.name)
                                urlgrp_solo = ' https://app.360learning.com/api/v1/groups/' + id_groupe + '/users/' + partner.email + '?company=' + company_id + '&apiKey=' + api_key
                                respgrp_solo = requests.put(urlgrp_solo, headers=headers, data=data_group)
                                print('affecté à solo', respgrp_solo.status_code)

                            # Affecter à un pack pro
                            pack_pro = "Digimoov - Pack Pro"
                            if (("pro" in product_name) and (nom_groupe == pack_pro.upper())):
                                print(partner.module_id.name)
                                urlgrp_pro = ' https://app.360learning.com/api/v1/groups/' + id_groupe + '/users/' + partner.email + '?company=' + company_id + '&apiKey=' + api_key
                                respgrp_pro = requests.put(urlgrp_pro, headers=headers, data=data_group)
                            # Affecter à unpremium
                            packprem = "Digimoov - Pack Premium"
                            if (("premium" in product_name) and (nom_groupe == packprem.upper())):
                                print(partner.module_id.name)
                                urlgrp_prim = 'https://app.360learning.com/api/v1/groups/' + id_groupe + '/users/' + partner.email + '?company=' + company_id + '&apiKey=' + api_key
                                respgrp_prim = requests.put(urlgrp_prim, headers=headers, data=data_group)

                            # Affecter apprenant à Digimoov-Révision
                            revision = "Digimoov - Pack Repassage Examen"
                            if (("Repassage d'examen" in product_name) and (nom_groupe == revision.upper())):
                                urlgrp_revision = ' https://app.360learning.com/api/v1/groups/' + id_groupe + '/users/' + partner.email + '?company=' + company_id + '&apiKey=' + api_key
                                respgrp_revision = requests.put(urlgrp_revision, headers=headers, data=data_group)

                            # Affecter apprenant à Digimoov-lourd
                            lourd = "Digimoov - Formation capacité lourde"
                            if (("lourd" in product_name) and (nom_groupe == lourd.upper())):
                                urlgrp_revision = 'https://app.360learning.com/api/v1/groups/' + id_groupe + '/users/' + partner.email + '?company=' + company_id + '&apiKey=' + api_key
                                respgrp_revision = requests.put(urlgrp_revision, headers=headers, data=data_group)

                            # Affecter apprenant à une session d'examen
                            print('date, ville', ville, date_session)
                            if (ville in nom_groupe) and (date_session in nom_groupe):
                                existe = True
                                urlsession = 'https://app.360learning.com/api/v1/groups/' + id_groupe + '/users/' + partner.email + '?company=' + company_id + '&apiKey=' + api_key
                                respsession = requests.put(urlsession, headers=headers, data=data_group)

                    # Si la session n'est pas trouvée sur 360 on l'ajoute
                    print('exist', existe)
                    if not (existe):
                        nom = ville + ' - ' + date_session
                        nomgroupe = unidecode(nom)
                        print(nomgroupe)
                        urlgroups = 'https://app.360learning.com/api/v1/groups?company=' + company_id + '&apiKey=' + api_key
                        data_session = '{"name":"' + nomgroupe + '","parent":"' + id_Digimoov_Examen_Attestation + '"  , "public":"false" }'
                        create_session = requests.post(urlgroups, headers=headers, data=data_session)
                        print('creer  une session', create_session.status_code)
                        response_grpss = requests.get(url_groups, params=params)
                        groupess = response_grpss.json()
                        for groupe in groupess:
                            # Convertir le nom en majuscule
                            nom_groupe = str(groupe['name']).upper()
                            id_groupe = groupe['_id']
                            # Affecter apprenant à la nouvelle session d'examen
                            if (ville in nom_groupe) and (date_session in nom_groupe):
                                existe = True
                                urlsession = 'https://app.360learning.com/api/v1/groups/' + id_groupe + '/users/' + partner.email + '?company=' + company_id + '&apiKey=' + api_key
                                respsession = requests.put(urlsession, headers=headers, data=data_group)
                                print(existe, 'ajouter à son session', respsession.status_code)

                    self.send_email(partner)
                    """"we send sms to client contains link to register in 360learning."""
                    body = "Digimoov vous confirme votre inscription à la Formation capacité de transport de marchandises. RDV sur notre plateforme https://www.digimoov.fr/r/SnB"
                    self.send_sms(body, partner)
                if not (create):
                    """Créer des tickets contenant le message  d'erreur pour service client et service IT
                    si l'apprenant n'est pas ajouté sur 360"""
                    if responce_api and str(responce_api) != "{'error': 'user_already_exists'}":
                        if str(responce_api) == "{'error': 'unavailableEmails'}":

                            vals = {
                                'description': 'Apprenant non ajouté sur 360 %s' % (partner.name),
                                'name': 'Email non valide ',
                                'team_id': self.env['helpdesk.team'].sudo().search(
                                    [('name', 'like', 'Client'), ('company_id', "=", 2)],
                                    limit=1).id,
                            }
                            description = "Apprenant non ajouté sur 360 " + str(partner.name)
                            ticket = self.env['helpdesk.ticket'].sudo().search([("description", "=", description),
                                                                                ("team_id.name", 'like', 'Client')])
                            if not ticket:
                                new_ticket = self.env['helpdesk.ticket'].sudo().create(
                                    vals)
                            """Si message d'erreur "unavailableEmails" on ajoute #digimoov à l'email pour qu'il sera ajouté sur la plateforme 360"""
                            old_email = partner.email
                            position = old_email.index('@')
                            new_email = old_email[:position] + '#digimoov' + old_email[position:]
                            _logger.info("new email %s" % new_email)
                            partner.email = new_email
                            partner.second_email = new_email
                            """Changer format du numero de tel pour envoyer le sms """
                            if partner.email and "#" in partner.email:
                                _logger.info("send mail and sms %s" % str(partner.email))
                                if partner.phone:
                                    phone = str(partner.phone.replace(' ', ''))[-9:]
                                    phone = '+33' + ' ' + phone[0:1] + ' ' + phone[1:3] + ' ' + phone[
                                                                                                3:5] + ' ' + phone[
                                                                                                             5:7] + ' ' + phone[
                                                                                                                          7:]
                                    partner.phone = phone
                                """envoyer SMS pour informer l'apprenant de sa nouvelle adresse email """
                                new_login = partner.email
                                name = partner.name
                                body = "DIGIMOOV. Cher(e) %s, nous vous informons que nous avons procédé pour des raisons de sécurité au changement de votre adresse email. Pour plus d'infos, veuillez consulter votre boite mail. " % (
                                    name)
                                if body:
                                    composer = self.env['sms.composer'].with_context(
                                        default_res_model='res.partner',
                                        default_res_id=partner.id,
                                        default_composition_mode='comment',
                                    ).sudo().create({
                                        'body': body,
                                        'mass_keep_log': True,
                                        'mass_force_send': False,
                                        'use_active_domain': False,
                                    })
                                    composer.action_send_sms()  # we send sms to client contains link to register in cma.
                                    if partner.phone:
                                        partner.phone = '0' + str(partner.phone.replace(' ', ''))[
                                                              -9:]
                                """envoyer email pour informer l'apprenant de sa nouvelle adresse email """
                                # partner.email=old_email
                                mail_compose_message = self.env['mail.compose.message']
                                mail_compose_message.fetch_sendinblue_template()
                                template_id = self.env['mail.template'].sudo().search(
                                    [('subject', "=", "Avis de changement de Login"),
                                     ('model_id', "=", 'res.partner')],
                                    limit=1)  # we get the mail template from sendinblue
                                if template_id:
                                    message = self.env['mail.message'].sudo().search(
                                        [('subject', "=", "Avis de changement de Login"),
                                         ('model', "=", 'res.partner'), ('res_id', "=", partner.id)],
                                        limit=1)  # check if we have already sent the email
                                    if not message:
                                        partner.with_context(force_send=True).message_post_with_template(
                                            template_id.id,
                                            composition_mode='comment',
                                        )  # send the email to client

                        # else:

                        # vals = {
                        #     'description': 'Apprenant non ajouté sur 360 %s %s' % (partner.name, responce_api),
                        #     'name': 'Apprenant non ajouté sur 360 ',
                        #     'team_id': self.env['helpdesk.team'].sudo().search(
                        #         [('name', 'like', 'IT'), ('company_id', "=", 2)],
                        #         limit=1).id,
                        # }
                        # description = "Apprenant non ajouté sur 360"+" " + str(partner.name) +" "+str(responce_api)
                        # ticket = self.env['helpdesk.ticket'].sudo().search([("description", "=", description),
                        #                                                        ("team_id.name", 'like', 'IT')])
                        #
                        # if not ticket:
                        #     new_ticket = self.env['helpdesk.ticket'].sudo().create(
                        #         vals)
                        # vals_client = {
                        #     'description': 'Apprenant non ajouté sur 360 %s %s' % (partner.name, responce_api),
                        #     'name': 'Apprenant non ajouté sur 360 ',
                        #     'team_id': self.env['helpdesk.team'].sudo().search(
                        #         [('name', 'like', 'Client'), ('company_id', "=", 2)],
                        #         limit=1).id,
                        # }
                        # description_client = "Apprenant non ajouté sur 360"+" "+ str(partner.name) +" "+ str(
                        #     responce_api)
                        # ticket_client = self.env['helpdesk.ticket'].sudo().search(
                        #     [("description", "=", description_client),
                        #      ("team_id.name", 'like', 'Client')])
                        # if not ticket_client:
                        #     new_ticket_client = self.env['helpdesk.ticket'].sudo().create(
                        #         vals_client)

    def supprimer_ione_auto(self):

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if "localhost" not in str(base_url) and "dev.odoo" not in str(base_url):
            company_id = '56f5520e11d423f46884d593'
            api_key = 'cnkcbrhHKyfzKLx4zI7Ub2P5'
            headers = CaseInsensitiveDict()
            headers["Accept"] = "*/*"
            params = (
                ('company', '56f5520e11d423f46884d593'),
                ('apiKey', 'cnkcbrhHKyfzKLx4zI7Ub2P5'),
            )
            response = requests.get('https://app.360learning.com/api/v1/users', params=params)
            users = response.json()
            for user in users:
                iduser = user['_id']
                email = user['mail']
                # Pour chaque partner vérifier qu'il n'est pas un formateur ou surveillant
                partner = self.env['res.partner'].sudo().search([('email', "=", email),
                                                                 ('est_surveillant', "=", False),
                                                                 ('est_intervenant', "=", False)], order='id desc',
                                                                limit=1)
                groupe = self.env.ref('base.group_user')
                print('groupe user', groupe.users)
                existe = False
                for user in groupe.users:
                    if user.partner_id == partner:
                        existe = True
                        print("if partner ", partner.name, existe)
                # verifier si date_suppression est aujourd'hui
                # pour assurer la suppresion automatique
                if partner and partner.mcm_session_id.date_exam and not existe:
                    # date de suppression est date d'examen + 4jours
                    date_suppression = partner.mcm_session_id.date_exam
                    today = date.today()
                    if (date_suppression <= today):
                        email = partner.email
                        print('date_sup', email, date_suppression, today, email)
                        _logger.info('liste à supprimé %s' % str(email))
                        url = 'https://app.360learning.com/api/v1/users/' + email + '?company=' + company_id + '&apiKey=' + api_key
                        resp = requests.delete(url)

    def supprimer_ione_manuelle(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if "localhost" not in str(base_url) and "dev.odoo" not in str(base_url):
            company_id = '56f5520e11d423f46884d593'
            api_key = 'cnkcbrhHKyfzKLx4zI7Ub2P5'
            headers = CaseInsensitiveDict()
            headers["Accept"] = "*/*"
            url = 'https://app.360learning.com/api/v1/users/' + self.email + '?company=' + company_id + '&apiKey=' + api_key
            resp = requests.delete(url)

    # Extraire firstName et lastName à partir du champs name
    def diviser_nom(self, partner):
        # _logger.info('name au debut  %s' %partner.name)
        if not partner.firstName or not partner.lastName:
            if partner.name == "":
                partner.firstName = partner.name
                partner.lastName = partner.name
            # Cas d'un nom composé
            else:
                if " " in partner.name:

                    name = partner.name.split(" ", 1)
                    if name:
                        partner.firstName = name[0]
                        partner.lastName = name[1]
                # Cas d'un seul nom
                else:

                    partner.firstName = partner.name
                    partner.lastName = partner.name
                    print('first', partner.firstName)

    """recuperer les dossier avec état accepté apartir d'api wedof,
    puis faire le parcours pour chaque dossier,
    si tout les conditions sont vérifiés on Passe le dossier dans l'état 'en formation'"""

    def wedof_api_integration(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if "localhost" not in str(base_url) and "dev.odoo" not in str(base_url):
            companies = self.env['res.company'].sudo().search([('id', "=", 2)])
            api_key = ""
            if companies:
                api_key = companies.wedof_api_key
            headers = {
                'accept': 'application/json',
                'Content-Type': 'application/json',
                'X-API-KEY': api_key,
            }
            params_wedof = (
                ('order', 'desc'),
                ('type', 'all'),
                ('state', 'accepted'),
                ('billingState', 'all'),
                ('certificationState', 'all'),
                ('sort', 'lastUpdate'),
            )
            param_360 = (
                ('company', '56f5520e11d423f46884d593'),
                ('apiKey', 'cnkcbrhHKyfzKLx4zI7Ub2P5'),
            )
            data = '{}'
            response = requests.get('https://www.wedof.fr/api/registrationFolders', headers=headers,
                                    params=params_wedof)
            registrations = response.json()
            for dossier in registrations:
                externalId = dossier['externalId']
                diplome = dossier['trainingActionInfo']['title']
                email = dossier['attendee']['email']
                certificat = dossier['_links']['certification']['name']
                certificat_info = dossier['_links']['certification']['certifInfo']
                date_formation = dossier['trainingActionInfo']['sessionStartDate']
                """convertir date de formation """
                date_split = date_formation[0:10]
                date_ = datetime.strptime(date_split, "%Y-%m-%d")
                dateFormation = date_.date()
                idform = dossier['trainingActionInfo']['externalId']
                module = ""
                if "_" in idform:
                    idforma = idform.split("_", 1)
                    if idforma:
                        module = idforma[1]

                today = date.today()
                lastupdatestr = str(dossier['lastUpdate'])
                lastupdate = datetime.strptime(lastupdatestr, '%Y-%m-%dT%H:%M:%S.%fz')
                newformat = "%d/%m/%Y %H:%M:%S"
                lastupdateform = lastupdate.strftime(newformat)
                lastupd = datetime.strptime(lastupdateform, "%d/%m/%Y %H:%M:%S")
                print('date', today, dateFormation, certificat, idform)
                """Si date de formation <= ajourdhui et s'il a choisi  la formation de transport  léger de marchandises
                on cherche l'apprenant par numero de dossier cpf sur odoo"""
                if 'digimoov' in str(idform) and (dateFormation <= today):
                    _logger.info('wedooooffffff %s' % certificat)
                    _logger.info('dateformation %s' % dateFormation)
                    _logger.info('email %s' % email)
                    partner = self.env['res.partner'].search([('numero_cpf', "=", externalId)], limit=1)
                    if partner:
                        _logger.info('if partner %s ' % str(externalId))
                        partner_email = partner.email
                        """Chercher l'apprenant sur 360 par email"""
                        response_plateforme = requests.get('https://app.360learning.com/api/v1/users', params=param_360)
                        users = response_plateforme.json()
                        for user in users:
                            user_mail = user['mail']
                            user_id = user['_id']
                            response_user = requests.get('https://app.360learning.com/api/v1/users/' + user_id,
                                                         params=param_360)
                            table_user = response_user.json()
                            totalTime = int(table_user['totalTimeSpentInMinutes'])
                            """si l'apprenant est connecté sur 360 
                            on change le statut de son dossier sur wedof """
                            if (user_mail.upper() == partner_email.upper()) and (totalTime >= 1):
                                _logger.info('users %s ' % partner_email.upper())
                                _logger.info('user email %s' % user['mail'].upper())
                                response_post = requests.post(
                                    'https://www.wedof.fr/api/registrationFolders/' + externalId + '/inTraining',
                                    headers=headers, data=data)
                                _logger.info('response post %s' % str(response_post.text))
                                print('response post', str(response_post.text))

                                """Si dossier passe en formation on met à jour statut cpf sur la fiche client"""

                                product_id = self.env['product.template'].sudo().search(
                                    [('id_edof', "=", str(module)), ('company_id', "=", 2)], limit=1)

                                if response_post.status_code == 200:

                                    partner = self.env['res.partner'].sudo().search(
                                        [('numero_cpf', "=", str(externalId))])

                                    if len(partner) > 1:
                                        for part in partner:
                                            part_email = part.email
                                            if part_email.upper() == email.upper():
                                                _logger.info('if partner >1 %s' % partner.numero_cpf)
                                                partner.statut_cpf = "in_training"
                                                partner.date_cpf = lastupd
                                                if product_id:
                                                    partner.id_edof = product_id.id_edof

                                    elif len(partner) == 1:
                                        _logger.info('if partner %s' % partner.numero_cpf)
                                        partner.statut_cpf = "in_training"
                                        partner.date_cpf = lastupd
                                        partner.diplome = diplome
                                        if product_id:
                                            partner.id_edof = product_id.id_edof

    """changer l'etat sur wedof de non traité vers validé à partir d'API"""

    def change_state_wedof_validate(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if "localhost" not in str(base_url) and "dev.odoo" not in str(base_url):
            companies = self.env['res.company'].sudo().search([])
            if companies:
                for company in companies:
                    api_key = company.wedof_api_key
                    params_wedof = (
                        ('order', 'desc'),
                        ('type', 'all'),
                        ('state', 'notProcessed'),
                        ('billingState', 'all'),
                        ('certificationState', 'all'),
                        ('sort', 'lastUpdate'),
                    )
                    headers = {
                        'accept': 'application/json',
                        'Content-Type': 'application/json',
                        'X-API-KEY': api_key,
                    }
                    response = requests.get('https://www.wedof.fr/api/registrationFolders/', headers=headers,
                                            params=params_wedof)
                    """recuperer date debut de session minimale """
                    url = "https://www.wedof.fr/api/registrationFolders/utils/sessionMinDates"
                    date_session_min = requests.request("GET", url, headers=headers)
                    print(date_session_min.text)
                    datemin = date_session_min.json()
                    date_debutstr = datemin.get('cpfSessionMinDate')
                    date_debut = datetime.strptime(date_debutstr, '%Y-%m-%dT%H:%M:%S.%fz')
                    registrations = response.json()
                    for dossier in registrations:
                        _logger.info("validate_________ %s" % str(dossier))
                        externalid = dossier['externalId']
                        email = dossier['attendee']['email']
                        email = email.replace("%", ".")  # remplacer % par .
                        email = email.replace(" ", "")  # supprimer les espaces envoyés en paramètre email
                        email = str(
                            email).lower()  # recupérer l'email en miniscule pour éviter la création des deux comptes
                        print('dossier', dossier)
                        idform = dossier['trainingActionInfo']['externalId']
                        training_id = ""
                        if "_" in idform:
                            idforma = idform.split("_", 1)
                            if idforma:
                                training_id = idforma[1]

                        print('training', training_id)
                        state = dossier['state']
                        lastupdatestr = str(dossier['lastUpdate'])
                        lastupdate = datetime.strptime(lastupdatestr, '%Y-%m-%dT%H:%M:%S.%fz')
                        newformat = "%d/%m/%Y %H:%M:%S"
                        lastupdateform = lastupdate.strftime(newformat)
                        lastupd = datetime.strptime(lastupdateform, "%d/%m/%Y %H:%M:%S")
                        residence = ""
                        if "residence" in dossier['attendee']['address']:
                            residence = dossier['attendee']['address']['residence']
                        num_voie = ""
                        if "number" in dossier['attendee']['address']:
                            num_voie = dossier['attendee']['address']['number']

                        voie = ""
                        if "roadTypeLabel" in dossier['attendee']['address']:
                            voie = dossier['attendee']['address']['roadTypeLabel']
                        nom_voie = ""
                        if "roadName" in dossier['attendee']['address']:
                            nom_voie = dossier['attendee']['address']['roadName']
                        street = str(num_voie) + ' ' + str(voie) + ' ' + str(nom_voie)
                        tel = ""
                        if "phoneNumber" in dossier['attendee']:
                            tel = dossier['attendee']['phoneNumber']
                        if "zipCode" in dossier['attendee']['address']:
                            code_postal = dossier['attendee']['address']['zipCode']
                        else:
                            code_postal = ""
                        if "city" in dossier['attendee']['address']:
                            ville = dossier['attendee']['address']['city']
                        else:
                            ville = ""
                        if 'firstName' in dossier['attendee']['firstName']:
                            nom = dossier['attendee']['firstName']
                        else:
                            nom = ""

                        if "lastName" in dossier['attendee']['lastName']:
                            prenom = dossier['attendee']['lastName']
                        else:
                            prenom = ""
                        diplome = dossier['trainingActionInfo']['title']

                        today = date.today()
                        # datedebut = today + timedelta(days=15)
                        """chercher user sur odoo par tel ou par email """
                        user = self.env['res.users'].sudo().search([('login', "=", email)], limit=1)
                        exist = True
                        if not user:
                            if tel:
                                user = self.env["res.users"].sudo().search(
                                    [("phone", "=", str(tel))], limit=1)
                                if not user:
                                    phone_number = str(tel).replace(' ', '')
                                    if '+33' not in str(
                                            phone_number):  # check if edof api send the number of client with +33
                                        phone = phone_number[0:2]
                                        if str(phone) == '33' and ' ' not in str(
                                                tel):  # check if edof api send the number of client in this format (number_format: 33xxxxxxx)
                                            phone = '+' + str(tel)
                                            user = self.env["res.users"].sudo().search([("phone", "=", phone)], limit=1)
                                            if not user:
                                                phone = phone[0:3] + ' ' + phone[3:4] + ' ' + phone[4:6] + ' ' + phone[
                                                                                                                 6:8] + ' ' + phone[
                                                                                                                              8:10] + ' ' + phone[
                                                                                                                                            10:]
                                                user = self.env["res.users"].sudo().search([("phone", "=", phone)],
                                                                                           limit=1)
                                            if not user:
                                                phone = '0' + str(phone[4:])
                                                user = self.env["res.users"].sudo().search(
                                                    ['|', ("phone", "=", phone),
                                                     ("phone", "=", phone.replace(' ', ''))], limit=1)
                                        phone = phone_number[0:2]
                                        if str(phone) == '33' and ' ' in str(
                                                tel):  # check if edof api send the number of client in this format (number_format: 33 x xx xx xx)
                                            phone = '+' + str(tel)
                                            user = self.env["res.users"].sudo().search(
                                                ['|', ("phone", "=", phone), ("phone", "=", phone.replace(' ', ''))],
                                                limit=1)
                                            if not user:
                                                phone = '0' + str(phone[4:])
                                                user = self.env["res.users"].sudo().search(
                                                    ['|', ("phone", "=", phone),
                                                     ("phone", "=", phone.replace(' ', ''))], limit=1)
                                        phone = phone_number[0:2]
                                        if str(phone) in ['06', '07'] and ' ' not in str(
                                                tel):  # check if edof api send the number of client in this format (number_format: 07xxxxxx)
                                            user = self.env["res.users"].sudo().search(
                                                ['|', ("phone", "=", str(tel)),
                                                 ("phone", "=", str('+33' + tel.replace(' ', '')[-9:]))],
                                                limit=1)
                                            if not user:
                                                phone = phone[0:2] + ' ' + phone[2:4] + ' ' + phone[4:6] + ' ' + phone[
                                                                                                                 6:8] + ' ' + phone[
                                                                                                                              8:]
                                                user = self.env["res.users"].sudo().search([("phone", "=", phone)],
                                                                                           limit=1)
                                            if not user:
                                                phone = '0' + str(phone[4:])
                                                user = self.env["res.users"].sudo().search(
                                                    ['|', ("phone", "=", phone),
                                                     ("phone", "=", phone.replace(' ', ''))], limit=1)
                                        phone = phone_number[0:2]
                                        if str(phone) in ['06', '07'] and ' ' in str(
                                                tel):  # check if edof api send the number of client in this format (number_format: 07 xx xx xx)
                                            user = self.env["res.users"].sudo().search(
                                                ['|', ("phone", "=", str(tel)), str(tel).replace(' ', '')], limit=1)
                                            if not user:
                                                phone_number = str(tel[1:])
                                                user = self.env["res.users"].sudo().search(
                                                    ['|', ("phone", "=", str('+33' + phone_number)),
                                                     ("phone", "=", ('+33' + phone_number.replace(' ', '')))], limit=1)
                                    else:  # check if edof api send the number of client with+33
                                        if ' ' not in str(tel):
                                            phone = str(tel)
                                            phone = phone[0:3] + ' ' + phone[3:4] + ' ' + phone[4:6] + ' ' + phone[
                                                                                                             6:8] + ' ' + phone[
                                                                                                                          8:10] + ' ' + phone[
                                                                                                                                        10:]
                                            user = self.env["res.users"].sudo().search(
                                                [("phone", "=", phone)], limit=1)
                                        if not user:
                                            user = self.env["res.users"].sudo().search(
                                                [("phone", "=", str(phone_number).replace(' ', ''))], limit=1)
                                            if not user:
                                                phone = str(phone_number)
                                                phone = phone[3:]
                                                phone = '0' + str(phone)
                                                user = self.env["res.users"].sudo().search(
                                                    [("phone", "like", phone.replace(' ', ''))], limit=1)
                            if not user:
                                """si l'apprenant n'est pas sur odoo, date debut de session sera celle de cpfSessionMinDate"""
                                date_debutstr = datemin.get('cpfSessionMinDate')
                                date_debut = datetime.strptime(date_debutstr, '%Y-%m-%dT%H:%M:%S.%fz')
                                print('cpf')
                        if user:
                            print('if userrr++++++++', user.email)
                            """Si pole emploi coché , l'apprenant commence sa formation apres 21 jours"""
                            if user.partner_id.is_pole_emploi:
                                date_debutstr = datemin.get('poleEmploiSessionMinDate')
                                date_debut = datetime.strptime(date_debutstr, '%Y-%m-%dT%H:%M:%S.%fz')
                                print('pole emploi')
                            else:
                                """Si non l'apprenant commence sa formation apres 14 jours"""
                                date_debutstr = datemin.get('cpfSessionMinDate')
                                date_debut = datetime.strptime(date_debutstr, '%Y-%m-%dT%H:%M:%S.%fz')
                                print('cpf')

                        datefin = str(date_debut + relativedelta(months=3) + timedelta(days=1))
                        datedebutstr = str(date_debut)
                        data = '{"trainingActionInfo":{"sessionStartDate":"' + datedebutstr + '","sessionEndDate":"' + datefin + '" }}'
                        dat = '{\n  "weeklyDuration": 14,\n  "indicativeDuration": 102\n}'
                        """Avant validation modifier les dates de session selon le mode de financement pole emploi/cpf """
                        response_put = requests.put('https://www.wedof.fr/api/registrationFolders/' + externalid,
                                                    headers=headers, data=data)

                        status = str(response_put.status_code)
                        statuss = str(json.loads(response_put.text))
                        _logger.info("validate put _________ %s" % str(status))
                        _logger.info("validate_________ %s" % str(statuss))
                        response_post = requests.post(
                            'https://www.wedof.fr/api/registrationFolders/' + externalid + '/validate',
                            headers=headers, data=dat)
                        status = str(response_post.status_code)
                        statuss = str(json.loads(response_post.text))
                        _logger.info("validate_________ %s" % str(status))
                        _logger.info("validate_________ %s" % str(statuss))
                        """Si dossier passe à l'etat validé on met à jour statut cpf sur la fiche client"""
                        if status == "200":
                            print('validate', email)
                            self.cpf_validate(training_id, email, residence, num_voie, nom_voie, voie, street, tel,
                                              code_postal, ville,
                                              diplome, dossier['attendee']['lastName'],
                                              dossier['attendee']['firstName'],
                                              dossier['externalId'], lastupd)

    """Mettre à jour les statuts cpf sur la fiche client selon l'etat sur wedof """

    def change_state_cpf_partner(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if "localhost" not in str(base_url) and "dev.odoo" not in str(base_url):
            companies = self.env['res.company'].sudo().search([])
            if companies:
                for company in companies:
                    api_key = company.wedof_api_key
                    params_wedof = (
                        ('order', 'desc'),
                        ('type', 'all'),
                        ('state',
                         'validated,inTraining,refusedByAttendee,refusedByOrganism,serviceDoneDeclared,serviceDoneValidated,canceledByAttendee,canceledByAttendeeNotRealized,canceledByOrganism'),
                        ('billingState', 'all'),
                        ('certificationState', 'all'),
                        ('sort', 'lastUpdate'),
                        ('limit', '100'),
                        ('page', '1')
                    )
                    headers = {
                        'accept': 'application/json',
                        'Content-Type': 'application/json',
                        'X-API-KEY': api_key,
                    }
                    response = requests.get('https://www.wedof.fr/api/registrationFolders/', headers=headers,
                                            params=params_wedof)
                    registrations = response.json()
                    for dossier in registrations:
                        print('dosssier', dossier['attendee']['address'])
                        externalId = dossier['externalId']
                        email = dossier['attendee']['email']
                        email = email.replace("%", ".")  # remplacer % par .
                        email = email.replace(" ", "")  # supprimer les espaces envoyés en paramètre email
                        email = str(
                            email).lower()  # recupérer l'email en miniscule pour éviter la création des deux comptes
                        # Takwa removed code of cpf mode financement to the cron with  personnel mode code
                        idform = dossier['trainingActionInfo']['externalId']
                        training_id = ""
                        if "_" in idform:
                            idforma = idform.split("_", 1)
                            if idforma:
                                training_id = idforma[1]

                        print('training', training_id)
                        state = dossier['state']
                        lastupdatestr = str(dossier['lastUpdate'])
                        lastupdate = datetime.strptime(lastupdatestr, '%Y-%m-%dT%H:%M:%S.%fz')
                        newformat = "%d/%m/%Y %H:%M:%S"
                        lastupdateform = lastupdate.strftime(newformat)
                        lastupd = datetime.strptime(lastupdateform, "%d/%m/%Y %H:%M:%S")
                        num_voie = ""
                        if "number" in dossier['attendee']['address']:
                            num_voie = dossier['attendee']['address']['number']

                        voie = ""
                        if "roadTypeLabel" in dossier['attendee']['address']:
                            voie = dossier['attendee']['address']['roadTypeLabel']
                        nom_voie = ""
                        if "roadName" in dossier['attendee']['address']:
                            nom_voie = dossier['attendee']['address']['roadName']
                        street = str(num_voie) + ' ' + str(voie) + ' ' + str(nom_voie)
                        tel = ""
                        if "phoneNumber" in dossier['attendee']:
                            tel = dossier['attendee']['phoneNumber']

                        code_postal = ""
                        if "zipCode" in dossier['attendee']['address']:
                            code_postal = dossier['attendee']['address']['zipCode']

                        ville = ""
                        if "city" in dossier['attendee']['address']:
                            ville = dossier['attendee']['address']['city']
                        residence = ""
                        if "residence" in dossier['attendee']['address']:
                            residence = dossier['attendee']['address']['residence']
                        nom = ""
                        if 'firstName' in dossier['attendee']['firstName']:
                            nom = dossier['attendee']['firstName']
                            nom = unidecode(nom)

                        prenom = ""
                        if "lastName" in dossier['attendee']['lastName']:
                            prenom = dossier['attendee']['lastName']
                            prenom = unidecode(prenom)
                        diplome = dossier['trainingActionInfo']['title']
                        product_id = self.env['product.template'].sudo().search(
                            [('id_edof', "=", str(training_id))], limit=1)

                        if state == "validated":
                            print('validate', email, dossier['attendee']['lastName'], dossier['attendee']['firstName'])
                            self.cpf_validate(training_id, email, residence, num_voie, nom_voie, voie, street, tel,
                                              code_postal, ville,
                                              diplome, dossier['attendee']['lastName'],
                                              dossier['attendee']['firstName'],
                                              dossier['externalId'], lastupd)
                        else:
                            users = self.env['res.users'].sudo().search(
                                [('login', "=", email)])  # search user with same email sended
                            user = False
                            if len(users) > 1:
                                user = users[1]
                                print('userss', users)
                                for utilisateur in users:
                                    if utilisateur.partner_id.id_edof and utilisateur.partner_id.date_examen_edof and utilisateur.partner_id.session_ville_id:  # if more than user ,check between them wich user is come from edof
                                        user = utilisateur
                                        print('if userssss', user.partner_id.email)
                            else:
                                user = users
                            if user:  # if user finded
                                print('if__________________user', user.partner_id.statut_cpf, user.partner_id.email)
                                user.partner_id.mode_de_financement = 'cpf'  # update field mode de financement to cpf
                                user.partner_id.funding_type = 'cpf'  # update field funding type to cpfprint('partner',partner.numero_cpf,user.login)
                                print(user.partner_id.date_cpf)

                                if state == "inTraining":
                                    print('intraining', email)
                                    user.partner_id.statut_cpf = "in_training"
                                    user.partner_id.numero_cpf = externalId
                                    user.partner_id.date_cpf = lastupd
                                    user.partner_id.diplome = diplome
                                    if product_id:
                                        user.partner_id.id_edof = product_id.id_edof

                                if state == "terminated":
                                    print('terminated', email)
                                    user.partner_id.statut_cpf = "out_training"
                                    user.partner_id.numero_cpf = externalId
                                    user.partner_id.diplome = diplome
                                    user.partner_id.date_cpf = lastupd
                                    if product_id:
                                        user.partner_id.id_edof = product_id.id_edof
                                if state == "serviceDoneDeclared":
                                    print('serviceDoneDeclared', email)
                                    user.partner_id.statut_cpf = "service_declared"
                                    user.partner_id.numero_cpf = externalId
                                    user.partner_id.date_cpf = lastupd
                                    user.partner_id.diplome = diplome
                                    if product_id:
                                        user.partner_id.id_edof = product_id.id_edof

                                if state == "serviceDoneValidated":
                                    print('serviceDoneValidated', email)

                                    user.partner_id.statut_cpf = "service_validated"
                                    user.partner_id.numero_cpf = externalId
                                    user.partner_id.date_cpf = lastupd
                                    user.partner_id.diplome = diplome
                                    if product_id:
                                        user.partner_id.id_edof = product_id.id_edof
                                if state == "canceledByAttendee" or state == "canceledByAttendeeNotRealized" or state == "canceledByOrganism" or state == "refusedByAttendee" or state == "refusedByOrganism":
                                    if user.partner_id.numero_cpf == externalId:
                                        user.partner_id.statut_cpf = "canceled"
                                        user.partner_id.statut = "canceled"
                                        user.partner_id.date_cpf = lastupd
                                        user.partner_id.diplome = diplome
                                        print("product id annulé digi", user.partner_id.id_edof, training_id)

                                        if product_id:
                                            user.partner_id.id_edof = product_id.id_edof

    def cpf_validate(self, module, email, residence, num_voie, nom_voie, voie, street, tel, code_postal, ville, diplome,
                     nom,
                     prenom, dossier, lastupd):
        user = self.env['res.users'].sudo().search([('login', "=", email)], limit=1)
        exist = True
        if not user:
            if tel:
                user = self.env["res.users"].sudo().search(
                    [("phone", "=", str(tel))], limit=1)
                if not user:
                    phone_number = str(tel).replace(' ', '')
                    if '+33' not in str(phone_number):  # check if edof api send the number of client with +33
                        phone = phone_number[0:2]
                        if str(phone) == '33' and ' ' not in str(
                                tel):  # check if edof api send the number of client in this format (number_format: 33xxxxxxx)
                            phone = '+' + str(tel)
                            user = self.env["res.users"].sudo().search([("phone", "=", phone)], limit=1)
                            if not user:
                                phone = phone[0:3] + ' ' + phone[3:4] + ' ' + phone[4:6] + ' ' + phone[
                                                                                                 6:8] + ' ' + phone[
                                                                                                              8:10] + ' ' + phone[
                                                                                                                            10:]
                                user = self.env["res.users"].sudo().search([("phone", "=", phone)], limit=1)
                            if not user:
                                phone = '0' + str(phone[4:])
                                user = self.env["res.users"].sudo().search(
                                    ['|', ("phone", "=", phone), ("phone", "=", phone.replace(' ', ''))], limit=1)
                        phone = phone_number[0:2]
                        if str(phone) == '33' and ' ' in str(
                                tel):  # check if edof api send the number of client in this format (number_format: 33 x xx xx xx)
                            phone = '+' + str(tel)
                            user = self.env["res.users"].sudo().search(
                                ['|', ("phone", "=", phone), ("phone", "=", phone.replace(' ', ''))], limit=1)
                            if not user:
                                phone = '0' + str(phone[4:])
                                user = self.env["res.users"].sudo().search(
                                    ['|', ("phone", "=", phone), ("phone", "=", phone.replace(' ', ''))], limit=1)
                        phone = phone_number[0:2]
                        if str(phone) in ['06', '07'] and ' ' not in str(
                                tel):  # check if edof api send the number of client in this format (number_format: 07xxxxxx)
                            user = self.env["res.users"].sudo().search(
                                ['|', ("phone", "=", str(tel)), ("phone", "=", str('+33' + tel.replace(' ', '')[-9:]))],
                                limit=1)
                            if not user:
                                phone = phone[0:2] + ' ' + phone[2:4] + ' ' + phone[4:6] + ' ' + phone[
                                                                                                 6:8] + ' ' + phone[8:]
                                user = self.env["res.users"].sudo().search([("phone", "=", phone)], limit=1)
                            if not user:
                                phone = '0' + str(phone[4:])
                                user = self.env["res.users"].sudo().search(
                                    ['|', ("phone", "=", phone), ("phone", "=", phone.replace(' ', ''))], limit=1)
                        phone = phone_number[0:2]
                        if str(phone) in ['06', '07'] and ' ' in str(
                                tel):  # check if edof api send the number of client in this format (number_format: 07 xx xx xx)
                            user = self.env["res.users"].sudo().search(
                                ['|', ("phone", "=", str(tel)), str(tel).replace(' ', '')], limit=1)
                            if not user:
                                phone_number = str(tel[1:])
                                user = self.env["res.users"].sudo().search(
                                    ['|', ("phone", "=", str('+33' + phone_number)),
                                     ("phone", "=", ('+33' + phone_number.replace(' ', '')))], limit=1)
                    else:  # check if edof api send the number of client with+33
                        if ' ' not in str(tel):
                            phone = str(tel)
                            phone = phone[0:3] + ' ' + phone[3:4] + ' ' + phone[4:6] + ' ' + phone[6:8] + ' ' + phone[
                                                                                                                8:10] + ' ' + phone[
                                                                                                                              10:]
                            user = self.env["res.users"].sudo().search(
                                [("phone", "=", phone)], limit=1)
                        if not user:
                            user = self.env["res.users"].sudo().search(
                                [("phone", "=", str(phone_number).replace(' ', ''))], limit=1)
                            if not user:
                                phone = str(phone_number)
                                phone = phone[3:]
                                phone = '0' + str(phone)
                                user = self.env["res.users"].sudo().search(
                                    [("phone", "like", phone.replace(' ', ''))], limit=1)

            # if user:
            #     if not (user.partner_id.date_examen_edof) or not (user.partner_id.session_ville_id):
            #         """Envoyez un SMS aux apprenants qui arrivent de CPF."""
            #         url = '%smy' % str(user.partner_id.company_id.website)  # get the signup_url
            #         short_url = pyshorteners.Shortener()
            #         short_url = short_url.tinyurl.short(
            #             url)  # convert the url to be short using pyshorteners library
            # 
            #         sms_body_contenu = 'Chere(e) %s , Vous avez été invité par %s  à compléter votre inscription : %s . Votre courriel de connection est: %s' % (
            #             user.partner_id.name, user.partner_id.company_id.name, short_url,
            #             user.partner_id.email)  # content of sms
            #         
            #         sms = self.env['mail.message'].sudo().search(
            #             [("body", "like", short_url), ("message_type", "=", 'sms'), ('partner_ids', 'in', partner.id),
            #              ('model', "=", "res.partner")])
            #         if not sms:
            #             _logger.info('if not sms %s' %str(sms_body_contenu))
            #             self.send_sms(sms_body_contenu, user.partner_id)



            if not user:
                # créer
                exist = False

                if "digimoov" in str(module):  # module from wedof
                    user = self.env['res.users'].sudo().create({
                        'name': str(prenom) + " " + str(nom),
                        'login': str(email),
                        'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])],
                        'email': email,
                        'notification_type': 'email',
                        'website_id': 2,
                        'company_ids': [2],
                        'company_id': 2,
                        'inscription_cpf': "moncompteformation.gouv.fr"
                    })
                    user.company_id = 2
                    user.partner_id.company_id = 2
                else:
                    user = self.env['res.users'].sudo().create({
                        'name': str(prenom) + " " + str(nom),
                        'login': str(email),
                        'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])],
                        'email': email,
                        'notification_type': 'email',
                        'website_id': 1,
                        'company_ids': [1],
                        'company_id': 1,
                        'inscription_cpf':"moncompteformation.gouv.fr"

                    })
                    user.company_id = 1
                    user.partner_id.company_id = 1
                # if user:
                #     phone = str(tel.replace(' ', ''))[-9:]
                #     phone = '+33' + ' ' + phone[0:1] + ' ' + phone[1:3] + ' ' + phone[3:5] + ' ' + phone[
                #                                                                                    5:7] + ' ' + phone[
                #                                                                                                 7:]  # convert the number in this format : +33 x xx xx xx xx
                #     url = str(user.signup_url)  # get the signup_url
                #     short_url = pyshorteners.Shortener()
                #     short_url = short_url.tinyurl.short(
                #         url)  # convert the signup_url to be short using pyshorteners library
                #     body = 'Chere(e) %s , Vous avez été invité par %s  à compléter votre inscription : %s . Votre courriel de connection est: %s' % (
                #         user.partner_id.name, user.partner_id.company_id.name, short_url,
                #         user.partner_id.email)  # content of sms
                #     sms_body_contenu = 'Chere(e) %s , Vous avez été invité par %s  à compléter votre inscription : %s . Votre courriel de connection est: %s' % (
                #         user.partner_id.name, user.partner_id.company_id.name, short_url,
                #         user.partner_id.email)  # content of sms
                # 
                #     
                #     sms = self.env['sms.sms'].sudo().create({
                #         'partner_id': user.partner_id.id,
                #         'number': phone,
                #         'body': str(body)
                #     })  # create sms
                #     # sms = self.env['mail.message'].sudo().search(
                #     #     [("body", "like", body), ("message_type", "=", 'sms'), ('res_id', '=', partner.id),('model',"=","res.partner")])
                #     # if not sms:
                #     sms_id = sms.id

        # user = request.env['res.users'].sudo().search([('login', "=", email)])
        if user:
            client = self.env['res.partner'].sudo().search(
                [('id', '=', user.partner_id.id)], limit=1)
            if client:
                """Envoyez un SMS aux apprenants pour accepter leurs dossiers cpf."""
                sms_body_ = "%s! Votre demande de financement par CPF a été validée. Connectez-vous sur moncompteformation.gouv.fr en partant dans l’onglet. Dossiers, Proposition de l’organisme, Financement, ensuite confirmer mon inscription." % (
                    user.partner_id.company_id.name)  # content of sms
                sms = self.env['mail.message'].sudo().search(
                    [("body", "like", sms_body_), ("message_type", "=", 'sms'), ('partner_ids', 'in',  user.partner_id.id),
                     ('model', "=", "res.partner")])
                if not sms:
                    _logger.info('if not sms %s' % str(sms_body_))
                    self.send_sms(sms_body_, user.partner_id)
                _logger.info("if client %s" % str(client.email))
                _logger.info("dossier %s" % str(dossier))
                client.mode_de_financement = 'cpf'
                client.funding_type = 'cpf'
                client.numero_cpf = dossier
                client.statut_cpf = 'validated'
                client.statut = 'indecis'
                client.street2 = residence
                client.phone = '0' + str(tel.replace(' ', ''))[-9:]
                client.street = street
                client.num_voie = num_voie
                client.nom_voie = nom_voie
                client.voie = voie
                if code_postal != "":
                    client.zip = code_postal
                client.city = ville
                client.diplome = diplome  # attestation capacitév ....
                client.date_cpf = lastupd
                client.name = str(prenom) + " " + str(nom)
                module_id = False
                product_id = False
                if "digimoov" in str(module):
                    user.write({'company_ids': [1, 2], 'company_id': 2})
                    product_id = self.env['product.template'].sudo().search(
                        [('id_edof', "=", str(module)), ('company_id', "=", 2)], limit=1)
                    print("product id validate digi", product_id.id_edof)
                    if product_id:
                        client.id_edof = product_id.id_edof

                        """Créer un devis et Remplir le panier par produit choisit sur edof"""
                        sale = self.env['sale.order'].sudo().search([('partner_id', '=', client.id),
                                                                     ('company_id', '=', 2),
                                                                     ('website_id', '=', 2),
                                                                     ('order_line.product_id', '=', product_id.id)])

                        if not sale:
                            so = self.env['sale.order'].sudo().create({
                                'partner_id': client.id,
                                'company_id': 2,
                                'website_id': 2
                            })

                            so_line = self.env['sale.order.line'].sudo().create({
                                'name': product_id.name,
                                'product_id': product_id.id,
                                'product_uom_qty': 1,
                                'product_uom': product_id.uom_id.id,
                                'price_unit': product_id.list_price,
                                'order_id': so.id,
                                'tax_id': product_id.taxes_id,
                                'company_id': 2,
                            })
                            #
                            # prix de la formation dans le devis
                            amount_before_instalment = so.amount_total
                            # so.amount_total = so.amount_total * 0.25
                            for line in so.order_line:
                                line.price_unit = so.amount_total
                else:
                    user.write({'company_ids': [(4, 2)], 'company_id': 1})
                    product_id = self.env['product.template'].sudo().search(
                        [('id_edof', "=", str(module)), ('company_id', "=", 1)], limit=1)
                    print("product id validate mcm", product_id.id_edof)
                    if product_id:
                        client.id_edof = product_id.id_edof

                        """Créer un devis et Remplir le panier par produit choisit sur edof"""
                        sale = self.env['sale.order'].sudo().search([('partner_id', '=', client.id),
                                                                     ('company_id', '=', 1),
                                                                     ('website_id', '=', 1),
                                                                     ('order_line.product_id', '=', product_id.id)])

                        if not sale:
                            so = self.env['sale.order'].sudo().create({
                                'partner_id': client.id,
                                'company_id': 1,
                                'website_id': 1
                            })

                            so_line = self.env['sale.order.line'].sudo().create({
                                'name': product_id.name,
                                'product_id': product_id.id,
                                'product_uom_qty': 1,
                                'product_uom': product_id.uom_id.id,
                                'price_unit': product_id.list_price,
                                'order_id': so.id,
                                'tax_id': product_id.taxes_id,
                                'company_id': 1,
                            })
                            #
                            # prix de la formation dans le devis
                            amount_before_instalment = so.amount_total
                            # so.amount_total = so.amount_total * 0.25
                            for line in so.order_line:
                                line.price_unit = so.amount_total

    """Changer statut cpf vers accepté selon l'etat récupéré avec api wedof"""

    def change_statut_accepte(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if "localhost" not in str(base_url) and "dev.odoo" not in str(base_url):
            companies = self.env['res.company'].sudo().search([])
            if companies:
                for company in companies:
                    api_key = company.wedof_api_key
                    params_wedof = (
                        ('order', 'desc'),
                        ('type', 'all'),
                        ('state', 'accepted'),
                        ('billingState', 'all'),
                        ('certificationState', 'all'),
                        ('sort', 'lastUpdate'),
                        ('limit', '100')
                    )
                    headers = {
                        'accept': 'application/json',
                        'Content-Type': 'application/json',
                        'X-API-KEY': api_key,
                    }
                    response = requests.get('https://www.wedof.fr/api/registrationFolders/', headers=headers,
                                            params=params_wedof)
                    registrations = response.json()
                    for dossier in registrations:
                        externalId = dossier['externalId']
                        email = dossier['attendee']['email']
                        email = email.replace("%", ".")  # remplacer % par .
                        email = email.replace(" ", "")  # supprimer les espaces envoyés en paramètre email
                        email = str(
                            email).lower()  # recupérer l'email en miniscule pour éviter la création des deux comptes
                        print('dossier', dossier)
                        idform = dossier['trainingActionInfo']['externalId']
                        training_id = ""
                        if "_" in idform:
                            idforma = idform.split("_", 1)
                            if idforma:
                                training_id = idforma[1]
                        state = dossier['state']
                        lastupdatestr = str(dossier['lastUpdate'])
                        lastupdate = datetime.strptime(lastupdatestr, '%Y-%m-%dT%H:%M:%S.%fz')
                        newformat = "%d/%m/%Y %H:%M:%S"
                        lastupdateform = lastupdate.strftime(newformat)
                        lastupd = datetime.strptime(lastupdateform, "%d/%m/%Y %H:%M:%S")

                        if "phoneNumber" in dossier['attendee']:
                            tel = dossier['attendee']['phoneNumber']
                        else:
                            tel = ""
                        diplome = dossier['trainingActionInfo']['title']
                        print('training', training_id)
                        today = date.today()
                        date_min = today - relativedelta(months=2)
                        users = self.env['res.users'].sudo().search([('login', "=", email)])
                        """si apprenant non trouvé par email on cherche par numero telephone"""
                        if not users:
                            if '+33' not in str(tel):
                                users = self.env["res.users"].sudo().search(
                                    [("phone", "=", str(tel).replace(' ', ''))], limit=1)
                                if not users:
                                    phone = str(tel)
                                    phone = phone[1:]
                                    phone = '+33' + str(phone)
                                    users = self.env["res.users"].sudo().search(
                                        [("phone", "=", phone.replace(' ', ''))], limit=1)
                            else:
                                users = self.env["res.users"].sudo().search(
                                    [("phone", "=", str(tel).replace(' ', ''))], limit=1)
                                if not users:
                                    phone = str(tel)
                                    phone = phone[3:]
                                    phone = '0' + str(phone)
                                    users = self.env["res.users"].sudo().search(
                                        [("phone", "=", phone.replace(' ', ''))], limit=1)

                        user = False
                        if len(users) > 1:
                            user = users[1]
                            for utilisateur in users:
                                if utilisateur.partner_id.id_edof and utilisateur.partner_id.date_examen_edof and utilisateur.partner_id.ville:
                                    user = utilisateur
                        else:
                            user = users

                        if user:
                            if not (user.partner_id.date_examen_edof) or not (user.partner_id.session_ville_id):
                                """Envoyez un SMS aux apprenants qui arrivent de CPF."""
                                url = '%smy' % str(user.partner_id.company_id.website)  # get the signup_url
                                short_url = pyshorteners.Shortener()
                                short_url = short_url.tinyurl.short(
                                    url)  # convert the url to be short using pyshorteners library

                                sms_body_contenu = 'Chere(e) %s , Vous avez été invité par %s  à compléter votre inscription : %s . Votre courriel de connection est: %s' % (
                                    user.partner_id.name, user.partner_id.company_id.name, short_url,
                                    user.partner_id.email)  # content of sms

                                sms = self.env['mail.message'].sudo().search(
                                    [("body", "like", short_url), ("message_type", "=", 'sms'),
                                     ('partner_ids', 'in', user.partner_id.id),
                                     ('model', "=", "res.partner")])
                                if not sms:
                                    _logger.info('if not sms %s' % str(sms_body_contenu))
                                    self.send_sms(sms_body_contenu, user.partner_id)

                        if not user:
                            # créer
                            exist = False

                            if "digimoov" in str(training_id):  # module from wedof
                                user = self.env['res.users'].sudo().create({
                                    'name': str(prenom) + " " + str(nom),
                                    'login': str(email),
                                    'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])],
                                    'email': email,
                                    'notification_type': 'email',
                                    'website_id': 2,
                                    'company_ids': [2],
                                    'company_id': 2
                                })
                                user.company_id = 2
                                user.partner_id.company_id = 2
                            else:
                                user = self.env['res.users'].sudo().create({
                                    'name': str(prenom) + " " + str(nom),
                                    'login': str(email),
                                    'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])],
                                    'email': email,
                                    'notification_type': 'email',
                                    'website_id': 1,
                                    'company_ids': [1],
                                    'company_id': 1

                                })
                                user.company_id = 1
                                user.partner_id.company_id = 1
                            if user:
                                phone = str(tel.replace(' ', ''))[-9:]
                                phone = '+33' + ' ' + phone[0:1] + ' ' + phone[1:3] + ' ' + phone[3:5] + ' ' + phone[
                                                                                                               5:7] + ' ' + phone[
                                                                                                                            7:]  # convert the number in this format : +33 x xx xx xx xx
                                url = str(user.signup_url)  # get the signup_url
                                short_url = pyshorteners.Shortener()
                                short_url = short_url.tinyurl.short(
                                    url)  # convert the signup_url to be short using pyshorteners library
                                body = 'Chere(e) %s , Vous avez été invité par %s  à compléter votre inscription : %s . Votre courriel de connection est: %s' % (
                                    user.partner_id.name, user.partner_id.company_id.name, short_url,
                                    user.partner_id.email)  # content of sms
                                sms_body_contenu = 'Chere(e) %s , Vous avez été invité par %s  à compléter votre inscription : %s . Votre courriel de connection est: %s' % (
                                    user.partner_id.name, user.partner_id.company_id.name, short_url,
                                    user.partner_id.email)  # content of sms
                                sms = self.env['sms.sms'].sudo().create({
                                    'partner_id': user.partner_id.id,
                                    'number': phone,
                                    'body': str(body)
                                })  # create sms
                                sms_id = sms.id
                                if (sms):
                                    sms.send()  # send the sms
                                    subtype_id = self.env['ir.model.data'].xmlid_to_res_id('mt_note')
                                    body = False
                                    sms = self.env["sms.sms"].sudo().search(
                                        [("id", "=", sms_id)], limit=1)
                                    if (sms):
                                        if sms.state == 'error':
                                            body = "Le SMS suivant n'a pas pu être envoyé : %s " % (sms_body_contenu)
                                    else:
                                        body = "Le SMS suivant a été bien envoyé : %s " % (sms_body_contenu)
                                    if body:
                                        message = self.env['mail.message'].sudo().create({
                                            'subject': 'Invitation de rejoindre le site par sms',
                                            'model': 'res.partner',
                                            'res_id': user.partner_id.id,
                                            'message_type': 'notification',
                                            'subtype_id': subtype_id,
                                            'body': body,
                                        })  # create note in client view
                        if user:
                            """mettre à jour les informations sur fiche client"""
                            print("if user", user.login, user.partner_id.statut_cpf)
                            user.partner_id.mode_de_financement = 'cpf'
                            user.partner_id.statut_cpf = 'accepted'
                            user.partner_id.date_cpf = lastupd
                            user.partner_id.numero_cpf = externalId
                            user.partner_id.diplome = diplome
                            module_id = False
                            product_id = False
                            _logger.info('userrr %s' % str(user.partner_id.name))
                            """chercher le produit sur odoo selon id edof de formation"""

                            if 'digimoov' in str(training_id):

                                product_id = self.env['product.template'].sudo().search(
                                    [('id_edof', "=", str(training_id)), ('company_id', "=", 2)], limit=1)
                                if product_id:
                                    user.partner_id.id_edof = product_id.id_edof
                            else:
                                product_id = self.env['product.template'].sudo().search(
                                    [('id_edof', "=", str(training_id)), ('company_id', "=", 1)], limit=1)
                                if product_id:
                                    user.partner_id.id_edof = product_id.id_edof
                            _logger.info('if digi %s' % str(product_id))
                            if product_id and product_id.company_id.id == 2 and user.partner_id.id_edof and user.partner_id.date_examen_edof and user.partner_id.session_ville_id:

                                print('if product_id digimoov', product_id.id_edof, user.login)
                                module_id = self.env['mcmacademy.module'].sudo().search(
                                    [('company_id', "=", 2),
                                     ('session_ville_id', "=", user.partner_id.session_ville_id.id),
                                     ('date_exam', "=", user.partner_id.date_examen_edof),
                                     ('product_id', "=", product_id.id),
                                     ('session_id.number_places_available', '>', 0)], limit=1)
                                _logger.info('before if modulee %s' % str(module_id))
                                if module_id:
                                    _logger.info('if modulee %s' % str(module_id))
                                    user.partner_id.module_id = module_id
                                    user.partner_id.mcm_session_id = module_id.session_id
                                    product_id = self.env['product.product'].sudo().search(
                                        [('product_tmpl_id', '=', module_id.product_id.id)])
                                    user.partner_id.mcm_session_id = module_id.session_id
                                    user.partner_id.module_id = module_id
                                    self.env.user.company_id = 2
                                    # """chercher facture avec numero de dossier si n'existe pas on crée une facture"""
                                    # invoice = self.env['account.move'].sudo().search(
                                    #     [('numero_cpf', "=", externalId),
                                    #      ('state', "=", 'posted'),
                                    #      ('partner_id', "=", user.partner_id.id)],limit=1)
                                    # print('invoice',invoice.name)
                                    # if not invoice :
                                    #     print('if  not invoice digi ')
                                    #     so = self.env['sale.order'].sudo().create({
                                    #         'partner_id': user.partner_id.id,
                                    #         'company_id': 2,
                                    #     })
                                    #     so.module_id = module_id
                                    #     so.session_id = module_id.session_id
                                    #
                                    #     so_line = self.env['sale.order.line'].sudo().create({
                                    #         'name': product_id.name,
                                    #         'product_id': product_id.id,
                                    #         'product_uom_qty': 1,
                                    #         'product_uom': product_id.uom_id.id,
                                    #         'price_unit': product_id.list_price,
                                    #         'order_id': so.id,
                                    #         'tax_id': product_id.taxes_id,
                                    #         'company_id': 2,
                                    #     })
                                    #     # prix de la formation dans le devis
                                    #     amount_before_instalment = so.amount_total
                                    #     # so.amount_total = so.amount_total * 0.25
                                    #     for line in so.order_line:
                                    #         line.price_unit = so.amount_total
                                    #     so.action_confirm()
                                    #     ref = False
                                    #     # Creation de la Facture Cpf
                                    #     # Si la facture est de type CPF :  On parse le pourcentage qui est 25 %
                                    #     # methode_payment prend la valeur CPF pour savoir bien qui est une facture CPF qui prend la valeur 25 % par default
                                    #
                                    #     if so.amount_total > 0 and so.order_line:
                                    #         moves = so._create_invoices(final=True)
                                    #         for move in moves:
                                    #             move.type_facture = 'interne'
                                    #             # move.cpf_acompte_invoice= True
                                    #             # move.cpf_invoice =True
                                    #             move.methodes_payment = 'cpf'
                                    #             move.numero_cpf = externalId
                                    #             move.pourcentage_acompte = 25
                                    #             move.module_id = so.module_id
                                    #             move.session_id = so.session_id
                                    #             if so.pricelist_id.code:
                                    #                 move.pricelist_id = so.pricelist_id
                                    #             move.company_id = so.company_id
                                    #             move.price_unit = so.amount_total
                                    #             # move.cpf_acompte_invoice=True
                                    #             # move.cpf_invoice = True
                                    #             move.methodes_payment = 'cpf'
                                    #             move.post()
                                    #             ref = move.name
                                    #
                                    #     so.action_cancel()
                                    #     so.unlink()
                                    user.partner_id.statut = 'won'
                                    list = []
                                    for client in module_id.session_id.client_ids:  # get list of existing clients ids
                                        list.append(client.id)
                                    list.append(user.partner_id.id)  # append partner to the list
                                    module_id.session_id.write(
                                        {'client_ids': [(6, 0, list)]})  # update the list of clients
                                    """changer step à validé dans espace client """
                                    user.partner_id.step = 'finish'
                                    session = self.env['partner.sessions'].search(
                                        [('client_id', '=', user.partner_id.id),
                                         (
                                             'session_id', '=', module_id.session_id.id)])
                                    if not session:
                                        new_history = self.env['partner.sessions'].sudo().create({
                                            'client_id': user.partner_id.id,
                                            'session_id': module_id.session_id.id,
                                            'module_id': module_id.id,
                                            'company_id': 2,
                                        })
                                    if not user.partner_id.renounce_request:
                                        """Envoyer SMS pour renoncer au droit de rétractation"""
                                        url = '%smy' % str(user.partner_id.company_id.website)
                                        short_url = pyshorteners.Shortener()
                                        short_url = short_url.tinyurl.short(
                                            url)  # convert the url to be short using pyshorteners library
                                        sms_body_ = "Afin d'intégrer notre plateforme de formation de suite, veuillez renoncer à votre droit de rétractation sur votre espace client %s" % (
                                            short_url)
                                        # content of sms
                                        sms = self.env['mail.message'].sudo().search(
                                            [("body", "like", short_url), ("message_type", "=", "sms"),
                                             ('partner_ids', 'in', user.partner_id.id),
                                             ('model', "=", "res.partner")])
                                        if not sms:
                                            self.send_sms(sms_body_, user.partner_id)

                            elif product_id and product_id.company_id.id == 1 and user.partner_id.id_edof and user.partner_id.date_examen_edof and user.partner_id.session_ville_id:
                                _logger.info('if product_id mcm %s' % str(product_id))
                                user.partner_id.id_edof = product_id.id_edof
                                module_id = self.env['mcmacademy.module'].sudo().search(
                                    [('company_id', "=", 1),
                                     ('session_ville_id', "=", user.partner_id.session_ville_id.id),
                                     ('date_exam', "=", user.partner_id.date_examen_edof),
                                     ('product_id', "=", product_id.id),
                                     ('session_id.number_places_available', '>', 0)], limit=1)
                                if module_id:
                                    user.partner_id.module_id = module_id
                                    user.partner_id.mcm_session_id = module_id.session_id
                                    product_id = self.env['product.product'].sudo().search(
                                        [('product_tmpl_id', '=', module_id.product_id.id)])
                                    user.partner_id.mcm_session_id = module_id.session_id
                                    user.partner_id.module_id = module_id
                                    self.env.user.company_id = 1
                                    today = date.today()
                                    date_min = today - relativedelta(months=2)
                                    """chercher facture avec numero de dossier si n'existe pas on crée une facture"""
                                    # invoice = self.env['account.move'].sudo().search(
                                    #     [('numero_cpf', "=", externalId),
                                    #      ('state', "=", 'posted'),
                                    #      ('partner_id', "=", user.partner_id.id)], limit=1)
                                    # print('invoice', invoice)
                                    # if not invoice :
                                    #     print('if  not invoice mcm')
                                    #     so = self.env['sale.order'].sudo().create({
                                    #         'partner_id': user.partner_id.id,
                                    #         'company_id': 1,
                                    #     })
                                    #     self.env['sale.order.line'].sudo().create({
                                    #         'name': product_id.name,
                                    #         'product_id': product_id.id,
                                    #         'product_uom_qty': 1,
                                    #         'product_uom': product_id.uom_id.id,
                                    #         'price_unit': product_id.list_price,
                                    #         'order_id': so.id,
                                    #         'tax_id': product_id.taxes_id,
                                    #         'company_id': 1
                                    #     })
                                    #     # Enreggistrement des valeurs de la facture
                                    #     # Parser le pourcentage d'acompte
                                    #     # Creation de la fcture étape Finale
                                    #     # Facture comptabilisée
                                    #     so.action_confirm()
                                    #     so.module_id = module_id
                                    #     so.session_id = module_id.session_id
                                    #     moves = so._create_invoices(final=True)
                                    #     for move in moves:
                                    #         move.type_facture = 'interne'
                                    #         move.module_id = so.module_id
                                    #         # move.cpf_acompte_invoice=True
                                    #         # move.cpf_invoice =True
                                    #         move.methodes_payment = 'cpf'
                                    #         move.numero_cpf=externalId
                                    #         move.pourcentage_acompte = 25
                                    #         move.session_id = so.session_id
                                    #         move.company_id = so.company_id
                                    #         move.website_id = 1
                                    #         for line in move.invoice_line_ids:
                                    #             if line.account_id != line.product_id.property_account_income_id and line.product_id.property_account_income_id:
                                    #                 line.account_id = line.product_id.property_account_income_id
                                    #         move.post()
                                    #     so.action_cancel()
                                    #     so.unlink()
                                    user.partner_id.statut = 'won'
                                    """changer step à validé dans espace client """
                                    user.partner_id.step = 'finish'
                                    session = self.env['partner.sessions'].search(
                                        [('client_id', '=', user.partner_id.id),
                                         (
                                             'session_id', '=', module_id.session_id.id)])
                                    if not session:
                                        new_history = self.env['partner.sessions'].sudo().create({
                                            'client_id': user.partner_id.id,
                                            'session_id': module_id.session_id.id,
                                            'module_id': module_id.id,
                                            'company_id': 1,
                                        })
                                    if not user.partner_id.renounce_request:
                                        """Envoyer SMS pour renoncer au droit de rétractation"""
                                        url = '%smy' % str(user.partner_id.company_id.website) 
                                        short_url = pyshorteners.Shortener()
                                        short_url = short_url.tinyurl.short(
                                            url)  # convert the url to be short using pyshorteners library
                                        sms_body_ = "Afin d'intégrer notre plateforme de formation de suite, veuillez renoncer à votre droit de rétractation sur votre espace client %s" % (short_url)
                                        # content of sms
                                        sms = self.env['mail.message'].sudo().search(
                                            [("body", "like", short_url), ("message_type", "=", "sms"),
                                             ('partner_ids', 'in', user.partner_id.id),
                                             ('model', "=", "res.partner")])
                                        if not sms:
                                            self.send_sms(sms_body_, user.partner_id)
                            else:
                                if 'digimoov' in str(training_id):
                                    vals = {
                                        'description': 'CPF: vérifier la date et ville de %s' % (user.name),
                                        'name': 'CPF : Vérifier Date et Ville ',
                                        'team_id': self.env['helpdesk.team'].sudo().search(
                                            [('name', 'like', 'Client'), ('company_id', "=", 2)],
                                            limit=1).id,
                                    }
                                    description = "CPF: vérifier la date et ville de " + str(user.name)
                                    ticket = self.env['helpdesk.ticket'].sudo().search(
                                        [("description", "=", description)])
                                    if not ticket:
                                        new_ticket = self.env['helpdesk.ticket'].sudo().create(
                                            vals)
                                else:
                                    vals = {
                                        'partner_email': '',
                                        'partner_id': False,
                                        'description': 'CPF: id module edof %s non trouvé' % (training_id),
                                        'name': 'CPF : ID module edof non trouvé ',
                                        'team_id': self.env['helpdesk.team'].sudo().search(
                                            [('name', "like", _('Client')), ('company_id', "=", 1)],
                                            limit=1).id,
                                    }
                                    description = 'CPF: id module edof ' + str(training_id) + ' non trouvé'
                                    ticket = self.env['helpdesk.ticket'].sudo().search(
                                        [('description', 'ilike', description)])
                                    if not ticket:
                                        new_ticket = self.env['helpdesk.ticket'].sudo().create(
                                            vals)

    """Remplir champ numero cpf sur tout les factures cpf"""

    def num_cpf_facture(self):
        partners = self.env['res.partner'].sudo().search([('statut', "=", "won"), ('mode_de_financement', "=", "cpf")])
        _logger.info('for partnerss')
        for partner in partners:
            _logger.info(' partner %s' % partner.name)
            invoice = self.env['account.move'].sudo().search([('partner_id', "=", partner.id)], limit=1,
                                                             order="id desc")

            if invoice and partner.numero_cpf:
                _logger.info(' if invoice %s' % str(invoice.name))
                invoice.numero_cpf = partner.numero_cpf
                _logger.info(' if invoice %s' % str(invoice.numero_cpf))

    def update_carte_bleu_cpf_partner_field_financement(self):
        """ Tache cron pour remplir le champ financement dans la fiche client avec état de paiement
        de (paid, not paid, in paiement) à partir de la dernière facture de client"""
        try:
            companies = self.env['res.company'].sudo().search([])
            if companies:
                for company in companies:
                    api_key = company.wedof_api_key
                    params_wedof = (
                        ('order', 'desc'),
                        ('type', 'all'),
                        ('state',
                         'validated,inTraining,refusedByAttendee,refusedByOrganism,serviceDoneDeclared,serviceDoneValidated,canceledByAttendee,canceledByAttendeeNotRealized,canceledByOrganism'),
                        ('billingState', 'all'),
                        ('certificationState', 'all'),
                        ('sort', 'lastUpdate'),
                        ('limit', '100'),
                        ('page', '1')
                    )
                    headers = {
                        'accept': 'application/json',
                        'Content-Type': 'application/json',
                        'X-API-KEY': api_key,
                    }
                    response = requests.get('https://www.wedof.fr/api/registrationFolders/', headers=headers,
                                            params=params_wedof)
                    registrations = response.json()
                    for dossier in registrations:
                        print('dosssier', dossier['attendee']['address'])
                        externalId = dossier['externalId']
                        email = dossier['attendee']['email']
                        email = email.replace("%", ".")  # remplacer % par .
                        email = email.replace(" ", "")  # supprimer les espaces envoyés en paramètre email
                        email = str(
                            email).lower()  # recupérer l'email en miniscule pour éviter la création des deux comptes
                        # Recherche dans la table utilisateur si login de wedof = email
                        user = self.env["res.users"].sudo().search([("login", "=", email)])
                        for users in user:
                            if users and users.partner_id.mode_de_financement == "cpf":
                                # Initialisation de champ etat_financement_cpf_cb
                                etat_financement_cpf_cb = dossier['state']
                                if etat_financement_cpf_cb == "untreated":
                                    users.partner_id.sudo().write({
                                        'etat_financement_cpf_cb': 'untreated'})  # write la valeur untreated dans le champ etat_financement_cpf_cb
                                elif etat_financement_cpf_cb == "validated":
                                    users.partner_id.sudo().write({'etat_financement_cpf_cb': 'validated'})
                                elif etat_financement_cpf_cb == "accepted":
                                    users.partner_id.sudo().write({'etat_financement_cpf_cb': 'accepted'})
                                elif etat_financement_cpf_cb == "inTraining":
                                    users.partner_id.sudo().write({'etat_financement_cpf_cb': 'in_training'})
                                elif etat_financement_cpf_cb == "out_training":
                                    users.partner_id.sudo().write({'etat_financement_cpf_cb': 'terminated'})
                                elif etat_financement_cpf_cb == "serviceDoneDeclared":
                                    users.partner_id.sudo().write({'etat_financement_cpf_cb': 'service_declared'})
                                elif etat_financement_cpf_cb == "serviceDoneValidated":
                                    users.partner_id.sudo().write({'etat_financement_cpf_cb': 'service_validated'})
                                elif etat_financement_cpf_cb == "canceled" or etat_financement_cpf_cb == "canceledByAttendee" or etat_financement_cpf_cb == "canceledByAttendeeNotRealized" or etat_financement_cpf_cb == "refusedByAttendee" or etat_financement_cpf_cb == "refusedByOrganism":
                                    users.partner_id.sudo().write({'etat_financement_cpf_cb': 'canceled'})
                                else:
                                    users.partner_id.etat_financement_cpf_cb = users.partner_id.statut_cpf
        except Exception:
            self.env.cr.rollback()
        try:
            #client with particulier mode
            for partner in self.env['res.partner'].search(
                    [('statut', "=", "won"), ('mcm_session_id.date_exam', '>', '01/05/2022')]):  # Récupérer les clients qui sont gagnés et sont modes de financement carte bleu
                if partner.mode_de_financement == 'particulier':
                    for invoice in self.env['account.move'].sudo().search(
                            [('partner_id', "=", partner.id)],
                            order='create_date asc'):
                        _logger.info(
                            "user INVOICE----invoice_payment_state------------°°°°°°°°°°°°°°° %s " % str(
                                invoice.invoice_payment_state))
                        _logger.info(
                            "user Partner id----------------°°°°°°°°°°°°°°° %s " % str(
                                invoice.partner_id.display_name))
                        if invoice and invoice.invoice_payment_state:
                            etat_financement_cpf_cb = invoice.invoice_payment_state
                            if invoice.invoice_payment_state == "in_payment":
                                etat_financement_cpf_cb = invoice.invoice_payment_state
                                invoice.partner_id.sudo().write({'etat_financement_cpf_cb': 'in_payment'})
                            elif invoice.invoice_payment_state == "paid":
                                etat_financement_cpf_cb = invoice.invoice_payment_state
                                invoice.partner_id.sudo().write({'etat_financement_cpf_cb': 'paid'})
                            elif invoice.invoice_payment_state == "not_paid":
                                etat_financement_cpf_cb = invoice.invoice_payment_state
                                invoice.partner_id.sudo().write({'etat_financement_cpf_cb': 'not_paid'})
                elif partner.etat_financement_cpf_cb is not True:
                    if partner.statut_cpf == 'bill':
                        partner.sudo().write({'etat_financement_cpf_cb': 'bill'})
                    elif partner.statut_cpf == 'service_declared':
                        partner.sudo().write({'etat_financement_cpf_cb': 'service_declared'})
                    elif partner.statut_cpf == 'accepted':
                        partner.sudo().write({'etat_financement_cpf_cb': 'accepted'})
                    elif partner.statut_cpf == 'in_training':
                        partner.sudo().write({'etat_financement_cpf_cb': 'in_training'})
                    elif partner.statut_cpf == 'validated':
                        partner.sudo().write({'etat_financement_cpf_cb': 'validated'})
        except Exception:
            self.env.cr.rollback()

    def get_session(self):

        company = self.env['res.company'].sudo().search([('id', "=", 2)])
        api_key = ""
        if company:
            api_key = company.wedof_api_key

        url = "https://www.wedof.fr/api/registrationFolders/utils/sessionMinDates"

        headers = {
            "Content-Type": "application/json",
            "X-API-KEY": api_key
        }

        response = requests.request("GET", url, headers=headers)

        print(response.text)
        datemin = response.json()
        date_debutstr = datemin.get('cpfSessionMinDate')
        date_debut = datetime.strptime(date_debutstr, '%Y-%m-%dT%H:%M:%S.%fz')
        if datetime.today() <= date_debut:
            print(date_debut, datetime.today())
        if date_debut <= datetime.today():
            print('else')

    def test_email(self):
        partner = self.env['res.partner'].sudo().search([('email', "=", "ilahmar@digimoov.fr")], limit=1)
        """Si message d'erreur "unavailableEmails" on ajoute #digimoov à l'email pour qu'il sera ajouté sur la plateforme 360"""
        print('partner', partner)
        old_email = partner.email
        position = old_email.index('@')
        new_email = old_email[:position] + '#digimoov' + old_email[position:]
        _logger.info("new email %s" % new_email)
        partner.email = new_email
        partner.second_email = new_email
        """Changer format du numero de tel pour envoyer le sms """
        if partner.email and "#" in partner.email:
            _logger.info("send mail and sms %s" % str(partner.email))
            if partner.phone:
                phone = str(partner.phone.replace(' ', ''))[-9:]
                phone = '+33' + ' ' + phone[0:1] + ' ' + phone[1:3] + ' ' + phone[
                                                                            3:5] + ' ' + phone[
                                                                                         5:7] + ' ' + phone[
                                                                                                      7:]
                partner.phone = phone
            """envoyer SMS pour informer l'apprenant de sa nouvelle adresse email """
            new_login = partner.email
            name = partner.name
            body = "DIGIMOOV. Cher(e) %s, nous vous informons que nous avons procédé pour des raisons de sécurité au changement de votre adresse email. Pour plus d'infos, veuillez consulter votre boite mail. " % (
                name)
            if body:
                sms = self.env['mail.message'].sudo().search([('partner_ids', 'in', partner.id),
                                                              ('message_type', '=', "sms"),
                                                              ('body', '=', body)])
                state = False
                if sms:
                    print('sms')
                    for notification_id in sms.notification_ids:
                        if notification_id.notification_status == "sent":
                            state = True
                if not state:
                    print('sms false ')
                    composer = self.env['sms.composer'].with_context(
                        default_res_model='res.partner',
                        default_res_id=partner.id,
                        default_composition_mode='comment',
                    ).sudo().create({
                        'body': body,
                        'mass_keep_log': True,
                        'mass_force_send': False,
                        'use_active_domain': False,
                    })
                    composer.action_send_sms()  # we send sms to client contains link to register in cma.
            if partner.phone:
                partner.phone = '0' + str(partner.phone.replace(' ', ''))[
                                      -9:]
            """envoyer email pour informer l'apprenant de sa nouvelle adresse email """
            # partner.email = old_email
            print('partttttt', partner.email, old_email)
            mail_compose_message = self.env['mail.compose.message']
            mail_compose_message.fetch_sendinblue_template()
            template_id = self.env['mail.template'].sudo().search(
                [('subject', "=", "Avis de changement de Login"),
                 ('model_id', "=", 'res.partner')],
                limit=1)  # we get the mail template from sendinblue
            if template_id:
                print("template", template_id)
                message = self.env['mail.message'].sudo().search(
                    [('subject', "=", "Avis de changement de Login"),
                     ('model', "=", 'res.partner'), ('partner_ids', 'in', partner.id)],
                    limit=1)  # check if we have already sent the email
                if not message:
                    print('hiiii')
                    partner.with_context(force_send=True).message_post_with_template(
                        template_id.id,
                        composition_mode='comment',
                    )  # send the email to client
                # partner.email = new_email

    def test_api(self):

        company_id = '56f5520e11d423f46884d593'
        api_key = 'cnkcbrhHKyfzKLx4zI7Ub2P5'
        headers = CaseInsensitiveDict()
        headers["Accept"] = "*/*"
        params = (
            ('company', '56f5520e11d423f46884d593'),
            ('apiKey', 'cnkcbrhHKyfzKLx4zI7Ub2P5'),
        )
        get_custom_fields = requests.get(
            "https://app.360learning.com/api/v1/customfields?company=" + company_id + "&apiKey=" + api_key,
            headers=headers)
        response = get_custom_fields.json()
        for field in response:

            print('geeeett', field, field['_id'])
            id = field['_id']
            if field['name'] == "Pack":
                response = requests.get('https://app.360learning.com/api/v1/users', params=params)
                users = response.json()
                # Faire un parcours sur chaque user et extraire ses statistiques
                for user in users:
                    iduser = user['_id']
                    email = user['mail']
                    response_user = requests.get('https://app.360learning.com/api/v1/users/' + iduser,
                                                 params=params)
                    table_user = response_user.json()
                    if email == "ilahmar#test@digimoov.fr":
                        payload = json.dumps({
                            "values": [
                                {
                                    "customFieldId": id,
                                    "value": "Formation premium"
                                }
                            ]
                        })
                        response_post = requests.put(
                            "https://app.360learning.com/api/v1/users/" + iduser + "/customfields?company=" + company_id + "&apiKey=" + api_key,
                            data=payload, headers=headers)
                        print('response json', response_post.json())
                        response_user = requests.get(
                            'https://app.360learning.com/api/v1/users/' + iduser, params=params)
                        table_user = response_user.json()
                        print("user info", table_user)

    def send_email(self, partner):
        _logger.info('send email', partner)
        if self.env.su:
            # sending mail in sudo was meant for it being sent from superuser
            self = self.with_user(SUPERUSER_ID)
        if not partner.lang:
            partner.lang = 'fr_FR'
        _logger.info('avant email %s' % str(partner.name))
        # message = self.env['mail.message'].search(
        #     [('res_id', "=", partner.id), ('subject', "ilike", "Digimoov - Accès à la plateforme en ligne")])
        # if not message:
        template_id = int(self.env['ir.config_parameter'].sudo().get_param(
            'plateforme_pedagogique.mail_template_add_ione_to_plateforme_digimoov_mcm'))
        template_id = self.env['mail.template'].search([('id', '=', template_id)]).id
        if not template_id:
            template_id = self.env['ir.model.data'].xmlid_to_res_id(
                'plateforme_pedagogique.mail_template_add_ione_to_plateforme_digimoov_mcm',
                raise_if_not_found=False)
        if not template_id:
            template_id = self.env['ir.model.data'].xmlid_to_res_id(
                'plateforme_pedagogique.mail_template_add_ione_to_plateforme_digimoov_mcm',
                raise_if_not_found=False)
        if template_id:
            partner.with_context(force_send=True).message_post_with_template(template_id,
                                                                             composition_mode='comment',
                                                                             )
        _logger.info('if template  %s' % str(partner.name))

    def send_email_manuel(self):
        """check if user added to plateform"""
        """send mail with button"""
        company_id = '56f5520e11d423f46884d593'
        api_key = 'cnkcbrhHKyfzKLx4zI7Ub2P5'
        headers = CaseInsensitiveDict()
        headers["Accept"] = "*/*"
        params = (
            ('company', '56f5520e11d423f46884d593'),
            ('apiKey', 'cnkcbrhHKyfzKLx4zI7Ub2P5'),
        )
        response = requests.get('https://app.360learning.com/api/v1/users', params=params)
        users = response.json()
        # Faire un parcours sur chaque user vérifier l'existance d'apprenant sur email
        existant = False
        for user in users:
            email = user['mail']
            if email == self.email:
                existant = True
        if (existant):
            message = self.env['mail.message'].search(
                [('res_id', "=", self.id), ('subject', "ilike", "Digimoov - Accès à la plateforme en ligne")])
            if message:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _(' Mail déja envoyé'),
                        'sticky': False,
                        'className': 'bg-danger'
                    }
                }
            if not message:
                self.send_email(self)
                message_exist = self.env['mail.message'].search(
                    [('res_id', "=", self.id), ('subject', "ilike", "Digimoov - Accès à la plateforme en ligne")])
                if message_exist:
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': _(' Mail envoyé avec succès'),
                            'sticky': False,
                            'className': 'success'
                        }
                    }
                body = "Digimoov vous confirme votre inscription à la Formation capacité de transport de marchandises. RDV sur notre plateforme https://www.digimoov.fr/r/SnB"
                self.send_sms(body, self)

        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _(' Mail non envoyé'),
                    'message': _("L'apprenant n'est pas sur la plateforme !‍️"),
                    'sticky': False,
                    'className': 'bg-danger'
                }
            }

    def send_sms(self, body, partner):
        """Changer format du numero de tel pour envoyer le sms"""
        _logger.info("send  sms %s" % str(partner.email))
        if partner.phone:
            _logger.info("send  sms %s" % str(partner.email))
            phone = str(partner.phone.replace(' ', ''))[-9:]
            phone = '+33' + ' ' + phone[0:1] + ' ' + phone[1:3] + ' ' + phone[
                                                                        3:5] + ' ' + phone[
                                                                                     5:7] + ' ' + phone[
                                                                                                  7:]
            partner.phone = phone
            name = partner.name
            # sms = self.env['mail.message'].sudo().search(
            #     [("body", "like", body), ("message_type", "=", 'sms'), ('res_id', '=', partner.id),('model',"=","res.partner")])
            # if not sms:
            composer = self.env['sms.composer'].with_context(
                default_res_model='res.partner',
                default_res_id=partner.id,
                default_composition_mode='comment',
            ).sudo().create({

                'body': body,
                'mass_keep_log': True,
                'mass_force_send': False,
                'use_active_domain': False,
            })
            _logger.info('phooooneee ======================== %s' % str(partner.phone))
            composer.action_send_sms()  # we send sms.
            if partner.phone:
                partner.phone = '0' + str(partner.phone.replace(' ', ''))[
                                      -9:]

    

