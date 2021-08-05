from odoo import fields, models, api


class InheritResPartner(models.Model):
    _inherit = "res.partner"
    _description = "Inherit this class to add list of villes"

    session_ville_id = fields.Many2one('session.ville', string="Liste des villes")
    # add relation with class adress for partner
    salle_id = fields.Many2one('session.adresse.examen', help="Choisir une adresse pour la salle d'examen!")
