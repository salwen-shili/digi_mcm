# -*- coding: utf-8 -*-
import datetime

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
    temppassetotale = fields.Char(string="Temps passé sur moocit En H : ")
    attendees_count = fields.Integer(
        string="Temps passée", compute='_get_attendees_count', store=True)
    partner = fields.Many2one('res.partner')

    @api.depends('temppasse')
    def _get_attendees_count(self):
        for r in self:
            r.attendees_count = len(r.temppasse)

    def recherche(self):
        temppassetotale = 0
        # chercher dans la partie cour le mail et calculer le temps passer sur moocit
        for exist in self.env['mcm_openedx.course_stat'].sudo().search(
                [('email', "=", self.email)]):

            if (exist):
                temppassetotale = exist.seconde + temppassetotale
                heure = temppassetotale / 3600
                self.temppassetotale = heure
        temppassetotale = self.temppassetotale
        print(temppassetotale)
        self.partner=exist.partner.id
        # chercher ddans res partner l'user qui possede le meme email pour lui affecter les valeurs
        for apprenant in self.env['res.partner'].sudo().search([('statut', "=", "won"),
                                                                ('company_id', '!=', 2),
                                                                ('email', 'ilike', exist.email)]):
            print(apprenant.email)
            print("sss", self.email)
            # deux jour erreur :) psk maj vs mini :)
            apprenant.date_imortation_stat = datetime.date.today()
            apprenant.mooc_temps_passe = temppassetotale
            apprenant.mooc_dernier_coonx = exist.jour
        exist.partner = apprenant.id
        print(exist.partner.name)
