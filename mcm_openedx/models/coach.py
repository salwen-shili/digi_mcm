# -*- coding: utf-8 -*-
from odoo import models, fields, api


class Coach(models.Model):
    _name = 'mcm_openedx.coach'
    _description = "coaches module en va affecter pour chaque coach sa liste des apprennats"
    nombre_apprenant = fields.Integer()
    coach_name = fields.Many2one('res.partner', string="Tuteur", domain=[('est_coach', '=', True)])
    apprenant_name = fields.Many2many('res.partner', domain=[('est_coach', '=', False)])
    seats = fields.Integer(string="nombre de places")
    taken_seats = fields.Float(string="nombre des places ocuppé ", compute='_taken_seats')

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

                # print("nombre d'apprenant par coach ", coach_name, nombre_apprenant)

    # code affectation automatique , parcourir la liste des apprenants qui n'on pas  un coach_peda et lui affecter aléatoirement des coach
    def affectation_automatique(self):

        listcoach = []
        listcoachh = []
        nombre_coach = 0
        listaffecter = []
        sanscoach = 0

        for coach1 in self.env['mcm_openedx.coach'].sudo().search([('coach_name', '!=', '')]):
            nombre_coach = nombre_coach + 1

            if (coach1.coach_name.est_coach == False):
                print("n'est plus un coach ", coach1.coach_name.name)
        for apprenatsanscoach in self.env['res.partner'].sudo().search(
                [('statut', "=", "won"), ('coach_peda', '=', False), ('company_id', '=', 1)]):
            sanscoach = sanscoach + 1
            # listaffecter.append()
        print("nb sans coach", sanscoach)

        limit = divmod(sanscoach, nombre_coach)
        print("div", limit[0])
        print("Rest", limit[1])

        for coach in self.env['mcm_openedx.coach'].sudo().search([('coach_name', '!=', '')]):
            i = 0

            listexiste = []
            listexiste.append(coach.apprenant_name)
            for apprenat in self.env['res.partner'].sudo().search(
                    [('statut', "=", "won"), ('coach_peda', '=', False), ('company_id', '=', 1)],
                    limit=limit[0]):
                if apprenat.id not in listexiste:
                    print("app", apprenat.id)
                    apprenat.coach_peda = coach.coach_name
            for coachh in coach:
                listcoach.append(coachh.nombre_apprenant)
                print(coachh.coach_name.name)
                print(coachh.nombre_apprenant)
                listcoach.sort()
                print(listcoach)
                for i in range(len(listcoach)):
                    if i < i + 1:
                        print("inffffffff")
                if (listcoach[0] == coach.nombre_apprenant):
                    print("tesssssssssssssssstttttttttt",coachh.coach_name.name)
                    if apprenat.id not in listexiste:
                        apprenat.coach_peda = coach.coach_name


