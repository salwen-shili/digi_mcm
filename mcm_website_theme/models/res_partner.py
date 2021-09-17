# -*- coding: utf-8 -*-

from odoo import fields, models, api



class Partner(models.Model):
    _inherit = "res.partner"

    street2 = fields.Char("Complément d'adresse")
    voie = fields.Char("type de voie")
    nom_voie = fields.Char("nom de voie")
    num_voie = fields.Char("num de voie")
    # """multistep = fields.Selection(
    #     [('financement', 'Financement'), ('document', 'Document'), ('validation', 'Validation')])"""
    
    step = fields.Char("step")