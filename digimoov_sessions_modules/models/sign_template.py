# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, _
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
        res = super(SignRequestTemplate, self).create(vals)
        if "CERFA" in res.name:
            res.redirect_url = str("https://form.jotform.com/222334146537352")
            res.redirect_url_text = str("Importer vos documents")

        folder_exist = self.env['documents.folder'].sudo().search(
            [('name', '=', "CERFA")], limit=1)

        # Create a folder with date exam if not exist in document module to save signed document
        # If folder CERFA exist
        if folder_exist:
            # if folder CERFA exist
            res.folder_id = folder_exist.id
        else:
            folder_list = {
                'name': "CERFA",
                'parent_folder_id': False,
                'company_id': self.env.company.id,
            }
            cerfa_f_name = self.env['documents.folder'].sudo().create(folder_list)
        _logger.info('----Folder name---- %s' % folder_exist)

        folder_name = res.name.split()
        # Get last text element(folder_name) = date exam
        f_name = folder_name[-1]
        f_name_date_exam = self.env['documents.folder'].sudo().search(
            [('name', '=', f_name)], limit=1).id
        if f_name_date_exam:
            res.folder_id.parent_folder_id = f_name_date_exam
        else:
            folder_list = {
                'name': f_name,
                'parent_folder_id': folder_exist.id,
                'company_id': self.env.company.id,
            }
            create_folder = self.env['documents.folder'].sudo().create(folder_list)
            res.folder_id = create_folder
        return res
