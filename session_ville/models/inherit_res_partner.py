from odoo import fields, models


class InheritResPartner(models.Model):
    _inherit = "res.partner"

    # lier les clients cpf par une ville
    session_ville_id = fields.Many2one('session.ville', string="Ville")
    # add relation with class adress for partner
    salle_id = fields.Many2one('session.adresse.examen', related='mcm_session_id.session_adresse_examen',
     readonly=True, help="Choisir une adresse pour la salle d'examen!")