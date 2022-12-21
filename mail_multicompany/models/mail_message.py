# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions
import logging

_logger = logging.getLogger(__name__)

class MailMessage(models.Model):

    _inherit = "mail.message"

    company_id = fields.Many2one("res.company", "Company")

    @api.model_create_multi
    def create(self, values_list):
        icp_domain = self.env["ir.config_parameter"].sudo().get_param("mail.catchall.domain")
        if icp_domain != self.env.company.alias_domain :
           # We need to do this part here to avoid concurrent updates error.
            try:
                with self.env.cr.savepoint():
                    query = "UPDATE res_config_settings SET "
                    query += """
                        alias_domain = %s
                    """
                    self.env.cr.execute(query, (self.env.company.alias_domain,), log_exceptions=False)
            except Exception:
                pass
        catchall_domain_key = "mail.catchall.domain"
        if icp_domain != self.env.company.alias_domain:
            # We need to do this part here to avoid concurrent updates error.
            try :
                with self.env.cr.savepoint():
                    query = "UPDATE res_config_settings SET "
                    query += """
                        alias_domain = %s
                         WHERE key = %s
                    """
                    self.env.cr.execute(query, (self.env.company.alias_domain, catchall_domain_key), log_exceptions=False)
            except Exception:
                    pass
                
        for vals in values_list:
            if vals.get("model") and vals.get("res_id"):
                current_object = self.env[vals["model"]].browse(vals["res_id"])
                if hasattr(current_object, "company_id") and current_object.company_id:
                    vals["company_id"] = current_object.company_id.id
            if not vals.get("company_id"):
                vals["company_id"] = self.env.company.id
            if not vals.get("mail_server_id"):
                vals["mail_server_id"] = (
                    self.sudo()
                    .env["ir.mail_server"]
                    .search(
                        [("company_id", "=", vals.get("company_id", False))],
                        order="sequence",
                        limit=1,
                    )
                    .id
                )
        return super(MailMessage, self).create(vals)
