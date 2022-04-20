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
    seconde = fields.Integer(setup="	Temps passés (sec)")
    color = fields.Integer()
    temppassetotale = fields.Integer(string="Temps passé sur moocit ")
    attendees_count = fields.Integer(
        string="Temps passée", compute='_get_attendees_count', store=True)

    @api.depends('temppasse')
    def _get_attendees_count(self):
        for r in self:
            r.attendees_count = len(r.temppasse)

    def recherche(self):
        for exist in self.env['mcm_openedx.course'].sudo().search(
                [('email', "=", self.email)
                 ]):
            temppassetotale = 0
            if (exist):
                exist.temppassetotale = exist.seconde + exist.temppassetotale

        print(exist.temppassetotale)
