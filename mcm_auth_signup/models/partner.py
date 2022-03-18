# -*- coding: utf-8 -*-

import werkzeug.urls


from odoo import api, exceptions, fields, models, _
import requests


class ResPartner(models.Model):
    _inherit = "res.partner"

    firstname=fields.Char('Prénom')

    @api.model
    def signup_retrieve_info(self, token):
        res = super(ResPartner, self).signup_retrieve_info(token)
        partner = self._signup_retrieve_partner(token, raise_exception=True)
        if partner.signup_valid:
            res['firstname'] = partner.firstname
            res['lastName'] = partner.lastName
            res['voie'] = partner.voie
            res['nom_voie'] = partner.nom_voie
            res['num_voie'] = partner.num_voie
            res['street'] = partner.street
            res['street2'] = partner.street2
            res['phone'] = partner.phone
            res['zip_code'] = str(partner.zip)
            res['city'] = str(partner.city)
            res['last_login'] = partner.last_login
            res['question_signup'] = partner.question_signup
        return res

    """This method was re-written because signup url is got from system parameter base_url
    This parameter does not change according to the company website (bug in odoo)"""
    def _get_signup_url_for_action(self, url=None, action=None, view_type=None, menu_id=None, res_id=None, model=None):
        """ generate a signup url for the given partner ids and action, possibly overriding
            the url state components (menu_id, id, view_type) """
        res = dict.fromkeys(self.ids, False)
        for partner in self:
            base_url = partner.get_base_url()
            #Define base_url according to partner company
            if partner.company_id.id == 1:
                base_url = "https://www.mcm-academy.fr"
            elif partner.company_id.id == 2:
                base_url = "https://www.digimoov.fr"
            # when required, make sure the partner has a valid signup token
            if self.env.context.get('signup_valid') and not partner.user_ids:
                partner.sudo().signup_prepare()
            route = 'login'
            # the parameters to encode for the query
            query = dict(db=self.env.cr.dbname)
            signup_type = self.env.context.get('signup_force_type_in_url', partner.sudo().signup_type or '')
            if signup_type:
                route = 'reset_password' if signup_type == 'reset' else signup_type
            if partner.sudo().signup_token and signup_type:
                query['token'] = partner.sudo().signup_token
            elif partner.user_ids:
                query['login'] = partner.user_ids[0].login
            else:
                continue  # no signup token, no user, thus no signup url!
            if url:
                query['redirect'] = url
            else:
                fragment = dict()
                base = '/web#'
                if action == '/mail/view':
                    base = '/mail/view?'
                elif action:
                    fragment['action'] = action
                if view_type:
                    fragment['view_type'] = view_type
                if menu_id:
                    fragment['menu_id'] = menu_id
                if model:
                    fragment['model'] = model
                if res_id:
                    fragment['res_id'] = res_id
                if fragment:
                    query['redirect'] = base + werkzeug.urls.url_encode(fragment)
            url = "/web/%s?%s" % (route, werkzeug.urls.url_encode(query))
            if not self.env.context.get('relative_url'):
                url = werkzeug.urls.url_join(base_url, url)
            res[partner.id] = url
        return res
