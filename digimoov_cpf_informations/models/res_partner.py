# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class resPartner(models.Model):
    _inherit = "res.partner"

    id_edof = fields.Char('ID Produit en edof')
    date_examen_edof = fields.Date("Date d'examen choisi")
    ville = fields.Selection(selection=[
        ('bordeaux', 'Bordeaux'),
        ('lille', 'Lille'),
        ('lyon', 'Lyon'),
        ('marseille', 'Marseille'),
        ('nantes', 'Nantes'),
        ('paris', 'Paris'),
        ('strasbourg', 'Strasbourg'),
        ('toulouse', 'Toulouse'),
    ], string='Ville')