from odoo import api, fields, models, _


class SessionStatistics(models.Model):
    _name = 'session.statistics'
    _description = "Statistiques"

    @api.model
    def _default_date_exam(self):
        if self.session_id:
            date = self.session_id.date_exam
            return date

    session_id = fields.Many2one('mcmacademy.session', 'Session', required=True, readonly=False)

    date_exam = fields.Date(string="Date examen", default=_default_date_exam)

    nbr_inscrits = fields.Integer(string="Nombre Inscrits", compute="_compute_nbr_inscrit", store=True,
                                  help="Nombre d'inscrits.")

    nbr_pack_solo_inscrits = fields.Integer(string="Solo Inscrit",
                                            compute="_compute_pack_solo_inscrit", store=True,
                                            help="Solo Inscrit.")

    nbr_pack_pro_inscrit = fields.Integer(string="Pro Inscrit",
                                          compute="_compute_pack_pro_inscrit", store=True,
                                          help="Pro Inscrit.")

    nbr_pack_premium_inscrit = fields.Integer(string="Premium Inscrit",
                                              compute="_compute_pack_premium_inscrit", store=True,
                                              help="Nombre Pack Premium Inscrit.")

    nbr_pack_repassage_inscrit = fields.Integer(string="Repassage Inscrit",
                                                compute="_compute_pack_repassage_inscrit", store=True,
                                                help="Nombre Pack Repassage Inscrit.")

    nbr_pack_solo_present = fields.Integer(string="Solo présent",
                                           compute="_compute_nbr_pack_solo_present", store=True,
                                           help="Nombre Pack Solo Présent.")

    nbr_pack_pro_present = fields.Integer(string="Pro Présent",
                                          compute="_compute_nbr_pack_pro_present",
                                          store=True,
                                          help="Nombre Pack Pro Présent.")

    nbr_pack_premium_present = fields.Integer(string="Premium Présent",
                                              compute="_compute_nbr_pack_premium_present",
                                              store=True,
                                              help="Nombre Pack Premium Présent.")

    nbr_pack_repassage_present = fields.Integer(string="Repassage Présent",
                                                compute="_compute_nbr_pack_repassage_present",
                                                store=True,
                                                help="Nombre Pack Repassage Présent.")

    nbr_present = fields.Integer(string="Présents", compute="_compute_nbr_present", store=True,
                                 help="Nombre de présents.")

    taux_solo_presence = fields.Integer(string="Taux Solo Présent", compute="_compute_taux_de_presence_solo",
                                        help="Taux Solo Présent.")
    taux_pro_presence = fields.Integer(string="Taux Pro Présent", compute="_compute_taux_de_presence_pro",
                                       help="Taux Pro Présent.")
    taux_premium_presence = fields.Integer(string="Taux Premium Présent", compute="_compute_taux_de_presence_premium",
                                           help="Taux Premium Présent.")
    taux_repassage_presence = fields.Integer(string="Taux Repassage Présent",
                                             compute="_compute_taux_de_presence_repassage",
                                             help="Taux Repassage Présent.")

    nbr_absence_justifiee = fields.Integer(string="Absence justifiée",
                                           compute="_compute_nbr_absence_justifiee",
                                           store=True, help="Nombre d'absence justifiée.")

    nbr_echec = fields.Integer(string="Nombre d'échec", compute="_compute_nbr_echec",
                               store=True, help="Nombre d'échec.")

    taux_echec = fields.Float(string="Taux d'échec", compute="_compute_taux_echec",
                              store=True, help="Taux d'échec %")

    company_id = fields.Many2one('res.company', string='Société',
                                 default=lambda self: self.env.company)

    color = fields.Integer('Color Index')

    partner_id = fields.Many2many('res.partner', compute="_compute_liste_client_present", readonly=True)

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
    def _compute_pack_solo_inscrit(self):
        # self.nbr_pack_solo_inscrits = int(self.session_id.pack_solo_present(sum_solo_present))
        nbr_from_examen_solo = 0
        for examen in self.env['info.examen'].sudo().search(
                [('date_exam', "=", self.session_id.date_exam), ('session_id', "=", self.session_id.id),
                 ('presence', "=", 'present')]):
            if examen.module_id.product_id.default_code in ["basique", "solo-ubereats"]:
                nbr_from_examen_solo += 1
        self.nbr_pack_solo_inscrits = nbr_from_examen_solo

    @api.depends('session_id')
    def _compute_pack_pro_inscrit(self):
        # self.nbr_pack_pro_inscrit = int(self.session_id.pack_pro_inscrit(sum_pro_inscrit))
        nbr_from_examen_pro = False
        for rec in self:
            for examen in self.env['info.examen'].search(
                    [('date_exam', "=", rec.session_id.date_exam), ('session_id', "=", rec.session_id.id)]):
                if examen.module_id.product_id.default_code == "avancee" and examen.partner_id.statut == 'won':
                    nbr_from_examen_pro += 1
            self.nbr_pack_pro_inscrit = nbr_from_examen_pro

    @api.depends('session_id')
    def _compute_pack_premium_inscrit(self):
        # self.nbr_pack_premium_inscrit = int(self.session_id.pack_premium_inscrit(sum_premium_inscrit))
        nbr_from_examen_premium = 0
        for examen in self.env['info.examen'].search(
                [('date_exam', "=", self.session_id.date_exam), ('session_id', "=", self.session_id.id)]):
            if examen.module_id.product_id.default_code == "premium" and examen.partner_id.statut == 'won':
                nbr_from_examen_premium += 1
        res_calc_premium = nbr_from_examen_premium
        self.nbr_pack_premium_inscrit = res_calc_premium

    @api.depends('session_id')
    def _compute_pack_repassage_inscrit(self):
        # self.nbr_pack_repassage_inscrit = int(self.session_id.pack_repassage_inscrit(sum_repassage_inscrit))

        nbr_from_examen = 0
        for examen in self.env['info.examen'].search(
                [('date_exam', "=", self.session_id.date_exam), ('session_id', "=", self.session_id.id)]):
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
    def _compute_nbr_pack_solo_present(self):
        nbr_from_examen_solo = 0
        for examen in self.env['info.examen'].sudo().search(
                [('date_exam', "=", self.session_id.date_exam), ('session_id', "=", self.session_id.id),
                 ('presence', "=", 'present')]):
            if examen.module_id.product_id.default_code in ["basique", "solo-ubereats"]:
                nbr_from_examen_solo += 1
        self.nbr_pack_solo_present = nbr_from_examen_solo

    @api.depends('session_id')
    def _compute_nbr_pack_premium_present(self):
        # self.nbr_pack_premium_present = int(self.session_id.pack_premium_present(sum_premium_present))
        # Pack Premium Présent
        for rec in self:
            examen = rec.env['info.examen'].search(
                [('date_exam', "=", rec.session_id.date_exam), ('session_id.id', "=", rec.session_id.id),
                 ('presence', "=", 'present'),
                 ('module_id.product_id.default_code', '=', "premium")])
            rec.nbr_pack_premium_present = len(examen)

    @api.depends('session_id')
    def _compute_nbr_pack_pro_present(self):
        # self.nbr_pack_pro_present = int(self.session_id.pack_pro_present(sum_pro_present))
        nbr_from_examen_pro = 0
        for rec in self:
            for examen in rec.env['info.examen'].search(
                    [('date_exam', "=", rec.session_id.date_exam), ('session_id', "=", rec.session_id.id),
                     ('presence', "=", 'present')]):
                if examen.module_id.product_id.default_code == "avancee":
                    nbr_from_examen_pro += 1
            rec.nbr_pack_pro_present = nbr_from_examen_pro

    @api.depends('session_id')
    def _compute_nbr_pack_repassage_present(self):
        for rec in self:
            # self.nbr_pack_repassage_present = int(self.session_id.pack_repassage_present(sum_repassage_present))

            nbr_from_examen_repassage = 0
            for examen in rec.env['info.examen'].search(
                    [('date_exam', "=", rec.session_id.date_exam), ('session_id', "=", rec.session_id.id),
                     ('presence', "=", 'present')]):
                if examen.module_id.product_id.default_code == "examen":
                    nbr_from_examen_repassage += 1
            rec.nbr_pack_repassage_present = nbr_from_examen_repassage

    @api.depends('session_id')
    def _compute_nbr_absence_justifiee(self):
        total_absence_justifiée = False
        # self.nbr_absence_justifiee = int(self.session_id.calculer_nombre_absence_justifiée(total_absence_justifiée))
        for examen in self.env['info.examen'].search([('date_exam', "=", self.date_exam)]):
            if examen:
                nbr_absence = examen.env['info.examen'].search_count(
                    [('session_id', "=", self.session_id.id), ('presence', "=", 'absence_justifiee')])
                self.nbr_absence_justifiee = nbr_absence

    @api.depends('session_id')
    def _compute_nbr_echec(self):
        nbr_echec = False
        # self.nbr_echec = int(self.session_id.nbr_echec(nbr_echec))
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

    @api.depends('session_id')
    def _compute_taux_de_presence_pro(self):
        """ Calculer taux de presence par session selon le pack pro """
        for rec in self:
            pack_pro_present = rec.nbr_pack_pro_present
            nbr_inscrit_pro = rec.nbr_pack_pro_inscrit
            if nbr_inscrit_pro is None:
                nbr_inscrit_pro = 0
            if nbr_inscrit_pro > 0:
                taux_de_presence = pack_pro_present * 100 / nbr_inscrit_pro
                if taux_de_presence > 0:
                    rec.taux_pro_presence = taux_de_presence
                else:
                    rec.taux_pro_presence = taux_de_presence
            else:
                rec.taux_pro_presence = 0

    def _compute_taux_de_presence_premium(self):
        """ Calculer taux de présence pour les packs premium;
        avec une condition pour enlever la partie décimale
        si le résultat est égale à zéro"""
        for rec in self:
            pack_premium_present = rec.nbr_pack_premium_present
            nbr_inscrit = rec.nbr_pack_premium_inscrit
            if nbr_inscrit is None:
                nbr_inscrit = 0
            if nbr_inscrit > 0:
                taux_de_presence = pack_premium_present * 100 / nbr_inscrit
                if taux_de_presence > 0:
                    rec.taux_premium_presence = taux_de_presence
                else:
                    rec.taux_premium_presence = taux_de_presence
            else:
                rec.taux_premium_presence = 0

    def _compute_taux_de_presence_solo(self):
        """ Calculer taux solo"""
        for rec in self:
            pack_solo_present = rec.nbr_pack_solo_present
            nbr_inscrit = rec.nbr_pack_solo_inscrits
            if nbr_inscrit is None:
                nbr_inscrit = 0
            if nbr_inscrit > 0:
                taux_de_presence = pack_solo_present * 100 / nbr_inscrit
                if taux_de_presence > 0:
                    rec.taux_solo_presence = taux_de_presence
                else:
                    rec.taux_solo_presence = taux_de_presence
            else:
                rec.taux_solo_presence = 0

    def _compute_taux_de_presence_repassage(self):
        """ Calculer taux de presence par session selon le pack repassage """
        for rec in self:
            pack_repassage_present = rec.nbr_pack_repassage_present
            nbr_inscrit = rec.nbr_pack_repassage_inscrit
            if nbr_inscrit is None:
                nbr_inscrit = 0
            if nbr_inscrit > 0:
                taux_de_presence = pack_repassage_present * 100 / nbr_inscrit
                if taux_de_presence > 0:
                    rec.taux_repassage_presence = taux_de_presence
                else:
                    rec.taux_repassage_presence = taux_de_presence
            else:
                rec.taux_repassage_presence = 0

    @api.depends('session_id')
    def _compute_liste_client_present(self):
        for liste in self:
            # list = []
            for examen in liste.env['info.examen'].search(
                    [('date_exam', "=", liste.session_id.date_exam), ('session_id', "=", liste.session_id.id),
                     ('presence', "=", 'present')]):
                self.sudo().write({'partner_id': [(6, 0, examen.id)]})
