from odoo import fields,models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    idenfy_token = fields.Char('Idenfy Token')
    idenfy_scanref = fields.Char('Idenfy Scan Ref')
    idenfy_id = fields.Char('Idenfy Id')

    def create(self, vals_list):
        res = super(ResPartner, self).create(vals_list)
        return res