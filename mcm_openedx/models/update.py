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
                [('email', '!=', '')]):
            count = count + 1
            for apprenant in self.env['res.partner'].sudo().search([
                ('company_id', '=', 1),
                ('email', 'ilike', update.email)]):
                print(apprenant.email)
                print(update.coach)
                apprenant.coach_peda = update.coach

        print(count)
