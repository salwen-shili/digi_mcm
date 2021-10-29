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
        #Get all the inputs
        values = {key: qcontext.get(key) for key in ('login', 'name', 'firstname', 'lastName','password', 'phone', "zip", "city", "voie", "nom_voie",
            "num_voie",'street2')}
        #Remove spaces and lower cases in login
        values['login'] = values['login'].replace(' ', '').lower()
        #Generate when mandatory fields are empty
        if not values:
            raise UserError(_("Le formulaire n'est pas correctement rempli."))
        #This block of code was commented after fix error in button "s'inscrire" that was disabled
        """if '+33' not in values['phone']:
            phone = values['phone']
            phone = phone[1:]
            phone = '+33' + str(phone)
            values['phone'] = phone"""
        #Generate error when email and confirm email do not have the same value
        if values.get('login') != qcontext.get('confirm_email'):
            raise UserError(_("Les emails ne correspondent pas, veuillez les saisir à nouveau."))
        #Concatenate num_voie, voie and nom_voie inti street
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
        #Le step suivant est le questionnaire
        values['step'] = "coordonnées"
        values['notification_type'] = 'email'  # make default notificatication type by email for new users
        #Concatenate first name and last name into name
        if values['firstname'] and values['lastName']:
            values['name'] = values['firstname'] + ' ' + values['lastName']
        #Mettre par défaut France dans le pays
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
        #Generate an error when a user already uses this email
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
                    #Log signup error
                    if SignupError:
                        _logger.error("name %s", SignupError )
                    #Log assertion error
                    if AssertionError:
                        _logger.error("name %s", AssertionError)
                    qcontext['error'] = _("Could not create a new account.")

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
        print("redirect1", redirect)
        response = super(Home, self).web_login(redirect=redirect, **kw)
        print("redirect2",redirect)
        partner = request.env['res.partner'].sudo().search([('email', "=", login)], limit=1)
        order = request.env['sale.order'].sudo().search([('partner_id', "=", partner.id)], order='create_date desc', limit=1)
        order1 = request.website.sale_get_order()
        print("order1",order1)
        if request.website.id == 1:
            step = partner.step
            print("step",step)
            if redirect == '/felicitations':
                response = super(Home, self).web_login(redirect='/felicitations', **kw)
            elif order or order1:
                print("order exist")
                if step == "document":
                    print("afficher document")
                    redirect='/charger_mes_documents'
                    #response = super(Home, self).web_login(redirect='/charger_mes_documents', **kw)
                elif step == "coordonnées":
                    print("afficher coordonnées")
                    redirect='/coordonnees'
                    #response = super(Home, self).web_login(redirect='/coordonnees', **kw)
                elif step == "financement":
                    print("afficher financement")
                    redirect='/shop/cart'
                    #response = super(Home, self).web_login(redirect='/shop/cart', **kw)
                elif step == "finish":
                    print("afficher espace client")
                    redirect='/my'
                    #response = super(Home, self).web_login(redirect='/my', **kw)
            else:
                print("afficher pricelist")
                redirect = '/#pricing'
                response = super(Home, self).web_login(redirect='/#pricing', **kw)
        print("redirect3", redirect)
        response = super(Home, self).web_login(redirect=redirect, **kw)
        return response






