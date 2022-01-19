# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models,api


class Module(models.Model):
    _inherit = "mcmacademy.module"

    date_exam=fields.Date("Date d'examen",copy=False,required=True)
    ville = fields.Selection(selection=[
        ('bordeaux', 'Bordeaux'),
        ('lille', 'Lille'),
        ('lyon', 'Lyon'),
        ('marseille', 'Marseille'),
        ('nantes', 'Nantes'),
        ('paris', 'Paris'),
        ('strasbourg', 'Strasbourg'),
        ('toulouse', 'Toulouse'),
    ], string='Ville', default=lambda self:self.session_id.ville)

    # @api.model
    # def default_get(self, fields):
    #     res = super(Module, self).default_get(fields)
    #     if res['session_id']:
    #         session = self.env['mcmacademy.session'].sudo().search(
    #             [('id', "=", res['session_id'])])
    #         if session :
    #             res['date_exam'] = session.date_exam
    #     return res
