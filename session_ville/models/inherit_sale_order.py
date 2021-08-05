from odoo import fields, models, api


class Sale(models.Model):
    _inherit = "sale.order"

    session_ville_id = fields.Many2one('session.ville', string="Ville")
    # lier le contrat par une ville