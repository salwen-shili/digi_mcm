# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
#
from odoo import api, fields, models, _
import calendar
import requests
from requests.structures import CaseInsensitiveDict
from datetime import date, datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class Partner(models.Model):
    _inherit = 'res.partner'

    def create(self, vals):

        partner = super(Partner, self).create(vals)
        return partner

    def write(self, vals):

        if 'statut' in vals and self.company_id.id == 2:
            if vals['statut'] == 'canceled':
                self.changestage("Annulé", self)
        if 'statut_cpf' in vals and self.company_id.id == 2:
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
            # Si statut cpf non traité on classe l'apprenant dans le pipeline du crm  sous etat non traité
            if vals['statut_cpf'] == 'untreated':
                self.changestage("Non traité", self)
            # Si statut cpf validé on classe l'apprenant dans le pipeline du crm  sous etat validé
            if vals['statut_cpf'] == 'validated':
                self.changestage("Validé", self)
            # Si statut cpf accepté on classe l'apprenant dans le pipeline du crm  sous statut  accepté
            if vals['statut_cpf'] == 'accepted':
                if not (self.session_ville_id) or not (self.date_examen_edof):
                    self.changestage("Choix date d'examen - CPF", self)
            # Si statut cpf annulé on classe l'apprenant dans le pipeline du crm  sous statut  annulé
            if vals['statut_cpf'] == 'canceled':
                self.changestage("Annulé", self)

        record = super(Partner, self).write(vals)

        return record

    def changestage(self, name, partner):
        stage = self.env['crm.stage'].sudo().search([("name", "=", _(name))])

        if stage:

            lead = self.env['crm.lead'].sudo().search([('partner_id', '=', partner.id)], limit=1)
            if lead:

                num_dossier = ""
                if partner.numero_cpf:
                    num_dossier = partner.numero_cpf
                    lead.num_dossier = num_dossier
                lead.sudo().write({
                    'name': partner.name,
                    'partner_name': partner.name,
                    'num_dossier': num_dossier,
                    'num_tel': partner.phone,
                    'email': partner.email,
                    'email_from': partner.email,
                    'type': "opportunity",
                    'stage_id': stage.id,
                    'mode_de_financement': partner.mode_de_financement,
                    'module_id': partner.module_id if partner.module_id else False,
                    'mcm_session_id': partner.mcm_session_id if partner.mcm_session_id else False,

                })

            if not lead:
                num_dossier = ""
                if partner.numero_cpf:
                    num_dossier = partner.numero_cpf
                print("create lead self", partner)
                lead = self.env['crm.lead'].sudo().create({
                    'name': partner.name,
                    'partner_name': partner.name,
                    'num_dossier': num_dossier,
                    'num_tel': partner.phone,
                    'email': partner.email,
                    'email_from': partner.email,
                    'type': "opportunity",
                    'stage_id': stage.id,
                    'mode_de_financement': partner.mode_de_financement,

                })
                partner = self.env['res.partner'].sudo().search([('id', '=', partner.id)])
                if partner:
                    print("parnterrrr", lead.partner_id)
                    lead.partner_id = partner
                    lead.num_dossier = num_dossier
                    lead.mcm_session_id = partner.mcm_session_id if partner.mcm_session_id else False
                    lead.module_id = partner.module_id if partner.module_id else False

    def change_stage_existant(self):
        self.import_data("Plateforme 360")

        partners = self.env['res.partner'].sudo().search([('company_id.id', '=', 2)])
        for partner in partners:
            if partner.statut_cpf and (partner.statut_cpf == 'canceled' or partner.statut == 'canceled'):
                self.changestage("Annulé", partner)
            if (partner.statut != 'canceled') and (partner.statut_cpf) and (partner.statut_cpf != 'canceled'):
                date_creation = partner.create_date
                year = date_creation.year
                month = date_creation.month
                if (year > 2020) and (month > 1):
                    if partner.statut_cpf == "accepted":
                        if (not (partner.session_ville_id) or not (partner.date_examen_edof)) and not (
                                partner.mcm_session_id) and not (partner.module_id):
                            print('accepté')
                            self.changestage("Choix date d'examen - CPF", partner)
                    # Recuperer le contrat pour vérifier son statut
                    sale_order = self.env['sale.order'].sudo().search([('partner_id', '=', partner.id),
                                                                       ('session_id', '=', partner.mcm_session_id.id),
                                                                       ('module_id', '=', partner.module_id.id),
                                                                       ('session_id.date_exam', '>', date.today()),
                                                                       ], order="date_order desc", limit=1)
                    # Récupérer les documents
                    documents = self.env['documents.document'].sudo().search([('partner_id', '=', partner.id)])
                    # Classer client dans crm lead selon le statut de contrat
                    if sale_order:
                        if sale_order.state == "sent":
                            print('contrat non signé')
                            self.changestage("Contrat non Signé", partner)
                        if sale_order.state == "sale" and not (documents):
                            dateexam = str(sale_order.session_id.date_exam)
                            _logger.info('contrat signé %s', dateexam)
                            self.changestage("Contrat Signé", partner)
                            # vérifier l'existance des document en etat waiting
                            # pour classer sous document dans crm lead
                            if documents and sale_order.state == "sale":
                                waiting = False
                                document_valide = False
                                count = 0
                                for document in documents:
                                    if (document.state == "validated"):
                                        count = count + 1
                                    if (count == len(documents) and count != 0):
                                        document_valide = True
                                    if (document.state == "waiting"):
                                        _logger.info("document waiting")
                                        waiting = True
                                if waiting:
                                    self.changestage("Document non Validé", partner)
                                # Vérifier si ses documents sont validés
                                if document_valide:
                                    # delai de retractation
                                    failure = sale_order.failures
                                    renonciation = partner.renounce_request
                                    date_signature = sale_order.signed_on
                                    today = datetime.today()
                                    # si l'apprenant n'a pas fait une renonce
                                    # On l'ajoute sur etape Retractation non coché
                                    if not (failure) and not (renonciation):
                                        _logger.info('non retracté')
                                        self.changestage("Rétractation non Coché", partner)
                                    # elif (date_signature and (date_signature + timedelta(days=14)) > (today)):
                                    #     _logger.info('non retracté')
                                    #     self.changestage("Rétractation non Coché", partner)

    """Methode pour importation des données à partir de 360"""
    def import_data(self, name):
        """Supprimer les anciens apprenants et les remplacer par les nouveaux importés par api"""
        old_leads = self.env['crm.lead'].sudo().search([('stage_id.name', '=', 'Plateforme 360')])
        if old_leads:
            old_leads.unlink()
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
        partners = self.env['res.partner'].search([])
        for partner in partners:
            if not partner.company_id:
                user = self.env['res.users'].sudo().search([('partner_id', '=', partner.id)], limit=1)
                if user and user.company_id.id == 1:
                    _logger.info("parnter_company %s" % user.name)
                    _logger.info("_company %s" % user.company_id)
                    partner.company_id = user.company_id.id
                    # partner.sudo().write({
                    #  'company_id': user.company_id.id
                    # })
                    _logger.info("after add %s" % partner.company_id)
