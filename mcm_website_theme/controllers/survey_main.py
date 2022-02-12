from odoo import http
from odoo.http import request
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.survey.controllers.main import Survey
from odoo.addons.website_sale.controllers.main import TableCompute
from odoo.addons.website_sale.controllers.main import QueryURL
from odoo.addons.portal.controllers.web import Home
from werkzeug.exceptions import Forbidden, NotFound
from odoo.addons.website.models.ir_http import sitemap_qs2dom
from odoo.addons.payment.controllers.portal import PaymentProcessing
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.tools import groupby as groupbyelem
from odoo.osv.expression import OR
from collections import OrderedDict
from operator import itemgetter
from odoo.exceptions import ValidationError
from odoo import fields, http, SUPERUSER_ID, tools, _
from odoo.osv import expression
from datetime import datetime, date
import werkzeug
import locale
import json
import logging
import requests
from odoo.exceptions import UserError

class Survey(Survey):
    def _get_access_data(self, survey_token, answer_token, ensure_token=True):
        res = super(Survey, self)._get_access_data(survey_token,answer_token,ensure_token)
        order = request.website.sale_get_order()
        default_code_bolt = False
        res['exam_not_passed'] = 'False'
        res['exam_success'] = 'False'
        if order:
            if order.company_id.id == 1:
                if order.order_line:
                    for line in order.order_line:
                        if (line.product_id.default_code=='vtc_bolt'):
                            default_code_bolt = True
                    if default_code_bolt:
                        survey = request.env['survey.survey'].sudo().search([('title', "=", 'Examen blanc Français')],limit=1)
                        if survey:
                            survey_user = request.env['survey.user_input'].sudo().search(
                                [('partner_id', "=", request.env.user.partner_id.id), ('survey_id', '=', survey.id)],
                                order='create_date asc', limit=1)
                            if not survey_user:
                                res['exam_not_passed'] = 'True'
                            if survey_user and survey_user.state == 'new':
                                res['exam_not_passed'] = 'True'

                            if survey_user and survey_user.state == 'done':
                                if survey_user.quizz_passed:
                                    res['exam_success'] = 'True'
        return res

    @http.route('/survey/start/<string:survey_token>', type='http', auth='user', website=True)
    def survey_start(self, survey_token, answer_token=None, email=False, **post):
        """ Start a survey by providing
         * a token linked to a survey;
         * a token linked to an answer or generate a new token if access is allowed;
        """
        access_data = self._get_access_data(survey_token, answer_token, ensure_token=False)
        if access_data['validity_code'] is not True:
            return self._redirect_with_error(access_data, access_data['validity_code'])

        survey_sudo, answer_sudo = access_data['survey_sudo'], access_data['answer_sudo']
        exam_not_passed, exam_success = access_data['exam_not_passed'], access_data['exam_success']
        if not answer_sudo:
            try:
                answer_sudo = survey_sudo._create_answer(user=request.env.user, email=email)
            except UserError:
                answer_sudo = False

        if not answer_sudo:
            try:
                survey_sudo.with_user(request.env.user).check_access_rights('read')
                survey_sudo.with_user(request.env.user).check_access_rule('read')
            except:
                return werkzeug.utils.redirect("/")
            else:
                return request.render("survey.403", {'survey': survey_sudo})

        # Select the right page
        if answer_sudo.state == 'new':  # Intro page
            data = {'survey': survey_sudo, 'answer': answer_sudo, 'page': 0, 'exam_not_passed': exam_not_passed, 'exam_success':exam_success}
            return request.render('survey.survey_init', data)
        else:
            return request.redirect('/survey/fill/%s/%s' % (survey_sudo.access_token, answer_sudo.token))
        
        