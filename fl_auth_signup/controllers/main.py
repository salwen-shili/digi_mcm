# -*- coding: utf-8 -*-

import logging
import werkzeug
import odoo
from odoo import http, _
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.web.controllers.main import ensure_db, Home, SIGN_UP_REQUEST_PARAMS
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.exceptions import UserError
from odoo.http import request
from odoo.addons.web.controllers.main import Home
from odoo.addons.web.controllers import main

_logger = logging.getLogger(__name__)


class AuthSignupHome(AuthSignupHome):

    def do_signup(self, qcontext):
        """ Shared helper that creates a res.partner out of a token """
        values = {key: qcontext.get(key) for key in
                  ('login', 'lastName','firstname', 'password', 'phone', "zip", "city", "voie", "nom_voie",
                   "num_voie", 'street2')}
        values['login'] = values['login'].replace(' ', '').lower()
        if not values:
            raise UserError(_("Le formulaire n'est pas correctement rempli."))
        if '+33' not in values['phone']:
            phone = values['phone']
            phone = phone[1:]
            phone = '+33' + str(phone)
            values['phone'] = phone
        # if not qcontext.get('token'):
        #     if values.get('login') != qcontext.get('confirm_email').replace(' ', '').lower():
        #         raise UserError(_("Les emails ne correspondent pas, veuillez les saisir à nouveau."))
        if (values['num_voie'] and values['voie'] and values['nom_voie']):
            values['street'] = values['num_voie'] + " " + values['voie'] + " " + values['nom_voie']
        supported_lang_codes = [code for code, _ in request.env['res.lang'].get_installed()]
        lang = request.context.get('lang', '').split('_')[0]
        if lang in supported_lang_codes:
            values['lang'] = lang
        values['lang'] = 'fr_FR'
        if request.website.id == 2:
            values['company_ids'] = [1, 2]
            values['company_id'] = 2
        #values['step'] = "document"     
        values['step'] = "coordonnées"
        values['notification_type'] = 'email'  # make default notificatication type by email for new users
        if values['firstname'] and values['lastName']:
            values['name'] = values['firstname'] + ' ' + values['lastName']
        values['country_id'] = request.env['res.country'].sudo().search([('code', 'ilike', 'FR')]).id
        self._signup_with_values(qcontext.get('token'), values)
        request.env.cr.commit()

    def get_auth_signup_qcontext(self):
        """ Shared helper returning the rendering context for signup and reset password """
        SIGN_UP_REQUEST_PARAMS.add('phone')
        SIGN_UP_REQUEST_PARAMS.add('lastName')
        SIGN_UP_REQUEST_PARAMS.add('firstname')
        SIGN_UP_REQUEST_PARAMS.add('zip')
        SIGN_UP_REQUEST_PARAMS.add('voie')
        SIGN_UP_REQUEST_PARAMS.add('nom_voie')
        SIGN_UP_REQUEST_PARAMS.add('num_voie')
        SIGN_UP_REQUEST_PARAMS.add('street')
        SIGN_UP_REQUEST_PARAMS.add('street2')
        #add keys to SIGN_UP_REQUEST_PARAMS to get datas from signup form
        qcontext = {k: v for (k, v) in request.params.items() if k in SIGN_UP_REQUEST_PARAMS}
        qcontext.update(self.get_auth_signup_config())
        if not qcontext.get('token') and request.session.get('auth_signup_token'):
            qcontext['token'] = request.session.get('auth_signup_token')
        if qcontext.get('token'):
            try:
                # retrieve the user info (name, login or email) corresponding to a signup token
                token_infos = request.env['res.partner'].sudo().signup_retrieve_info(qcontext.get('token'))
                for k, v in token_infos.items():
                    qcontext.setdefault(k, v)
            except:
                qcontext['error'] = _("Invalid signup token")
                qcontext['invalid_token'] = True
        return qcontext

     

    @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()
        qcontext['states'] = request.env['res.country.state'].sudo().search([])
        qcontext['countries'] = request.env['res.country'].sudo().search([])
        qcontext['login'] = str(qcontext.get('login')).replace(' ', '').lower()
        if not qcontext.get('token') and not qcontext.get('signup_enabled'):
            raise werkzeug.exceptions.NotFound()
        if request.env["res.users"].sudo().search(
                [("login", "=", qcontext.get("login").replace(' ', '').lower())]):
            qcontext["error"] = _("Another user is already registered using this email address.")

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
                return self.web_login(*args, **kw)
            except UserError as e:
                qcontext['error'] = e.name or e.value
            except (SignupError, AssertionError) as e:
                if request.env["res.users"].sudo().search(
                        [("login", "=", qcontext.get("login").replace(' ', '').lower())]):
                    qcontext["error"] = _("Another user is already registered using this email address.")
                else:
                    _logger.error("%s", e)
                    if SignupError:
                        _logger.error("name %s", SignupError)
                    if AssertionError:
                        _logger.error("name %s", AssertionError)
                    qcontext['error'] = _("Could not create a new account.")

        response = request.render('auth_signup.signup', qcontext)
        # response = request.render('mcm_website_theme.mcm_template', qcontext)
        _logger.info('STATUS %s', response.status_code)
        response.headers['X-Frame-Options'] = 'DENY'
        if response.status_code != 204:
            return response
