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

    nbr_echec = fields.Char(string="Nombre d'échec", compute="_compute_nbr_echec",
                            store=True, help="Nombre d'échec.")

    company_id = fields.Many2one('res.company', string='Société', change_default=True,
                                 default=lambda self: self.env.company)

    color = fields.Integer('Color Index')

    @api.depends('session_id')
    def _compute_nbr_inscrit(self):
        nbr_inscrits = False
        res = self.session_id.nbr_client_par_session(nbr_inscrits)
        self.nbr_inscrits = res

    @api.depends('session_id')
    def _compute_nbr_present(self):
        nbr_present = False
        self.nbr_present = self.session_id.nbr_present_par_session(nbr_present)

    def _compute_nbr_absence_justifiee(self):
        total_absence_justifiée = False
        self.nbr_absence_justifiee = self.session_id.calculer_nombre_absence_justifiée(total_absence_justifiée)

    def _compute_nbr_echec(self):
        nbr_echec = False
        self.nbr_echec = self.session_id.nbr_echec(nbr_echec)
