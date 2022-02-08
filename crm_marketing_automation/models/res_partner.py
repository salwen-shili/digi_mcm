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
        if 'statut' in vals:
            if vals['statut'] == 'canceled':
                self.changestage("Annulé", self)
        if 'statut_cpf' in vals :
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
            if vals['statut_cpf'] == 'accepted':
                """Si statut cpf accepté et n'as pas encore choisi sa ville et sa date 
                 on classe l'apprenant   sous statut  choix date d'examen"""
                if not (self.session_ville_id) or not (self.date_examen_edof):
                    self.changestage("Choix date d'examen - CPF", self)
                else :
                    """Si non on classe l'apprenant   sous statut  accepté"""
                    self.changestage("Accepté",self)
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
                lead.sudo().write({
                    'name': partner.name,
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
                    'company_id':partner.company_id if partner.company_id else False
                })
            if not lead:
                lead = self.env['crm.lead'].sudo().create({
                    'name': partner.name,
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
                    lead.company_id=partner.company_id if partner.company_id else False
    def change_crm_lead_existant(self):
        self.import_data("Plateforme 360")
        partners = self.env['res.partner'].sudo().search([])
        for partner in partners:
            if partner.statut_cpf and (partner.statut_cpf == 'canceled' or partner.statut == 'canceled'):
                self.changestage("Annulé", partner)
            if (partner.statut != 'canceled') and (partner.statut_cpf) and (partner.statut_cpf != 'canceled'):
                date_creation = partner.create_date
                year = date_creation.year
                month = date_creation.month
                if (year > 2020) and (month > 1):
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
                        if sale_order and sale_order.state == "sent":
                            _logger.info('contrat non signé')
                            self.changestage("Contrat non Signé", partner)
                        if sale_order and sale_order.state == "sale":
                            if not document_valide:
                                self.changestage("Contrat Signé", partner)
                            if waiting:
                                self.changestage("Document non Validé", partner)
                            if document_valide:
                                failure = sale_order.failures  # delai de retractation
                                today = date.today()
                                """Si Il n'as pas fait la renonciation au contrat et sur la fiche 
                                 on le classe sous retractation non coché et on doit vérifier la date de signature si n'as
                                     pas depassé 14jours"""
                                if not (partner.renounce_request) and (date_facture) and (date_facture + timedelta(days=14)) > (today):
                                    self.changestage("Rétractation non Coché", partner)
                    """Si mode de financement cpf on doit vérifier seulement l'etat des documents  
                        et la renonciation sur la fiche client """
                    if partner.mode_de_financement == "cpf" and partner.mcm_session_id.date_exam and partner.mcm_session_id.date_exam > date.today():
                        if waiting:
                            self.changestage("Document non Validé", partner)
                        if document_valide and not (partner.renounce_request) and (date_facture)and \
                                (date_facture + timedelta(days=14)) > (today):
                            self.changestage("Rétractation non Coché", partner)
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
        partners = self.env['res.partner'].search([('company_id','=',False)])
        for partner in partners:
                user = self.env['res.users'].sudo().search([('partner_id', '=', partner.id)],limit=1)
                if user and user.company_id.id == 1:
                    _logger.info("parnter_company %s" % user.name)
                    _logger.info("_company %s" % user.company_id)
                    partner.company_id = user.company_id.id
                    # partner.sudo().write({
                    #  'company_id': user.company_id.id
                    # })
                    _logger.info("after add %s" % partner.company_id)
