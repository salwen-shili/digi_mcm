# -*- coding: utf-8 -*-

import requests
from datetime import datetime, timedelta, date
from odoo import _
import locale
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, SUPERUSER_ID

import logging

_logger = logging.getLogger(__name__)


class partner(models.Model):
    _inherit = 'res.partner'
    # ajouter champs au modele partner par defaut res.partner ne sont pas des instructors
    supprimerdemoocit = fields.Date("Date de suppression")
    departement = fields.Many2one('res.country.state')
    date_ajout_surMOOCIT = fields.Date(string="Date ajout moocit")
    client = fields.Char()
    est_coach = fields.Boolean(string="est Coach ?", default=False)
    coach = fields.Selection([('coach1', 'Safa'),
                              ('coachh2', 'Sara'),
                              ])
    coach_peda = fields.Many2one('res.partner', string="Coach_Pedagogique", domain=[('est_coach', '=', True)])
    state = fields.Selection([('en_attente', 'En attente'), ('en_formation', 'En Formation'), ('supprimé', 'Supprimé')],
                             required=True, default='en_attente')

    mooc_dernier_coonx = fields.Date()
    mooc_temps_passe = fields.Float()
    date_imortation_stat = fields.Date()

    # desinscrire les cours de formation  VTC a l'apprenant

    def desinscriteVTC(self, partner):
        user = self.env['res.users'].sudo().search([('partner_id', '=', self.id)], limit=1)

        url = "https://formation.mcm-academy.fr/api/bulk_enroll/v1/bulk_enroll"
        payload = {
            'auto_enroll': 'true',
            'email_students': 'false',
            'action': 'unenroll',
            'courses': 'course-v1:Digimoov+reg_vtc_02+2,'
                       'course-v1:Digimoov+dev_com_01+1,'
                       'course-v1:Digimoov+sec_rout_02+2,'
                       'course-v1:Digimoov+ges02+2,'
                       'course-v1:Digimoov+angl_01+1,'
                       'course-v1:Digimoov+fr_02+2',
            'identifiers': self.email,
        }

        header = {
            'Access-Control-Request-Headers': 'authorization',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Bearer 366b7bd572fe9d99d665ccd2a47faa29da262dab'
        }
        resp = requests.request("POST", url, headers=header, data=payload)

    # ajouter les cours de formation taxi a l'apprenant

    def inscriteVTC(self, partner):
        url = "https://formation.mcm-academy.fr/api/bulk_enroll/v1/bulk_enroll"
        payload = {
            'auto_enroll': 'true',
            'email_students': 'false',
            'action': 'enroll',
            'courses': 'course-v1:Digimoov+reg_vtc_02+2,'
                       'course-v1:Digimoov+dev_com_01+1,'
                       'course-v1:Digimoov+sec_rout_02+2,'
                       'course-v1Digimoov+ges02+2,'
                       'course-v1:Digimoov+angl_01+1,'
                       'course-v1:Digimoov+fr_02+2',
            'identifiers': self.email,
        }

        header = {
            'Access-Control-Request-Headers': 'authorization',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Bearer 366b7bd572fe9d99d665ccd2a47faa29da262dab'
        }
        resp = requests.request("POST", url, headers=header, data=payload)

    # desinscrire les cours de formation taxi a l'apprenant

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
                       'course-v1:DIGIMOOV+CN02+2022,'
                       'course-v1:Digimoov+angl_01+1,'
                       'course-v1:Digimoov+fr_02+2',
            'identifiers': self.email,
        }

        header = {
            'Access-Control-Request-Headers': 'authorization',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Bearer 366b7bd572fe9d99d665ccd2a47faa29da262dab'
        }
        resp = requests.request("POST", url, headers=header, data=payload)

    # ajouter les cours de formation taxi a l'apprenant
    def inscriteTaxi(self, partner):
        url = "https://formation.mcm-academy.fr/api/bulk_enroll/v1/bulk_enroll"
        payload = {
            'auto_enroll': 'true',
            'email_students': 'false',
            'action': 'enroll',
            'courses': 'course-v1:Digimoov+t3p_02+2,'
                       'course-v1:Digimoov+reg_taxi_02+2,'
                       'course-v1:Digimoov+sec_rout_02+2,'
                       'course-v1:DIGIMOOV+CN02+2022,'
                       'course-v1:Digimoov+ges02+2,'
                       'course-v1:Digimoov+angl_01+1,'
                       'course-v1:Digimoov+fr_02+2',
            'identifiers': self.email,
        }

        header = {
            'Access-Control-Request-Headers': 'authorization',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Bearer 366b7bd572fe9d99d665ccd2a47faa29da262dab'
        }
        resp = requests.request("POST", url, headers=header, data=payload)

    # ajouter les cours de la conaissance local pour le choix de departement
    def ajoutconnaisancelocalpasdecalais(self, partner):
        url = "https://formation.mcm-academy.fr/api/bulk_enroll/v1/bulk_enroll"
        payload = {
            'auto_enroll': 'true',
            'email_students': 'false',
            'action': 'enroll',
            'courses': 'course-v1:Digimoov+conn_loc_calais_02+2',
            'identifiers': self.email,
        }

        header = {
            'Access-Control-Request-Headers': 'authorization',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Bearer 366b7bd572fe9d99d665ccd2a47faa29da262dab'
        }
        resp = requests.request("POST", url, headers=header, data=payload)

    # ajouter les cours de la conaissance local pour le choix de departement
    def ajoutconnaisancelocalNord(self, partner):
        url = "https://formation.mcm-academy.fr/api/bulk_enroll/v1/bulk_enroll"
        payload = {
            'auto_enroll': 'true',
            'email_students': 'false',
            'action': 'enroll',
            'courses': 'course-v1:Digimoov+conn_loc_nord_02+2',
            'identifiers': self.email,
        }

        header = {
            'Access-Control-Request-Headers': 'authorization',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Bearer 366b7bd572fe9d99d665ccd2a47faa29da262dab'
        }
        resp = requests.request("POST", url, headers=header, data=payload)

    # ajouter les apprenants manuellemnt a partire de  la fiche Client
    def ajoutMoocit_automatique(self):
        for partner in self.env['res.partner'].sudo().search([('statut', "=", "won"),
                                                              ('company_id', '=', 1),
                                                              ('email', "=", 'vikada3017@topyte.com'),
                                                              ('statut_cpf', "!=", "canceled")
                                                              ]):
            _logger.info(partner.name)
            _logger.info(partner.module_id.id)
            today = datetime.today()

            # ajout automatique  des utilsateur sur MOOCit
            # verifier staut de sale
            sale_order = self.env['sale.order'].sudo().search([('partner_id', '=', partner.id),
                                                               ('session_id', '=', partner.mcm_session_id.id),
                                                               ('module_id', '=', partner.module_id.id),
                                                               ('state', '=', 'sale'),
                                                               ], limit=1, order="id desc")
            _logger.info(sale_order.name)
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
            if (count == len(documentss) and count != 0):
                document_valide = True

            _logger.info("document %s" % str(document_valide))

            _logger.info("sale_order %s" % str(sale_order.state))
            # en va changer numero_evalbox avec numero eval ..
            # verifier si la case evalbox est True
            print(partner.numero_evalbox)
            if (partner.numero_evalbox != False):
                # defenir le mode de financement
                if partner.mode_de_financement == "particulier":
                    # verifier si le sale et les documents et satut sont valides
                    if ((sale_order) and (document_valide)):
                        _logger.info('document et sale valide Condition 1 validee')
                        # Vérifier si contrat signé ou non

                        if (sale_order.state == 'sale') and (sale_order.signature):
                            # Si demande de renonce est coché donc l'apprenant est ajouté sans attendre 14jours
                            if (partner.renounce_request):
                                self.ajouter_IOne_MCM(partner)

                            # si non il doit attendre 14jours pour etre ajouté a la platform
                            if not partner.renounce_request and (sale_order.signed_on + timedelta(days=14)) <= today:
                                self.ajouter_IOne_MCM(partner)

                if partner.mode_de_financement == "cpf":
                    _logger.info(partner.mode_de_financement)
                    _logger.info(partner.numero_evalbox)
                    _logger.info(partner.mcm_session_id.date_exam)
                    _logger.info(partner.mcm_session_id.date_exam)
                    if (document_valide) and (partner.mcm_session_id.date_exam) and (
                            partner.mcm_session_id.date_exam > date.today()):

                        if (partner.renounce_request):
                            self.ajouter_IOne_MCM(partner)
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
                                dateDebutSession = datetime.strptime(dateDebutSession_str, '%Y-%m-%dT%H:%M:%S.%fz')
                                if dateDebutSession <= datetime.today():
                                    self.ajouter_IOne_MCM(partner)

    # ajouter les apprenants manuellemnt a partire de  la fiche Client
    def ajoutMoocit_manuelle(self):
        # ajout manuelle  des utilsateur sur MOOCit
        # verifier staut de sale
        sale_order = self.env['sale.order'].sudo().search(
            [('partner_id', '=', self.id),
             ('state', '=', 'sale'),
             ('session_id', '=', self.mcm_session_id.id),
             ('module_id', '=', self.module_id.id),
             ], limit=1, order="id desc")
        # Récupérer les documents et vérifier si ils sont validés ou non
        documents = self.env['documents.document'].sudo().search([('partner_id', '=', self.id)])
        document_valide = False
        count = 0
        for document in documents:
            if (document.state == "validated"):
                count = count + 1
        _logger.info('count %s ' % str(count))
        _logger.info('len %s' % str(len(documents)))
        if (count == len(documents) and count != 0):
            document_valide = True
        else:
            # si les document ne sont  pas valide une notif appartient sur odoo
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Document a verifier :)  '),
                    'message': _('Document a verifier :)'),
                    'sticky': True,
                    'className': 'bg-danger'
                }
            }
        # en va changer numero_evalbox avec numero eval ..
        # verifier si la case evalbox est True
        _logger.info('numeroooooooo %s' % str(self.numero_evalbox))

        if (self.numero_evalbox != False):
            # defenir le mode de financement
            if self.mode_de_financement == "particulier":
                _logger.info('mode_de_financement %s' % str(self.mode_de_financement))

                # verifier si le sale et les documents et satut sont valides
                if ((sale_order) and (document_valide) and (self.statut == "won")):
                    _logger.info('document et sale valide Condition 1 validee %s')
                    # Vérifier si contrat signé ou non

                    if (sale_order.state == 'sale') and (sale_order.signature):
                        # Si demande de renonce est coché donc l'apprenant est ajouté sans attendre 14jours
                        if (self.renounce_request):
                            self.ajouter_IOne_MCM(self)

                        # si non il doit attendre 14jours pour etre ajouté a la platform*
                        today = date.today()
                        if not self.renounce_request and (sale_order.signed_on + timedelta(days=14)) <= today:
                            self.ajouter_IOne_MCM(self)



                else:
                    # si sale order ou bien les document ne sont pas valides  ou bien satut nest pas ganger alors en affiche une alert
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': _(' verifier sale order ou bien signature ou bien staut '),
                            'message': _(' verifier sale order ou bien signature ou bien staut'),
                            'sticky': True,
                            'className': 'bg-danger'
                        }
                    }
            if self.mode_de_financement == "cpf":
                _logger.info(' date exman %s' % str(self.mcm_session_id.date_exam))
                if (document_valide) and (self.mcm_session_id.date_exam) and (
                        self.mcm_session_id.date_exam > date.today()):
                    if (self.renounce_request):
                        self.ajouter_IOne_MCM(self)
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
                            _logger.info(' Donnnnnnne %s')
                            self.ajouter_IOne_MCM(self)


                    else:
                        _logger.info("seesion et date exman")
                        return {
                            'type': 'ir.actions.client',
                            'tag': 'display_notification',
                            'params': {
                                'title': _('Verifier session et date exman:( '),
                                'message': _('Verifier session et date exman:('),
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
                    'title': _('Eval Box Non cocher :)  '),
                    'message': _('Eval Box Non cocher :)'),
                    'sticky': True,
                    'className': 'bg-danger'
                }
            }

    # fonction pour tester si le client en partenriat Avec Bolt ou non Si nn i la va  identifier le Client avec le nom de la company
    def estBolt(self):
        for user in self.env['res.partner'].sudo().search(
                [('company_id', '=', 1), ('client', '=', False),
                 ]):
            # user.bolt = True
            if (user):
                if (user.bolt == True):
                    user.client = 'BOLT'
                    _logger.info(user.client)
                else:
                    user.client = user.company_id.name
                    _logger.info(user.client)

    # ajout d'ione avec test de departement et de module choisit par l'apprenant  et lui affecter aux cours automatiquement
    def ajouter_IOne_MCM(self, partner):
        # Remplacez les paramètres régionaux de l'heure par le paramètre de langue actuel
        # du compte dans odoo
        locale.setlocale(locale.LC_TIME, str(self.env.user.lang) + '.utf8')
        user = self.env['res.users'].sudo().search([('partner_id', '=', self.id)], limit=1)
        partner.password360 = user.password360
        password = user.password360
        url = "https://formation.mcm-academy.fr/user_api/v1/account/registration/"
        payload = {'username': self.name.upper().replace(" ", ""),
                   'email': self.email,
                   'password': password,
                   'terms_of_service': 'true',
                   'name': self.name,
                   'honor_code': 'true'}
        headers = {
            'Access-Control-Request-Headers': 'authorization',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Bearer 366b7bd572fe9d99d665ccd2a47faa29da262dab'
        }
        response = requests.request("POST", url, headers=headers, data=payload)

        _logger.info('user %s' % str(payload))
        _logger.info('existantttttt dejaa %s')
        if (response.status_code == 409):
            for rec in self:
                self.write({'state': 'en_formation'})
            self.inscrit_mcm = date.today()
            partner.lang = 'fr_FR'
            if self.env.su:
                # sending mail in sudo was meant for it being sent from superuser
                selff = self.with_user(SUPERUSER_ID)
                template_id = int(self.env['ir.config_parameter'].sudo().get_param(
                    'mcm_openedx.mail_template_add_Ione_MOOcit'))
                template_id = self.env['mail.template'].search([('id', '=', template_id)]).id
                if not template_id:
                    template_id = self.env['ir.model.data'].xmlid_to_res_id(
                        'mcm_openedx.mail_template_add_Ione_MOOcit',
                        raise_if_not_found=False)
                if not template_id:
                    template_id = self.env['ir.model.data'].xmlid_to_res_id(
                        'mcm_openedx.email_template_add_Ione_MOOcit',
                        raise_if_not_found=False)
                if template_id:
                    partner.with_context(force_send=True).message_post_with_template(template_id,
                                                                                     composition_mode='comment', )

            bolt = self.bolt
            evalbox = self.numero_evalbox
            departement = self.state_id.code
            _logger.info(departement)
            if (partner.module_id.product_id.default_code == "taxi"):
                _logger.info("formation valide")
                if (departement == "59"):
                    self.inscriteTaxi(self)
                    self.ajoutconnaisancelocalNord(self)

                    self.supprimer_sixmoins(self)
                    _logger.info("ajouter a formation taxi car il a choisit et  departement 59")

                elif (departement == "62"):
                    self.inscriteTaxi(self)
                    self.ajoutconnaisancelocalpasdecalais(self)

                    self.supprimer_sixmoins(self)

                else:
                    _logger.info(" appeler ERicc pour realiser un cours")
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': _(' utilisateur digimoov '),
                            'message': _(' utilisateur ne appartient pas a MCM_Academy '),
                            'sticky': True,
                            'className': 'bg-danger'
                        }
                    }
            # Formation à distance VTC-BOLT je doit l'ajouter
            elif (partner.module_id.product_id.default_code == "vtc"):
                _logger.info("client Bolt Formation VTC")
                self.inscriteVTC(self)
                self.supprimer_sixmoins(self)

            elif (partner.module_id.product_id.default_code == "vtc_bolt"):
                if (bolt == True):
                    _logger.info("client Bolt Formation VTC")
                    self.inscriteVTC(self)
                    self.supprimer_sixmoins(self)
            # notification = {
            #     'type': 'ir.actions.client',
            #     'tag': 'display_notification',
            #     'params': {
            #         'title': (' Ajout a ete effectuer avec succeé 🤓 🤓'),
            #         'message': ' Ajout a ete effectuer avec succeé ',
            #         'sticky': False,
            #         'type': 'success'
            #     },
            # }
            # return notification

        elif (response.status_code == 200):
            _logger.info('existantttttt dejaa %s')

    # envoit d'un sms
    def testsms(self, partner):
        if partner.phone:
            phone = str(partner.phone.replace(' ', ''))[-9:]
            phone = '+33' + ' ' + phone[0:1] + ' ' + phone[1:3] + ' ' + phone[3:5] + ' ' + phone[
                                                                                           5:7] + ' ' + phone[
                                                                                                        7:]
            partner.phone = phone
            _logger.info(partner.phone)
        body = "Bonjour %s,  Bienvenu Chez MCM ACADEMY" % (
            partner.name)
        if body:
            sms = self.env['mail.message'].sudo().search(
                [("body", "=", body), ("message_type", "=", 'sms'), ("res_id", "=", partner.id)])
            if not sms:
                composer = self.env['sms.composer'].with_context(
                    default_res_model='res.partner',
                    default_res_ids=partner.id,
                    default_composition_mode='mass',
                ).sudo().create({
                    'body': body,
                    'mass_keep_log': True,
                    'mass_force_send': True,
                })
                composer.action_send_sms()  # send sms of end of exam and waiting for result
            if partner.phone:
                partner.phone = '0' + str(partner.phone.replace(' ', ''))[-9:]

    # supprimer ione le desinscrire des cours sur la platfrom moocit
    def supprimer_IOne_MCM(self):
        departement = self.state_id.code
        _logger.info(departement)
        for rec in self:
            self.write({'state': 'supprimé'})
        if (self.module_id.product_id.default_code == "taxi"):
            self.desinscriteTaxi(self)
        elif (self.module_id.product_id.default_code == "vtc"):
            self.desinscriteVTC(self)

        elif (self.module_id.product_id.default_code == "vtc_bolt"):
            self.desinscriteVTC(self)

    # affecter la date de suppression apres l'ajout de 6 mois

    def supprimer_sixmoins(self, partner):
        partner.supprimerdemoocit = partner.inscrit_mcm + (relativedelta(months=6))
        _logger.info("supprimer aprex 6 mois")

    # ajouter une date de suppression pour les ancien utilsateur avant prod
    def supprimer_avantprod(self):
        for partner in self.env['res.partner'].sudo().search([('company_id', '=', 1),
                                                              ('inscrit_mcm', '!=', False),

                                                              ]):
            if (partner):
                for rec in partner:
                    if (partner.state == "en_attente"):
                        partner.sudo().write({'state': 'en_formation'})
                partner.supprimerdemoocit = partner.inscrit_mcm + (relativedelta(months=6))
                _logger.info("supprimer aprex 6 mois")

    # supprimer ione  automatique le desinscrire des cours sur la platfrom moocit

    def supprimer_automatique(self):
        # chercher dans res.partner la liste de apprennats puis verifier la
        for partner in self.env['res.partner'].sudo().search([('statut', "=", "won"),
                                                              ('company_id', '=', 1),
                                                              ('email', "=", 'vikada3017@topyte.com'),
                                                              ('statut_cpf', "!=", "canceled")
                                                              ]):
            if (partner.supprimerdemoocit == date.today()):
                if (partner.module_id.product_id.default_code == "taxi"):
                    self.desinscriteTaxi(self)
                elif (partner.module_id.product_id.default_code == "vtc"):
                    self.desinscriteVTC(self)
                elif (partner.module_id.product_id.default_code == "vtc_bolt"):
                    self.desinscriteVTC(self)

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
