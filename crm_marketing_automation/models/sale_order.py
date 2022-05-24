# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
#
from odoo import api, fields, models, _
import calendar
from datetime import date, datetime
import logging
_logger = logging.getLogger(__name__)
class Sale(models.Model):
    _inherit = 'sale.order'

    # @api.model
    # def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
    # 
    #     if self.user_has_groups('crm_marketing_automation.group_bolt'):
    #         domain += [('partner_id.bolt', '=', True)]
    # 
    #     res = super(Sale, self).search_read(domain, fields, offset, limit, order)
    # 
    #     return res

    @api.model
    def create(self, vals):
        res = super(Sale, self).create(vals)
        print('drafttt', vals)
        partner_id = vals['partner_id']
        pricelist_id=vals['pricelist_id']
        product=self.env['product.pricelist'].sudo().search([('id',"=",pricelist_id)])
        if product:
            print("product",product.name,self.order_line)
        partner = self.env['res.partner'].sudo().search([('id', '=', partner_id)], limit=1)
        print('partner', partner)
        if partner and partner.statut_cpf != "validated" and not partner.bolt:
            self.change_stage_lead("Prospection", partner)
            # for so in self.order_line:
            print("order line",self.pricelist_id.name)

        return res
    def write(self, vals):
        record = super(Sale, self).write(vals)
        # Si le contrat a changé d'état
        # on change le statut de l'apprenant dans le lead
        #company = self.partner_id.user_id.company_id.id
        if 'state' in vals:
            if vals['state'] == 'sent':
                partner = self.partner_id
                print('sent', partner)
                print('change statut', partner.mcm_session_id.id, partner.session_id.id)
                if (partner.mcm_session_id.id) and (partner.mcm_session_id.id == self.session_id.id) and not partner.bolt and self.module_id.product_id.default_code != "vtc_bolt":
                    print('contrat signé')
                    self.change_stage_lead("Contrat non Signé", partner)
                if (partner.mcm_session_id.id) and (partner.mcm_session_id.id == self.session_id.id) and (partner.bolt or self.module_id.product_id.default_code == "vtc_bolt"):
                    print('bolt contrat signé')
                    self.change_stage_lead("Bolt-Contrat non Signé", partner)
            if vals['state'] == 'sale':
                partner = self.partner_id
                print('sale', partner)
                print('change statut', partner.mcm_session_id.id, partner.session_id.id)
                if (partner.mcm_session_id.id) and (partner.mcm_session_id.id == self.session_id.id):
                    if not partner.bolt and self.module_id.product_id.default_code != "vtc_bolt":
                        self.change_stage_lead("Contrat Signé", partner)
                    else :

                        """classer les apprenant de bolt"""
                        self.change_stage_lead("Bolt-Contrat Signé", partner)
        return record
    def change_stage_lead(self, statut, partner):
        if partner.name:
            partner.diviser_nom(partner)
        stage = self.env['crm.stage'].sudo().search([("name", "=", _(statut))])
        print('stageeeee', stage)
        if stage:
            lead = self.env['crm.lead'].sudo().search([('partner_id', '=', partner.id)], limit=1)
            if lead and _(lead.stage_id.name) != statut:
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
            if not lead:
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
                lead.partner_id = partner
                lead.mcm_session_id = partner.mcm_session_id if partner.mcm_session_id else False
                lead.module_id = partner.module_id if partner.module_id else False
                lead.company_id = partner.company_id if partner.company_id else False