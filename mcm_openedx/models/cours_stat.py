# -*- coding: utf-8 -*-
import datetime

from odoo import models, fields, api


class Cours_stat(models.Model):
    _name = 'mcm_openedx.course_stat'
    _description = "importer les listes des cours pour calculer les statestiques"
    #
    # nomutilisateur = fields.Char(string="Nom Utilisateur")
    # email = fields.Char(string="Email")
    # idcour = fields.Char(string="ID Cours")
    # jour = fields.Date(string="Jour")
    # temppasse = fields.Char(string="Temps passés")
    # seconde = fields.Integer(setup="	Temps passés (sec)")
    # color = fields.Integer()
    # temppassetotale = fields.Char(string="Temps passé sur moocit En H : ")
    # attendees_count = fields.Integer(
    #     string="Temps passée", compute='_get_attendees_count', store=True)
    # partner = fields.Many2one('res.partner')
    #
    # @api.depends('temppasse')
    # def _get_attendees_count(self):
    #     for r in self:
    #         r.attendees_count = len(r.temppassetotale)
    #
    # def recherche(self):
    #     temppassetotale = 0
    #
    #     # chercher dans la partie cour le mail et calculer le temps passer sur moocit
    #     for exist in self.env['mcm_openedx.course_stat'].sudo().search(
    #             [('email', "=", self.email)]):
    #         listjour = []
    #         listjour.append(exist.jour)
    #         listjour.sort()
    #
    #
    #         if (exist):
    #             temppassetotale = exist.seconde + temppassetotale
    #             heure = temppassetotale / 3600
    #             self.temppassetotale = heure
    #         exist.temppassetotale = self.temppassetotale
    #
    #         # chercher ddans res partner l'user qui possede le meme email pour lui affecter les valeurs
    #
    #
    #         for apprenant in self.env['res.partner'].sudo().search([
    #             ('company_id', '!=', 2),
    #             ('email', 'ilike', exist.email)]):
    #             apprenant.date_imortation_stat = datetime.date.today()
    #             apprenant.mooc_temps_passe = exist.temppassetotale
    #             apprenant.mooc_dernier_coonx = exist.jour
    #             exist.partner = apprenant.id
    #             self.partner = exist.partner
