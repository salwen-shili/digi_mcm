# -*- coding: utf-8 -*-

import logging
import werkzeug
import odoo
from odoo import http, _
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.exceptions import UserError
from odoo.http import request
from odoo.addons.web.controllers.main import Home
from odoo.addons.web.controllers import main

_logger = logging.getLogger(__name__)


class AuthSignupHome(AuthSignupHome):

    def do_signup(self, qcontext):
        """ Shared helper that creates a res.partner out of a token """
        # Get all the inputs
        values = {key: qcontext.get(key) for key in
                  ('login', 'name', 'firstname', 'lastName', 'password', 'phone', "zip", "city", "voie", "nom_voie",
                   "num_voie", 'street2','question_signup')}
        # Remove spaces and lower cases in login
        values['login'] = values['login'].replace(' ', '').lower()
        # Generate when mandatory fields are empty
        if not values:
            raise UserError(_("Le formulaire n'est pas correctement rempli."))
        # This block of code was commented after fix error in button "s'inscrire" that was disabled
        """if '+33' not in values['phone']:
            phone = values['phone']
            phone = phone[1:]
            phone = '+33' + str(phone)
            values['phone'] = phone"""
        # Generate error when email and confirm email do not have the same value
        # if not qcontext.get('token'):
        #     if values.get('login') != qcontext.get('confirm_email').replace(' ', '').lower():
        #         raise UserError(_("Les emails ne correspondent pas, veuillez les saisir à nouveau."))
        # Concatenate num_voie, voie and nom_voie inti street
        if (values['num_voie'] and values['voie'] and values['nom_voie']):
            values['street'] = values['num_voie'] + " " + values['voie'] + " " + values['nom_voie']
        supported_lang_codes = [code for code, _ in request.env['res.lang'].get_installed()]
        lang = request.context.get('lang', '').split('_')[0]
        if lang in supported_lang_codes:
            values['lang'] = lang
        values['lang'] = 'fr_FR'
        if hasattr(request, 'website'):
            if request.website.id == 2:
                values['company_ids'] = [1, 2]
                values['company_id'] = 2
        # Le step suivant est le questionnaire
        values['step'] = "coordonnées"
        values['notification_type'] = 'email'  # make default notificatication type by email for new users
        # Concatenate first name and last name into name
        if values['firstname'] and values['lastName']:
            values['name'] = values['firstname'] + ' ' + values['lastName']
        # Mettre par défaut France dans le pays
        values['country_id'] = request.env['res.country'].sudo().search([('code', 'ilike', 'FR')]).id
        self._signup_with_values(qcontext.get('token'), values)
        request.env.cr.commit()

    @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()
        qcontext['states'] = request.env['res.country.state'].sudo().search([])
        qcontext['countries'] = request.env['res.country'].sudo().search([])
        qcontext['login'] = str(qcontext.get('login')).replace(' ', '').lower()
        if not qcontext.get('token') and not qcontext.get('signup_enabled'):
            raise werkzeug.exceptions.NotFound()
        # Generate an error when a user already uses this email
        _logger.info("mcm auth signup finded user %s" % (str(qcontext.get("login"))))
        if qcontext.get("login") and qcontext.get("login") != 'none':#check if qcontext of login != none
            if request.env["res.users"].sudo().search(
                    [("login", "=", qcontext.get("login").replace(' ', '').lower())]):
                qcontext["error"] = _("Another user is already registered using this email address.")
        if 'error' not in qcontext :
            res_users = request.env["res.users"]
            user=res_users.find_user_with_phone(qcontext.get("phone"))
            if user :
                qcontext["error"] = _("Another user is already registered using this phone number.")
        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                qcontext['login'] = qcontext['login'].replace(' ', '').lower()
                self.do_signup(qcontext)
                # Send an account creation confirmation email
                if qcontext.get('token'):

                    user_sudo = request.env['res.users'].sudo().search(
                        [('login', "=", qcontext.get('login').replace(' ', '').lower())])
                    template = request.env.ref('auth_signup.mail_template_user_signup_account_created',
                                               raise_if_not_found=False)
                    if user_sudo and template:
                        template.sudo().with_context(
                            lang=user_sudo.lang,
                            auth_login=werkzeug.url_encode({'auth_login': user_sudo.email}),
                        ).send_mail(user_sudo.id, force_send=True)
                    user_sudo = request.env['res.users'].sudo().search(
                        [('login', "=", qcontext.get('login').replace(' ', '').lower())])
                    if user_sudo:
                        user_sudo.street = str(request.website.name)
                kw['login'] = qcontext.get('login').replace(' ', '').lower()
                user_sudo = request.env['res.users'].sudo().search(
                    [('login', "=", qcontext.get('login').replace(' ', '').lower())])
                _logger.info('qcontext1 : %s' % str(qcontext))
                if 'passerelle' in qcontext :
                    _logger.info('passerelle: %s' % str(qcontext.get('passerelle')))
                    _logger.info('user sudo : %s' % str(user_sudo))
                    _logger.info('post qcontext : %s' % str(qcontext))
                    if user_sudo:
                        product_id = request.env['product.product'].sudo().search(
                            [('default_code', "=", "taxi"), ('company_id', "=", 1)], limit=1)
                        if product_id:
                            so = request.env['sale.order'].sudo().create({
                                'partner_id': user_sudo.partner_id.id,
                                'company_id': 1,
                                'website_id': 1
                            })

                            so_line = request.env['sale.order.line'].sudo().create({
                                'name': product_id.name,
                                'product_id': product_id.id,
                                'product_uom_qty': 1,
                                'product_uom': product_id.uom_id.id,
                                'price_unit': product_id.list_price,
                                'order_id': so.id,
                                'tax_id': product_id.taxes_id,
                                'company_id': 1,
                            })
                            if so :
                                kw['redirect'] = 'felicitations'
                    else:
                        _logger.info('kw : %s' % str(kw))
                return self.web_login(*args, **kw)
            except UserError as e:
                qcontext['error'] = e.name or e.value
            except (SignupError, AssertionError) as e:
                if request.env["res.users"].sudo().search(
                        [("login", "=", qcontext.get("login").replace(' ', '').lower())]):
                    qcontext["error"] = _("Another user is already registered using this email address.")
                else:
                    _logger.error("%s", e)
                    # Log signup error
                    if SignupError:
                        _logger.error("name %s", SignupError)
                    # Log assertion error
                    if AssertionError:
                        _logger.error("name %s", AssertionError)
                    qcontext['error'] = _("Could not create a new account.")
        print('token:',qcontext.get('token'))
        print('qcontext1:', qcontext)
        response = request.render('auth_signup.signup', qcontext)
        _logger.info('STATUS %s', response.status_code)
        response.headers['X-Frame-Options'] = 'DENY'
        if response.status_code != 204:
            return response


class Home(Home):

    @http.route('/web/login', type='http', auth="public")
    def web_login(self, redirect=None, **kw):
        login = ""
        if 'login' in request.params:
            request.params['login'] = request.params['login'].replace(' ', '').lower()
            login = request.params['login']
        response = super(Home, self).web_login(redirect=redirect, **kw)
        partner = request.env['res.partner'].sudo().search([('email', "=", login)], limit=1)
        order = request.env['sale.order'].sudo().search([('partner_id', "=", partner.id)], order='create_date desc',
                                                        limit=1)
        order1 = request.website.sale_get_order()
        if redirect and request.website.is_public_user():
            url = '/web/signup?redirect=%s' % (redirect)
            return werkzeug.utils.redirect(url, '301')
        if request.website.id == 1 or request.website.id == 2:
            step = partner.step
            if redirect == '/felicitations':
                response = super(Home, self).web_login(redirect='/felicitations', **kw)
            elif order:
                if step == "document":
                    redirect = '/charger_mes_documents'
                    # response = super(Home, self).web_login(redirect='/charger_mes_documents', **kw)
                elif step == "coordonnées":
                    redirect = '/coordonnees'
                    # response = super(Home, self).web_login(redirect='/coordonnées', **kw)
                elif step == "financement":
                    redirect = '/shop/cart'
                    # response = super(Home, self).web_login(redirect='/shop/cart', **kw)
                elif step == "finish":
                    redirect = '/my'
                    # response = super(Home, self).web_login(redirect='/my', **kw)
            else:

                if request.website.sale_get_order() and not request.website.is_public_user():
                    redirect = '/shop/cart'
                    response = super(Home, self).web_login(redirect='/shop/cart', **kw)
                else:
                    redirect = '/#pricing'
                    response = super(Home, self).web_login(redirect='/#pricing', **kw)

        else:
            response = super(Home, self).web_login(redirect=redirect, **kw)
        # if request.httprequest.method == 'POST':
        #     order = request.website.sale_get_order()
        #     default_code_bolt = False
        #     if order:
        #         for line in order.order_line:
        #             if (line.product_id.default_code=='vtc_bolt'): # check the shop cart if the product choosed is bolt based on default code of product 'vtc_bolt'
        #                 default_code_bolt = True
        #                 request.env.user.partner_id.bolt = True
        #                 mail_compose_message = request.env['mail.compose.message']
        #                 mail_compose_message.fetch_sendinblue_template()
        #                 template_id = request.env['mail.template'].sudo().search([('subject', "=", "Passez votre examen blanc avec MCM ACADEMY X BOLT"),('model_id',"=",'res.partner')],limit=1) # if product of bolt in shop cart we send mail contains link of exam to client. we get the mail template from sendinblue
        #                 print('template :',template_id)
        #                 if template_id:
        #                     message = request.env['mail.message'].sudo().search(
        #                         [('subject', "=", "Passez votre examen blanc avec MCM ACADEMY X BOLT"),
        #                          ('model', "=", 'res.partner'),('res_id',"=",request.env.user.partner_id.id)], limit=1) # check if we have already sent the email
        #                     if not message:
        #                         partner.with_context(force_send=True).message_post_with_template(template_id.id,
        #                                                                                      composition_mode='comment',
        #                                                                                      ) #send the email to client
        #         if default_code_bolt:
        #             survey = request.env['survey.survey'].sudo().search([('title', "=", 'Examen blanc Français')],
        #                                                                 limit=1) # search in survey model for exam with title ' Examen blanc Français'
        #             if survey:
        #                 survey_user = request.env['survey.user_input'].sudo().search(
        #                     [('partner_id', "=", request.env.user.partner_id.id), ('survey_id', '=', survey.id)],
        #                     order='create_date asc', limit=1)
        #                 if not survey_user:
        #                     url = '/survey/start/'+str(survey.access_token) #check if client has not yet passed the exam , we redirect him to the exam
        #                     response = super(Home, self).web_login(redirect=url, **kw)
        #                 if survey_user and survey_user.state == 'new':
        #                     url = '/survey/start/' + str(survey.access_token)
        #                     response = super(Home, self).web_login(redirect=url, **kw)
        #                 if survey_user and survey_user.state == 'skip':
        #                     response = super(Home, self).web_login(
        #                         redirect=str('survey/fill/%s/%s' % (str(survey.access_token), str(survey_user.token))),
        #                         **kw)
        #                 if survey_user and survey_user.state == 'done':
        #                     if survey_user.quizz_passed:
        #                         response = super(Home, self).web_login(redirect='/shop/cart', **kw) #check if client has passed the exam and he succeeded we redirect him to shop cart to continue the process of document and payment
        #                     else:
        #                         response = super(Home, self).web_login(redirect='/bolt ', **kw) #check if client has passed the exam and he failed, we redirect him to bolt page
        return response