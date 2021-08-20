# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools


class TestMassMailing(models.TransientModel):
    _inherit = 'mailing.mailing.test'

    # @api.multi
    def send_mail_test(self):
        self.ensure_one()
        mailing = self.mass_mailing_id
        test_emails = tools.email_split(self.email_to)
        if mailing.sendinblue_template_id:
            return mailing.send_test_mail_sendinblue(test_emails)
        return super(TestMassMailing, self).send_mail_test()
