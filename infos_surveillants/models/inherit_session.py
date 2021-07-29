from odoo import fields, models


class McmacademySessionVille(models.Model):
    _inherit = "mcmacademy.session"
    _description = "Inherit this mcmacademy.session to add List des surveillant(e)s"

    surveillant_id = fields.Many2many('infos.surveillant')
