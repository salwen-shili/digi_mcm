import uuid
from odoo import fields,models,api

class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def _signup_create_user(self, values):
        idenfy_data_obj = self.env['idenfy.data']
        new_user = super(ResUsers, self)._signup_create_user(values)
        website = self.env['website'].get_current_website()
        idenfy_data_obj.search([('partner_id', '=', new_user.partner_id.id)]).unlink()
        idenfy_id = uuid.uuid4().hex[:8]
        req_data = {"clientId": '{}'.format(idenfy_id), 'locale': 'fr', 'documents': ['ID_CARD', 'PASSPORT', 'RESIDENCE_PERMIT'],'tokenType': 'IDENTIFICATION'}
        res = website._idenfy_send_request('token', request_data=req_data)
        idenfy_data_obj.create(
            {
                'type':'other_documents',
                'req_data':req_data,
                'res_data':res,
                'idenfy_id': idenfy_id,
                'token': res.get('authToken', ''),
                'scanref': res.get('scanRef', ''),
                'partner_id':new_user.partner_id.id,
                'website_id':website.id
            }
        )
        dl_idenfy_id = uuid.uuid4().hex[:8]
        dr_req_data = {"clientId": '{}'.format(dl_idenfy_id), 'locale': 'fr', 'documents': ['DRIVER_LICENSE'], 'tokenType': 'IDENTIFICATION',}
        dl_res = website._idenfy_send_request('token', request_data=req_data)
        idenfy_data_obj.create(
            {
                'type': 'licence',
                'req_data': dr_req_data,
                'res_data': dl_res,
                'idenfy_id': dl_idenfy_id,
                'token': dl_res.get('authToken', ''),
                'scanref': dl_res.get('scanRef', ''),
                'partner_id': new_user.partner_id.id,
                'website_id': website.id
            }
        )
    # new_user.partner_id.write({'idenfy_id':idenfy_id,'idenfy_token':res.get('authToken',''),'idenfy_scanref':res.get('scanRef','')})
        return new_user