# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
import time
import logging
import datetime
import locale
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
            # res.redirect_url = str("https://form.jotform.com/222334146537352")
            # res.redirect_url_text = str("Importer vos documents")
            folder_exist = res.env['documents.folder'].sudo().search(
                [('name', '=', "CERFA")], limit=1)
            if folder_exist:
                folder_name = res.name.split()
                # Get last text element(folder_name) = date exam
                f_name_date = folder_name[-1]
                date = "%d %B %Y"
                locale.setlocale(locale.LC_TIME, str(res.env.user.lang) + '.utf8')
                datetime_object = datetime.datetime.strptime(f_name_date, '%d/%m/%Y')
                f_name = str(datetime_object.strftime(date).title())
                _logger.info('----request f_name ---- %s' % f_name)
                f_name_date_exam = res.env['documents.folder'].sudo().search(
                    [('name', '=', f_name)], limit=1).id
                # if folder CERFA exist
                if f_name_date_exam:
                    # template.folder_id = folder_exist.id
                    res.folder_id = f_name_date_exam
                    _logger.info('----Folder name test Takwa---- %s' % f_name_date_exam)
                else:
                    folder_list = {
                        'name': f_name,
                        'parent_folder_id': folder_exist.id,
                        'company_id': self.env.company.id,
                    }
                    create_folder = self.env['documents.folder'].sudo().create(folder_list)
                    res.folder_id = create_folder
        return res