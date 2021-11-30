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

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from unidecode import unidecode
import logging

_logger = logging.getLogger(__name__)


class partner(models.Model):
    _inherit = 'res.partner'

    # ajouter champs au modele partner par defaut res.partner ne sont pas des instructors

    apprenant = fields.Boolean("Apprenant sur 360")
    group_id = fields.Many2many('plateforme_pedagogique.groupe', string="Groupe")
    # champs pour recuperer les statistiques
    assignedPrograms = fields.Integer(string='Nombre de programmes attribués')

    last_login = fields.Char(string="Derniere Activité", readonly=True)
    # learner_achivement=fields.Char(string="Réalisations des apprenants")
    averageScore = fields.Integer(string="Score Moyen", readonly=True)
    totalTimeSpentInMinutes = fields.Char(string="temps passé en minutes", readonly=True)
    password360 = fields.Char()  # Champs pour stocker le mot de passe non crypté
    firstName = fields.Char()
    lastName = fields.Char()
    date_creation = fields.Char(string="Date d'inscription")
    messages = fields.Char(string='Messages Postés')
    publications = fields.Char(string='Cours ou programmes publiés')
    comments = fields.Char(string='Commentaires Postés')
    reactions = fields.Char(string="Réactions dans les forums d'activités")
    renounce_request = fields.Boolean(
        "Renonciation au droit de rétractation conformément aux dispositions de l'article L.221-28 1°")
    toDeactivateAt = fields.Char("Date de suppression")
    passage_exam = fields.Boolean("Examen passé", default=False)
    stats_ids = fields.Many2one('plateforme_pedagogique.user_stats')
    temps_minute = fields.Integer(string="Temps passé en minutes")  # Champs pour récuperer temps en minute par api360
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
            response_user = requests.get('https://app.360learning.com/api/v1/users/' + iduser, params=params)
            table_user = response_user.json()
            lastlogin = ""
            if 'lastLoginAt' in table_user:
                lastlogin = str(table_user['lastLoginAt'])

            print('user date supp', table_user['toDeactivateAt'])
            times = ''
            # Ecrire le temps récupéré de 360 sous forme d'heures et minutes
            if 'totalTimeSpentInMinutes' in table_user:
                time = int(table_user['totalTimeSpentInMinutes'])
                heure = time // 60
                minute = time % 60
                times = str(heure) + 'h' + str(minute) + 'min'
                if (heure == 0):
                    times = str(minute) + 'min'
                    print(times)
                if (minute == 0):
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
            publication = ''
            if ('publications' in table_user):
                publication = table_user['publications']
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
                    partner.sudo().write({
                        'last_login': last_login,
                        'averageScore': average,
                        'comments': comment,
                        'reactions': reaction,
                        'publications': publication,
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

    def write(self, vals):
        if 'statut' in vals:
            # Si statut annulé on supprime i-One
            if vals['statut'] == 'canceled':
                self.supprimer_ione_manuelle()
        record = super(partner, self).write(vals)
        return record

    # Ajout automatique d' i-One sur 360learning
    def Ajouter_iOne_auto(self):
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
            # Pour chaque apprenant chercher sa facture
            facture = self.env['account.move'].sudo().search([('session_id', '=', partner.mcm_session_id.id),
                                                              ('module_id', '=', partner.module_id.id),
                                                              ('state', '=', 'posted')
                                                              ], order="invoice_date desc", limit=1)
            date_facture = facture.invoice_date
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
                        if not partner.renounce_request and date_facture and (date_facture + timedelta(days=14)) <= today:
                            self.ajouter_iOne(partner)
            """cas de cpf on vérifie la validation des document , la case de renonciation et la date d'examen qui doit etre au futur """
            if partner.mode_de_financement == "cpf":
                if document_valide and partner.mcm_session_id.date_exam and (
                        partner.mcm_session_id.date_exam > date.today()):
                    if partner.renounce_request:
                        self.ajouter_iOne(partner)
                    if not partner.renounce_request and date_facture and (date_facture + timedelta(days=14)) <= today:
                        self.ajouter_iOne(partner)

    # Ajouter ione manuellement
    def ajouter_iOne_manuelle(self):
        # _logger.info("++++++++++++Cron ajouter_iOne_manuelle++++++++++++++++++++++")
        product_name = self.module_id.product_id.name
        sale_order = self.env['sale.order'].sudo().search([('partner_id', '=', self.id),
                                                           ('session_id', '=', self.mcm_session_id.id),
                                                           ('module_id', '=', self.module_id.id),
                                                           ('state', '=', 'sale'),
                                                           ], limit=1, order="id desc")
        # Pour chaque apprenant chercher sa facture
        facture = self.env['account.move'].sudo().search([('session_id', '=', self.mcm_session_id.id),
                                                          ('module_id', '=', self.module_id.id),
                                                          ('state', '=', 'posted')
                                                          ], order="invoice_date desc", limit=1)
        date_facture = facture.invoice_date
        # Calculer date d'ajout apres 14jours de date facture
        date_ajout = date_facture + timedelta(days=14)
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
                    if (not (self.renounce_request) and (date_ajout <= today)):
                        self.ajouter_iOne(self)
        """cas de cpf on vérifie la validation des document , la case de renonciation et la date d'examen qui doit etre au futur """
        if self.mode_de_financement == "cpf":
            if (document_valide) and (self.mcm_session_id.date_exam) and (
                    self.mcm_session_id.date_exam > date.today()):
                if (self.renounce_request):
                    self.ajouter_iOne(self)
                if not (self.renounce_request) and (date_ajout <= today):
                    self.ajouter_iOne(self)

    def ajouter_iOne(self, partner):
        # Remplacez les paramètres régionaux de l'heure par le paramètre de langue actuel
        # du compte dans odoo
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

            # Récuperer le mot de passe à partir de res.users
            user = self.env['res.users'].sudo().search([('partner_id', '=', partner.id)],limit=1)
            _logger.info('avant if login user %s' %user.login)
            _logger.info('avant if partner email %s' %partner.email)
            _logger.info('avant if password  %s ' % user.password360)

            if user:
                id_Digimoov_bienvenue = '56f5520e11d423f46884d594'
                id_Digimoov_Examen_Attestation = '5f9af8dae5769d1a2c9d5047'
                params = (
                    ('company', '56f5520e11d423f46884d593'),
                    ('apiKey', 'cnkcbrhHKyfzKLx4zI7Ub2P5'),
                )
                company_id = '56f5520e11d423f46884d593'
                api_key = 'cnkcbrhHKyfzKLx4zI7Ub2P5'
                urluser = 'https://app.360learning.com/api/v1/users?company=' + company_id + '&apiKey=' + api_key
                urlgroup_Bienvenue = 'https://app.360learning.com/api/v1/groups/' + id_Digimoov_bienvenue + '/users/' + partner.email + '?company=' + company_id + '&apiKey=' + api_key
                url_groups = 'https://app.360learning.com/api/v1/groups'
                url_unsubscribeToEmailNotifications = 'https://app.360learning.com/api/v1/users/unsubscribeToEmailNotifications?company=' + company_id + '&apiKey=' + api_key
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
                    _logger.info('if user  %s ' % user.password360)

                    # Ajouter i-One to table user
                    data_user = '{"mail":"' + partner.email + '" , "password":"' + user.password360 + '", "firstName":"' + partner.firstName + '", "lastName":"' + partner.lastName + '", "phone":"' + partner.phone + '", "lang":"fr","sendCredentials":"true"}'
                    resp = requests.post(urluser, headers=headers, data=data_user)
                    print(data_user, 'user', resp.status_code)
                    if (resp.status_code == 200):
                        create = True
                data_group = {}
                # Désactiver les notifications par email
                data_email = json.dumps({
                    "usersEmails": [
                        partner.email
                    ]
                })
                resp_unsub_email = requests.put(url_unsubscribeToEmailNotifications, headers=headers, data=data_email)
                # Si l'apprenant a été ajouté sur table user on l'affecte aux autres groupes
                if (create):
                    _logger.info('create %s' %user.login)
                    today = date.today()
                    new_format = '%d %B %Y'
                    # Changer format de date et la mettre en majuscule
                    date_ajout = today.strftime(new_format)
                    partner.date_creation = date_ajout
                    # Affecter i-One to groupe digimoov-bienvenue
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
                        digimoov_examen = "Digimoov - Attestation de capacité de transport de marchandises de moins de 3.5t"
                        # Si la company est digimoov on ajoute i-One sur 360
                        if (company == '2'):
                            if (nom_groupe == digimoov_examen.upper()):
                                id_Digimoov_Examen_Attestation = id_groupe
                                urlsession = 'https://app.360learning.com/api/v1/groups/' + id_groupe + '/users/' + partner.email + '?company=' + company_id + '&apiKey=' + api_key
                                respsession = requests.put(urlsession, headers=headers, data=data_group)

                                # Affecter à un pack solo
                            packsolo = "Digimoov - Pack Solo"
                            if (("solo" in product_name) and (nom_groupe == packsolo.upper())):
                                print(partner.module_id.name)
                                urlgrp_solo = 'https://app.360learning.com/api/v1/groups/' + id_groupe + '/users/' + partner.email + '?company=' + company_id + '&apiKey=' + api_key
                                respgrp_solo = requests.put(urlgrp_solo, headers=headers, data=data_group)
                                print('affecté à solo', respgrp_solo.status_code)

                            # Affecter à un pack pro
                            pack_pro = "Digimoov - Pack Pro"
                            if (("pro" in product_name) and (nom_groupe == pack_pro.upper())):
                                print(partner.module_id.name)
                                urlgrp_pro = 'https://app.360learning.com/api/v1/groups/' + id_groupe + '/users/' + partner.email + '?company=' + company_id + '&apiKey=' + api_key
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

    def supprimer_ione_auto(self):
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
            # Pour chaque partner verifier si date_suppression est aujourd'hui
            # pour assurer la suppresion automatique
            partner = self.env['res.partner'].sudo().search([('email', "=", email)], limit=1)
            if (partner and partner.mcm_session_id.date_exam):
                # date de suppression est date d'examen + 4jours
                date_suppression = partner.mcm_session_id.date_exam + timedelta(days=4)
                today = date.today()
                if (date_suppression <= today):
                    email = partner['email']
                    print('date_sup', email, date_suppression, today)
                    _logger.info('liste à supprimé %s' %str(email))
                    # url = 'https://app.360learning.com/api/v1/users/' + email + '?company=' + company_id + '&apiKey=' + api_key
                    # resp = requests.delete(url)
                    print('ress resp.status_code')

            else:
                print('date incompatible')

    def supprimer_ione_manuelle(self):
        company_id = '56f5520e11d423f46884d593'
        api_key = 'cnkcbrhHKyfzKLx4zI7Ub2P5'
        headers = CaseInsensitiveDict()
        headers["Accept"] = "*/*"
        url = 'https://app.360learning.com/api/v1/users/' + self.email + '?company=' + company_id + '&apiKey=' + api_key
        resp = requests.delete(url)


    # Extraire firstName et lastName à partir du champs name
    def diviser_nom(self, partner):
        # _logger.info('name au debut  %s' %partner.name)
        if partner.name == '':
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
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
            'X-API-KEY': '026514d6bc7d880515a27eae4947bccef4fbbf03',
        }
        params_wedof = (
            ('order', 'asc'),
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
            email = dossier['attendee']['email']
            certificat = dossier['_links']['certification']['name']
            certificat_info = dossier['_links']['certification']['certifInfo']
            date_formation = dossier['trainingActionInfo']['sessionStartDate']
            """convertir date de formatio """
            date_split = date_formation[0:10]
            date_ = datetime.strptime(date_split, "%Y-%m-%d")
            dateFormation = date_.date()
            today = date.today()
            print('date', today, dateFormation, certificat)
            """Si date de formation <= ajourdhui et s'il a choisi  la formation de transport  léger de marchandises
            on cherche l'apprenant par email sur 360"""
            if (
                    certificat == "Formation à l'obtention de l'attestation de capacité professionnelle en transport léger de marchandises") \
                    and (dateFormation <= today):
                _logger.info('wedooooffffff %s' % certificat)
                _logger.info('dateformation %s' % dateFormation)
                _logger.info('email %s' % email)
                response_plateforme = requests.get('https://app.360learning.com/api/v1/users', params=param_360)
                users = response_plateforme.json()
                for user in users:
                    user_mail = user['mail']
                    user_id = user['_id']
                    response_user = requests.get('https://app.360learning.com/api/v1/users/' + user_id,
                                                 params=param_360)
                    table_user = response_user.json()
                    totalTime = int(table_user['totalTimeSpentInMinutes'])
                    """si l'apprenant connecté sur 360 
                    on change le statut de son dossier sur wedof"""
                    if (user_mail.upper() == email.upper()) and (totalTime >= 1):
                        _logger.info('users %s ' % email.upper())
                        _logger.info('user email %s' % user['mail'].upper())
                        response_post = requests.post('https://www.wedof.fr/api/registrationFolders/'+externalId+'/inTraining',
                                                  headers=headers, data=data)
                        print('response post',response_post.status_code)
                        """Si dossier passe en formation on met à jour statut cpf sur la fiche client"""
                        # 
                        # partner = self.env['res.partner'].sudo().search([('numero_cpf', "=", str(externalId))])
                        # if len(partner) > 1:
                        #     for part in partner:
                        #         if part.email == email:
                        #             _logger.info('if partner >1 %s' % partner.numero_cpf)
                        #             partner.statut_cpf="in_training"
                        # elif len(partner) == 1:
                        #     _logger.info('if partner %s' % partner.numero_cpf)
                        #     partner.statut_cpf = "in_training"

    """changer l'etat sur wedof de non traité vers validé à partir d'API"""
    def change_state_wedof_validate(self):
        params_wedof = (
            ('order', 'asc'),
            ('type', 'all'),
            ('state', 'notProcessed'),
            ('billingState', 'all'),
            ('certificationState', 'all'),
            ('sort', 'lastUpdate'),
        )
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
            'X-API-KEY': '026514d6bc7d880515a27eae4947bccef4fbbf03',
        }
        response = requests.get('https://www.wedof.fr/api/registrationFolders/', headers=headers,
                                params=params_wedof)
        registrations = response.json()
        for dossier in registrations:
            externalid = dossier['externalId']
            email = dossier['attendee']['email']
            email = email.replace("%", ".")  # remplacer % par .
            email = email.replace(" ", "")  # supprimer les espaces envoyés en paramètre email
            email = str(email).lower()  # recupérer l'email en miniscule pour éviter la création des deux comptes
            print('dossier', dossier)
            idform = dossier['trainingActionInfo']['trainingId']
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
            if "roadName" in dossier['attendee']['address']:
                address = dossier['attendee']['address']['roadName']
            else:
                address = ""
            if "phoneNumber" in dossier['attendee']:
                tel = dossier['attendee']['phoneNumber']
            else:
                tel = ""
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
            datedebut = today + timedelta(days=15)
            datefin = str(datedebut + relativedelta(months=3) + timedelta(days=1))
            datedebutstr = str(datedebut)
            data = '{"trainingActionInfo":{"sessionStartDate":"' + datedebutstr + '","sessionEndDate":"' + datefin + '" }}'
            dat = '{\n  "weeklyDuration": 14,\n  "indicativeDuration": 102\n}'
            response_put = requests.put('https://www.wedof.fr/api/registrationFolders/' + externalid,
                                        headers=headers, data=data)
            response_post = requests.post('https://www.wedof.fr/api/registrationFolders/' + externalid + '/validate',
                                          headers=headers, data=dat)
            status = str(response_post.status_code)

            """Si dossier passe à l'etat validé on met à jour statut cpf sur la fiche client"""
            print('validate', email)
            # self.cpf_validate(training_id, email, address, tel, code_postal, ville, diplome, nom, prenom,
            #                       externalid, lastupd)
            # partner = self.env['res.partner'].sudo().search([('numero_cpf', "=", str(externalId))])
            # if len(partner) > 1:
            #     for part in partner:
            #         if part.email == email:
            #             _logger.info('if partner >1 %s' % partner.numero_cpf)
            #             partner.statut_cpf = "in_training"
            # elif len(partner) == 1:
            #     _logger.info('if partner %s' % partner.numero_cpf)
            #     partner.statut_cpf = "in_training"
            # put_status = str(response_put.status_code)
            # _logger.info("status put %s" % put_status)
            # _logger.info("status post %s" % status)

    """Mettre à jour les statuts cpf sur la fiche client selon l'etat sur wedof """
    def change_state_cpf_partner(self):
        params_wedof = (
            ('order', 'asc'),
            ('type', 'all'),
            ('state', 'canceledByAttendee,canceledByAttendeeNotRealized,canceledByOrganism'),
            ('billingState', 'all'),
            ('certificationState', 'all'),
            ('sort', 'lastUpdate'),
            ('limit', '10000000000')
        )
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
            'X-API-KEY': '026514d6bc7d880515a27eae4947bccef4fbbf03',
        }
        response = requests.get('https://www.wedof.fr/api/registrationFolders/', headers=headers,
                                params=params_wedof)
        registrations = response.json()
        for dossier in registrations:
            externalId=dossier['externalId']
            email = dossier['attendee']['email']
            email = email.replace("%", ".")  # remplacer % par .
            email = email.replace(" ", "")  # supprimer les espaces envoyés en paramètre email
            email = str(email).lower()  # recupérer l'email en miniscule pour éviter la création des deux comptes
            print('dossier',dossier)
            idform=dossier['trainingActionInfo']['trainingId']
            training_id=""
            if "_" in idform:
                idforma = idform.split("_", 1)
                if idforma:
                    training_id = idforma[1]
           
            print('training',training_id)
            state=dossier['state']
            lastupdatestr=str(dossier['lastUpdate'])
            lastupdate=datetime.strptime(lastupdatestr, '%Y-%m-%dT%H:%M:%S.%fz')
            newformat="%d/%m/%Y %H:%M:%S"
            lastupdateform=lastupdate.strftime(newformat)
            lastupd=datetime.strptime(lastupdateform, "%d/%m/%Y %H:%M:%S")
            if "roadName" in dossier['attendee']['address']:
                address = dossier['attendee']['address']['roadName']
            else:
                address = ""
            if "phoneNumber" in  dossier['attendee']:
                tel = dossier['attendee']['phoneNumber']
            else :
                tel = ""
            if "zipCode" in dossier['attendee']['address']:
                code_postal = dossier['attendee']['address']['zipCode']
            else :
                code_postal = ""
            if "city" in dossier['attendee']['address']:
                ville = dossier['attendee']['address']['city']
            else :
                ville =""
            if 'firstName' in dossier['attendee']['firstName']:
                nom = dossier['attendee']['firstName']
            else :
                nom=""
            
            if "lastName" in dossier['attendee']['lastName']:
                prenom = dossier['attendee']['lastName']
            else :
                prenom=""
            diplome = dossier['trainingActionInfo']['title']
            
            
            if state=="validated":
                print('validate',email)
                self.cpf_validate(training_id,email,address,tel,code_postal,ville,diplome,nom,prenom,externalId,lastupd)
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
                    
                if state=="inTraining":
                    user.partner_id.statut_cpf="in_training"
                if state=="terminated":
                    user.partner_id.statut_cpf="out_training"
                if state=="serviceDoneDeclared":
                    user.partner_id.statut_cpf="service_declared"
                if state=="serviceDoneValidated":
                    user.partner_id.statut_cpf="service_validated"
                if state=="canceledByAttendee" or state=="canceledByAttendeeNotRealized" or state=="canceledByOrganism"  :
                    user.partner_id.statut_cpf="canceled"
                user.partner_id.numero_cpf = externalId
                user.partner_id.date_cpf = lastupd


    def cpf_validate(self,module,email,address,tel,code_postal,ville,diplome,nom,prenom,dossier,lastupd):
        user = self.env['res.users'].sudo().search([('login', "=", email)])
        exist = True
        if not user:
            if '+33' not in str(tel):  # num edof
                user = self.env["res.users"].sudo().search(
                    [("phone", "=", str(tel).replace(' ', ''))], limit=1)
                if not user:
                    phone = str(tel)
                    phone = phone[1:]
                    phone = '+33' + str(phone)
                    user = self.env["res.users"].sudo().search(
                        [("phone", "=", phone.replace(' ', ''))], limit=1)
            else:
                user = self.env["res.users"].sudo().search(
                    [("phone", "=", str(tel).replace(' ', ''))], limit=1)
                if not user:
                    phone = str(tel)
                    phone = phone[3:]
                    phone = '0' + str(phone)
                    user = self.env["res.users"].sudo().search(
                        [("phone", "=", phone.replace(' ', ''))], limit=1)
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
        # user = request.env['res.users'].sudo().search([('login', "=", email)])
        if user:
            client = self.env['res.partner'].sudo().search(
                [('id', '=', user.partner_id.id)])
            if client:
                client.mode_de_financement = 'cpf'
                client.funding_type = 'cpf'
                client.numero_cpf = dossier
                client.statut_cpf = 'validated'
                client.phone = tel
                client.street = address
                client.zip = code_postal
                client.city = ville
                client.diplome = diplome  # attestation capacitév ....
                client.date_cpf = lastupd
                module_id = False
                product_id = False
                template_id = int(self.env['ir.config_parameter'].sudo().get_param(
                    'mcm_cpf_validation.digimoov_email_template_exam_date_center'))
                template_id = self.env['mail.template'].search([('id', '=', template_id)]).id
                if not template_id:
                    template_id = self.env['ir.model.data'].xmlid_to_res_id(
                        'mcm_cpf_validation.digimoov_email_template_exam_date_center', raise_if_not_found=False)
                if not template_id:
                    template_id = self.env['ir.model.data'].xmlid_to_res_id(
                        'mcm_cpf_validation.digimoov_email_template_exam_date_center',
                        raise_if_not_found=False)
                if "digimoov" in str(module):
                    user.write({'company_ids': [1, 2], 'company_id': 2})
                    product_id = self.env['product.template'].sudo().search(
                        [('id_edof', "=", str(module)), ('company_id', "=", 2)], limit=1)
                    if product_id:
                        client.id_edof = product_id.id_edof
                        if template_id:
                            client.with_context(force_send=True).message_post_with_template(template_id,
                                                                                            composition_mode='comment')
                else:
                    user.write({'company_ids': [(4, 2)], 'company_id': 1})
                    product_id = self.env['product.template'].sudo().search(
                        [('id_edof', "=", str(module)), ('company_id', "=", 1)], limit=1)
                    if product_id:
                        client.id_edof = product_id.id_edof


    """Changer statut cpf vers accepté selon l'etat récupéré avec api wedof"""
    def change_statut_accepte(self):
        params_wedof = (
            ('order', 'asc'),
            ('type', 'all'),
            ('state', 'accepted'),
            ('billingState', 'all'),
            ('certificationState', 'all'),
            ('sort', 'lastUpdate'),
            ('limit', '10000000000')
        )
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
            'X-API-KEY': '026514d6bc7d880515a27eae4947bccef4fbbf03',
        }
        response = requests.get('https://www.wedof.fr/api/registrationFolders/', headers=headers,
                                params=params_wedof)
        registrations = response.json()
        for dossier in registrations:
            externalId = dossier['externalId']
            email = dossier['attendee']['email']
            email = email.replace("%", ".")  # remplacer % par .
            email = email.replace(" ", "")  # supprimer les espaces envoyés en paramètre email
            email = str(email).lower()  # recupérer l'email en miniscule pour éviter la création des deux comptes
            print('dossier', dossier)
            idform = dossier['trainingActionInfo']['trainingId']
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
            users = self.env['res.users'].sudo().search([('login', "=", email)])
            # redirect link to generate validate cpf link to create the client with all info of client
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
                print("if user", user.login,user.partner_id.statut_cpf)
                user.partner_id.mode_de_financement = 'cpf'
                user.partner_id.statut_cpf = 'accepted'
                user.partner_id.date_cpf= lastupd
                module_id = False
                product_id = False
                if 'digimoov' in str(training_id):
                    product_id = self.env['product.template'].sudo().search(
                        [('id_edof', "=", str(training_id)), ('company_id', "=", 2)], limit=1)
                else:
                    product_id = self.env['product.template'].sudo().search(
                        [('id_edof', "=", str(training_id)), ('company_id', "=", 1)], limit=1)

                if product_id and product_id.company_id.id == 2 and user.partner_id.id_edof and user.partner_id.date_examen_edof and user.partner_id.session_ville_id:
                    module_id = self.env['mcmacademy.module'].sudo().search(
                        [('company_id', "=", 2), ('session_ville_id', "=", user.partner_id.session_ville_id.id),
                         ('date_exam', "=", user.partner_id.date_examen_edof), ('product_id', "=", product_id.id),
                         ('session_id.number_places_available', '>', 0)], limit=1)
                    if module_id:
                        user.partner_id.module_id = module_id
                        user.partner_id.mcm_session_id = module_id.session_id
                        product_id = self.env['product.product'].sudo().search(
                            [('product_tmpl_id', '=', module_id.product_id.id)])
                        user.partner_id.mcm_session_id = module_id.session_id
                        user.partner_id.module_id = module_id
                        self.env.user.company_id = 2
                        invoice = self.env['account.move'].sudo().search(
                            [('module_id', "=", module_id.id), ('state', "=", 'posted'),
                             ('partner_id', "=", user.partner_id.id)])
                        if not invoice:
                            so = self.env['sale.order'].sudo().create({
                                'partner_id': user.partner_id.id,
                                'company_id': 2,
                            })
                            so.module_id = module_id
                            so.session_id = module_id.session_id

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
                            # prix de la formation dans le devis
                            amount_before_instalment = so.amount_total
                            # so.amount_total = so.amount_total * 0.25
                            for line in so.order_line:
                                line.price_unit = so.amount_total
                            so.action_confirm()
                            ref = False
                            # Creation de la Facture Cpf
                            # Si la facture est de type CPF :  On parse le pourcentage qui est 25 %
                            # methode_payment prend la valeur CPF pour savoir bien qui est une facture CPF qui prend la valeur 25 % par default

                            if so.amount_total > 0 and so.order_line:
                                moves = so._create_invoices(final=True)
                                for move in moves:
                                    move.type_facture = 'interne'
                                    # move.cpf_acompte_invoice= True
                                    # move.cpf_invoice =True
                                    move.methodes_payment = 'cpf'
                                    move.pourcentage_acompte = 25
                                    move.module_id = so.module_id
                                    move.session_id = so.session_id
                                    if so.pricelist_id.code:
                                        move.pricelist_id = so.pricelist_id
                                    move.company_id = so.company_id
                                    move.price_unit = so.amount_total
                                    # move.cpf_acompte_invoice=True
                                    # move.cpf_invoice = True
                                    move.methodes_payment = 'cpf'
                                    move.post()
                                    ref = move.name
                            so.action_cancel()
                            so.unlink()
                            user.partner_id.statut = 'won'

                    elif product_id and product_id.company_id.id == 1 and user.partner_id.id_edof and user.partner_id.date_examen_edof and user.partner_id.session_ville_id:
                        module_id = self.env['mcmacademy.module'].sudo().search(
                            [('company_id', "=", 1), ('session_ville_id', "=", user.partner_id.session_ville_id.id),
                             ('date_exam', "=", user.partner_id.date_examen_edof), ('product_id', "=", product_id.id),
                             ('session_id.number_places_available', '>', 0)], limit=1)
                        if module_id:
                            user.partner_id.module_id = module_id
                            user.partner_id.mcm_session_id = module_id.session_id
                            product_id = self.env['product.product'].sudo().search(
                                [('product_tmpl_id', '=', module_id.product_id.id)])
                            user.partner_id.mcm_session_id = module_id.session_id
                            user.partner_id.module_id = module_id
                            self.env.user.company_id = 1
                            invoice = self.env['account.move'].sudo().search(
                                [('module_id', "=", module_id.id), ('state', "=", 'posted'),
                                 ('partner_id', "=", user.partner_id.id)])
                            if not invoice:
                                so = self.env['sale.order'].sudo().create({
                                    'partner_id': user.partner_id.id,
                                    'company_id': 1,
                                })
                                self.env['sale.order.line'].sudo().create({
                                    'name': product_id.name,
                                    'product_id': product_id.id,
                                    'product_uom_qty': 1,
                                    'product_uom': product_id.uom_id.id,
                                    'price_unit': product_id.list_price,
                                    'order_id': so.id,
                                    'tax_id': product_id.taxes_id,
                                    'company_id': 1
                                })
                                # Enreggistrement des valeurs de la facture
                                # Parser le pourcentage d'acompte
                                # Creation de la fcture étape Finale
                                # Facture comptabilisée
                                so.action_confirm()
                                so.module_id = module_id
                                so.session_id = module_id.session_id
                                moves = so._create_invoices(final=True)
                                for move in moves:
                                    move.type_facture = 'interne'
                                    move.module_id = so.module_id
                                    # move.cpf_acompte_invoice=True
                                    # move.cpf_invoice =True
                                    move.methodes_payment = 'cpf'
                                    move.pourcentage_acompte = 25
                                    move.session_id = so.session_id
                                    move.company_id = so.company_id
                                    move.website_id = 1
                                    for line in move.invoice_line_ids:
                                        if line.account_id != line.product_id.property_account_income_id and line.product_id.property_account_income_id:
                                            line.account_id = line.product_id.property_account_income_id
                                    move.post()
                                so.action_cancel()
                                so.unlink()
                                user.partner_id.statut = 'won'

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
                        ticket = self.env['helpdesk.ticket'].sudo().search([("description", "=", description)])
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
                        ticket = self.env['helpdesk.ticket'].sudo().search([('description', 'ilike', description)])
                        if not ticket:
                            new_ticket = self.env['helpdesk.ticket'].sudo().create(
                                vals)




