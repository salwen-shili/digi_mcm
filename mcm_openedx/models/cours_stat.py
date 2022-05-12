# -*- coding: utf-8 -*-
from datetime import datetime, date, timedelta

from odoo import models, fields, api
import numpy as np


class Cours_stat(models.Model):
    _name = 'mcm_openedx.course_stat'
    _description = "importer les listes des cours pour calculer les statestiques"
    name = fields.Char(string="Nom Utilisateur")
    email = fields.Char(string="Email")
    color = fields.Char(string="color")
    idcour = fields.Char(string="ID Cours")
    jour = fields.Date(string="Jour")
    temppasse = fields.Char(string="Temps passés")
    seconde = fields.Float(string="Temps passés (sec)")
    temppassetotale = fields.Integer(string="Temps Totale")
    attendees_count = fields.Integer(string="Temps passée", compute='_get_attendees_count', store=True)
    partner = fields.Many2one('res.partner')
    mooc_temps_passe_heure = fields.Integer(string="temps passé en heure")
    mooc_temps_passe_min = fields.Integer(string="temps passé en minute")
    mooc_temps_passe_seconde = fields.Integer(string="temps passé en Seconde")

    @api.depends('temppasse')
    def _get_attendees_count(self):
        for r in self:
            r.attendees_count = r.mooc_temps_passe_heure

    def calcul_temps_total(self):
        temppassetotale = 0
        listjour = []

        for existt in self.env['mcm_openedx.course_stat'].sudo().search(
                [('email', "=", self.email)]):
            temppassetotale = existt.seconde + temppassetotale
            heure = int((temppassetotale / 3600))
            minute = int((temppassetotale - (3600 * heure)) / 60)
            secondes = int(temppassetotale - (3600 * heure) - (60 * minute))
            timee = (heure, minute, secondes)

            listjour.append(existt.jour)
            # affecter les jours a une liste pour faire le tri et extraire la derniere et la premiere date de connexion
            listjour.sort()
        print("lowwww", listjour[0])
        print("highhh", listjour[-1])

        # chercher ddans res partner l'user qui possede le meme email pour lui affecter les valeurs
        for apprenant in self.env['res.partner'].sudo().search([
            ('company_id', '!=', 2),
            ('email', 'ilike', existt.email)]):
            apprenant.date_imortation_stat = date.today()
            apprenant.mooc_temps_passe_heure = heure
            apprenant.mooc_temps_passe_min = minute
            apprenant.mooc_temps_passe_seconde = secondes
            apprenant.mooc_dernier_coonx = listjour[-1]
            if (apprenant.inscrit_mcm == False):
                apprenant.inscrit_mcm = listjour[0]

            existt.partner = apprenant.id
            self.partner = existt.partner
            self.mooc_temps_passe_heure = heure
            self.mooc_temps_passe_min = minute
            self.mooc_temps_passe_seconde = secondes

    def supprimer_duplicatio(self):
        # cree une  liste pour stocker les duplication
        listcourduplicated = []
        print("tacheeee supppppppppppp")
        # chercher tout personne ayant un mail existant
        for exist in self.env['mcm_openedx.course_stat'].sudo().search(
                [('email', "!=", False)]):
            # verifier si la personne ayant les meme information
            if exist.id not in listcourduplicated:
                # chercher mail ,idcour,jour,id
                duplicates = self.env['mcm_openedx.course_stat'].search(
                    [('email', "=", exist.email), ('idcour', '=', exist.idcour), ('jour', "=", exist.jour),
                     ('id', '!=', exist.id)
                     ])
                # parcourir la liste de duplication
                for dup in duplicates:
                    # ajouter les duplicant a la liste
                    listcourduplicated.append(dup.id)
        # supprimer duplication
        self.browse(listcourduplicated).sudo().unlink()
