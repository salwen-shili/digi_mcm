from odoo import fields, models, api


class Module(models.Model):
    _inherit = "mcmacademy.module"

    session_ville_id = fields.Many2one('session.ville', string="Ville")
    #lier chaque module par une ville