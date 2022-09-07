# -*- coding: utf-8 -*-

import requests
from datetime import datetime, timedelta, date
from odoo import _
import locale
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, SUPERUSER_ID
import json
import logging

_logger = logging.getLogger(__name__)


class partner(models.Model):
    _inherit = 'res.partner'
    # Ajouter champs au modeule partner par defaut res.partner ne sont pas des instructors
    supprimerdemoocit = fields.Date("Date de suppression")
    departement = fields.Many2one('res.country.state')
    date_ajout_surMOOCIT = fields.Date(string="Date ajout moocit")
    client = fields.Char()
    est_coach = fields.Boolean(string="est Coach ?", default=False)
    coach = fields.Selection([('coach1', 'Safa'),
                              ('coachh2', 'Sara'),
                              ])
    coach_peda = fields.Many2one('res.partner', track_visibility='onchange', string="Coach_Pedagogique",
                                 domain=[('est_coach', '=', True), ])
    state = fields.Selection([('ancien', 'Ancien iOne'), ('en_attente', 'En attente'), ('en_formation', 'En Formation'),
                              ('supprimé', 'Supprimé')],
                             required=True, default='en_attente', track_visibility='onchange', string="Statut")
    mooc_dernier_coonx = fields.Date()
    mooc_temps_passe_heure = fields.Integer()
    mooc_temps_passe_min = fields.Integer()
    mooc_temps_passe_seconde = fields.Integer()
    date_imortation_stat = fields.Date()

    # Ajouter Des condition pour supprimer apprenant
    # Si absence justifiée  => ne sort pas de la formation
    # Si ajournée + absence sans justification == > Supprimer
    # Si présent  + échec = > Supprimer ==> 100 Euro => Ajouter
    # Si ajournée + Absente = > Supprimer == > 200 Euro => Ajouter
    def reppasage_exman(self):
        for partner in self.env['res.partner'].sudo().search([('company_id', '=', 1)]):
            if (partner.presence == "Présent(e)") and (partner.resultat == "Ajourné(e)"):
                _logger.info(" suppprimer et Repassage 100 EUROOOO")
                partner.state = "supprimé"
                # self.desinscriteVTC(partner)
                # self.desinscriteTaxi(partner)
            if (partner.presence == "Absence justifiée") and (partner.resultat == "Ajourné(e)"):
                _logger.info(" suppprimer et Repassage 200 EUROOOO")
                partner.state = "supprimé"
                # self.desinscriteVTC(partner)
                # self.desinscriteTaxi(partner)
            if (partner.presence == "Absent(e)") and (partner.resultat == "Ajourné(e)"):
                _logger.info("supprimerrrrrrrrrrrr")
                partner.state = "supprimé"
                # self.desinscriteVTC(partner)
                # self.desinscriteTaxi(partner)

    # Supprimer iOne  Resulta = Réussi(e)
    def supp_Réussie(self):
        for partner in self.env['res.partner'].sudo().search([('company_id', '=', 1), ('resultat', "=", "Réussi(e)")]):
            # supprimer l'apprenats en verifiant le module choisit
            partner.state = "supprimé"
            if (partner.module_id.product_id.default_code == "taxi"):
                self.desinscriteTaxi(partner)
                partner.supprimerdemoocit = date.today()
            elif (partner.module_id.product_id.default_code == "vtc"):
                self.desinscriteVTC(partner)
                partner.supprimerdemoocit = date.today()
            elif (partner.module_id.product_id.default_code == "vtc_bolt"):
                self.desinscriteVTC(partner)
                partner.supprimerdemoocit = date.today()

    # Ajout d'une fonction pour filtrer les Anciens iOnes et les supprimer
    def anicen_app(self):
        todays_date = date.today()

        for partner in self.env['res.partner'].sudo().search(
                [('company_id', '=', 1), ('state', '!=', "en_formation")]):
            if partner.create_date.year < todays_date.year:
                if (partner.state != "en_formation") and \
                        (partner.state != "supprimé"):
                    partner.state = "ancien"
                    if (partner.module_id.product_id.default_code == "taxi"):
                        self.desinscriteTaxi(partner)
                        partner.supprimerdemoocit = date.today()
                    elif (partner.module_id.product_id.default_code == "vtc"):
                        self.desinscriteVTC(partner)
                        partner.supprimerdemoocit = date.today()
                    elif (partner.module_id.product_id.default_code == "vtc_bolt"):
                        self.desinscriteVTC(partner)
                        partner.supprimerdemoocit = date.today()

    # Dsinscrire l'apprenant  des cours VTC
    def desinscriteVTC(self, partner):
        user = self.env['res.users'].sudo().search([('partner_id', '=', self.id)], limit=1)
        url = "https://formation.mcm-academy.fr/api/bulk_enroll/v1/bulk_enroll"
        payload = {
            'auto_enroll': 'true',
            'email_students': 'false',
            'action': 'unenroll',
            'courses': 'course-v1:Digimoov+reg_vtc_02+2,'
                       'course-v1:Digimoov+dev_com_02+2,'
                       'course-v1:Digimoov+t3p_02+2,'
                       'course-v1:Digimoov+sec_rout_02+2,'
                       'course-v1:Digimoov+ges02+2,'
                       'course-v1:Digimoov+angl_02+2,'
                       'course-v1:Digimoov+fr_02+2',
            'identifiers': partner.email,
        }

        header = {
            'Access-Control-Request-Headers': 'authorization',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Bearer 366b7bd572fe9d99d665ccd2a47faa29da262dab'
        }

        response = requests.request("POST", url, headers=header, data=payload)
        _logger.info('response.text de linscripstion  ou desincs cour %s' % str(response.text))
        _logger.info('response.status_code de linscripstion  ou desincs cour %s' % str(response.status_code))

    # Ajouter l'apprenant au cours VTC
    def inscriteVTC(self, partner):
        url = "https://formation.mcm-academy.fr/api/bulk_enroll/v1/bulk_enroll"
        payload = {
            'auto_enroll': 'true',
            'email_students': 'false',
            'action': 'enroll',
            'courses': 'course-v1:Digimoov+reg_vtc_02+2,'
                       'course-v1:Digimoov+dev_com_02+2,'
                       'course-v1:Digimoov+sec_rout_02+2,'
                       'course-v1:Digimoov+t3p_02+2,'
                       'course-v1:Digimoov+ges02+2,'
                       'course-v1:Digimoov+angl_02+2,'
                       'course-v1:Digimoov+fr_02+2',
            'identifiers': partner.email,
        }

        header = {
            'Access-Control-Request-Headers': 'authorization',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Bearer 366b7bd572fe9d99d665ccd2a47faa29da262dab'
        }
        response = requests.request("POST", url, headers=header, data=payload)

        _logger.info('response.status_code de linscripstion  ou desincs cour %s' % str(response.text))
        _logger.info('response.status_code de linscripstion  ou desincs cour %s' % str(response.status_code))

    # Desinscrire l'apprenant des cours TAXI
    def desinscriteTaxi(self, partner):
        url = "https://formation.mcm-academy.fr/api/bulk_enroll/v1/bulk_enroll"
        payload = {
            'auto_enroll': 'true',
            'email_students': 'false',
            'action': 'unenroll',
            'courses': 'course-v1:Digimoov+t3p_02+2,'
                       'course-v1:Digimoov+reg_taxi_02+2,'
                       'course-v1:Digimoov+conn_loc_calais_02+2,'
                       'course-v1:Digimoov+conn_loc_nord_02+2,'
                       'course-v1:Digimoov+sec_rout_02+2,'
                       'course-v1:Digimoov+ges02+2,'
                       'course-v1:Digimoov+angl_02+2,'
                       'course-v1:DIGIMOOV+CN02+2022,'
                       'course-v1:Digimoov+fr_02+2',
            'identifiers': partner.email,
        }

        header = {
            'Access-Control-Request-Headers': 'authorization',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Bearer 366b7bd572fe9d99d665ccd2a47faa29da262dab'
        }
        response = requests.request("POST", url, headers=header, data=payload)
        _logger.info('response.text de linscripstion  ou desincs cour %s' % str(response.text))

        _logger.info('response.status_code de linscripstion  ou desincs cour %s' % str(response.status_code))

    # Ajouter l'apprenant au cours de formation taxi
    # Ajouter cours connaisances locale 2022
    def inscriteTaxi(self, partner):
        url = "https://formation.mcm-academy.fr/api/bulk_enroll/v1/bulk_enroll"
        payload = {
            'auto_enroll': 'true',
            'email_students': 'false',
            'action': 'enroll',
            'courses':
                'course-v1:Digimoov+ges02+2,'
                'course-v1:Digimoov+angl_02+2,'
                'course-v1:DIGIMOOV+CN02+2022,'
                'course-v1:Digimoov+reg_taxi_02+2,'
                'course-v1:Digimoov+sec_rout_02+2,'
                'course-v1:Digimoov+t3p_02+2,'
                'course-v1:Digimoov+fr_02+2',
            'identifiers': partner.email,
        }

        header = {
            'Access-Control-Request-Headers': 'authorization',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Bearer 366b7bd572fe9d99d665ccd2a47faa29da262dab'
        }
        response = requests.request("POST", url, headers=header, data=payload)
        _logger.info('response.status_code de linscripstion  ou desincs cour %s' % str(response.status_code))
        _logger.info('response.text de linscripstion  ou desincs cour %s' % str(response.text))

    # Ajouter l'apprenant au cours de conaissance locale département(Pas-de-Calais)
    def ajoutconnaisancelocalpasdecalais(self, partner):
        url = "https://formation.mcm-academy.fr/api/bulk_enroll/v1/bulk_enroll"
        payload = {
            'auto_enroll': 'true',
            'email_students': 'false',
            'action': 'enroll',
            'courses': 'course-v1:Digimoov+conn_loc_calais_02+2',
            'identifiers': partner.email,
        }

        header = {
            'Access-Control-Request-Headers': 'authorization',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Bearer 366b7bd572fe9d99d665ccd2a47faa29da262dab'
        }
        response = requests.request("POST", url, headers=header, data=payload)
        _logger.info('response.text de linscripstion  ou desincs cour %s' % str(response.text))
        _logger.info('response.status_code de linscripstion cour %s' % str(response.status_code))

    # Ajouter l'apprenant au cours de conaissance locale département (Nord)
    def ajoutconnaisancelocalNord(self, partner):
        url = "https://formation.mcm-academy.fr/api/bulk_enroll/v1/bulk_enroll"
        payload = {
            'auto_enroll': 'true',
            'email_students': 'false',
            'action': 'enroll',
            'courses': 'course-v1:Digimoov+conn_loc_nord_02+2',
            'identifiers': partner.email,
        }

        header = {
            'Access-Control-Request-Headers': 'authorization',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Bearer 366b7bd572fe9d99d665ccd2a47faa29da262dab'
        }
        resp = requests.request("POST", url, headers=header, data=payload)
        _logger.info('response.status_code de linscripstion  ou desincs cour %s' % str(resp.status_code))
        _logger.info('response.text de linscripstion  ou desincs cour %s' % str(resp.text))

        # ajouter les apprenants    automatiquememnt a partire de  la fiche Client

    # Ajout automatique apprenant à moocit
    def ajoutMoocit_automatique(self):
        _logger.info(" ajoutMoocit_automatique lors de changement de Evalbox sur fiche client")
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if "localhost" not in str(base_url) and "dev.odoo" not in str(base_url):
            for partner in self.env['res.partner'].sudo().search([('statut', "=", "won"),
                                                                  ('company_id', '=', 1),
                                                                  ('numero_evalbox', '!=', False),
                                                                  ('statut_cpf', "!=", "canceled")
                                                                  ]):
                _logger.info(partner.name)
                _logger.info(partner.module_id.id)
                today = date.today()
                # ajout automatique  des utilsateur sur MOOCit
                # verifier staut de sale
                sale_order = self.env['sale.order'].sudo().search([('partner_id', '=', partner.id),
                                                                   ('session_id', '=', partner.mcm_session_id.id),
                                                                   ('module_id', '=', partner.module_id.id),
                                                                   ('state', '=', 'sale'),
                                                                   ('session_id.date_exam', '>', date.today()),
                                                                   ], limit=1, order="id desc")
                _logger.info(sale_order.name)

                if (partner.numero_evalbox != False):
                    bolt = partner.bolt
                    if (bolt):
                        self.ajouter_IOne_MCM(partner)
                    else:
                        # Récupérer les documents et vérifier si ils sont validés ou non
                        documentss = self.env['documents.document'].sudo().search([('partner_id', '=', partner.id)
                                                                                   ])
                        document_valide = False
                        count = 0
                        for document in documentss:
                            if (document.state == "validated"):
                                count = count + 1
                                _logger.info('valide')
                                _logger.info(document.state)
                        _logger.info('count', count, 'len', len(documentss))
                        if (count == len(documentss) and count != 0 and (bolt == False)):
                            document_valide = True
                        _logger.info("document %s" % str(document_valide))
                        _logger.info("sale_order %s" % str(sale_order.state))
                        # en va changer numero_evalbox avec numero eval ..
                        # verifier si la case evalbox est True
                        print(partner.numero_evalbox)
                        # defenir le mode de financement
                        if partner.mode_de_financement == "particulier":
                            # verifier si le sale et les documents et satut sont valides
                            if ((sale_order) and (document_valide) and (bolt == False)):
                                _logger.info('document et sale valide Condition 1 validee')
                                # Vérifier si contrat signé ou non
                                if (sale_order.state == 'sale') and (sale_order.signature) and (bolt == False):
                                    # Si demande de renonce est coché donc l'apprenant est ajouté sans attendre 14jours
                                    if (partner.renounce_request):
                                        self.ajouter_IOne_MCM(partner)
                                        _logger.info(' tout est valide %s')
                                    # si non il doit attendre 14jours pour etre ajouté a la platform
                                    if not partner.renounce_request and (
                                            sale_order.signed_on + timedelta(days=14)) <= today:
                                        self.ajouter_IOne_MCM(partner)
                                        _logger.info(' tout est valide %s')
                        if partner.mode_de_financement == "cpf":
                            _logger.info(partner.mode_de_financement)
                            _logger.info(partner.numero_evalbox)
                            _logger.info(partner.mcm_session_id.date_exam)
                            _logger.info(partner.mcm_session_id.date_exam)
                            if (document_valide) and (bolt == False) and (partner.mcm_session_id.date_exam) and (
                                    partner.mcm_session_id.date_exam > date.today()):
                                if (partner.renounce_request):
                                    self.ajouter_IOne_MCM(partner)
                                    _logger.info(' tout est valide %s')
                                if not (partner.renounce_request) and partner.numero_cpf:
                                    """chercher le dossier cpf sur wedof pour prendre la date d'ajout"""
                                    headers = {
                                        'accept': 'application/json',
                                        'Content-Type': 'application/json',
                                        'X-API-KEY': partner.company_id.wedof_api_key,
                                    }
                                    responsesession = requests.get(
                                        'https://www.wedof.fr/api/registrationFolders/' + partner.numero_cpf,
                                        headers=headers)
                                    dossier = responsesession.json()
                                    dateDebutSession_str = ""
                                    _logger.info('session %s' % str(dossier))
                                    if "trainingActionInfo" in dossier:
                                        dateDebutSession_str = dossier['trainingActionInfo']['sessionStartDate']
                                        dateDebutSession = datetime.strptime(dateDebutSession_str,
                                                                             '%Y-%m-%dT%H:%M:%S.%fz')
                                        if dateDebutSession <= datetime.today():
                                            self.ajouter_IOne_MCM(partner)
                                            _logger.info(' tout est valide %s')

                # ajouter les apprenants manuellemnt a partire de  la fiche Client

    # Ajout manuelle apprenant à moocit
    def ajoutMoocit_manuelle(self):

        _logger.info(self.company_id)
        print("okkokokookok", self.module_id.name)
        _logger.info(' email utilisateur %s' % str(self.email))
        _logger.info('password360%s' % str(self.password360))
        sale_order = self.env['sale.order'].sudo().search(
            [('partner_id', '=', self.id),
             ('state', '=', 'sale'),
             ('session_id', '=', self.mcm_session_id.id),
             ('module_id', '=', self.module_id.id),
             ], limit=1, order="id desc")
        # On va changer numero_evalbox avec numero eval ..
        # Verifier si la case evalbox est True
        _logger.info('numero %s' % str(self.numero_evalbox))
        if (self.numero_evalbox != False and (self.statut == "won")):
            bolt = self.bolt
            _logger.info('self.numero_evalbox != False ')
            if (bolt):
                self.ajouter_IOne_MCM(self)
                _logger.info('ceci est un client bolt il va etre ajouter ssans verifer les autres conditions ')
            else:
                # Récupérer les documents et vérifier si ils sont validés ou non
                documents = self.env['documents.document'].sudo().search([('partner_id', '=', self.id)])
                document_valide = False
                count = 0
                for document in documents:
                    if (document.state == "validated"):
                        count = count + 1
                _logger.info('count %s ' % str(count))
                _logger.info('len %s' % str(len(documents)))
                if (count == len(documents) and count != 0 and bolt == False):
                    document_valide = True
                else:
                    # si les document ne sont  pas valide une notif appartient sur odoo
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': _('Merci de vérifier les documents !   '),
                            'message': _('Merci de vérifier les documents ! ️'),
                            'sticky': True,
                            'className': 'bg-danger'
                        }
                    }
                # defenir le mode de financement
                if self.mode_de_financement == "particulier":
                    _logger.info('mode_de_financement %s' % str(self.mode_de_financement))
                    # verifier si le sale et les documents et satut sont valides
                    if ((sale_order) and (document_valide) and (self.statut == "won") and (bolt == False)):
                        _logger.info('document et sale valide Condition 1 validee %s')
                        # verifer avec ines statue sale.order
                        if (sale_order.state == 'sale') and (sale_order.signature) and (bolt == False):
                            _logger.info('sale order et signature valide %s')

                            # Si demande de renonce est coché donc l'apprenant est ajouté sans attendre 14jours
                            if (self.renounce_request):
                                self.ajouter_IOne_MCM(self)
                                _logger.info(' tout est valide %s')

                            # si non il doit attendre 14jours pour etre ajouté a la platform*
                            today = date.today()
                            if not self.renounce_request and (sale_order.signed_on + timedelta(days=14)) <= today:
                                self.ajouter_IOne_MCM(self)
                                _logger.info('Tout est valide %s')
                    else:
                        # si sale order ou bien les document ne sont pas valides  ou bien satut nest pas ganger alors en affiche une alert
                        return {
                            'type': 'ir.actions.client',
                            'tag': 'display_notification',
                            'params': {
                                'title': _('Merci de vérifier le contrat de formation !'),
                                'message': _('Merci de vérifier le contrat de formation !'),
                                'sticky': True,
                                'className': 'bg-danger'
                            }
                        }
                if self.mode_de_financement == "cpf":
                    _logger.info(' date exman %s' % str(self.mcm_session_id.date_exam))
                    if (document_valide) and (self.mcm_session_id.date_exam) and (
                            self.mcm_session_id.date_exam > date.today()) and (bolt is False):
                        _logger.info('document valide , date exlan > datetoday , et nest pas bolt %s')
                        if (self.renounce_request):
                            self.ajouter_IOne_MCM(self)
                            _logger.info('tout est valide %s')

                    if not (self.renounce_request) and self.numero_cpf:
                        """chercher le dossier cpf sur wedof pour prendre la date d'ajout"""
                        headers = {
                            'accept': 'application/json',
                            'Content-Type': 'application/json',
                            'X-API-KEY': self.company_id.wedof_api_key,
                        }
                        params_wedof = (
                            ('order', 'desc'),
                            ('type', 'all'),
                            ('state', 'accepted'),
                            ('billingState', 'all'),
                            ('certificationState', 'all'),
                            ('sort', 'lastUpdate'),
                        )
                        responsesession = requests.get(
                            'https://www.wedof.fr/api/registrationFolders/' + self.numero_cpf,
                            headers=headers, params=params_wedof)
                        dossier = responsesession.json()
                        dateDebutSession_str = ""
                        _logger.info('session %s' % str(dossier))
                        if "trainingActionInfo" in dossier:
                            dateDebutSession_str = dossier['trainingActionInfo']['sessionStartDate']
                            _logger.info(' testtt %s')
                            dateDebutSession = datetime.strptime(dateDebutSession_str, '%Y-%m-%dT%H:%M:%S.%fz')
                            _logger.info('dateDebutSession %s' % str(dateDebutSession))
                            print(datetime.today())
                            if dateDebutSession <= datetime.today():
                                self.ajouter_IOne_MCM(self)
                                _logger.info(' tout est valide %s')
                        else:
                            _logger.info("seesion et date exman")
                            return {
                                'type': 'ir.actions.client',
                                'tag': 'display_notification',
                                'params': {
                                    'title': _('Merci de vérifier la date d’examen ? '),
                                    'title': _('Merci de vérifier la date d’examen ? '),
                                    'sticky': True,
                                    'className': 'bg-danger'
                                }
                            }
        else:
            # si les document ne sont  pas valide une notif appartient sur odoo
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Manque numéro d’Evalbox-CMA !'),
                    'sticky': True,
                    'className': 'bg-danger'
                }
            }

    # Vérification client Bolt ou MCM
    def Bolt(self):
        todays_date = date.today()
        for user in self.env['res.partner'].sudo().search(
                [('company_id', '=', 1), ('mcm_session_id.date_exam', '!=', False)
                 ]):
            # user.bolt = True
            if user.mcm_session_id.date_exam.year >= todays_date.year:
                if user.mcm_session_id.date_exam.month >= todays_date.month:
                    if user:
                        if user.bolt is True or (user.module_id.product_id.default_code == "vtc_bolt"):
                            user.client = 'BOLT'
                            user.bolt = True
                            _logger.info('nom de l apprennat est_bolt  %s' % str(user.client))
                            partner.password360 = user.password360
                            password = user.password360
                            _logger.info('password client bolt  %s' % str(user.client))
                            if user.password_evalbox is False:
                                user.password_evalbox = password
                        else:
                            user.client = user.company_id.name
                            _logger.info(user.client)

    # Fonction d'affectation des apprenants à la plateforme et aux cours.
    def ajouter_IOne_MCM(self, partner):
        print(partner)
        _logger.info('E-mail de lapprenant %s' % str(partner.email))
        user = self.env['res.users'].sudo().search([('partner_id', '=', partner.id)], limit=1)
        bolt = partner.bolt
        todays_date = date.today()
        departement = partner.state_id.code
        partner.password360 = user.password360
        password = user.password360
        if (partner.name and partner.email):
            url = "https://formation.mcm-academy.fr/user_api/v1/account/registration/"
            payload = {'username': partner.name.upper().replace(" ", ""),
                       'email': partner.email,
                       'password': password,
                       'terms_of_service': 'true',
                       'name': partner.name,
                       'honor_code': 'true'}
            headers = {
                'Access-Control-Request-Headers': 'authorization',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': 'Bearer 366b7bd572fe9d99d665ccd2a47faa29da262dab'
            }
            response_ajouter_iOne_MCM = requests.request("POST", url, headers=headers, data=payload)
            _logger.info(
                'response_ajouter_iOne_MCM de la fonction ajout ione %s' % str(
                    response_ajouter_iOne_MCM.status_code))
            _logger.info(
                'response_ajouter_iOne_MCM de la fonction ajout ione %s' % str(response_ajouter_iOne_MCM.text))
            _logger.info('user %s' % str(payload))
            if (response_ajouter_iOne_MCM.status_code == 200):
                partner.inscrit_mcm = date.today()
                # The finally__block gets executed no matter if the try block raises any errors or not:

                try:

                    if self.env.su:
                        # sending mail in sudo was meant for it being sent from superuser
                        self = self.with_user(SUPERUSER_ID)
                    if not partner.lang:
                        partner.lang = 'fr_FR'
                    _logger.info('avant email mcm_openedx %s' % str(partner.name))
                    # tester si l'apprenat a deja recu un mail
                    message = self.env['mail.message'].search(
                        [('res_id', "=", partner.id), ('subject', "ilike", "Bienvenue chez MCM Academy")])
                    if not message:
                        template_id = int(self.env['ir.config_parameter'].sudo().get_param(
                            'mcm_openedx.mail_template_add_ione_MOOcit'))
                        template_id = self.env['mail.template'].search([('id', '=', template_id)]).id
                        if not template_id:
                            template_id = self.env['ir.model.data'].xmlid_to_res_id(
                                'mcm_openedx.mail_template_add_ione_MOOcit',
                                raise_if_not_found=False)
                        if not template_id:
                            template_id = self.env['ir.model.data'].xmlid_to_res_id(
                                'mcm_openedx.email_template_add_ione_MOOcit',
                                raise_if_not_found=False)
                        if template_id:
                            partner.with_context(force_send=True).message_post_with_template(template_id,
                                                                                             composition_mode='comment', )

                            _logger.info("E-mail envoyé")
                            _logger.info(partner.email)
                            _logger.info('E-mail envoyé  %s' % str(partner.name))

                            if partner.phone:
                                phone = str(partner.phone.replace(' ', ''))[-9:]
                                phone = '+33' + ' ' + phone[0:1] + ' ' + phone[1:3] + ' ' + phone[3:5] + ' ' + phone[
                                                                                                               5:7] + ' ' + phone[
                                                                                                                            7:]
                                partner.phone = phone
                                _logger.info(partner.phone)
                            body = "Cher(e)  %s, MCM Academy vous informe que vous pouvez desormais commencer votre %s, en utilisant les memes identifiants que sur notre site web. https://formation.mcm-academy.fr/" % (
                                partner.name, partner.module_id.name)
                            if body:
                                sms = self.env['mail.message'].sudo().search(
                                    [("body", "=", body), ("message_type", "=", 'sms'), ("res_id", "=", partner.id)])
                                if not sms:
                                    composer = self.env['sms.composer'].with_context(
                                        default_res_model='res.partner',
                                        default_res_ids=partner.id,
                                        default_composition_mode='comment',
                                    ).sudo().create({
                                        'body': body,
                                        'mass_keep_log': True,
                                        'mass_force_send': True,
                                    })
                                    composer.action_send_sms()  # send sms of end of exam and waiting for result
                                if partner.phone:
                                    partner.phone = '0' + str(partner.phone.replace(' ', ''))[-9:]
                except:
                    _logger.info('E-mail non envoyé')
                finally:
                    partner.inscrit_mcm = date.today()
                    _logger.info('print date.today()')
                    self.write({'state': 'en_formation'})
                    partner.write({'state': 'en_formation'})

                # ajouter une fonction pour connaitre l'utilisateur connecter et lui notifier si il a un nouveau apprenant
                for coach in self.env['mcm_openedx.coach'].sudo().search(
                        [('coach_name', '!=', '')]):
                    context = self._context
                    current_uid = context.get('uid')
                    user = self.env['res.users'].browse(current_uid)
                    print("email", user.email)
                    if user.email == coach.coach_name.email:
                        return {
                            'type': 'ir.actions.client',
                            'tag': 'display_notification',
                            'params': {
                                'title': _('Nouveau iOne sur la plateforme '),
                                'sticky': False,
                                'className': 'bg-danger'
                            }
                        }
                _logger.info('departement %s' % str(departement))
                _logger.info('partner.inscrit_mcm = date.today() affecter date ajout')
                _logger.info('Client ajouter a la platforme staut code 200 %s' % str(partner.email))

                # Formation à distance Taxi
                if (partner.module_id.product_id.default_code == "taxi"):
                    _logger.info("partner.module_id.product_id.default_code")
                    if (departement == "59"):
                        self.inscriteTaxi(partner)
                        self.ajoutconnaisancelocalNord(partner)
                        _logger.info("Departement 59")
                    elif (departement == "62"):
                        self.inscriteTaxi(partner)
                        self.ajoutconnaisancelocalpasdecalais(partner)
                        _logger.info("Departement 62")
                    else:
                        self.inscriteTaxi(partner)
                        _logger.info("Ajouter a formation taxi ")
                # Formation à distance VTC
                elif (partner.module_id.product_id.default_code == "vtc"):
                    _logger.info("Formation VTC")
                    self.inscriteVTC(partner)
                # Formation à distance VTC-BOLT
                elif (partner.module_id.product_id.default_code == "vtc_bolt"):
                    if (bolt == True):
                        _logger.info("Bolt Formation VTC")
                        _logger.info(
                            'Ceci est un client Bolt sans autre condition')
                        self.inscriteVTC(partner)
            if (response_ajouter_iOne_MCM.status_code == 409):
                # voir si statut de l'apprenant en formation ou la date de mise en formation est vide alors mettre la date pour la date.today
                if partner.mcm_session_id.date_exam:
                    if (partner.mcm_session_id.date_exam.year):
                        if (partner.state != 'en_formation' and
                                partner.mcm_session_id.date_exam.year >= todays_date.year):
                            partner.write({'state': 'en_formation'})
                        # Formation à distance Taxi
                        if (partner.module_id.product_id.default_code == "taxi"):
                            _logger.info("partner.module_id.product_id.default_code")
                            if (departement == "59"):
                                self.inscriteTaxi(partner)
                                self.ajoutconnaisancelocalNord(partner)
                                _logger.info("Departement 59")
                            elif (departement == "62"):
                                self.inscriteTaxi(partner)
                                self.ajoutconnaisancelocalpasdecalais(partner)
                                _logger.info("Departement 62")
                            else:
                                self.inscriteTaxi(partner)
                                _logger.info("Ajouter a formation taxi ")
                        # Formation à distance VTC
                        elif (partner.module_id.product_id.default_code == "vtc"):
                            _logger.info("Formation VTC")
                            self.inscriteVTC(partner)
                        # Formation à distance VTC-BOLT
                        elif (partner.module_id.product_id.default_code == "vtc_bolt"):
                            if (bolt == True):
                                _logger.info("Bolt Formation VTC")
                                _logger.info(
                                    'Ceci est un client Bolt sans autre condition')
                                self.inscriteVTC(partner)
                        # Si l'apprenant achete le module de repasage vtc
                        elif partner.module_id.name == "Repassage VTC":
                            _logger.info("Ajouter a Repassage ")
                            self.inscriteVTC(partner)
                        # Si l'apprenant achete le module de repasage vtc
                        elif partner.module_id.name == "Repassage TAXI":
                            _logger.info("Repassage taxi")
                            _logger.info("partner.module_id.product_id.default_code")
                            if (departement == "59"):
                                self.inscriteTaxi(partner)
                                self.ajoutconnaisancelocalNord(partner)
                                _logger.info("Departement 59")
                                _logger.info("Ajouter a Repassage ")

                            elif (departement == "62"):
                                self.inscriteTaxi(partner)
                                self.ajoutconnaisancelocalpasdecalais(partner)
                                _logger.info("Departement 62")
                                _logger.info("Ajouter a Repassage ")

                            else:
                                self.inscriteTaxi(partner)
                                _logger.info("Ajouter a Repassage ")

                # Ajout ticket pour notiifer le service client pour changer mp
                """Créer des tickets contenant le message  d'erreur pour service client  si l'apprenant n'est pas ajouté sur moocit   """
            if (response_ajouter_iOne_MCM.status_code == 400 and partner.state != 'en_formation'):

                _logger.info('Utilisateur  mot de passe invalide %s')
                vals = {
                    'description': 'verifier mot de passe %s' % (partner.name),
                    'name': 'Le mot de passe est trop semblable au champ Email ',
                    'team_id': self.env['helpdesk.team'].sudo().search(
                        [('name', 'like', 'Service Examen MCM'), ('company_id', "=", 1)],
                        limit=1).id,
                }
                description = "test " + str(partner.name)
                ticket = self.env['helpdesk.ticket'].sudo().search(
                    [("description", "=", description)])
                if not ticket:
                    print("cree ticket")
                    new_ticket = self.env['helpdesk.ticket'].sudo().create(
                        vals)

    # Envoyer des e-mails aux apprenants.
    def sendmail(self, partner):
        print(partner.name)
        if partner.company_id.id == 1 and partner.state == "en_formation" and partner.inscrit_mcm != False:
            if self.env.su:
                # sending mail in sudo was meant for it being sent from superuser
                self = self.with_user(SUPERUSER_ID)
            if not partner.lang:
                partner.lang = 'fr_FR'
            _logger.info('avant email mcm_openedx %s' % str(partner.name))
            # tester si l'apprenat a deja recu un mail
            message = self.env['mail.message'].search(
                [('res_id', "=", partner.id), ('subject', "ilike", "Bienvenue chez MCM Academy")])
            if not message:
                template_id = int(self.env['ir.config_parameter'].sudo().get_param(
                    'mcm_openedx.mail_template_add_ione_MOOcit'))
                template_id = self.env['mail.template'].search([('id', '=', template_id)]).id
                if not template_id:
                    template_id = self.env['ir.model.data'].xmlid_to_res_id(
                        'mcm_openedx.mail_template_add_ione_MOOcit',
                        raise_if_not_found=False)
                if not template_id:
                    template_id = self.env['ir.model.data'].xmlid_to_res_id(
                        'mcm_openedx.email_template_add_ione_MOOcit',
                        raise_if_not_found=False)
                if template_id:
                    partner.with_context(force_send=True).message_post_with_template(template_id,
                                                                                     composition_mode='comment', )

                    _logger.info("E-mail envoyé")
                    _logger.info(partner.email)
                    _logger.info('E-mail envoyé  %s' % str(partner.name))

    # Notifier les apprenants
    def notifierapprenant(self):
        if (self.numero_evalbox != False and self.module_id != False and self.state != "supprimé"):
            if self.env.su:
                # sending mail in sudo was meant for it being sent from superuser
                self = self.with_user(SUPERUSER_ID)
            if not self.lang:
                self.lang = 'fr_FR'
            _logger.info('avant email mcm_openedx %s' % str(self.name))
            # tester si l'apprenat a deja recu un mail
            message = self.env['mail.message'].search(
                [('res_id', "=", self.id), ('subject', "ilike", "Bienvenue chez MCM Academy")])
            if not message:
                template_id = int(self.env['ir.config_parameter'].sudo().get_param(
                    'mcm_openedx.mail_template_add_ione_MOOcit'))
                template_id = self.env['mail.template'].search([('id', '=', template_id)]).id
                if not template_id:
                    template_id = self.env['ir.model.data'].xmlid_to_res_id(
                        'mcm_openedx.mail_template_add_ione_MOOcit',
                        raise_if_not_found=False)
                if not template_id:
                    template_id = self.env['ir.model.data'].xmlid_to_res_id(
                        'mcm_openedx.email_template_add_ione_MOOcit',
                        raise_if_not_found=False)
                if template_id:
                    self.with_context(force_send=True).message_post_with_template(template_id,
                                                                                  composition_mode='comment', )

                    _logger.info("email envoyé")
                    _logger.info(self.email)
                    if self.phone:
                        phone = str(self.phone.replace(' ', ''))[-9:]
                        phone = '+33' + ' ' + phone[0:1] + ' ' + phone[1:3] + ' ' + phone[3:5] + ' ' + phone[
                                                                                                       5:7] + ' ' + phone[
                                                                                                                    7:]
                        self.phone = phone
                        _logger.info(self.phone)
                    body = "Cher(e)  %s, MCM Academy vous informe que vous pouvez désormais commencer votre %s, en utilisant les mêmes identifiants que sur notre site web. https://formation.mcm-academy.fr/" % (
                        self.name, self.module_id.name)
                    if body:
                        sms = self.env['mail.message'].sudo().search(
                            [("body", "=", body), ("message_type", "=", 'sms'), ("res_id", "=", self.id)])
                        if not sms:
                            composer = self.env['sms.composer'].with_context(
                                default_res_model='res.partner',
                                default_res_ids=self.id,
                                default_composition_mode='comment',
                            ).sudo().create({
                                'body': body,
                                'mass_keep_log': True,
                                'mass_force_send': True,
                            })
                            composer.action_send_sms()  # send sms of end of exam and waiting for result
                        if self.phone:
                            self.phone = '0' + str(self.phone.replace(' ', ''))[-9:]

                    notification = {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': _('E-mail envoyé avec succès'),
                            'sticky': False,
                            'className': 'success'
                        },
                    }
                    return notification

            else:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('E-mail déjà envoyé'),
                        'sticky': False,
                        'className': 'bg-danger'
                    }
                }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _(' Mail non envoyé  '),
                    'message': _('Manque numéro d’Evalbox-CMA !️'),
                    'sticky': True,
                    'className': 'bg-danger'
                }
            }

    # Suppression d'iOne
    def supprimer_IOne_MCM(self):
        departement = self.state_id.code
        _logger.info(departement)
        # supprimer l'apprenats en verifiant le module choisit
        if (self.module_id.product_id.default_code == "taxi"):
            self.desinscriteTaxi(self)
            self.supprimerdemoocit = date.today()
            self.write({'state': 'supprimé'})
            _logger.info('state: supprimé')


        elif (self.module_id.product_id.default_code == "vtc"):
            self.desinscriteVTC(self)
            self.supprimerdemoocit = date.today()
            self.write({'state': 'supprimé'})
            _logger.info('state: supprimé')


        elif (self.module_id.product_id.default_code == "vtc_bolt"):
            self.desinscriteVTC(self)
            self.supprimerdemoocit = date.today()
            _logger.info('state: supprimé')

        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Merci de vérifier dans Session-module !'),
                    'sticky': True,
                    'className': 'bg-danger'
                }
            }

    # Affecter la date de suppression
    def update_datesupp(self):
        for partner in self.env['res.partner'].sudo().search([('company_id', '=', 1),
                                                              ('inscrit_mcm', '!=', False),
                                                              ('mcm_session_id.date_exam', '!=', False),

                                                              ]):
            if (partner):
                print(partner.mcm_session_id.date_exam)
                for rec in partner:
                    if (partner.state == "en_attente"):
                        partner.sudo().write({'state': 'en_formation'})
                        partner.supprimerdemoocit = partner.mcm_session_id.date_exam + timedelta(days=5)
                        _logger.info("supprimer aprex 5 j")

    # Suppression automatique du iOne
    def supprimer_automatique(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if "localhost" not in str(base_url) and "dev.odoo" not in str(base_url):
            # chercher dans res.partner la liste de apprennats puis verifier la
            for partner in self.env['res.partner'].sudo().search([
                ('company_id', '=', 1)]):
                self.write({'state': 'supprimé'})
                _logger.info("supprimer autooo")

                if (partner.supprimerdemoocit < date.today()):
                    if (partner.module_id.product_id.default_code == "taxi"):
                        self.desinscriteTaxi(partner)
                    elif (partner.module_id.product_id.default_code == "vtc"):
                        self.desinscriteVTC(partner)
                    elif (partner.module_id.product_id.default_code == "vtc_bolt"):
                        self.desinscriteVTC(partner)

    def convertir_date_inscription(self):
        """Convertir date d'inscription de string vers date avec une format %d/%m/%Y"""
        locale.setlocale(locale.LC_TIME, str(self.env.user.lang) + '.utf8')
        for rec in self.env['res.partner'].sudo().search([('statut', "=", "won")]):
            if rec.inscrit_mcm:
                new_date_format = datetime.strptime(str(rec.inscrit_mcm), "%d %B %Y").date().strftime(
                    '%d/%m/%Y')
                rec.inscrit_mcm = new_date_format

            if rec.supprimerdemoocit:
                new_date_format = datetime.strptime(str(rec.supprimerdemoocit), "%d %B %Y").date().strftime('%d/%m/%Y')
                rec.supprimerdemoocit = new_date_format
