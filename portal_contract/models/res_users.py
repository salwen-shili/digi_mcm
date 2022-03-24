# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.addons.auth_signup.models.res_partner import SignupError, now
import logging
import pyshorteners
_logger = logging.getLogger(__name__)

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
                raise UserError(_("Cannot send email: user %s has no email address.") % user.name)
            with self.env.cr.savepoint():
                force_send = not (self.env.context.get('import_file', False))
                template.with_context(lang=user.lang).send_mail(user.id, force_send=force_send, raise_exception=True)
            _logger.info("Password reset email sent for user <%s> to <%s>", user.login, user.email)
            if user.phone :
                phone = str(user.phone.replace(' ', ''))[-9:]
                phone = '+33' + ' ' + phone[0:1] + ' ' + phone[1:3] + ' ' + phone[
                                                                            3:5] + ' ' + phone[
                                                                                         5:7] + ' ' + phone[
                                                                                                      7:]
                user.phone = phone
                url = user.signup_url
                short_url = pyshorteners.Shortener()
                short_url = short_url.tinyurl.short(
                    url)
                body = "Une demande de changement de mot de passe nous a été signalée, si vous etes à l'origine de cette action cliquez ici : %s (valable 24h)" % (
                    short_url)
                if body:
                    composer = self.env['sms.composer'].with_context(
                        default_res_model='res.partner',
                        default_res_id=user.partner_id.id,
                        default_composition_mode='comment',
                    ).sudo().create({
                        'body': body,
                        'mass_keep_log': True,
                        'mass_force_send': False,
                        'use_active_domain': False,
                    })
                    composer.action_send_sms() # we send sms to client contains link of reset password.
                    if user.phone:
                        user.phone = '0' + str(user.phone.replace(' ', ''))[
                                                      -9:]
