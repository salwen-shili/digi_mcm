import uuid
from odoo import http
from odoo.http import request
from odoo import fields
from datetime import datetime, date, time
from odoo.addons.mcm_website_theme.controllers.main import Routes_Site
from odoo.addons.mcm_contact_documents.controllers.main import CustomerPortal
from odoo.addons.digimoov_sessions_modules.controllers.main import WebsiteSale
import locale
import werkzeug

class IdenfyWebsiteSale(WebsiteSale):
    @http.route(
        ['''/<string:product>/<string:partenaire>/shop/cart''', '''/<string:product>/shop/cart''', '''/shop/cart'''],
        type='http', auth="user", website=True, sitemap=False)
    def cart(self, access_token=None, product=None, revive='', partenaire=None, **post):
        if not request.env.user.lang:
            request.env.user.lang ='fr_FR'
        locale.setlocale(locale.LC_TIME, str(request.env.user.lang) + '.utf8')
        order = request.website.sale_get_order()
        name = http.request.env.user.name
        email = http.request.env.user.email
        order.partner_id.idenfy_document_data_id.status != 'APPROVED' and order.partner_id.check_status(request.website) or ''
        status = order.partner_id.idenfy_document_data_id.status
        if order.partner_id and not request.env.user.has_group('base.group_user') and status in ['APPROVED']:
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
        order = request.website.sale_get_order()
        if not order:
            return request.redirect("/pricing")
        else:
            default_code_bolt = False
            if order.order_line:
                for line in order.order_line:
                    if (line.product_id.default_code=='vtc_bolt'):
                        default_code_bolt = True
                if default_code_bolt:
                    survey = request.env['survey.survey'].sudo().search([('title', "=", 'Examen blanc Français')],
                                                                        limit=1)
                    if survey:
                        print(survey)
                        survey_user = request.env['survey.user_input'].sudo().search(
                            [('partner_id', "=", request.env.user.partner_id.id), ('survey_id', '=', survey.id)],
                            order='create_date asc', limit=1)
                        if not survey_user:
                            # url = 'https://www.mcm-academy.fr/survey/start/'+str(survey.access_token)
                            url = str(survey.public_url)
                            return werkzeug.utils.redirect(url, 301)
                        if survey_user and survey_user.state == 'new':
                            # url = 'https://www.mcm-academy.fr/survey/start/' + str(survey.access_token)
                            url = str(survey.public_url)
                            return werkzeug.utils.redirect(url, 301)
                        if survey_user and survey_user.state == 'skip':
                            return werkzeug.utils.redirect(
                                str('survey/fill/%s/%s' % (str(survey.access_token), str(survey_user.token))), 301)
                        if survey_user and survey_user.state == 'done':
                            if not survey_user.quizz_passed:
                                return werkzeug.utils.redirect('/bolt', 301)
        name = http.request.env.user.name
        email = http.request.env.user.email
        partner_id = http.request.env.user.partner_id
        if not partner_id.check_status(request.website):
            request.website.generate_idenfy_token(user_id=http.request.env.user.id)
            partner_id.idenfy_document_data_id.write({'status':'ACTIVE'})#called because updating status in the idenfy record.
        status = partner_id.idenfy_document_data_id.status
        if partner_id and status and (status != 'APPROVED' or status == 'ACTIVE'):
            if request.website.id == 2:  # id 2 of website in database means website DIGIMOOV
                return http.request.render('mcm_contact_documents.mcm_contact_document_charger_mes_documents', {
                    'email': email, 'name': name, 'partner_id': partner_id, 'ex_warning':'','error_identity': '', 'error_permis': '', 'error_permis_number': '', 'error_domicile': ''})
            elif request.website.id == 1:  # id 1 of website in database means website MCM ACADEMY
                return http.request.render('mcm_contact_documents.mcm_contact_documents_charger_mes_documents_mcm', {
                    'email': email, 'name': name, 'partner_id': partner_id, 'error_identity': '', 'error_permis': '', 'error_permis_number': '', 'error_domicile': ''})
        else:
            return request.redirect("/shop/cart/")