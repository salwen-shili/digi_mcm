# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Cours(models.Model):
    _name = 'mcm_openedx.course'
    _description = "importer les listes des cours"
    partner = fields.Many2one('res.partner', string='Apprenant')
    nomutilisateur = fields.Char(string="Nom Utilisateur")
    email = fields.Char(string="Email")
    idcour = fields.Char(string="ID Cours")
    jour = fields.Date(string="Jour")
    temppasse = fields.Char(string="Temps passés")
    seconde = fields.Char(setup="	Temps passés (sec)")
    color = fields.Integer()
    attendees_count = fields.Integer(
        string="Temps passée", compute='_get_attendees_count', store=True)

    @api.depends('temppasse')
    def _get_attendees_count(self):
        for r in self:
            r.attendees_count = len(r.temppasse)

    def recherche(self):

        for recc in self.env['res.partner'].sudo().search([('email', "like", '@')
                                                           ]):
            tmp = 0
            for exist in self.env['mcm_openedx.course'].sudo().search(
                    [('email', "=", recc.email), ('temppasse', '=', self.temppasse)
                     ]):
                if (exist.email == recc.email):
                    tmp = int(exist.temppasse) + tmp
                print(tmp)
