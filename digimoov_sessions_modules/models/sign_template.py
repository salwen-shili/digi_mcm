# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models,_
import logging

from odoo import fields, models, _, api, http

_logger = logging.getLogger(__name__)


class SignRequestTemplate(models.Model):
    _inherit = "sign.template"

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    def write(self, values):
        """ """
        res = super(SignRequestTemplate, self).write(values)
        if 'name':
            folder_exist = self.env['documents.folder'].sudo().search(
                [('name', '=', "CERFA")], limit=1)
            if not folder_exist:
                n_folder_list = {
                    'name': "CERFA",
                }
                create_folder = self.env['documents.folder'].sudo().create(n_folder_list)
                self.folder_id = create_folder
                _logger.info('----Folder name---- %s' % self.folder_id.parent_folder_id)
        return res

    @api.model
    def create(self, vals):
        """ Affectation url jotform dans le modéle de cerfa
        lors de creation d'un nouveau modéle cerfa dans sign.template """
        res = super(SignRequestTemplate, self).create(vals)
        if "CERFA" in res.name:
            res.redirect_url = str("https://form.jotform.com/222334146537352")
            res.redirect_url_text = str("Importer vos documents")
        if res.name:
            _logger.info('----Folder name test Takwa---- %s' % res.folder_id.name)
        return res