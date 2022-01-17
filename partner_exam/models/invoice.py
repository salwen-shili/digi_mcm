# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.tools import datetime, base64
from odoo.exceptions import ValidationError
import requests
from requests.structures import CaseInsensitiveDict
import logging
_logger = logging.getLogger(__name__)


class Facture(models.Model):
    _inherit="account.move"

    """lorsque la facture est créée  on fait la mise à jour 
    de mode de financement sur la vue examen informations """
    @api.model
    def create(self, vals):
        if 'methodes_payment' in vals:
            partner_id=vals['partner_id']
            info_exam = self.env['info.examen'].sudo().search([('partner_id', '=', partner_id)])
            if info_exam:
                 info_exam.mode_de_financement=vals['methodes_payment']
        res = super(Facture, self).create(vals)
        return res

    """lorsque le mode de payment est changé au niveau de facture 
    on fait la mise à jour sur la vue examen informations """
    def write(self, vals):
        if 'methodes_payment' in vals :
            info_exam=self.env['info.examen'].sudo().search([('partner_id','=',self.partner_id.id)])
            if info_exam:
                info_exam.mode_de_financement=vals['methodes_payment']
        # Value in field financement related to field payment in invoice tree view
        for rec in self:
            for partner in self.env['res.partner'].sudo().search([('id', '=', rec.partner_id.id)]):
                if partner and rec.amount_residual == 0:
                    partner.etat_financement_cpf_cb = 'paid'
                else:
                    partner.etat_financement_cpf_cb = 'not_paid'
        record = super(Facture, self).write(vals)
        return record