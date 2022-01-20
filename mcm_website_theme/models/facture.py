from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    stripe_sub_reference = fields.Char("Reference d'abonnement")