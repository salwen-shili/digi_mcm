import uuid
from odoo import http
from odoo.http import request
from odoo.addons.mcm_website_theme.controllers.main import Routes_Site


class IdenfyIntegration(Routes_Site):

    @http.route('/update_partner', type='http', auth='user', website=True)
    def update_partner(self, **kw):
        res = super(IdenfyIntegration, self).update_partner(**kw)
        user_id = request.uid
        partner = request.env['res.users'].sudo().search([('id', "=", user_id)]).partner_id
        idenfy_id = uuid.uuid4().hex[:8]
        res = request.website._idenfy_send_request('token', request_data={"clientId": '{}'.format(idenfy_id)})
        partner.write({'idenfy_id':idenfy_id,'idenfy_token':res.get('authToken',''),'idenfy_scanref':res.get('scanRef','')})
        return request.render("mcm_contact_documents.mcm_contact_documents_charger_mes_documents_mcm", {'partner_id': partner})
        # vals = {}
        # partner.sudo().write(vals)
        #need to generate token

        # vals = {}
        # vals['lastName'] = kw.get("lastName")
        # vals['firstname'] = kw.get("firstname")
        # vals['zip'] = kw.get("zip")
        # vals['city'] = kw.get("city")
        # vals['street2'] = kw.get("street2")
        # vals['phone'] = kw.get("phone")
        # vals['street'] = kw.get("num_voie") + " " + kw.get("voie") + " " + kw.get("nom_voie")
        # user_id = request.uid
        # partner = request.env['res.users'].sudo().search([('id', "=", user_id)]).partner_id
        # partner.sudo().write(vals)
        # return res

