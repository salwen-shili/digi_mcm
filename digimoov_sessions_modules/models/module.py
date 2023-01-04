# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class Module(models.Model):
    _inherit = "mcmacademy.module"

    date_exam = fields.Date("Date d'examen", copy=False, required=True)  # edit date exam to be required
    ville = fields.Selection(selection=[
        ('bordeaux', 'Bordeaux'),
        ('lille', 'Lille'),
        ('lyon', 'Lyon'),
        ('marseille', 'Marseille'),
        ('nantes', 'Nantes'),
        ('paris', 'Paris'),
        ('strasbourg', 'Strasbourg'),
        ('toulouse', 'Toulouse'),
    ], string='Ville',
        default=lambda self: self.session_id.ville)  # edit default ville of module to get ville of session
