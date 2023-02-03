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
                                           help="Nombre Pack Solo Présent.")

    nbr_pack_pro_present = fields.Integer(string="Nombre Pack Pro Présent",
                                          compute="_compute_nbr_pack_solo_pro_premium_repassage_present",
                                          store=True,
                                          help="Nombre Pack Pro Présent.")

    nbr_pack_premium_present = fields.Integer(string="Nombre Pack Premium Présent",
                                              compute="_compute_nbr_pack_solo_pro_premium_repassage_present",
                                              store=True,
                                              help="Nombre Pack Premium Présent.")

    nbr_pack_repassage_present = fields.Integer(string="Nombre Pack Repassage Présent",
                                                compute="_compute_nbr_pack_solo_pro_premium_repassage_present",
                                                store=True,
                                                help="Nombre Pack Repassage Présent.")

    nbr_present = fields.Integer(string="Nombre de présents", compute="_compute_nbr_present", store=True,
                                 help="Nombre de présents.")

    nbr_absence_justifiee = fields.Integer(string="Nombre d'absence justifiée",
                                           compute="_compute_nbr_absence_justifiee",
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
        self.nbr_inscrits = int(res)

    @api.depends('session_id')
    def _compute_pack_solo_pro_prem_repassage_inscrit(self):
        # self.nbr_pack_solo_inscrits = int(self.session_id.pack_solo_present(sum_solo_present))
        nbr_from_examen_solo = 0
        for examen in self.env['info.examen'].sudo().search(
                [('date_exam', "=", self.session_id.date_exam), ('session_id', "=", self.session_id.id),
                 ('presence', "=", 'present')]):
            if examen.module_id.product_id.default_code in ["basique", "solo-ubereats"]:
                nbr_from_examen_solo += 1
        self.nbr_pack_solo_present = nbr_from_examen_solo
        # self.nbr_pack_pro_inscrit = int(self.session_id.pack_pro_inscrit(sum_pro_inscrit))
        nbr_from_examen_pro = False
        for examen in self.env['info.examen'].search(
                [('date_exam', "=", self.session_id.date_exam), ('session_id', "=", self.session_id.id)]):
            if examen.module_id.product_id.default_code == "avancee" and examen.partner_id.statut == 'won':
                nbr_from_examen_pro += 1
        tot = nbr_from_examen_pro
        self.nbr_pack_pro_inscrit = tot
        # self.nbr_pack_premium_inscrit = int(self.session_id.pack_premium_inscrit(sum_premium_inscrit))
        nbr_from_examen_premium = 0
        for examen in self.env['info.examen'].search(
                [('date_exam', "=", self.session_id.date_exam), ('session_id', "=", self.session_id.id)]):
            if examen.module_id.product_id.default_code == "premium" and examen.partner_id.statut == 'won':
                nbr_from_examen_premium += 1
        res_calc_premium = nbr_from_examen_premium
        self.nbr_pack_premium_inscrit = res_calc_premium
        # self.nbr_pack_repassage_inscrit = int(self.session_id.pack_repassage_inscrit(sum_repassage_inscrit))

        nbr_from_examen = 0
        for examen in self.env['info.examen'].search(
                [('date_exam', "=", self.date_exam), ('session_id', "=", self.id)]):
            if examen.module_id.product_id.default_code == "examen" and examen.partner_id.statut == 'won':
                nbr_from_examen += 1
        sum_repassage_inscrit = nbr_from_examen
        self.nbr_pack_repassage_inscrit = sum_repassage_inscrit

    @api.depends('session_id')
    def _compute_nbr_present(self):
        nbr_present = False
        # self.nbr_present = int(self.session_id.nbr_present_par_session(nbr_present))
        nbr_present = self.session_id.client_ids.filtered(lambda cl: cl.presence == 'Présent(e)')
        self.nbr_present = len(nbr_present)

    @api.depends('session_id')
    def _compute_nbr_pack_solo_pro_premium_repassage_present(self):
        nbr_from_examen_solo = 0
        for examen in self.env['info.examen'].sudo().search(
                [('date_exam', "=", self.session_id.date_exam), ('session_id', "=", self.session_id.id),
                 ('presence', "=", 'present')]):
            if examen.module_id.product_id.default_code in ["basique", "solo-ubereats"]:
                nbr_from_examen_solo += 1
        self.nbr_pack_solo_present = nbr_from_examen_solo
        # self.nbr_pack_premium_present = int(self.session_id.pack_premium_present(sum_premium_present))
        # Pack Premium Présent
        examen = self.env['info.examen'].search(
            [('date_exam', "=", self.session_id.date_exam), ('session_id.id', "=", self.session_id.id),
             ('presence', "=", 'present'),
             ('module_id.product_id.default_code', '=', "premium")])
        self.nbr_pack_premium_present = len(examen)
        # self.nbr_pack_pro_present = int(self.session_id.pack_pro_present(sum_pro_present))

        nbr_from_examen_pro = 0
        for examen in self.env['info.examen'].search(
                [('date_exam', "=", self.session_id.date_exam), ('session_id', "=", self.session_id.id),
                 ('presence', "=", 'present')]):
            if examen.module_id.product_id.default_code == "avancee":
                nbr_from_examen_pro += 1
        self.nbr_pack_pro_present = nbr_from_examen_pro
        # self.nbr_pack_repassage_present = int(self.session_id.pack_repassage_present(sum_repassage_present))

        nbr_from_examen_repassage = 0
        for examen in self.env['info.examen'].search(
                [('date_exam', "=", self.session_id.date_exam), ('session_id', "=", self.session_id.id), ('presence', "=", 'present')]):
            if examen.module_id.product_id.default_code == "examen":
                nbr_from_examen_repassage += 1
        self.nbr_pack_repassage_present = nbr_from_examen_repassage

    @api.depends('session_id')
    def _compute_nbr_absence_justifiee(self):
        total_absence_justifiée = False
        #self.nbr_absence_justifiee = int(self.session_id.calculer_nombre_absence_justifiée(total_absence_justifiée))
        for examen in self.env['info.examen'].search([('date_exam', "=", self.date_exam)]):
            if examen:
                nbr_absence = examen.env['info.examen'].search_count(
                    [('session_id', "=", self.session_id.id), ('presence', "=", 'absence_justifiee')])
                self.nbr_absence_justifiee = nbr_absence

    @api.depends('session_id')
    def _compute_nbr_echec(self):
        nbr_echec = False
        #self.nbr_echec = int(self.session_id.nbr_echec(nbr_echec))
        for examen in self.env['info.examen'].search([('date_exam', "=", self.date_exam)]):
            nbr_absence = examen.env['info.examen'].search_count(
                [('session_id', "=", self.session_id.id), ('presence', "=", 'present'), ('resultat', "=", 'ajourne')])
            self.nbr_echec = nbr_absence

    @api.depends('session_id')
    def _compute_taux_echec(self):
        prc_echec = False
        # self.taux_echec = int(self.session_id.pourcentage_echec(prc_echec))

        nbr_echec = self.session_id.nbr_echec(self)
        nbr_present_tot = self.session_id.nbr_present_par_session(self)
        if nbr_present_tot > 0:
            res = (nbr_echec * 100 / nbr_present_tot)
            if res > 0:
                prc_echec = f'{res:.2f}'.replace('.00', '')
                self.taux_echec = prc_echec
            else:
                prc_echec = f'{res:.0f}'
                self.taux_echec = prc_echec
