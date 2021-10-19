import uuid
from odoo import http
from odoo.http import request
from odoo.addons.mcm_website_theme.controllers.main import Routes_Site
from odoo.addons.mcm_contact_documents.controllers.main import CustomerPortal
from odoo.addons.digimoov_sessions_modules.controllers.main import WebsiteSale

class IdenfyWebsiteSale(WebsiteSale):
    @http.route(
        ['''/<string:product>/<string:partenaire>/shop/cart''', '''/<string:product>/shop/cart''', '''/shop/cart'''],
        type='http', auth="user", website=True, sitemap=False)
    def cart(self, access_token=None, product=None, revive='', partenaire=None, **post):
        order = request.website.sale_get_order()
        if order.partner_id:
            order.partner_id.fetch_document_details_from_idenfy(request.website)
        return super(IdenfyWebsiteSale, self).cart(access_token=access_token, product=product, revive=revive, partenaire=partenaire, **post)


class IdenfyIntegration(Routes_Site):

    @http.route('/update_partner', type='http', auth='user', website=True)
    def update_partner(self, **kw):
        res = super(IdenfyIntegration, self).update_partner(**kw)
        idenfy_data_obj = request.env['idenfy.data']
        user_id = request.uid
        user = request.env['res.users'].sudo().search([('id', "=", user_id)])
        partner = user.partner_id
        idenfy_data_obj.search([('partner_id', '=', partner.id)]).unlink()
        idenfy_id = uuid.uuid4().hex[:8]
        req_data = {"clientId": '{}'.format(idenfy_id), 'locale': 'fr', 'documents': ['ID_CARD', 'PASSPORT', 'RESIDENCE_PERMIT'], 'tokenType': 'IDENTIFICATION'}
        res = request.website._idenfy_send_request('token', request_data=req_data)
        idenfy_data_obj.create(
            {
                'type': 'other_documents',
                'req_data': req_data,
                'res_data': res,
                'idenfy_id': idenfy_id,
                'token': res.get('authToken', ''),
                'scanref': res.get('scanRef', ''),
                'partner_id': partner.id,
                'website_id': request.website.id
            }
        )
        dl_idenfy_id = uuid.uuid4().hex[:8]
        dr_req_data = {"clientId": '{}'.format(dl_idenfy_id), 'locale': 'fr', 'documents': ['PASSPORT','DRIVER_LICENSE'], 'tokenType': 'IDENTIFICATION'}
        dl_res = request.website._idenfy_send_request('token', request_data=req_data)
        idenfy_data_obj.create(
            {
                'type': 'licence',
                'req_data': dr_req_data,
                'res_data': dl_res,
                'idenfy_id': dl_idenfy_id,
                'token': dl_res.get('authToken', ''),
                'scanref': dl_res.get('scanRef', ''),
                'partner_id': partner.id,
                'website_id': request.website.id
            }
        )
        # res = request.website._idenfy_send_request('token', request_data={"clientId": '{}'.format(idenfy_id),'locale':'fr','documents':['ID_CARD','PASSPORT','RESIDENCE_PERMIT'],'tokenType':'IDENTIFICATION','dummyStatus': 'APPROVED'})
        # partner.write({'idenfy_id':idenfy_id,'idenfy_token':res.get('authToken',''),'idenfy_scanref':res.get('scanRef','')})
        return request.render("mcm_contact_documents.mcm_contact_documents_charger_mes_documents_mcm", {'partner_id': partner})

class IdenfyCustomerPortal(CustomerPortal):

    @http.route('/charger_mes_documents', type="http", auth="user", website=True)
    def create_documents_digimoov(self, **kw):
        res = super(IdenfyCustomerPortal, self).create_documents_digimoov(**kw)
        # name = http.request.env.user.name
        # email = http.request.env.user.email
        partner_id = http.request.env.user.partner_id
        # partner_id.idenfy_data_ids
        # res.qcontext['document_token'] = partner_id
        return res