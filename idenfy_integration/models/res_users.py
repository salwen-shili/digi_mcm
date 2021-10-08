import uuid
from odoo import fields,models,api

class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def _signup_create_user(self, values):
        new_user = super(ResUsers, self)._signup_create_user(values)
        website = self.env['website'].get_current_website()
        idenfy_id = uuid.uuid4().hex[:8]
        res = website._idenfy_send_request('token',request_data={"clientId":'{}'.format(idenfy_id)})
        new_user.partner_id.write({'idenfy_id':idenfy_id,'idenfy_token':res.get('authToken',''),'idenfy_scanref':res.get('scanRef','')})
        return new_user