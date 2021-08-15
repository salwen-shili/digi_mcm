from odoo import fields, models


class McmacademySessionIntervenant(models.Model):
    _inherit = "mcmacademy.session"
    _description = "Inherit this mcmacademy.session to add List intervenant"

    intervenant_id = fields.Many2many('info.listeintervenants')
