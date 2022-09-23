# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import locale
import logging
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import random
from num2words import num2words

from datetime import datetime, timedelta, date

_logger = logging.getLogger(__name__)

class Session(models.Model):
    _name = 'mcmacademy.session'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Sessions de formation"

    name = fields.Char('Nom du session', required=True, track_visibility='always')

    type_client = fields.Selection(selection=[
        ('intra', 'INTRA'),
        ('inter_entreprise', 'INTER ENTREPRISE'),
    ], string='Type de client', copy=True)
    # copy=True : the field will be automaticly duplicated when we duplicate the session
    # copy=False : the field will not be duplicated when we duplicate the session and he will get his default value
    sous_traitance = fields.Boolean("Réalisé en sous traitance d'un autre organisme", copy=True)
    action_type_id = fields.Many2one('mcmacademy.action', string="Type d'action de formation", copy=True)
    domaine_formation = fields.Many2one('mcmacademy.domain', string='Domaine de formation', copy=True)
    diplome_vise = fields.Char('Diplôme visé par la formation', copy=True, track_visibility='always')
    module_ids = fields.One2many('mcmacademy.module', inverse_name='session_id', string='Liste des modules', copy=True)
    client_ids = fields.Many2many('res.partner', 'session_clients_rel', 'session_id', 'client_id', string='',
                                  copy=False)
    prospect_ids = fields.Many2many('res.partner', 'session_prospect_rel', 'session_id', 'prospect_id', string='',
                                    copy=False)
    canceled_prospect_ids = fields.Many2many('res.partner', 'session_canceled_prospect_rel', 'session_id',
                                             'prospect_id', string='', copy=False)
    panier_perdu_ids = fields.Many2many('res.partner', 'session_panier_perdu_rel', 'session_id', 'prospect_id',
                                        string='', copy=False)
    stage_id = fields.Many2one('mcmacademy.stage', 'État', group_expand='_read_group_stage_ids')
    color = fields.Integer(string='Color Index', copy=True)
    date_debut = fields.Date('Date de debut de session', copy=False)
    date_fin = fields.Date('Date de fin de session', copy=False)
    count = fields.Integer('Nombre des clients', compute='_count_clients', copy=False)
    number = fields.Char('Numéro', compute='_get_session_number')
    count_client = fields.Integer('', compute='_compute_count_clients', copy=False)
    count_stagiaires = fields.Integer('', compute='_compute_count_clients', copy=False)
    count_perdu = fields.Integer('', compute='_compute_count_clients', copy=False)
    count_annule = fields.Integer('', compute='_compute_count_clients', copy=False)
    count_prospect = fields.Integer('', compute='_compute_count_clients', copy=False)
    count_panier_perdu = fields.Integer('', compute='_compute_count_clients', copy=False)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    # Les champs pour le rapport jury
    ville_jury_id = fields.Many2one('session.ville', string="Ville de jury",
                                    track_visibility='always')  # edit the field to be required and show field edit history
    adresse_jury_id = fields.Many2one('session.adresse.examen', "Adresse de jury")
    date_jury = fields.Date()

    @api.onchange('adresse_jury_id')
    def onchange_session_ville_id(self):
        """ Cette fonction pour afficher la liste des adresses de centre d'examen
        liée par une seul ville choisi par l'utilisateur dans l'interface de session"""
        for rec in self:
            return {'domain': {'adresse_jury_id': [('adresse_jury_id', '=', rec.ville_jury_id.id)]}}

    # define a function in python to convert
    def date_to_text(self, yearformat, dayformat):
        """ Convertir date vers lettre en utilisant la bibliothéque python: num2words (pour template de rapport jury)"""
        date = self.date_exam
        yearformat = "%Y"
        dayformat = "%d"
        yearformat = (int(date.strftime(yearformat)))
        dayformat = (int(date.strftime(dayformat)))
        yearformat_txt = num2words(yearformat, lang='fr').upper().replace(',', ' ')
        dayformat_txt = num2words(dayformat, lang='fr').upper()
        date_en_lettre = yearformat_txt + " " + dayformat_txt
        return date_en_lettre

    # def nbr_client_par_session(self, nbr_inscrits):
    #     """ Cette fonction permet de faire la somme d'inscrit de nombre de client avec statut (gagné, annulé et perdu).
    #      La fonction est utilisé dans la template de rapport jury"""
    #     nbr_inscrits = 0
    #     nbr_inscrits = nbr_inscrits + self.count_stagiaires + self.count_annule + self.count_panier_perdu + self.count_perdu
    #     return nbr_inscrits

    def nombre_abandon(self, nbr_ab):
        """ Nombre d'abandon"""
        nbr_ab = 0
        nbr_ab = self.nbr_canceled_state_after_14_day(self)
        return nbr_ab

    def nbr_client_par_session(self, nbr_inscrits):
        """ Cette fonction permet de faire la somme d'inscrit de nombre de client avec statut (gagné, annulé et perdu).
         La fonction est utilisé dans la template de rapport jury"""
        nbr_inscrits = 0
        today = date.today()
        nbr_partner_cpf_annule= self.env['partner.sessions'].sudo().search(
            [('date_exam', "=", self.date_exam), ('session_id', "=", self.id), ('client_id.mode_de_financement','=', 'cpf'),('client_id.statut','=', 'canceled'),('date_creation', ">", self.date_exam + timedelta(days=14))])
        _logger.info("nbr_partner_annule %s" % str(nbr_partner_cpf_annule))
        nbr_partner_won_cpf = self.env['partner.sessions'].sudo().search(
            [('date_exam', "=", self.date_exam), ('session_id.id', "=", self.id), ('client_id.statut','=', 'won')])
        _logger.info("nbr_partner_won_cpf %s" % str(nbr_partner_won_cpf))

        nbr_partner_personel_annule = self.env['partner.sessions'].sudo().search(
            [('date_exam', "=", self.date_exam), ('session_id.id', "=", self.id), ('client_id.mode_de_financement','=', 'particulier'), ('client_id.statut','=', 'canceled')])
        count_per_an = False
        for sale in nbr_partner_personel_annule:

            if sale.client_id.signed_on > self.date_exam + timedelta(days=14):
                count_per_an += 1
        counter_per_an = count_per_an
        _logger.info("nbr_partner_personel_annule %s" % str(nbr_partner_personel_annule))
        nbr_inscrits = len(nbr_partner_cpf_annule) + len(nbr_partner_won_cpf) + counter_per_an
        return nbr_inscrits
        # for examen in nbr_partner_sessions:
        #     if nbr_partner_sessions.mode_de_financement == 'cpf' and nbr_partner_sessions.partner_id.statut == 'won':
        #         nbr_inscrits += 1
        #     return nbr_inscrits
        # if nbr_partner_sessions.mode_de_financement == 'particulier':
        #     sale_order = self.env['sale.order'].sudo().search([('session_id.id', '=',
        #                                                         self.id),
        #                                                        ('module_id', '=', self.module_id.id),
        #                                                        ('session_id.date_exam', '>',
        #                                                         date.today())], limit=1)
        #     for sale in sale_order:
        #         sign_date = sale.signed_on
    #     nbr_inscrits = nbr_inscrits + self.count_stagiaires + self.count_annule + self.count_panier_perdu + self.count_perdu

    def nbr_present_par_session(self, nbr_present):
        """ Cette fonction permet de faire la somme d'inscrit de nombre de client avec statut (gagné, annulé et perdu).
         La fonction est utilisé dans la template de rapport jury"""
        nbr_present = self.client_ids.filtered(lambda cl: cl.presence == 'Présent(e)')
        return len(nbr_present)

    def prc_present(self, prc_present):
        nbr_present = self.nbr_present_par_session(self)
        nbr_inscrit = self.nbr_client_par_session(self)
        if nbr_inscrit > 0:
            res = (nbr_present * 100 / nbr_inscrit)
            prc_present = f'{res:.2f}'.replace('.00', '')
            return prc_present

    def nbr_recus_par_session(self, total_nbr_recu):
        """ Nombre de recus par session"""
        for examen in self.env['info.examen'].search([('date_exam', "=", self.date_exam)]):
            if examen:
                nbr_recu = examen.env['info.examen'].search_count(
                    [('session_id', "=", self.id), ('resultat', "=", 'recu')])
                total_nbr_recu = nbr_recu
        return total_nbr_recu

    # takwa
    def nbr_recus_solo(self):
        """ Nombre d'admis par session Solo"""
        nbr_recu_solo = 0
        x = self.env['info.examen'].sudo().search(
            [('date_exam', "=", self.date_exam), ('session_id', "=", self.id), ('resultat', "=", 'recu')])
        for examen in x:
            if examen.module_id.product_id.default_code == "basique":
                nbr_recu_solo += 1
        return nbr_recu_solo

    def nbr_recus_pro(self):
        """ Nombre d'admis par session pro"""
        nbr_recu_pro = 0
        x = self.env['info.examen'].sudo().search(
            [('date_exam', "=", self.date_exam), ('session_id', "=", self.id), ('resultat', "=", 'recu')])
        for examen in x:
            if examen.module_id.product_id.default_code == "avancee":
                nbr_recu_pro += 1
        return nbr_recu_pro

    def nbr_recus_premium(self):
        """ Nombre d'admis par session premium"""
        nbr_recu_premium = 0
        x = self.env['info.examen'].sudo().search(
            [('date_exam', "=", self.date_exam), ('session_id', "=", self.id), ('resultat', "=", 'recu')])
        for examen in x:
            if examen.module_id.product_id.default_code == "premium":
                nbr_recu_premium += 1
        return nbr_recu_premium

    def nbr_recus_repassage(self):
        """ Nombre d'admis par session repassage"""
        nbr_recu_repassage = 0
        for examen in self.env['info.examen'].search(
                [('date_exam', "=", self.date_exam), ('session_id', "=", self.id), ('resultat', "=", 'recu')]):
            if examen:
                if examen.module_id.product_id.default_code == "examen":
                    nbr_recu_repassage += 1
        return nbr_recu_repassage

    def pourcentage_client_recu(self, pourcentage):
        """ Calculer pourcentage clients reçus"""
        nbr_recu_total = self.nbr_recus_par_session(self)
        nbr_present_total = self.nbr_present_par_session(self)
        pourcentage_without_round = 0
        if nbr_present_total > 0:
            pourcentage_without_round = (nbr_recu_total * 100 / nbr_present_total)
            pourcentage = f'{pourcentage_without_round:.2f}'.replace('.00',
                                                                     '')  # Garder justes deux chiddre après la virgule
            return pourcentage
        else:
            pourcentage = f'{pourcentage_without_round:.0f}'  # si 0 la resultat sera 0 %
            return pourcentage

    def date_session_frensh(self, date_examen):
        """ FORCER la date en francais par ce que odoo.sh applique """
        date_format = '%d %B %Y'
        locale.setlocale(locale.LC_TIME, str(self.env.user.lang) + '.utf8')
        date_examen = (self.date_exam).strftime(date_format).title()
        return date_examen

    def month_session_in_lettre(self, month_format):
        """ Fonction qui affiche les mois de date d'examen en lettres et en majuscules"""
        month_format = '%B'
        locale.setlocale(locale.LC_TIME, str(self.env.user.lang) + '.utf8')
        month_format = (self.date_exam).strftime(month_format).upper()
        return month_format

    def calculer_nombre_absence(self, total_absence):
        """ Calculer nombre des absences par session"""
        nbr_absence = 0
        for examen in self.env['info.examen'].search([('date_exam', "=", self.date_exam)]):
            if examen.partner_id.statut == 'won':
                nbr_absence = examen.env['info.examen'].search_count(
                    [('session_id', "=", self.id), ('presence', "=", 'Absent')])
            total_absence = nbr_absence
            return total_absence

    def pourcentage_absence(self, resultat):
        """ Pourcentage pour les absences par session"""
        nbr_absence = self.calculer_nombre_absence(self)
        nbr_inscrit = self.nbr_client_par_session(self)
        if nbr_inscrit > 0:
            res = (nbr_absence * 100 / nbr_inscrit)
            if res > 0:
                resultat = f'{res:.2f}'.replace('.00', '')
                return resultat
            else:
                resultat = f'{res:.0f}'
                return resultat

    def calculer_nombre_absence_justifiée(self, total_absence_justifiée):
        """ Calculer la somme des absences justifiées par session"""
        for examen in self.env['info.examen'].search([('date_exam', "=", self.date_exam)]):
            if examen:
                nbr_absence = examen.env['info.examen'].search_count(
                    [('session_id', "=", self.id), ('presence', "=", 'absence_justifiee')])
                total_absence_justifiée = nbr_absence
                return total_absence_justifiée

    def nbr_canceled_state_after_14_day_0min(self, res_calc):
        """ Calculer nbr canceled state after 14 day 0min """
        nbr_partner_personel_annule = self.env['partner.sessions'].sudo().search(
            [('date_exam', "=", self.date_exam), ('session_id.id', "=", self.id),
             ('client_id.mode_de_financement', '=', 'particulier'), ('client_id.statut', '=', 'canceled'), ('client_id.temps_minute', '=', 0)])
        nbr_partner_cpf_annule = self.env['partner.sessions'].sudo().search(
            [('date_exam', "=", self.date_exam), ('session_id', "=", self.id),
             ('client_id.mode_de_financement', '=', 'cpf'), ('client_id.statut', '=', 'canceled'),
             ('date_creation', ">", self.date_exam + timedelta(days=14)), ('client_id.temps_minute', '=', 0)])
        count_per_an = False
        # si le financement de client est personel
        for sale in nbr_partner_personel_annule:
            if sale.client_id.signed_on > self.date_exam + timedelta(days=14):
                count_per_an += 1
        counter_per_an = count_per_an
        res_calc = counter_per_an + len(nbr_partner_cpf_annule)
        return res_calc

    def calculer_zero_min_formation_gagne(self, zero_min_formation_gagne):
        """ Non présentation à la formation """
        for examen in self.env['info.examen'].search([('date_exam', "=", self.date_exam)]):
            if examen:
                zero_min = self.client_ids.filtered(lambda sw: sw.statut == 'won' and sw.temps_minute == 0)
                temps_minute_360 = len(zero_min)
                _logger.info("calculer_zero_min_formation_gagne %s" % str(temps_minute_360))
                zero_min_formation_gagne = temps_minute_360 + self.nbr_canceled_state_after_14_day_0min(self) #Somme nombre des clients gagnés avec nombre des clients annulés
                return zero_min_formation_gagne

    def pourcentage_calculer_formation_gagne(self, resultat):
        """ pourcentage calculer_zero_min_formation_gagne """
        zero_min = self.calculer_zero_min_formation_gagne(self)
        nbr_inscrit = self.nbr_client_par_session(self)
        if nbr_inscrit > 0:
            res = (zero_min * 100 / nbr_inscrit)
            if res > 0:
                resultat = f'{res:.2f}'.replace('.00', '')
                return resultat
            else:
                resultat = f'{res:.0f}'
                return resultat
    def pourcentage_absence_justifiée(self, resultat):
        """ pourcentage absence justifiée """
        nbr_absence_justifiee = self.calculer_nombre_absence_justifiée(self)
        nbr_inscrit = self.nbr_client_par_session(self)
        if nbr_inscrit > 0:
            res = (nbr_absence_justifiee * 100 / nbr_inscrit)
            if res > 0:
                resultat = f'{res:.2f}'.replace('.00', '')
                return resultat
            else:
                resultat = f'{res:.0f}'
                return resultat

    def pourcentage_abandon(self, prc_abandon):
        """ Calculer pourcentage d'abandon par session """
        nbr_absence_abandon = self.count_annule
        nbr_inscrit = self.nbr_client_par_session(self)
        if nbr_inscrit > 0:
            res = (nbr_absence_abandon * 100 / nbr_inscrit)
            if res > 0:
                prc_abandon = f'{res:.2f}'.replace('.00', '')
                return prc_abandon
            else:
                prc_abandon = f'{res:.0f}'
                return prc_abandon

    def nbr_echec(self, nbr_echec):
        """ Calculer nombre d'echec :
        resultat = ajournée
        presence = present"""
        for examen in self.env['info.examen'].search([('date_exam', "=", self.date_exam)]):
            nbr_absence = examen.env['info.examen'].search_count(
                [('session_id', "=", self.id), ('presence', "=", 'present'), ('resultat', "=", 'ajourne')])
            nbr_echec = nbr_absence
            return nbr_echec

    def pourcentage_echec(self, prc_echec):
        """ Calculer pourcentage des clients (echec)"""
        nbr_echec = self.nbr_echec(self)
        nbr_present_tot = self.nbr_present_par_session(self)
        if nbr_present_tot > 0:
            res = (nbr_echec * 100 / nbr_present_tot)
            if res > 0:
                prc_echec = f'{res:.2f}'.replace('.00', '')
                return prc_echec
            else:
                prc_echec = f'{res:.0f}'
                return prc_echec

    def pack_solo_inscrit(self, sum_solo_inscrit):
        """ Calculer le nombre du client inscrit par session selon le pack solo """
        nbr_from_examen = 0
        for examen in self.env['info.examen'].search(
                [('date_exam', "=", self.date_exam), ('session_id', "=", self.id)]):
            if examen.module_id.product_id.default_code == "basique" and examen.partner_id.statut == 'won':
                nbr_from_examen += 1
                # Appliquer regle si client a dépassé les 14 jours
            nbr_partner_personel_annule = self.env['partner.sessions'].sudo().search(
                [('date_exam', "=", self.date_exam), ('session_id.id', "=", self.id),
                 ('client_id.mode_de_financement', '=', 'particulier'), ('client_id.statut', '=', 'canceled'),
                 ('client_id.temps_minute', '=', 0)])
            nbr_partner_cpf_annule = self.env['partner.sessions'].sudo().search(
                [('date_exam', "=", self.date_exam), ('session_id', "=", self.id),
                 ('client_id.mode_de_financement', '=', 'cpf'), ('client_id.statut', '=', 'canceled'),
                 ('date_creation', ">", self.date_exam + timedelta(days=14)), ('client_id.temps_minute', '=', 0)])
            count_per_an = False
            # Si le financement de client est personel
            for sale in nbr_partner_personel_annule:
                if sale.client_id.signed_on > self.date_exam + timedelta(days=14) and sale.client_id.module_id.product_id.default_code == "basique":
                    count_per_an += 1
            counter_per_an = count_per_an
            res_calc = counter_per_an + len(nbr_partner_cpf_annule)

        sum_solo_inscrit = nbr_from_examen + res_calc
        return sum_solo_inscrit

    def pack_solo_present(self, sum_solo_present):
        """ Calculer le nombre du client present par session selon le pack solo """
        nbr_from_examen_solo = 0
        for examen in self.env['info.examen'].search(
                [('date_exam', "=", self.date_exam), ('session_id', "=", self.id), ('presence', "=", 'present')]):
            if examen.module_id.product_id.default_code == "basique":
                nbr_from_examen_solo += 1
        sum_solo_present = nbr_from_examen_solo
        return sum_solo_present

    def pack_pro_present(self, sum_pro_present):
        """ Calculer le nombre du client present par session selon le pack pro """
        nbr_from_examen_pro = 0
        for examen in self.env['info.examen'].search(
                [('date_exam', "=", self.date_exam), ('session_id', "=", self.id), ('presence', "=", 'present')]):
            if examen.module_id.product_id.default_code == "avancee":
                nbr_from_examen_pro += 1
        sum_pro_present = nbr_from_examen_pro
        return sum_pro_present

    def pack_premium_present(self, sum_premium_present):
        """ Calculer le nombre du client present par session selon le pack premium """
        nbr_from_examen_premium = 0
        examen = self.env['info.examen'].search(
                [('date_exam', "=", self.date_exam), ('session_id.id', "=", self.id), ('presence', "=", 'present'), ('module_id.product_id.default_code', '=', "premium")])
        #if examen.module_id.product_id.default_code == "premium":
        #nbr_from_examen_premium += 1
        sum_premium_present = len(examen)
        return sum_premium_present

    def pack_repassage_present(self, sum_repassage_present):
        """ Calculer le nombre du client present par session selon le pack repassage """
        nbr_from_examen_repassage = 0
        for examen in self.env['info.examen'].search(
                [('date_exam', "=", self.date_exam), ('session_id', "=", self.id), ('presence', "=", 'present')]):
            if examen.module_id.product_id.default_code == "examen":
                nbr_from_examen_repassage += 1
        sum_repassage_present = nbr_from_examen_repassage
        return sum_repassage_present

    def nbr_canceled_state_after_14_day(self, cal_days):
        """ Calculer nbr_canceled_state_after_14_day """
        nbr_partner_personel_annule = self.env['partner.sessions'].sudo().search(
            [('date_exam', "=", self.date_exam), ('session_id.id', "=", self.id),
             ('client_id.mode_de_financement', '=', 'particulier'), ('client_id.statut', '=', 'canceled')])
        nbr_partner_cpf_annule = self.env['partner.sessions'].sudo().search(
            [('date_exam', "=", self.date_exam), ('session_id', "=", self.id),
             ('client_id.mode_de_financement', '=', 'cpf'), ('client_id.statut', '=', 'canceled'),
             ('date_creation', ">", self.date_exam + timedelta(days=14))])
        count_per_an = False
        for sale in nbr_partner_personel_annule:
            if sale.client_id.signed_on > self.date_exam + timedelta(days=14):
                count_per_an += 1
        counter_per_an = count_per_an
        cal_days = counter_per_an + len(nbr_partner_cpf_annule) + len(nbr_partner_personel_annule)
        return cal_days

    def pack_pro_inscrit(self, sum_pro_inscrit):
        """ Calculer le nombre du client inscrit par session selon le pack pro """
        nbr_from_examen_pro = False
        for examen in self.env['info.examen'].search(
                [('date_exam', "=", self.date_exam), ('session_id', "=", self.id)]):
            if examen.module_id.product_id.default_code == "avancee" and examen.partner_id.statut == 'won':
                nbr_from_examen_pro += 1
        # Appliquer regle si client a dépassé les 14 jours
        nbr_partner_personel_annule_pro = self.env['partner.sessions'].sudo().search(
            [('date_exam', "=", self.date_exam), ('session_id.id', "=", self.id),
             ('client_id.mode_de_financement', '=', 'particulier'), ('client_id.statut', '=', 'canceled')])
        nbr_partner_cpf_annule = self.env['partner.sessions'].sudo().search(
            [('date_exam', "=", self.date_exam), ('session_id', "=", self.id),
             ('client_id.mode_de_financement', '=', 'cpf'), ('client_id.statut', '=', 'canceled'),
             ('date_creation', ">", self.date_exam + timedelta(days=14))])
        count_per_an = False
        # Si le financement de client est personel
        for sale in nbr_partner_personel_annule_pro:
            if sale.client_id.signed_on > self.date_exam + timedelta(
                    days=14) and sale.client_id.module_id.product_id.default_code == "avancee":
                count_per_an += 1
        counter_per_an = count_per_an
        res_calc = counter_per_an + len(nbr_partner_cpf_annule)
        tot = nbr_from_examen_pro + res_calc
        sum_pro_inscrit = tot
        return sum_pro_inscrit

    def pack_premium_inscrit(self, sum_premium_inscrit):
        """ Calculer le nombre du client inscrit par session selon le pack premium """
        nbr_from_examen_premium = 0
        for examen in self.env['info.examen'].search(
                [('date_exam', "=", self.date_exam), ('session_id', "=", self.id)]):

            if examen.module_id.product_id.default_code == "premium" and examen.partner_id.statut == 'won':
                nbr_from_examen_premium += 1
        # Appliquer regle si client a dépassé les 14 jours
        nbr_partner_personel_annule_premium = self.env['partner.sessions'].sudo().search(
            [('date_exam', "=", self.date_exam), ('session_id.id', "=", self.id),
             ('client_id.mode_de_financement', '=', 'particulier'), ('client_id.statut', '=', 'canceled'),
             ('client_id.temps_minute', '=', 0)])
        nbr_partner_cpf_annule_premium = self.env['partner.sessions'].sudo().search(
            [('date_exam', "=", self.date_exam), ('session_id', "=", self.id),
             ('client_id.mode_de_financement', '=', 'cpf'), ('client_id.statut', '=', 'canceled'),
             ('date_creation', ">", self.date_exam + timedelta(days=14)), ('client_id.temps_minute', '=', 0)])
        count_per_an_premium = False
        # Si le financement de client est personel
        for sale in nbr_partner_personel_annule_premium:
            if sale.client_id.signed_on > self.date_exam + timedelta(
                    days=14) and sale.client_id.module_id.product_id.default_code == "premium":
                count_per_an_premium += 1
        counter_per_an = count_per_an_premium
        res_calc_premium = counter_per_an + len(nbr_partner_cpf_annule_premium) + nbr_from_examen_premium
        sum_premium_inscrit = res_calc_premium
        return sum_premium_inscrit

    def pack_repassage_inscrit(self, sum_repassage_inscrit):
        """ Calculer le nombre du client inscrit par session selon le pack repassage """
        nbr_from_examen = 0
        for examen in self.env['info.examen'].search(
                [('date_exam', "=", self.date_exam), ('session_id', "=", self.id)]):
            if examen.module_id.product_id.default_code == "examen" and examen.partner_id.statut == 'won':
                nbr_from_examen += 1
        # Appliquer regle si client a dépassé les 14 jours
        nbr_partner_personel_annule = self.env['partner.sessions'].sudo().search(
            [('date_exam', "=", self.date_exam), ('session_id.id', "=", self.id),
             ('client_id.mode_de_financement', '=', 'particulier'), ('client_id.statut', '=', 'canceled'),
             ('client_id.temps_minute', '=', 0)])
        nbr_partner_cpf_annule = self.env['partner.sessions'].sudo().search(
            [('date_exam', "=", self.date_exam), ('session_id', "=", self.id),
             ('client_id.mode_de_financement', '=', 'cpf'), ('client_id.statut', '=', 'canceled'),
             ('date_creation', ">", self.date_exam + timedelta(days=14)), ('client_id.temps_minute', '=', 0)])
        count_per_an = False
        # Si le financement de client est personel
        for sale in nbr_partner_personel_annule:
            if sale.client_id.signed_on > self.date_exam + timedelta(
                    days=14) and sale.client_id.module_id.product_id.default_code == "examen":
                count_per_an += 1
        sum_repassage_inscrit = count_per_an + len(nbr_partner_cpf_annule) + nbr_from_examen
        return sum_repassage_inscrit

    def taux_de_presence_solo(self):
        """ Calculer taux de presence par session selon le pack solo """
        pack_solo_present = self.pack_solo_present(self)
        nbr_inscrit_solo = self.pack_solo_inscrit(self)
        if nbr_inscrit_solo > 0:
            taux_de_presence = pack_solo_present * 100 / nbr_inscrit_solo
            if taux_de_presence > 0:
                taux_de_presence_solo = f'{taux_de_presence:.2f}'.replace('.00', '')
                return taux_de_presence_solo
            else:
                taux_de_presence_solo = f'{taux_de_presence:.0f}'
                return taux_de_presence_solo
        else:
            taux_de_presence_solo = 0
            return taux_de_presence_solo

    def taux_de_presence_pro(self):
        """ Calculer taux de presence par session selon le pack pro """
        pack_pro_present = self.pack_pro_present(self)
        nbr_inscrit_pro = self.pack_pro_inscrit(self)
        if nbr_inscrit_pro > 0:
            taux_de_presence = pack_pro_present * 100 / nbr_inscrit_pro
            if taux_de_presence > 0:
                taux_de_presence_pro = f'{taux_de_presence:.2f}'.replace('.00', '')
                return taux_de_presence_pro
            else:
                taux_de_presence_pro = f'{taux_de_presence:.0f}'
                return taux_de_presence_pro
        else:
            taux_de_presence_pro = 0
            return taux_de_presence_pro

    def taux_de_presence_premium(self):
        """ Calculer taux de présence pour les packs premium;
        avec une condition pour enlever la partie décimale
        si la résultat est égale à zéro"""
        pack_premium_present = self.pack_premium_present(self)
        nbr_inscrit = self.pack_premium_inscrit(self)
        if nbr_inscrit > 0:
            taux_de_presence = pack_premium_present * 100 / nbr_inscrit
            if taux_de_presence > 0:
                taux_de_presence_premium = f'{taux_de_presence:.2f}'.replace('.00', '')
                return taux_de_presence_premium
            else:
                taux_de_presence_premium = f'{taux_de_presence:.0f}'
                return taux_de_presence_premium
        else:
            taux_de_presence_premium = 0
            return taux_de_presence_premium

    def taux_de_presence_repassage(self):
        """ Calculer taux de presence par session selon le pack repassage """
        pack_repassage_present = self.pack_repassage_present(self)
        nbr_inscrit = self.pack_repassage_inscrit(self)
        if nbr_inscrit > 0:
            taux_de_presence = pack_repassage_present * 100 / nbr_inscrit
            if taux_de_presence > 0:
                taux_de_presence_repassage = f'{taux_de_presence:.2f}'.replace('.00', '')
                return taux_de_presence_repassage
            else:
                taux_de_presence_repassage = f'{taux_de_presence:.0f}'
                return taux_de_presence_repassage
        else:
            taux_de_presence_repassage = 0
            return taux_de_presence_repassage

    def taux_de_reussite_solo(self):
        """ Calculer taux de reussite par session selon le pack solo """
        pack_solo_reussite = self.nbr_recus_solo()
        nbr_inscrit = self.pack_solo_present(self)
        if nbr_inscrit > 0:
            taux_de_reussite = pack_solo_reussite * 100 / nbr_inscrit
            if taux_de_reussite > 0:
                taux_de_reussite_solo = f'{taux_de_reussite:.2f}'.replace('.00', '')
                return taux_de_reussite_solo
            else:
                taux_de_reussite_solo = f'{taux_de_reussite:.0f}'
                return taux_de_reussite_solo
        else:
            taux_de_reussite_solo = 0
            return taux_de_reussite_solo

    def taux_de_reussite_pro(self):
        """ Calculer taux de reussite par session selon le pack pro """
        pack_pro_reussite = self.nbr_recus_pro()
        nbr_inscrit = self.pack_pro_present(self)
        if nbr_inscrit > 0:
            taux_de_reussite = pack_pro_reussite * 100 / nbr_inscrit
            if taux_de_reussite > 0:
                taux_de_reussite_pro = f'{taux_de_reussite:.2f}'.replace('.00', '')
                return taux_de_reussite_pro
            else:
                taux_de_reussite_pro = f'{taux_de_reussite:.0f}'
                return taux_de_reussite_pro
        else:
            taux_de_reussite_pro = 0
            return taux_de_reussite_pro

    def taux_de_reussite_premium(self):
        """ Calculer taux de reussite par session selon le pack premium """
        pack_premium_reussite = self.nbr_recus_premium()
        nbr_inscrit = self.pack_premium_present(self)
        if nbr_inscrit > 0:
            taux_de_reussite = pack_premium_reussite * 100 / nbr_inscrit
            if taux_de_reussite > 0:
                taux_de_reussite_premium = f'{taux_de_reussite:.2f}'.replace('.00', '')
                return taux_de_reussite_premium
            else:
                taux_de_reussite_premium = f'{taux_de_reussite:.0f}'
                return taux_de_reussite_premium
        else:
            taux_de_reussite_premium = 0
            return taux_de_reussite_premium

    def taux_de_reussite_repassage(self):
        """ Calculer taux de reussite par session selon le pack repassage """
        pack_repassage_reussite = self.nbr_recus_repassage()
        nbr_inscrit = self.pack_repassage_present(self)
        if nbr_inscrit > 0:
            taux_de_reussite = pack_repassage_reussite * 100 / nbr_inscrit
            if taux_de_reussite > 0:
                taux_de_reussite_repassage = f'{taux_de_reussite:.2f}'.replace('.00', '')
                return taux_de_reussite_repassage
            else:
                taux_de_reussite_repassage = f'{taux_de_reussite:.0f}'
                return taux_de_reussite_repassage
        else:
            taux_de_reussite_repassage = 0
            return taux_de_reussite_repassage

    @api.depends('epreuve_a')
    def moyenne_qcm(self):
        """ CALCULER moyenne de la note QCM des clients par session"""
        sum_qcm = 0
        moyenne_qcm = 0
        nbr_present = self.nbr_present_par_session(self)
        for rec in self.client_ids:
            for examen in self.env['info.examen'].sudo().search(
                    [('session_id', "=", self.id), ('partner_id', "=", rec.id)]):
                print("examen", examen)
                sum_qcm += sum(examen.mapped('epreuve_a'))
        if nbr_present > 0:
            moyenne_qcm = sum_qcm
            return f'{moyenne_qcm:.2f}'.replace('.00', '')
        else:
            return 0

    @api.depends('epreuve_b')
    def moyenne_qro(self):
        """ CALCULER moyenne de la note QRO des clients par session"""
        nbr_present = self.nbr_present_par_session(self)
        sum_qro = 0
        moyenne_qro = 0
        for rec in self.client_ids:
            for examen in self.env['info.examen'].sudo().search(
                    [('session_id', "=", self.id), ('partner_id', "=", rec.id)]):
                print("examen", examen.epreuve_b)
                sum_qro += sum(examen.mapped('epreuve_b'))
        if nbr_present > 0:
            moyenne_qro = sum_qro
            return f'{moyenne_qro:.2f}'.replace('.00', '')
        else:
            return 0

    @api.depends('moyenne_generale')
    def moyenne_des_somme_qcm_qro(self):
        """ CALCULER moyenne de somme de la note QRO et QCM par session"""
        sum_qcm_qro = 0
        moyenne_qcm_qro = 0
        nbr_present = self.nbr_present_par_session(self)
        for rec in self.client_ids:
            for examen in self.env['info.examen'].sudo().search(
                    [('session_id', "=", self.id), ('partner_id', "=", rec.id)]):
                sum_qcm_qro += sum(examen.mapped('moyenne_generale'))
        if nbr_present > 0:
            moyenne_qcm_qro = sum_qcm_qro
            return f'{moyenne_qcm_qro:.2f}'.replace('.00', '')
        else:
            return 0

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        """ Read group customization in order to display all the stages in the
            kanban view, even if they are empty
        """
        stage_ids = self.env['mcmacademy.stage'].search(
            [('name', "!=", _('Planifiées')), ('name', "!=", _('Terminées'))])
        return stage_ids

    @api.depends('client_ids', 'prospect_ids', 'canceled_prospect_ids')
    def _count_clients(self):
        for rec in self:
            rec.count = len(rec.client_ids) + len(rec.prospect_ids)

    def _get_session_number(self):
        """ Digiforma """
        for rec in self:
            rec.number = 'AF' + str(random.randint(1000000000, 9999999999))

    def _inverse_date(self):
        for rec in self:
            print(rec.date_debut)
            print(rec.date_fin)

    def write(self, values):
        for record in self:
            if 'stage_id' in values:
                stages = self.env['mcmacademy.stage'].search([('id', "=", values['stage_id'])])
                for stage in stages:
                    if stage.name in ['Archivées', 'Archivés'] and len(record.client_ids) > 0:
                        raise ValidationError(
                            "Impossible d'archiver une session qui contient des clients")  # raise validation error when we edit the session to stage 'Archivées or Archivés' and the session has won clients
                    elif stage.name in ['Archivées', 'Archivés'] and len(record.client_ids) == 0:
                        values[
                            'max_number_places'] = 0  # edit the max number of places to 0 when we edit the session to stage  ['Archivées','Archivés'] and session has no clients
        return super(Session, self).write(values)

    def unlink(self):
        for record in self:
            if len(record.client_ids) > 0:
                raise ValidationError(
                    "Impossible de supprimer une session qui contient des clients")  # raise validation error when we want to delete a session has clients
        return super(Session, self).unlink()

    @api.depends('client_ids', 'prospect_ids', 'canceled_prospect_ids')
    def _compute_count_clients(self):
        for rec in self:
            client_counter = 0
            stagiaire_counter = 0
            for client in rec.client_ids:
                if client.company_type == 'person':
                    stagiaire_counter += 1
                else:
                    client_counter += 1
            rec.count_stagiaires = stagiaire_counter
            rec.count_client = client_counter
            perdu_counter = 0
            canceled_counter = 0
            for client in rec.canceled_prospect_ids:
                if client.statut == 'perdu ':
                    perdu_counter += 1
                elif client.statut == 'canceled':
                    canceled_counter += 1
            rec.count_perdu = perdu_counter
            rec.count_annule = canceled_counter
            prospect_counter = 0
            count_prospect = 0
            rec.count_prospect = len(rec.prospect_ids)
            rec.count_panier_perdu = len(rec.panier_perdu_ids)
