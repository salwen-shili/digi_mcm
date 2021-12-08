# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models,_
import random

class Session(models.Model):
    _name = 'mcmacademy.session'
    _description = "Sessions de formation"

    name=fields.Char('Nom du session',required=True)

    type_client=fields.Selection(selection=[
        ('intra', 'INTRA'),
        ('inter_entreprise', 'INTER ENTREPRISE'),
    ], string='Type de client',copy=True)
    sous_traitance=fields.Boolean("Réalisé en sous traitance d'un autre organisme",copy=True)
    action_type_id=fields.Many2one('mcmacademy.action',string="Type d'action de formation",copy=True)
    domaine_formation=fields.Many2one('mcmacademy.domain',string='Domaine de formation',copy=True)
    diplome_vise=fields.Char('Diplôme visé par la formation',copy=True)
    module_ids = fields.One2many('mcmacademy.module', inverse_name='session_id', string='Liste des modules', copy=True)
    client_ids=fields.Many2many('res.partner','session_clients_rel', 'session_id', 'client_id', string='' ,copy=False)
    prospect_ids=fields.Many2many('res.partner','session_prospect_rel','session_id','prospect_id',string='',copy=False)
    canceled_prospect_ids=fields.Many2many('res.partner','session_canceled_prospect_rel','session_id','prospect_id',string='',copy=False)
    panier_perdu_ids=fields.Many2many('res.partner','session_panier_perdu_rel','session_id','prospect_id',string='',copy=False)
    stage_id=fields.Many2one('mcmacademy.stage','État',group_expand='_read_group_stage_ids')
    color = fields.Integer(string='Color Index',copy=True)
    date_debut=fields.Date('Date de debut de session',copy=False)
    date_fin=fields.Date('Date de fin de session',copy=False)
    count=fields.Integer('Nombre des clients',compute='_count_clients',copy=False)
    number=fields.Char('Numéro',compute='_get_session_number')
    count_client=fields.Integer('',compute='_compute_count_clients',copy=False)
    count_stagiaires=fields.Integer('',compute='_compute_count_clients',copy=False)
    count_perdu=fields.Integer('',compute='_compute_count_clients',copy=False)
    count_annule=fields.Integer('',compute='_compute_count_clients',copy=False)
    count_prospect=fields.Integer('',compute='_compute_count_clients',copy=False)
    count_panier_perdu=fields.Integer('',compute='_compute_count_clients',copy=False)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        """ Read group customization in order to display all the stages in the
            kanban view, even if they are empty
        """
        stage_ids = self.env['mcmacademy.stage'].search([('name',"!=",_('Planifiées')),('name',"!=",_('Terminées'))])
        return stage_ids

    @api.depends('client_ids','prospect_ids','canceled_prospect_ids')
    def _count_clients(self):
        for rec in self:
            rec.count=len(rec.client_ids)+len(rec.prospect_ids)

    def _get_session_number(self):
        for rec in self:
            rec.number='AF'+str(random.randint(1000000000,9999999999))

    def _inverse_date(self):
        for rec in self:
            print(rec.date_debut)
            print(rec.date_fin)

    @api.depends('client_ids','prospect_ids','canceled_prospect_ids')
    def _compute_count_clients(self):
        for rec in self:
            client_counter=0
            stagiaire_counter=0
            for client in rec.client_ids:
                if client.company_type=='person':
                    stagiaire_counter+=1
                else:
                    client_counter+=1
            rec.count_stagiaires=stagiaire_counter
            rec.count_client=client_counter
            perdu_counter=0
            canceled_counter=0
            for client in rec.canceled_prospect_ids:
                if client.statut == 'perdu ':
                    perdu_counter += 1
                elif client.statut=='canceled':
                    canceled_counter += 1
            rec.count_perdu=perdu_counter
            rec.count_annule=canceled_counter
            prospect_counter=0
            rec.count_prospect=len(rec.prospect_ids)
            rec.count_panier_perdu=len(rec.panier_perdu_ids)









