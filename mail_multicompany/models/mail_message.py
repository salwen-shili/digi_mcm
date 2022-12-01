# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions
import logging

_logger = logging.getLogger(__name__)

class MailMessage(models.Model):

    _inherit = "mail.message"

    company_id = fields.Many2one("res.company", "Company")

    @api.model_create_multi
    def create(self, values_list):
        get_param = self.env['ir.config_parameter'].sudo().get_param
        alias=self.env['res.config.settings'].sudo().write({
            'alias_domain':self.env.company.alias_domain,
        })
        _logger.info("res config setting alias domain : % et ")
        # alias_domain= self.env['ir.config_parameter'].sudo().search([('key', "=",'mail.catchall.domain')])
        # if alias_domain:
        #     alias_domain.sudo().write({'value':self.env.company.alias_domain})
        icp_domain = self.env["ir.config_parameter"].sudo().get_param("mail.catchall.domain") #get mail.catchall.domain parameter
        _logger.info("res config setting alias domain : %s et ir config paramètres mail catchall domain : %s" %(str(alias),str(icp_domain)))
        if alias != icp_domain: #check difference between parametre mail.catchall.domain and alias domain
            try :
                self.env["ir.config_parameter"].sudo().set_param("mail.catchall.domain", self.env.company.alias_domain)
                self._cr.commit()
            except Exception:
                _logger.exception("Failure to update mail catchall domain from %s to %s" %(str(icp_domain),str(self.env.company.alias_domain)))
                
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
