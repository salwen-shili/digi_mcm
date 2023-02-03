from odoo import api, fields, models, _


class SessionStatistics(models.Model):
    _name = 'session.statistics'
    _description = "Statistiques"

    session_id = fields.Many2one('mcmacademy.session', 'Session', required=True, readonly=False)

    date_exam = fields.Date(string="Date examen")

    nbr_inscrits = fields.Integer(string="Nombre d'inscrits", compute="_compute_nbr_inscrit", store=True,
                               help="Nombre d'inscrits.")

    nbr_pack_solo_inscrits = fields.Integer(string="Pack Solo Inscrit",
                                         compute="_compute_pack_solo_pro_prem_repassage_inscrit", store=True,
                                         help="Pack Solo Inscrit.")

    nbr_pack_pro_inscrit = fields.Integer(string="Nombre Pack Pro Inscrit",
                                       compute="_compute_pack_solo_pro_prem_repassage_inscrit", store=True,
                                       help="Nombre Pack Pro Inscrit.")

    nbr_pack_premium_inscrit = fields.Integer(string="Nombre Pack Premium Inscrit",
                                           compute="_compute_pack_solo_pro_prem_repassage_inscrit", store=True,
                                           help="Nombre Pack Premium Inscrit.")

    nbr_pack_repassage_inscrit = fields.Integer(string="Nombre Pack Repassage Inscrit",
                                             compute="_compute_pack_solo_pro_prem_repassage_inscrit", store=True,
                                             help="Nombre Pack Repassage Inscrit.")

    nbr_pack_solo_present = fields.Integer(string="Nombre Pack Solo présent",
                                        compute="_compute_nbr_pack_solo_pro_premium_repassage_present", store=True,
                                        help="Pack Solo Présent.")

    nbr_pack_pro_present = fields.Integer(string="Nombre Pack Pro Présent",
                                       compute="_compute_nbr_pack_solo_pro_premium_repassage_present",
                                       store=True,
                                       help="Nombre Pack Pro Présent.")

    nbr_pack_premium_present = fields.Integer(string="Nombre Pack Premium Présent",
                                           compute="_compute_nbr_pack_solo_pro_premium_repassage_present", store=True,
                                           help="Nombre Pack Premium Présent.")

    nbr_pack_repassage_present = fields.Integer(string="Nombre Pack Repassage Présent",
                                             compute="_compute_nbr_pack_solo_pro_premium_repassage_present", store=True,
                                             help="Nombre Pack Repassage Présent.")

    nbr_present = fields.Integer(string="Nombre de présents", compute="_compute_nbr_present", store=True,
                              help="Nombre de présents.")

    nbr_absence_justifiee = fields.Integer(string="Nombre d'absence justifiée", compute="_compute_nbr_absence_justifiee",
                                        store=True, help="Nombre d'absence justifiée.")

    nbr_echec = fields.Integer(string="Nombre d'échec", compute="_compute_nbr_echec",
                            store=True, help="Nombre d'échec.")

    taux_echec = fields.Float(string="Taux d'échec", compute="_compute_taux_echec",
                              store=True, help="Taux d'échec %")

    company_id = fields.Many2one('res.company', string='Société', change_default=True,
                                 default=lambda self: self.env.company)

    color = fields.Integer('Color Index')

    @api.depends('session_id')
    def _compute_date_examen(self):
        date = self.session_id.date_exam
        self.date_exam = date

    @api.depends('session_id')
    def _compute_nbr_inscrit(self):
        nbr_inscrits = False
        res = self.session_id.nbr_client_par_session(nbr_inscrits)
        self.nbr_inscrits = res

    @api.depends('session_id')
    def _compute_pack_solo_pro_prem_repassage_inscrit(self):
        sum_solo_present = False
        sum_pro_inscrit = False
        sum_premium_inscrit = False
        sum_repassage_inscrit = False
        self.nbr_pack_solo_inscrits = self.session_id.pack_solo_present(sum_solo_present)
        self.nbr_pack_pro_inscrit = self.session_id.pack_pro_inscrit(sum_pro_inscrit)
        self.nbr_pack_premium_inscrit = self.session_id.pack_premium_inscrit(sum_premium_inscrit)
        self.nbr_pack_repassage_inscrit = self.session_id.pack_repassage_inscrit(sum_repassage_inscrit)

    @api.depends('session_id')
    def _compute_nbr_present(self):
        nbr_present = False
        self.nbr_present = self.session_id.nbr_present_par_session(nbr_present)

    @api.depends('session_id')
    def _compute_nbr_pack_solo_pro_premium_repassage_present(self):
        nbr_present = False
        sum_premium_present = False
        sum_pro_present = False
        sum_repassage_present = False
        self.nbr_pack_solo_present = self.session_id.nbr_present_par_session(nbr_present)
        self.nbr_pack_premium_present = self.session_id.pack_premium_present(sum_premium_present)
        self.nbr_pack_pro_present = self.session_id.pack_pro_present(sum_pro_present)
        self.nbr_pack_repassage_present = self.session_id.pack_repassage_present(sum_repassage_present)

    @api.depends('session_id')
    def _compute_nbr_absence_justifiee(self):
        total_absence_justifiée = False
        self.nbr_absence_justifiee = self.session_id.calculer_nombre_absence_justifiée(total_absence_justifiée)

    @api.depends('session_id')
    def _compute_nbr_echec(self):
        nbr_echec = False
        self.nbr_echec = self.session_id.nbr_echec(nbr_echec)

    @api.depends('session_id')
    def _compute_taux_echec(self):
        prc_echec = False
        self.taux_echec = self.session_id.pourcentage_echec(prc_echec)
