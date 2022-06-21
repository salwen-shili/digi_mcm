from odoo import fields, models


class InheritResPartner(models.Model):
    _inherit = "res.partner"

    # This will be added in partner interface to filter if a partner is a supervisor or not.
    est_surveillant = fields.Boolean(default=False)
