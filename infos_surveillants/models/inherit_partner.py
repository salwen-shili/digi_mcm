from odoo import fields, models


class InheritResPartner(models.Model):
    _inherit = "res.partner"
    _description = "Les surveillants"

    est_surveillant = fields.Boolean(default=False)
