# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Update(models.Model):
    _name = 'mcm_openedx.update'

    email = fields.Char()
    coach = fields.Char()

    def update(self):
        # chercher les coaches
        for coach in self.env['res.partner'].sudo().search(
                [('est_coach', '=', 'True')]):
            # chercher dans la fiche excel les information
            for cour in self.env['mcm_openedx.update'].sudo().search(
                    []):
                # chercher dans fiche client les personne ayant la liste
                # des personnes ayant le meme mail que la liste dans excel
                for rec in self.env['res.partner'].sudo().search(
                        [('email', "=", cour.email)]):
                    # Si la personne dans la fiche excel possede le meme mail
                    # affecter le nom de coach sur la fiche excel
                    if (cour.email == rec.email):
                         rec.coach_peda = coach.id

                    else:
                        print("non")
