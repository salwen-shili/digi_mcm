# -*- coding: utf-8 -*-
from datetime import datetime, date, timedelta

from odoo import models, fields, api


class Cours_stat(models.Model):
    _name = 'mcm_openedx.course_stat'
    _description = "importer les listes des cours pour calculer les statestiques"
    name = fields.Char('Name')
    nomutilisateur = fields.Char(string="Nom Utilisateur")
    email = fields.Char(string="Email")
    color = fields.Char(string="color")
    idcour = fields.Char(string="ID Cours")
    jour = fields.Date(string="Jour")
    temppasse = fields.Char(string="Temps passés")
    seconde = fields.Float(string="Temps passés (sec)")
    temppassetotale = fields.Integer(string="Temps Totale")
    attendees_count = fields.Integer(string="Temps passée", compute='_get_attendees_count', store=True)
    partner = fields.Many2one('res.partner')

    @api.depends('temppasse')
    def _get_attendees_count(self):
        for r in self:
            r.attendees_count = r.temppassetotale

    def recherche(self):
        temppassetotale = 0
        # chercher dans la partie cour le mail et calculer le temps passer sur moocit
        for exist in self.env['mcm_openedx.course_stat'].sudo().search(
                [('email', "=", self.email)]):
            # eliminer repetion in days

            if (exist):
                print(exist.seconde)
                temppassetotale = exist.seconde + temppassetotale
                print("totale22", temppassetotale)
                q, s = divmod(temppassetotale, 60)
                h, m = divmod(q, 60)
            print("%d:%d:%d" % (h, m, s))
            heure = int((temppassetotale / 3600))
            minute = int((temppassetotale - (3600 * heure)) / 60)
            secondes = int(temppassetotale - (3600 * heure) - (60 * minute))
            timee = (heure, minute, secondes)
            print("timmmmme", minute)
            # chercher ddans res partner l'user qui possede le meme email pour lui affecter les valeurs
            for apprenant in self.env['res.partner'].sudo().search([
                ('company_id', '!=', 2),
                ('email', 'ilike', exist.email)]):
                apprenant.date_imortation_stat = date.today()
                apprenant.mooc_temps_passe_heure = heure
                apprenant.mooc_temps_passe_min = minute
                apprenant.mooc_temps_passe_seconde = secondes
                apprenant.mooc_dernier_coonx = exist.jour
                exist.partner = apprenant.id
                self.partner = exist.partner
                # self.sudo().with_context(key=existt.id).sudo().unlink()
