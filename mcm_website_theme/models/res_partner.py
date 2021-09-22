# -*- coding: utf-8 -*-

from odoo import fields, models, api



class Partner(models.Model):
    _inherit = "res.partner"

    # Ces champs sont utilisés dans le formulaire d'inscription
    street2 = fields.Char("Complément d'adresse")
    voie = fields.Char("type de voie")
    nom_voie = fields.Char("nom de voie")
    num_voie = fields.Char("num de voie")
    # Ce champ est utilisé pour l'espace client
    # À chaque fois que l'on termine une étape, le champ step prends la valeur de l'étape suivante
    step = fields.Char("step")