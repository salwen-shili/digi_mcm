from odoo import fields, models


class ResCountryState(models.Model):
    _inherit = "res.country.state"

    session_ville_id = fields.Many2one('session.ville', string='Region')
    