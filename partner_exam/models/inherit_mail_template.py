from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


class InheritMailTemplate(models.Model):
    _inherit = "mail.template"

    @api.model
    def create(self, vals):
        """ Pour définir le nom PDF automatiquement lors de l'envoi d'un e-mail,
         la configuration basée sur le champ du rapport optionnel à imprimer à joindre et nom du fichier du rapport. """
        result = super(InheritMailTemplate, self).create(vals)
        report_name = "- ${object.display_name} - ${object.mcm_session_id.session_ville_id.display_name} - ${object.mcm_session_id.date_exam.strftime('%d/%m/%Y')}"
        report_name_exam = "- ${object.partner_id.display_name} - ${object.session_id.session_ville_id.display_name} - ${object.session_id.date_exam.strftime('%d/%m/%Y')}"
        if result.model_id.model == "res.partner" or result.model_id.model == "info.examen":
            if "Convocation" in vals.get('name'):  # Si mot CONVOCATION existe dans le nom de rapport
                result.auto_delete = False
                result.report_template = self.env['ir.actions.report'].search([('name', '=', str("Convocation"))],
                                                                              limit=1)
                if result.model_id.model == "res.partner":
                    result.report_name = str(result.report_template.name) + report_name
                elif result.model_id.model == "info.examen":
                    result.report_name = str(result.report_template.name) + report_name_exam
            elif "Cerfa" in vals.get('name'):
                result.auto_delete = False
                result.report_template = self.env['ir.actions.report'].search([('name', '=', str("Cerfa"))], limit=1)
                if result.model_id.model == "res.partner":
                    result.report_name = str(result.report_template.name) + report_name
                elif result.model_id.model == "info.examen":
                    result.report_name = str(result.report_template.name) + report_name_exam
            elif "Attestation de fin de formation" in vals.get('name'):
                result.auto_delete = False
                result.report_template = self.env['ir.actions.report'].search(
                    [('name', '=', str("Attestation Suivi Formation"))], limit=1)
                if result.model_id.model == "res.partner":
                    result.report_name = str(result.report_template.name) + report_name
                elif result.model_id.model == "info.examen":
                    result.report_name = str(result.report_template.name) + report_name_exam
            elif "Relevé de notes" in vals.get('name'):
                result.auto_delete = False
                result.report_template = self.env['ir.actions.report'].search(
                    [('name', '=', str("Générer les relevés de notes"))], limit=1)
                if result.model_id.model == "res.partner":
                    result.report_name = str(result.report_template.name) + report_name
                elif result.model_id.model == "info.examen":
                    result.report_name = str(result.report_template.name) + report_name_exam
            elif "Relevé de connexion" in vals.get('name'):
                result.auto_delete = False
                result.report_template = self.env['ir.actions.report'].search(
                    [('name', '=', str("Générer un relevé de connexion"))], limit=1)
                if result.model_id.model == "res.partner":
                    result.report_name = str(result.report_template.name) + report_name
                elif result.model_id.model == "info.examen":
                    result.report_name = str(result.report_template.name) + report_name_exam
            elif "Procès verbal" in vals.get('name'):
                result.auto_delete = False
                result.report_template = self.env['ir.actions.report'].search(
                    [('name', '=', str("RAPPORT DE SESSION D’EXAMEN"))], limit=1)
                if result.model_id.model == "res.partner":
                    result.report_name = str(result.report_template.name) + report_name
                elif result.model_id.model == "info.examen":
                    result.report_name = str(result.report_template.name) + report_name_exam
        return result
