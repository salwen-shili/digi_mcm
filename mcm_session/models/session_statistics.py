from odoo import api, fields, models, _


class SessionStatistics(models.Model):
    _name = 'session.statistics'
    _description = "Statestiques"

    session_id = fields.Many2one('mcmacademy.session', 'Session', required=True, readonly=False)

    nbr_inscrits = fields.Char(string="Nombre d'inscrits", compute="_compute_nbr_inscrit", store=True,
                               help="Nombre d'inscrits.")

    nbr_present = fields.Char(string="Nombre de présents", compute="_compute_nbr_present", store=True,
                              help="Nombre de présents.")

    nbr_absence_justifiee = fields.Char(string="Nombre d'absence justifiée", compute="_compute_nbr_absence_justifiee",
                                        store=True, help="Nombre d'absence justifiée.")

    nbr_echec = fields.Char(string="Nombre d'échec", compute="_compute_nbr_echec",
                            store=True, help="Nombre d'échec.")

    company_id = fields.Many2one('res.company', string='Société', change_default=True,
                                 default=lambda self: self.env.company)

    color = fields.Integer('Color Index')

    def _compute_nbr_inscrit(self):
        print("")
    def _compute_nbr_present(self):
        print("")
    def _compute_nbr_absence_justifiee(self):
        print("")
    def _compute_nbr_echec(self):
        print("")
