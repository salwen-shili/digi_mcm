# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Update(models.Model):
    _name = 'mcm_openedx.update'
    _description = 'mcm_openedx.update'

    email = fields.Char()
    coach = fields.Char()

    def update(self):
        count = 0
        # chercher dans la fiche excel les information
        listapprenant = []
        for update in self.env['mcm_openedx.update'].sudo().search(
                [('coach', 'like', self.coach)]):
            count = count + 1
            print(update.coach)
            print(update.email)

            countexist = 0
            for app in self.env['res.partner'].sudo().search(
                    [('email', "=", update.email)]):
                countexist = countexist + 1
                listapprenant.append(app.id)
                print(listapprenant)
                list_coach = []
                for coach in self.env['mcm_openedx.coach'].sudo().search(
                        []):
                    print(coach.coach_name)
                    if (coach.coach_name.id == 15000):
                        if app.id in listapprenant:
                            print("app", app.id)
                            print(coach.coach_name)
                            app.coach_peda = coach.coach_name
                            coach.sudo().write({'apprenant_name': [(6, 0, listapprenant)],
                                                })


                    elif (coach.coach_name.id == 14682):
                        if app.id in listapprenant:
                            print("app", app.id)
                            print("app", app.email)
                            print(coach.coach_name)
                            app.coach_peda = coach.coach_name
                            coach.sudo().write({'apprenant_name': [(6, 0, listapprenant)],
                                                })

                    elif (coach.coach_name.id == 19018):
                        if app.id not in listapprenant:
                            print("app", app.id)
                            print(coach.coach_name)
                            app.coach_peda = coach.coach_name
                            coach.sudo().write({'apprenant_name': [(6, 0, listapprenant)],
                                                   })

        print(count)
