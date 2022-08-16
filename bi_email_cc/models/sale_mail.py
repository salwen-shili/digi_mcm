import base64
from odoo.tools import pycompat
from ast import literal_eval
from odoo import _, api, fields, models, SUPERUSER_ID, tools
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    cc_partner_ids = fields.Many2many(
        'res.partner', 'mail_compose_message_res_cc_partner_rel',
        'wizard_id', 'cc_partner_id', 'cc', readonly=False)
    bcc_partner_ids = fields.Many2many(
        'res.partner', 'mail_compose_message_res_bcc_partner_rel',
        'wizard_id', 'bcc_partner_id', 'BCC TEST', readonly=False)
    rply_partner_id = fields.Many2one('res.partner', string='Default Reply-To', readonly=False)
    is_cc = fields.Boolean(string='Enable Email CC')
    is_bcc = fields.Boolean(string='Enable Email BCC')
    is_reply = fields.Boolean(string='Reply')

    @api.model
    def default_get(self, fields):
        res = super(MailComposeMessage, self).default_get(fields)
        active_ids = self._context.get('active_ids')
        rply_partner_id = self.env["ir.config_parameter"].sudo().get_param("bi_email_cc.rply_partner_id")
        cc_partner_ids = self.env["ir.config_parameter"].sudo().get_param("bi_email_cc.cc_partner_ids")
        if (self.template_id, 'ilike', "DIGIMOOV RÉSULTATS FAVORABLES"):
            bcc_partner_ids = self.env['res.partner'].sudo().search([('email', "=", "digimoov.fr+25e168c414@invite.trustpilot.com")])
            _logger.info("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%ù test %s" % self.template_id)
        else:
            bcc_partner_ids = self.env["ir.config_parameter"].sudo().get_param("bi_email_cc.bcc_partner_ids")
        is_cc = self.env["ir.config_parameter"].sudo().get_param("bi_email_cc.email_cc")
        is_bcc = self.env["ir.config_parameter"].sudo().get_param("bi_email_cc.email_bcc")
        is_reply = self.env["ir.config_parameter"].sudo().get_param("bi_email_cc.email_reply")
        if cc_partner_ids or bcc_partner_ids:
            res.update({
                'rply_partner_id': int(rply_partner_id),
                'cc_partner_ids': [(6, 0, literal_eval(cc_partner_ids))],
                'bcc_partner_ids': [(6, 0, bcc_partner_ids.ids)],
                'is_cc': is_cc,
                'is_bcc': is_bcc,
                'is_reply': is_reply,
            })
        else:
            res.update({
                'rply_partner_id': int(rply_partner_id),
                'is_cc': is_cc,
                'is_bcc': is_bcc,
                'is_reply': is_reply,
            })
        return res

    def get_mail_values(self, res_ids):
        res = super(MailComposeMessage, self).get_mail_values(res_ids)

        for rec in res_ids:
            res[rec].update({
                "cc_partner_ids": [(6, 0, self.cc_partner_ids.ids)],
                "bcc_partner_ids": [(6, 0, self.bcc_partner_ids.ids)],
                "rply_partner_id": self.rply_partner_id.id,
            })

        return res
