from odoo import api, fields, models, _
from datetime import datetime

class AccountMove(models.Model):
    _inherit = "mcmacademy.session"

    temps_convocation = fields.Selection(selection=[
        ('matin', 'Matin'),
        ('apres_midi', 'Aprés Midi')],
        default=False, string="Examen Matin/Aprés Midi")

    heure_examen_matin = fields.Char(default="09H00")
    heure_examen_apres_midi = fields.Char(default="14H00")
    date_exam = fields.Date("Date d'examen")
    # Ajouter adresse d'examen field pour l'afficher dans la convocation
    adresse_examen = fields.Char(string="Adresse D'examen")
    date_convocation = fields.Date(string="Date d'envoi de convocation", default=datetime.today())
    horaire_email = fields.Char(compute="_compute_auto_horaire_email", string="Horaire Email", help="Heure d'examen qui sera affiché "
                                                                                                    "dans le text de l'email pour la convocation.")

    def _compute_auto_horaire_email(self):
        """ This function for dynamic field in email template,
            used to display "time of exam", if field (temps_convocation == matin)
            the field horaire_email will display (09H00 Matin)
            else it will display (14H00 Aprés Midi) """

        if self.temps_convocation == 'matin':
            self.horaire_email = '09H00 Matin'
        elif self.temps_convocation == 'apres_midi':
            self.horaire_email = '14H00 Aprés Midi'
        else:
            self.horaire_email = " "
