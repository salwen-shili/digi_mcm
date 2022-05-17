# -*- coding: utf-8 -*-

from odoo import models, fields, api, SUPERUSER_ID


class Coach(models.Model):
    _name = 'mcm_openedx.coach'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    _description = "coaches module en va affecter pour chaque coach sa liste des apprennats"
    name = fields.Char(string="Coaches")
    nombre_apprenant = fields.Integer()
    coach_name = fields.Many2one('res.partner', string="Tuteur", domain=[('est_coach', '=', True)])
    apprenant_name = fields.Many2many('res.partner', domain=[('est_coach', '=', False)])
    seats = fields.Integer(string="nombre de places")
    taken_seats = fields.Float(string="nombre des places ocuppé ", compute='_taken_seats')
    commentaire = fields.Char(string="Commentaires")
    color = fields.Integer()
    apprenant_email = fields.Char()

    @api.depends('seats', 'apprenant_name')
    def _taken_seats(self):
        for r in self:
            if not r.seats:
                r.taken_seats = 0.0
            else:
                r.taken_seats = 100.0 * len(r.apprenant_name) / r.seats

    # tester le nombre des coach et le nombre d'apprenant pour chaque un  , pour controller l'affectation des apprenants pour chaque'un
    @api.depends('nombre_apprenant', 'coach_name', 'apprenant_name', 'seats')
    def test_coach(self):
        count_apprennat = 0
        # determiner le nombre total des apprenants
        for apprenant in self.env['res.partner'].sudo().search([('statut', "=", "won"), ('company_id', '=', 1)]):
            count_apprennat = count_apprennat + 1


        # definir si le partner et coach
        for coach in self.env['res.partner'].sudo().search(
                [('est_coach', '=', 'True')]):
            count = 0

            # extraire les client ganger ayant le meme nom de coach dans la liste des partner
            # crer une liste pour stocker les apprennats ayant les informations que en est en train de chercher
            listapprenant = []
            for rec in self.env['res.partner'].sudo().search(
                    [('statut', "=", "won"), ('coach_peda', 'like', coach.name)]):

                if (rec.coach_peda.name == coach.name):
                    count = count + 1
                    # stoker dans la liste les apprennats
                    listapprenant.append(rec.id)

            nombre_apprenant = count
            # si le partner est un coach alors en va verifier si il existe deja dans la liste des coach pour lui affecter les apprenants

            if (coach):

                coach_name = coach.name
                print("coachs names", coach_name)
                # verfier dans la class Coach si il existe un coach ayant le meme nom que le coach affecter pour les apprenants

                exist = self.env['mcm_openedx.coach'].sudo().search([('coach_name', '=', coach.id)])
                # si le coach existe alors en va lui affecter la liste des apprenats ayant le nom de ce caoch

                if (exist):
                    exist.seats = count_apprennat
                    exist.nombre_apprenant = nombre_apprenant
                    exist.sudo().write({'apprenant_name': [(6, 0, listapprenant)],
                                        })

                # si non en va creé le coach
                if not exist:
                    newcoach = self.env['mcm_openedx.coach'].sudo().create({
                        'coach_name': coach.id, })
                    newcoach.seats = count_apprennat
                    newcoach.nombre_apprenant = nombre_apprenant
                    newcoach.sudo().write({'apprenant_name': [(6, 0, listapprenant)],
                                           })

                print("nombre d'apprenant par coach ", coach_name, nombre_apprenant)

    # chercher les nombre des apprennats qui n'on pas des coach et
    # chercher le nombre d'apprennats par  coach pour voir la differance et affecter les apprenat aux coach qui a le nombre inferieur aux autres
    def egalité(self):
        # ctrlf8
        self.test_coach()

        listcoach = []
        nombre_coach = 0
        sanscoach = 0
        # calculer nb coach
        for coach1 in self.env['mcm_openedx.coach'].sudo().search(
                [('coach_name', '!=', '')]):
            nombre_coach = nombre_coach + 1
            listcoach.append(coach1.nombre_apprenant)
            listcoach.sort()
            print(listcoach)
            print(listcoach[0])
            # calculer nb apprenants sans coaches
        for apprenatsanscoach in self.env['res.partner'].sudo().search(
                [('statut', "=", "won"), ('coach_peda', '=', False), ('company_id', '=', 1)]):
            sanscoach = sanscoach + 1
            # listaffecter.append()
        print("nb sans coach", sanscoach)
        limit = divmod(sanscoach, nombre_coach)
        print("div", limit[0])
        print("Rest", limit[1])
        for coach in self.env['mcm_openedx.coach'].sudo().search(
                [('coach_name', '!=', ''), ('nombre_apprenant', '=', listcoach[0])], limit=1):
            i = 0
            for apprenat in self.env['res.partner'].sudo().search(
                    [('statut', "=", "won"), ('coach_peda', '=', False), ('company_id', '=', 1)],
                    limit=limit[0]):
                # a = apprenat.coach_peda.id
                # team = self.env['helpdesk.team'].sudo().search([('name', "=", 'Coach_team')], limit=1)
                # print("team", team)
                # vals = {
                #     'partner_email': coach.coach_name.email,
                #     'partner_id': False,
                #     'email_cc': "khouloudachour.97@gmail.com",
                #     'user_id': a,
                #     'description': 'new apprenat assgned to youuuuu',
                #     'name': 'Ticket coach: new apprenat assigned to youuuuu ',
                #     'team_id': team.id,
                # }
                # print("vals", vals)
                # coach_ticket = self.env['helpdesk.ticket'].sudo().create(
                #     vals)
                # print("coach_ticket", coach_ticket)
                # # send mail
                #
                # print("tesssssssssssssssstttttttttt", coach.coach_name.name)
                coach.apprenant_email = apprenat.name
                listexiste = []
                listexiste.append(coach.apprenant_name)
                coach.lang = 'fr_FR'
                if self.env.su:
                    # sending mail in sudo was meant for it being sent from superuser
                    selff = self.with_user(SUPERUSER_ID)
                    template_id = int(self.env['ir.config_parameter'].sudo().get_param(
                        'mcm_openedx.mail_coachh'))
                    template_id = self.env['mail.template'].search([('id', '=', template_id)]).id
                    if not template_id:
                        template_id = self.env['ir.model.data'].xmlid_to_res_id(
                            'mcm_openedx.mail_coachh',
                            raise_if_not_found=False)
                    if not template_id:
                        template_id = self.env['ir.model.data'].xmlid_to_res_id(
                            'mcm_openedx.email_coachh',
                            raise_if_not_found=False)
                    if template_id:
                        coach.with_context(force_send=True).message_post_with_template(template_id,
                                                                                       composition_mode='comment', )
                        # ajouter une fonction pour connaitre l'utilisateur connecter et lui notifier si il a un nouveau apprenant
                        context = self._context
                        current_uid = context.get('uid')
                        user = self.env['res.users'].browse(current_uid)
                        print("emaillllllllllll", user.email)
                        if (user.email == coach.coach_name.email):
                            return {
                                'type': 'ir.actions.client',
                                'tag': 'display_notification',
                                'params': {
                                    'title': (' You have a new Mail🤓 🤓  '),
                                    'message': ('consulter votre boite  maill'),
                                    'sticky': True,
                                    'className': 'bg-danger'
                                }
                            }

                if apprenat.id not in listexiste:
                    print("app", apprenat.id)
                    print(coach.coach_name)
                    apprenat.coach_peda = coach.coach_name

                # appeler la fonction pour affecter les apprenats aux coach
            self.test_coach()
