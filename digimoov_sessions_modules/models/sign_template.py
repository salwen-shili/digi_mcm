# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models,_
import logging

from odoo import fields, models, _, api, http

_logger = logging.getLogger(__name__)



class SignRequestTemplate(models.Model):
    _inherit = "sign.template"

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    @api.model
    def create(self, vals):
        """ Affectation url jotform dans le modéle de cerfa
        lors de creation d'un nouveau modéle cerfa dans sign.template """
        _logger.info("Sign before res %s " % str(vals))
        res = super(SignRequestTemplate, self).create(vals['name'])
        _logger.info("sign model after res %s " % str(res.name))
        if "CREFA" in res.name:
            res.redirect_url = "https://form.jotform.com/222334146537352"
        else:
            res.redirect_url = False
        return res