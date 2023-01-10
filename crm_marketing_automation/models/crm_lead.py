# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
#
from odoo import api, fields, models, _
import calendar
from datetime import date, datetime
import logging
_logger = logging.getLogger(__name__)


class CRM(models.Model):
    _inherit = "crm.lead"
    num_dossier = fields.Char(string="numéro de dossier",)
    num_tel = fields.Char(string="numéro de téléphone")
    email = fields.Char(string="email")
    nom = fields.Char(string="Nom")
    prenom = fields.Char(string="Prénom")
    mode_de_financement = fields.Selection(selection=[
        ('particulier', 'Personnel'),
        ('cpf', 'Mon Compte Formation, CPF'),
        ('chpf', 'Région Hauts-de-France, CHPF'),
        ('aif', 'Pôle emploi, AIF'),
    ], string='Mode de financement')
    module_id = fields.Many2one('mcmacademy.module')
    mcm_session_id = fields.Many2one('mcmacademy.session')
    numero_action = fields.Char(string="Identifiant interne d'action")
    motif=fields.Char(string="Motif de l'archivage")
    conseiller=fields.Char( string="Conseiller", default='Inscription spontanée')
    

    # @api.model
    # def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
    #
    #     if self.user_has_groups('crm_marketing_automation.group_bolt'):
    #         domain += [('partner_id.bolt', '=',True)]
    #
    #     res = super(CRM, self).search_read(domain, fields, offset, limit, order)
    #
    #     return res

    """Affecter les crm lead aux apprenants convenables après l'importation
     Et supression des duplications"""

    def crm_import_data(self):
        _logger.info('------------lead ')
        leads = self.env['crm.lead'].search([])
        duplicate_lead = []
        """chercher la fiche client par num_dossier et 
        attribuer cette fiche au crm lead de meme apprenant"""
        for lead in leads:
            num_dossier = str(lead.num_dossier)
            partners = self.env['res.partner'].search(
                [('numero_cpf', "=", num_dossier)])
            _logger.info('lead %s' % lead.name)
            # for partner in partners:
            # if lead.stage_id.name != "Plateforme 360":
            #     if (partner.numero_cpf) and (partner.numero_cpf == lead.num_dossier):
            #         """Changer statut_cpf des fiches client selon
            #           statut de dossier nsur edof"""
            #         # if lead.stage_id.name == "En formation":
            #         #     partner.statut_cpf = "in_training"
            #         # if "Annulé" in lead.stage_id.name:
            #         #     partner.statut_cpf = "canceled"
            #         # if lead.stage_id.name == "Sortie de formation":
            #         #     partner.statut_cpf = "out_training"
            #         # if lead.stage_id.name == "Facturé":
            #         #     partner.statut_cpf = "bill"
            #         # if lead.stage_id.name == "Service fait déclaré":
            #         #     partner.statut_cpf = "service_declared"
            #         # if "Service fait validé" in lead.stage_id.name:
            #         #     partner.statut_cpf = "service_validated"
            #         # if lead.stage_id.name == "Annulation titulaire":
            #         #     partner.statut_cpf = "canceled"
            # lead.sudo().write({
            #             'partner_id': partner,
            #             'name': partner.name,
            #             'mode_de_financement': 'cpf',
            #             'module_id': partner.module_id,
            #             'mcm_session_id': partner.mcm_session_id,
            #             'company_id': partner.company_id if partner.company_id else False
            #         })
            # _logger.info("lead %s" % lead.name)
            """Supprimer les doublons par num_dossier"""
            if lead.num_dossier and lead.id not in duplicate_lead:
                duplicates = self.env['crm.lead'].search(
                    [('id', '!=', lead.id),
                     ('num_dossier', '=', lead.num_dossier)])
                for dup in duplicates:
                    duplicate_lead.append(dup.id)
                    _logger.info("duplicate_contacts %s" % dup.name)
        self.browse(duplicate_lead).unlink()

    def write(self, vals):
        if 'stage_id' in vals:
            aircall_detail = self.env['call.detail'].sudo().search([("call_contact", "=", self.partner_id.id),
                                                                    ("owner", "!=", False)
                                                                    ], order="create_date asc", limit=1)
            if aircall_detail:
                _logger.info("aircall %s" % str(aircall_detail.owner))
                # if aircall_detail.owner and not self.conseiller:
                #     #_logger.info("consieller")
                #     vals['conseiller'] = str(aircall_detail.owner)
                #     _logger.info("consieller")
        write_result = super(CRM, self).write(vals)
        return write_result

