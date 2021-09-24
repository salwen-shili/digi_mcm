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
    ], string='Mode de financement')
    module_id = fields.Many2one('mcmacademy.module')
    mcm_session_id = fields.Many2one('mcmacademy.session')
    """Affecter les crm lead aux apprenants convenables après l'importation
     Et supression des duplications"""
    def crm_import_data(self):
        _logger.info('------------lead ')
        leads = self.env['crm.lead'].search([])
        duplicate_lead = []
        for lead in leads:
            num_dossier = lead.num_dossier
            partners = self.env['res.partner'].search([('company_id.id', '=', 2)])
            for partner in partners:
                if lead.stage_id.name != "Plateforme 360":
                    if (partner.numero_cpf) and (partner.numero_cpf == lead.num_dossier):
                        """Changer statut_cpf des fiches client selon
                          statut de dossier nsur edof"""
                        # if lead.stage_id.name == "En formation":
                        #     partner.statut_cpf = "in_training"
                        # if "Annulé" in lead.stage_id.name:
                        #     partner.statut_cpf = "canceled"
                        # if lead.stage_id.name == "Sortie de formation":
                        #     partner.statut_cpf = "out_training"
                        # if lead.stage_id.name == "Facturé":
                        #     partner.statut_cpf = "bill"
                        # if lead.stage_id.name == "Service fait déclaré":
                        #     partner.statut_cpf = "service_declared"
                        # if "Service fait validé" in lead.stage_id.name:
                        #     partner.statut_cpf = "service_validated"
                        # if lead.stage_id.name == "Annulation titulaire":
                        #     partner.statut_cpf = "canceled"
                        lead.sudo().write({
                            'partner_id': partner,
                            'name': partner.name,
                            'mode_de_financement': 'cpf',
                            'module_id': partner.module_id,
                            'mcm_session_id': partner.mcm_session_id,
                        })
                        _logger.info("lead %s" % lead.name)
            if lead.num_dossier and lead.id not in duplicate_lead:
                duplicates = self.env['crm.lead'].search(
                    [('id', '!=', lead.id),
                     ('num_dossier', '=', lead.num_dossier)])
                print(duplicates)
                for dup in duplicates:
                    print("dup", dup)
                    duplicate_lead.append(dup.id)
                    _logger.info("duplicate_contacts %s" % dup.name)
        self.browse(duplicate_lead).unlink()
        _logger.info('supprimé')
        new_leads = self.env['crm.lead'].search([])