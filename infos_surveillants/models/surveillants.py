from odoo import fields, models


class InheritResPartner(models.Model):
    _name = "infos.surveillant"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Interface pour les surveillants"

    surveillant_id = fields.Many2one('res.partner', string="Nom & Prenom du Surveillant")
    phone = fields.Char(related="surveillant_id.phone")
    email = fields.Char(related="surveillant_id.email")
    active = fields.Boolean('Active', default=True)
