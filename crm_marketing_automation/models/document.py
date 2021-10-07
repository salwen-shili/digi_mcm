
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
#
from odoo import api, fields, models, _
import calendar
from datetime import date, datetime
import logging
_logger = logging.getLogger(__name__)
class Document(models.Model):
    _inherit = 'documents.document'
    def write(self, vals):
        _logger.info(' write ')
        if 'state' in vals and not ('partner_id' in vals):
            if vals['state'] == 'waiting':
                partner = self.partner_id
                _logger.info('if state in write  %s' % partner.name)
                self.change_stage_lead("Document non Validé", partner)
        if 'state' in vals and 'partner_id' in vals:
            if vals['state'] == 'waiting':
                partner = vals['partner_id']
                self.change_stage_lead("Document non Validé", partner)
        if not ('state' in vals) and 'partner_id' in vals:
            if self.state == 'waiting':
                partner = vals['partner_id']
                self.change_stage_lead("Document non Validé", partner)
        record = super(Document, self).write(vals)
        return record
    def change_stage_lead(self, statut, partner):
        stage = self.env['crm.stage'].sudo().search([("name", "=", _(statut))])
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
                    'company_id': partner.company_id if partner.company_id else False
                })
            if not lead:
                lead = self.env['crm.lead'].sudo().create({
                    'name': partner.name,
                    'partner_name': partner.name,
                    'num_dossier': partner.numero_cpf if partner.numero_cpf else "",
                    'email': partner.email,
                    'email_from': partner.email,
                    'type': "opportunity",
                    'stage_id': stage.id,
                    'mode_de_financement': partner.mode_de_financement,
                })
                lead.partner_id = partner.id
                lead.mcm_session_id = partner.mcm_session_id if partner.mcm_session_id else False
                lead.module_id = partner.module_id if partner.module_id else False
                lead.company_id = partner.company_id if partner.company_id else False
