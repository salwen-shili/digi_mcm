from odoo import api, fields, models, _

class InheritResCompany(models.Model):
    _inherit = "res.company"

    signature_convocation = fields.Binary('Signature', store=True)