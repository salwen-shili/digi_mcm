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
        request.website.generate_idenfy_token()
        user_id = request.uid
        user = request.env['res.users'].sudo().search([('id', "=", user_id)])
        partner = user.partner_id
        return request.render("mcm_contact_documents.mcm_contact_documents_charger_mes_documents_mcm", {'partner_id': partner})