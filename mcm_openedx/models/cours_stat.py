# -*- coding: utf-8 -*-
from datetime import datetime, date, timedelta

from odoo import models, fields, api
import numpy as np
import logging

_logger = logging.getLogger(__name__)


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
            # print("lowwww", listjour[0])
            # print("highhh", listjour[-1])
            # chercher ddans res partner l'user qui possede le meme email pour lui affecter les valeurs
            mail_evalbox = self.env['res.partner'].search(
                [('company_id', '!=', 2), ('id_evalbox', 'ilike', existt.email)])
            print(mail_evalbox.id_evalbox)
            for apprenant in self.env['res.partner'].sudo().search([('company_id', '!=', 2),
                                                                    ('email', 'ilike', existt.email)]):

                # print("statteeeeeeeeeee", apprenant.state)
                apprenant.date_imortation_stat = date.today()
                apprenant.mooc_temps_passe_heure = heure
                apprenant.mooc_temps_passe_min = minute
                apprenant.mooc_temps_passe_seconde = secondes
                apprenant.mooc_dernier_coonx = listjour[-1]
                if (apprenant.inscrit_mcm == False):
                    apprenant.inscrit_mcm = listjour[0]
                existt.partner = apprenant.id
                apprenant.partner = existt.partner
                apprenant.mooc_temps_passe_heure = heure
                apprenant.mooc_temps_passe_min = minute
                apprenant.mooc_temps_passe_seconde = secondes
                todays_date = date.today()
                if (apprenant.mooc_dernier_coonx):
                    if (apprenant.state != 'en_formation') and (apprenant.mooc_dernier_coonx.year == todays_date.year):
                        apprenant.state = 'en_formation'

    def suupprimer_bouton_fiche_client(self):
        # cree une  liste pour stocker les duplication
        listcourduplicated = []
        temppassetotale = 0
        listjour = []
        # chercher tout personne ayant un mail existant
        for exist in self.env['mcm_openedx.course_stat'].sudo().search(
                [('email', "=", self.email)]):
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

    def supprimer_duplicatio(self):
        # cree une  liste pour stocker les duplication
        listcourduplicated = []
        _logger.info('supprimer duplicationnn %s')

        # chercher tout personne ayant un mail existant
        for exist in self.env['mcm_openedx.course_stat'].sudo().search(
                [('email', "!=", False)]):
            # verifier si la personne ayant les meme information
            if exist.id not in listcourduplicated:
                # chercher mail ,idcour,jour,id
                duplicates = self.env['mcm_openedx.course_stat'].search(
                    [('email', "=", exist.email), ('idcour', '=', exist.idcour), ('jour', "=", exist.jour),
                     ('id', '!=', exist.id)])
                # parcourir la liste de duplication
                for dup in duplicates:
                    # ajouter les duplicant a la liste
                    listcourduplicated.append(dup.id)
        # supprimer duplication
        _logger.info('dupplication %s' % str(listcourduplicated))

        self.browse(listcourduplicated).sudo().unlink()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }


class actif_inactif(models.Model):
    _name = 'mcm_openedx.state'
    _description = "importer les listes des cours pour calculer les statestiques"
    # # # add new fields
    statut = fields.Char(string="Statut")

    genre = fields.Char(string="Genre")
    email = fields.Char(string="Email")
    idcour = fields.Char(string="ID Cours")

    @api.depends('statut')
    def _get_attendees_count(self):
        for r in self:
            r.statut = len(r.statut)

    def test_app(self):
        # cree une  liste pour stocker les duplication
        listcourduplicated = []
        _logger.info('supprimer duplicationnn %s')

        # chercher tout personne ayant un mail existant
        for exist in self.env['mcm_openedx.state'].sudo().search(
                [('email', "!=", False)]):
            # verifier si la personne ayant les meme information
            if exist.id not in listcourduplicated:
                # chercher mail ,idcour,jour,id
                duplicates = self.env['mcm_openedx.state'].search(
                    [('email', "=", exist.email), ('idcour', '=', exist.idcour) ,
                     ('id', '!=', exist.id)])
                # parcourir la liste de duplication
                for dup in duplicates:
                    # ajouter les duplicant a la liste
                    listcourduplicated.append(dup.id)
        # supprimer duplication
        _logger.info('dupplication %s' % str(listcourduplicated))

        self.browse(listcourduplicated).sudo().unlink()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
