# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import random
from num2words import num2words


class Session(models.Model):
    _name = 'mcmacademy.session'
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
    ville_jury_id = fields.Many2one('session.ville', string="Ville de jury", required=True,
                                       track_visibility='always')  # edit the field to be required and show field edit history
    adresse_jury_id = fields.Many2one('session.adresse.examen', "Adresse de jury")
    date_jury = fields.Date()
    date_session_en_lettre = fields.Char()
    heure_jury = fields.Char()
    num_agrement_jury = fields.Char()

    @api.onchange('adresse_jury_id')
    def onchange_session_ville_id(self):
        """ Cette fonction pour afficher la liste des adresses de centre d'examen
        liée par une seul ville choisi par l'utilisateur dans l'interface de session"""
        for rec in self:
            return {'domain': {'adresse_jury_id': [('adresse_jury_id', '=', rec.ville_jury_id.id)]}}

    # define a function in python to convert
    def date_to_text(self, yearformat, dayformat,monthformat):
        """ Convertir date vers lettre en utilisant la bibliothéque python: num2words (pour template de rapport jury)"""
        date = self.date_exam
        yearformat = "%Y"
        dayformat = "%d"
        monthformat = "%m"
        yearformat = (int(date.strftime(yearformat)))
        monthformat = (int(date.strftime(monthformat)))
        dayformat = (int(date.strftime(dayformat)))
        yearformat_txt = num2words(yearformat, lang='fr').upper().replace(',', ' ')
        dayformat_txt = num2words(dayformat, lang='fr').upper()
        monthformat_txt = num2words(monthformat, lang='fr').upper()
        return yearformat_txt, dayformat_txt, monthformat_txt

    def nbr_client_par_session(self, nbr_inscrits):
        """ Cette fonction permet de faire la somme d'inscrit de nombre de client avec statut (gagné, annulé et perdu).
         La fonction est utilisé dans la template de rapport jury"""
        nbr_inscrits = 0
        nbr_inscrits = nbr_inscrits + self.count_stagiaires + self.count_annule + self.count_panier_perdu
        return nbr_inscrits

    def nbr_present_par_session(self, nbr_present):
        """ Cette fonction permet de faire la somme d'inscrit de nombre de client avec statut (gagné, annulé et perdu).
         La fonction est utilisé dans la template de rapport jury"""
        nbr_present = self.client_ids.filtered(lambda cl: cl.presence == 'Présent(e)')
        print("ghghgh",len(nbr_present))
        return len(nbr_present)

    def nbr_recus_par_session(self, nbr_recu):
        for rec in self.client_ids:
            print(len(rec))
            for examen in rec.note_exam_id.filtered(lambda cl: cl.date_exam == self.date_exam):
                if examen.resultat == 'recu':
                    nbr_recu = len(examen)
                    return nbr_recu

    def pourcentage_client_recu(self, pourcentage):
        nbr_recu_total = self.nbr_recus_par_session(self)
        print(nbr_recu_total)
        nbr_inscrits_total = self.nbr_client_par_session(self)
        pourcentage = nbr_recu_total * 100 / nbr_inscrits_total
        pourcentage = round(pourcentage)
        print(pourcentage)
        return pourcentage

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
            rec.count_prospect = len(rec.prospect_ids)
            rec.count_panier_perdu = len(rec.panier_perdu_ids)
