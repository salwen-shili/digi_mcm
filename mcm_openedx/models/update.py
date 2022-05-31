# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Update(models.Model):
    _name = 'mcm_openedx.update'

    email = fields.Char()
    coach = fields.Char()

    def update(self):
        count = 0

        # chercher dans la fiche excel les information
        for update in self.env['mcm_openedx.update'].sudo().search(
                [('coach', '!=', '')]):
            print(update.coach)
            count = count + 1
            for coach in self.env['res.partner'].sudo().search([
                ('est_coach', '=', True), ('name', 'like', update.coach)]):
                print(coach.name)

                for apprenant in self.env['res.partner'].sudo().search([
                    ('company_id', '=', 1),
                    ('email', "=", update.email)]):
                    print(coach.name)
                    #apprenant.coach_peda = coach

        print(count)
