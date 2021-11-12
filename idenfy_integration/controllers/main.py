import uuid
from odoo import http
from odoo.http import request
from odoo import fields
from datetime import datetime, date, time
from odoo.addons.mcm_website_theme.controllers.main import Routes_Site
from odoo.addons.mcm_contact_documents.controllers.main import CustomerPortal
from odoo.addons.digimoov_sessions_modules.controllers.main import WebsiteSale

class IdenfyWebsiteSale(WebsiteSale):
    @http.route(
        ['''/<string:product>/<string:partenaire>/shop/cart''', '''/<string:product>/shop/cart''', '''/shop/cart'''],
        type='http', auth="user", website=True, sitemap=False)
    def cart(self, access_token=None, product=None, revive='', partenaire=None, **post):
        order = request.website.sale_get_order()
        name = http.request.env.user.name
        email = http.request.env.user.email
        if order.partner_id:
            order.partner_id.fetch_document_details_from_idenfy(request.website)
        if order.partner_id.idenfy_document_data_id and order.partner_id.idenfy_document_data_id.res_data:
            docExpiry = eval(order.partner_id.idenfy_document_data_id.res_data).get('docExpiry', '')
            current_date = fields.Date.today()
            if docExpiry and fields.Date.from_string(docExpiry) < current_date:
                if request.website.id == 2:  # id 2 of website in database means website DIGIMOOV
                    return http.request.render('mcm_contact_documents.mcm_contact_document_charger_mes_documents', {
                        'email': email, 'name': name, 'partner_id': order.partner_id, 'expired_license':'true', 'error_identity': '', 'error_permis': '', 'error_permis_number': '',
                        'error_domicile': ''})
                elif request.website.id == 1:  # id 1 of website in database means website MCM ACADEMY
                    return http.request.render('mcm_contact_documents.mcm_contact_documents_charger_mes_documents_mcm', {
                        'email': email, 'name': name, 'partner_id': order.partner_id,'expired_license':'true', 'error_identity': '', 'error_permis': '', 'error_permis_number': '', 'error_domicile': ''})
        res = super(IdenfyWebsiteSale, self).cart(access_token=access_token, product=product, revive=revive, partenaire=partenaire, **post)
        return res


class IdenfyIntegration(Routes_Site):

    @http.route('/update_partner', type='http', auth='user', website=True)
    def update_partner(self, **kw):
        res = super(IdenfyIntegration, self).update_partner(**kw)
        request.website.generate_idenfy_token()
        user_id = request.uid
        user = request.env['res.users'].sudo().search([('id', "=", user_id)])
        partner = user.partner_id
        return request.render("mcm_contact_documents.mcm_contact_documents_charger_mes_documents_mcm", {'partner_id': partner})

class IdenfyCustomPortal(CustomerPortal):

    @http.route('/charger_mes_documents', type="http", auth="user", website=True)
    def create_documents_digimoov(self, **kw):
        name = http.request.env.user.name
        email = http.request.env.user.email
        partner_id = http.request.env.user.partner_id
        status = partner_id.uploaded_doc_after_check_status(request.website)
        if not partner_id.check_status(request.website):
            request.website.generate_idenfy_token(user_id=http.request.env.user.id)
        if partner_id and status != 'APPROVED':
            if request.website.id == 2:  # id 2 of website in database means website DIGIMOOV
                return http.request.render('mcm_contact_documents.mcm_contact_document_charger_mes_documents', {
                    'email': email, 'name': name, 'partner_id': partner_id, 'ex_warning':'','error_identity': '', 'error_permis': '', 'error_permis_number': '', 'error_domicile': ''})
            elif request.website.id == 1:  # id 1 of website in database means website MCM ACADEMY
                return http.request.render('mcm_contact_documents.mcm_contact_documents_charger_mes_documents_mcm', {
                    'email': email, 'name': name, 'partner_id': partner_id, 'error_identity': '', 'error_permis': '', 'error_permis_number': '', 'error_domicile': ''})
        else:
            return request.redirect("/shop/cart/")