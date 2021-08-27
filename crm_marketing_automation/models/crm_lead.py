# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
#
from odoo import api, fields, models,_
import calendar
from datetime import date,datetime
import logging

_logger = logging.getLogger(__name__)

class CRM(models.Model):
    _inherit = "crm.lead"

    num_dossier=fields.Char(string="numéro de dossier",)
    num_tel=fields.Char(string="numéro de téléphone")
    email=fields.Char(string="email")
    mode_de_financement = fields.Selection(selection=[
        ('particulier', 'Personnel'),
        ('cpf', 'Mon Compte Formation, CPF'),
        ('chpf', 'Région Hauts-de-France, CHPF'),
        ('aif', 'Pôle emploi, AIF'),
    ], string='Mode de financement', default="particulier")
    module_id = fields.Many2one('mcmacademy.module')
    mcm_session_id = fields.Many2one('mcmacademy.session')


    #Fonction qui va affecter chaque crm lead à sa fiche client et supprimer les duplications
    def crm_import_data(self):
        leads = self.env['crm.lead'].search([])
        duplicate_lead = []
        for lead in leads:
            num_dossier = lead.num_dossier
            partners = self.env['res.partner'].search([])
            for partner in partners:
                if (partner.numero_cpf) and (partner.numero_cpf == lead.num_dossier):
                    lead.sudo().write({
                        'partner_id': partner,
                        'name': partner.name,
                        'mode_de_financement': 'cpf',
                        'module_id': partner.module_id,
                        'mcm_session_id': partner.mcm_session_id,
                    })
                    print('lead', lead)
            if lead.num_dossier and lead.id not in duplicate_lead:
                duplicates = self.env['crm.lead'].search(
                    [('partner_id', '=', lead.partner_id.id), ('id', '!=', lead.id),
                     ('num_dossier', '=', lead.num_dossier)])
                print(duplicates)
                for dup in duplicates:
                    print("dup", dup)
                    duplicate_lead.append(dup.id)
                    _logger.info("duplicate_contacts", duplicate_lead)
        self.browse(duplicate_lead).unlink()
        leadss = self.env['crm.lead'].search([])
        #faire parcour sur les crm lead et supprimer ceux qui n'ont pas des fiches client
        for lead1 in leadss:
            if not lead1.partner_id:
                _logger.info('lead supprime')
                lead1.unlink()