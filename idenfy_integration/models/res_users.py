import uuid
from odoo import fields,models,api

class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def _signup_create_user(self, values):
        new_user = super(ResUsers, self)._signup_create_user(values)
        website = self.env['website'].get_current_website()
        website.generate_idenfy_token(user_id=new_user.id)
        return new_user