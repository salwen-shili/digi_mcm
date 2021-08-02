from odoo import fields, models

from odoo import api, fields, models, _
# ce programme est crée Par Mabrouk Seifeddinne le 28/06/2021
# est_intervenant fields boolean c'est le type du contact

class InheritPartner(models.Model) :

    _inherit = "res.partner"
    _description = "Les intervenants"

    est_intervenant = fields.Boolean(default=False)
