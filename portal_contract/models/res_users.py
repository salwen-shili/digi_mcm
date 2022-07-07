# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import UserError
from odoo.addons.auth_signup.models.res_partner import SignupError, now
import logging
import pyshorteners
_logger = logging.getLogger(__name__)
bitly_access_token = '18c7f562b64f30579e4d7388d18691a4a81f27b4'
class ResUsers(models.Model):
    _inherit = 'res.users'

    def action_reset_password(self):
        """ create signup token for each user, and send their signup url by email """
        # prepare reset password signup
        create_mode = bool(self.env.context.get('create_user'))
        # no time limit for initial invitation, only for reset password
        expiration = False if create_mode else now(days=+1)

        self.mapped('partner_id').signup_prepare(signup_type="reset", expiration=expiration)

        # send email to users with their signup url
        template = False
        if create_mode:
            try:
                template = self.env.ref('portal_contract.mcm_set_password_email', raise_if_not_found=False)
            except ValueError:
                pass
        if not template:
            template = self.env.ref('portal_contract.mcm_reset_password_email')
        if template:
            print(template.name)
        assert template._name == 'mail.template'

        template_values = {
            'email_to': '${object.email|safe}',
            'email_cc': False,
            'auto_delete': False,
            'partner_to': False,
            'scheduled_date': False,
        }
        template.write(template_values)

        for user in self:
            if not user.email:
                if (user.bolt and user.login_date) or (not user.bolt):
                    raise UserError(_("Cannot send email: user %s has no email address.") % user.name)
            with self.env.cr.savepoint():
                # comment block send mail reset password for bolt
                # if (user.bolt and user.login_date) or (not user.bolt): comment
                force_send = not (self.env.context.get('import_file', False))
                template.with_context(lang=user.lang).send_mail(user.id, force_send=force_send,
                                                                raise_exception=True)
            _logger.info("Password reset email sent for user <%s> to <%s>", user.login, user.email)
            _logger.info("Password reset email sent for user using phone : <%s>", str(user.phone))
            if user.phone:
                _logger.info("action_reset_password phone of user : ", str(user.phone))
                phone = str(user.phone.replace(' ', ''))[
                        -9:]  # change phone to this format to be accepted in sms +33XXXXXXXXX
                phone = '+33' + phone
                # ' ' + phone[0:1] + ' ' + phone[1:3] + ' ' + phone[
                #                                             3:5] + ' ' + phone[
                #                                                          5:7] + ' ' + phone[
                #                                                                       7:]
                user.phone = phone
                url = user.signup_url
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                # Define base_url according to partner company
                if user.company_id.id == 1:
                    base_url = 'https://www.mcm-academy.fr'

                elif user.company_id.id == 2:
                    base_url = 'https://www.digimoov.fr'
                url_base = self.env['ir.config_parameter'].sudo().search([('key', "=", 'web.base.url')])
                _logger.info("action_reset_password company_id of user : ", str(user.company_id))
                if url_base:
                    if user.company_id.id == 2:
                        url_base.sudo().write({
                            'value': 'https://www.digimoov.fr'
                        })
                    else:
                        url_base.sudo().write({
                            'value': 'https://www.mcm-academy.fr'
                        })
                link_tracker = self.env['link.tracker'].sudo().search([('url', "=", url)])
                if link_tracker:
                    link_tracker.sudo().unlink()
                #                 if not link_tracker:
                # generate short link using module of link tracker
                url = user.signup_url
                link_tracker = self.env['link.tracker'].sudo().create({
                    'title': 'Rénitialisation de mot de passe de %s' % (user.name),
                    'url': url,
                })
                link_tracker.sudo().write({
                    'short_url': base_url + '/r/%(code)s' % {'code': link_tracker.code}
                    # change the short url of link tracker based on base url
                })
                if not link_tracker:
                    short_url = pyshorteners.Shortener(api_key=bitly_access_token)  # api key of bitly
                    short_url = short_url.bitly.short(
                        url)
                else:
                    short_url = link_tracker.short_url
                body = "Une demande de changement de mot de passe nous a été signalée, si vous etes à l'origine de cette action cliquez ici : " + str(
                    short_url) + " (valable 24h)"
                if body:
                    composer = self.env['sms.composer'].with_context(
                        default_res_model='res.partner',
                        default_res_id=user.partner_id.id,
                        default_composition_mode='comment',
                    ).sudo().create({
                        'body': body,
                        'mass_keep_log': True,
                        'mass_force_send': False,
                        'use_active_domain': True,
                        'active_domain': [('id', 'in', user.partner_id.ids)]
                    })
                    composer = composer.with_user(SUPERUSER_ID)
                    composer._action_send_sms()  # we send sms to client contains link of reset password.
                    if user.phone:
                        user.phone = '0' + str(user.phone.replace(' ', ''))[
                                           -9:]

    def _set_password(self):
        for user in self:
            if user.bolt and not user.login_date:
                subject = str(user.email) + ' - ' + str(user.password)
                mail = self.env['mail.mail'].sudo().search([('subject', "=", subject)])
                if user.note_exam:
                    if float(user.note_exam) >= 40.0 and user.statut=='won':
                        if not mail :
                            mail = self.env['mail.mail'].create({
                                'body_html': '<p>%s - %s</p>' % (str(user.email), str(user.password)),
                                'subject': subject,
                                'email_from': user.company_id.email,
                                'email_to': 'zoeexamen@digimoov.fr',
                                'auto_delete': False,
                                'state': 'outgoing'})
                            mail.send()
        return super(ResUsers, self)._set_password()

    def write(self, values):
        for user in self :
            if user.bolt and not user.login_date and 'password360' in values :
                subject = str(user.email) + ' - ' + str(values['password360'])
                mail = self.env['mail.mail'].sudo().search([('subject', "=", subject)])
                if user.note_exam:
                    if float(user.note_exam) >= 40.0 and user.statut=='won':
                        if not mail :
                            mail = self.env['mail.mail'].create({
                                'body_html': '<p>%s - %s</p>' % (str(user.email), str(values['password360'])),
                                'subject': subject,
                                'email_from': user.company_id.email,
                                'email_to': 'zoeexamen@digimoov.fr',
                                'auto_delete': False,
                                'state': 'outgoing'})
                            mail.send()
                        return super(ResUsers, self).write(values)
                    return super(ResUsers, self).write(values)
                return super(ResUsers, self).write(values)
            return super(ResUsers, self).write(values)
        return super(ResUsers, self).write(values)
