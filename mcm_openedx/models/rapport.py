# -*- coding: utf-8 -*-
import requests
from datetime import datetime, timedelta, date

import stripe

from odoo import models, fields, api, SUPERUSER_ID
from odoo.tools import datetime
import logging

_logger = logging.getLogger(__name__)


class rapport(models.Model):
    _name = 'mcm_openedx.rapport'
    _description = "Rapport Marketing Finance"
    numero_dossier = fields.Char(string="NUMERO_DOSSIER")
    partner_id = fields.Many2one('res.partner')
    name = fields.Char(string="NOM")
    company = fields.Char(string="Company")
    prenom = fields.Char(string="PRENOM")
    montant_formation = fields.Char(string="MONTANT FORMATION")
    statut_dossier = fields.Selection([('untreated', 'Non Traité'),
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
    date_debut_session = fields.Date(string="   DATE DEBUT SESSION")
    acceptedDate = fields.Date(string="   AcceptedDate")
    date_fin_session = fields.Date(string=" DATE FIN SESSION")
    numero_formation = fields.Char(string=" NUMERO FORMATION")
    numero_action = fields.Char(string="  NUMERO ACTION")
    description = fields.Char(string="Description")
    numero_session = fields.Char(string="NUMERO SESSION")
    seller_message = fields.Char(string="Seller_message")
    created = fields.Date(string="Created")
    amount = fields.Char(string="Amount")
    customer_email = fields.Char(string="Customer Email")
    captured = fields.Char(string="Captured")
    type_financement = fields.Selection([('cpf', 'CPF'),
                                         ('stripe', 'Carte Bleu'),
                                         ])

    # add mcm controller
    # add repport
    # add button to update report
    # add comapny filter and Grouped by CPF / Carte bleu
    def rapport_wedof(self):
        print("rapport wedof")

        for existe in self.env['mcm_openedx.rapport'].sudo().search(
                [('customer_email', '!=', False), ('numero_formation', '=', False)]):
            for partner in self.env['res.partner'].search(
                    [('email', '=', existe.customer_email)]):
                sale_order = self.env['sale.order'].sudo().search([('partner_id', '=', partner.id)], limit=1,
                                                                  order="id desc")
                if partner.email == existe.customer_email:
                    existe.company = partner.company_id.name
                    existe.numero_formation = sale_order.order_line.product_id.name
                    existe.numero_action = sale_order.order_line.product_id.id_edof
                    existe.numero_session = sale_order.order_line.product_id.id_edof

                    _logger.info(partner.id)
                    _logger.info("ookokokokokokokokkkkkkkkkkkk")
                    existe.partner_id = partner.id

            if existe.description:
                desc = existe.description.split(" ")
                invoice = desc[0]
                if invoice == "Invoice":
                    existe.browse(existe.id).sudo().unlink()

        companies = self.env['res.company'].sudo().search([('id', "!=", False)])
        print(companies)
        api_key = ""
        for companiess in companies:
            api_key = companiess.wedof_api_key
            headers = {
                'accept': 'application/json',
                'Content-Type': 'application/json',
                'X-API-KEY': api_key,
            }
            params_we = (
                ('order', 'desc'),
                ('type', 'all'),
                ('state', 'accepted'),
                ('billingState', 'all'),
                ('certificationState', 'all'),
                ('sort', 'lastUpdate'),
            )

            data = '{}'
            response = requests.get('https://www.wedof.fr/api/registrationFolders/', headers=headers,
                                    params=params_we)
            registrations = response.json()
            print(registrations)
            _logger.info(response.status_code)
            for dossier in registrations:
                numero_action = dossier['externalId']
                diplome = dossier['trainingActionInfo']['title']
                email = dossier['attendee']['email']
                certificat = dossier['_links']['certification']['name']
                certificat_info = dossier['_links']['certification']['certifInfo']
                date_formation = dossier['trainingActionInfo']['sessionStartDate']
                date_fin_session = dossier['trainingActionInfo']['sessionEndDate']
                """convertir date de formation """
                date_split = date_formation[0:10]
                date_ = datetime.strptime(date_split, "%Y-%m-%d")
                dateFormation = date_.date()
                numero_formation = dossier['trainingActionInfo']['sessionId']
                print("oaoaoaoaooaoa", numero_formation.split("/")[0].split("_", 1)[1])
                count = 0
                today = date.today()
                lastupdatestr = str(dossier['lastUpdate'])
                lastupdate = datetime.strptime(lastupdatestr, '%Y-%m-%dT%H:%M:%S.%fz')
                newformat = "%d/%m/%Y %H:%M:%S"
                lastupdateform = lastupdate.strftime(newformat)
                name = dossier['attendee']['lastName']
                prenom = dossier['attendee']['firstName']
                statut_dossier = dossier['state']
                billingState = dossier['billingState']
                externalId = dossier['externalId']
                montant_formation = dossier['trainingActionInfo']['totalExcl']
                lastupd = datetime.strptime(lastupdateform, "%d/%m/%Y %H:%M:%S")
                acceptedDate = dossier['history']['acceptedDate'].split("T")[0]

                print("statut_dossier", statut_dossier)
                existe = self.env['mcm_openedx.rapport'].sudo().search([('numero_dossier', '=', dossier['externalId'])])

                if not existe:
                    new = self.env['mcm_openedx.rapport'].sudo().create({
                        'customer_email': email,
                        'numero_dossier': externalId,
                        'name': name,
                        'prenom': prenom,
                        'statut_dossier': statut_dossier,
                        'montant_formation': montant_formation,
                        'date_debut_session': date_,
                        'date_fin_session': date_fin_session,
                        'acceptedDate': acceptedDate,
                        'created': acceptedDate,
                        'numero_formation': numero_formation.split("/")[0].split("_", 1)[1],
                        'numero_action': numero_formation.split("/")[0].split("_", 1)[1].split("_20")[0],
                        'numero_session': numero_formation.split("/")[0].split("_", 1)[1].split("_20")[0],
                    })
                    new.type_financement = "cpf"
                    _logger.info(new)

        for existee in self.env['mcm_openedx.rapport'].sudo().search([('numero_dossier', '!=', False)]):
            for partner in self.env['res.partner'].search([('numero_cpf', '!=', False)]):
                if partner.numero_cpf == existee.numero_dossier:
                    if partner.numero_cpf == existee.numero_dossier:
                        existee.company = partner.company_id.name
                        existee.partner_id = partner.id
                        if partner.statut_cpf != "accepted":
                            existee.statut_dossier = partner.statut_cpf

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
