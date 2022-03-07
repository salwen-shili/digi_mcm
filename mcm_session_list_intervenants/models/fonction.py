from odoo import api, fields, models, _


class IntervenantFoncrion(models.Model):
    _name = "intervenant.fonction"
    _description = "Fonction"

    name = fields.Char(help="Ajouter une fonction telque : Président, Directeur général, Correcteur...")