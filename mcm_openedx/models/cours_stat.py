# -*- coding: utf-8 -*-
from datetime import date

from odoo import models, fields, api


class Cours_stat(models.Model):
    _name = 'mcm_openedx.course_stat'
    _description = "importer les listes des cours pour calculer les statestiques"
    partner = fields.Many2one('res.partner', string='Apprenant')
    nomutilisateur = fields.Char(string="Nom Utilisateur")
    email = fields.Char(string="Email")
    idcour = fields.Char(string="ID Cours")
    jour = fields.Date(string="Jour")
    temppasse = fields.Char(string="Temps passés")
    seconde = fields.Integer(setup="	Temps passés (sec)")
    color = fields.Integer()
    temppassetotale = fields.Float(string="Temps passé sur moocit En H : ")
    attendees_count = fields.Integer(
        string="Temps passée", compute='_get_attendees_count', store=True)

    @api.depends('temppasse')
    def _get_attendees_count(self):
        for r in self:
            r.attendees_count = len(r.temppasse)

    def recherche(self):
        temppassetotale = 0
        for exist in self.env['mcm_openedx.course_stat'].sudo().search([('email', "=", self.email)]):
            if (exist):
                print(exist.seconde)
                temppassetotale = exist.seconde + temppassetotale
                print(temppassetotale)
                heure = temppassetotale / 3600
                minute = (temppassetotale - (3600 * heure)) / 60
                # time = (heure)
                time = minute
            print(time)
            self.temppassetotale = time
            app = self.env['res.partner'].sudo().search([('email', "=", exist.email)])
            if (app.email == exist.email):
                print(app.email)
                print(exist.email)
                app.mooc_temps_passe = time
                app.mooc_dernier_coonx = exist.jour
                app.date_imortation_stat = date.today()
