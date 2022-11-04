from odoo import api, fields, models, _


class InheritMailTemplate(models.Model):
    _inherit = "mail.template"

    def write(self, vals):
        """ Pour définir le nom PDF automatiquement lors de l'envoi d'un e-mail,
         la configuration basée sur le champ du rapport optionnel à imprimer à joindre et nom du fichier du rapport. """
        result = super(InheritMailTemplate, self).write(vals)
        if 'report_template' in vals:
            report_template = 'report_template'
            if report_template == "Convocation":
                self.report_name = report_template + "- ${object.display_name} - ${object.mcm_session_id.session_ville_id.display_name} - ${object.mcm_session_id.date_exam.strftime('%d/%m/%Y')"

        return result
