# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.tools.float_utils import float_round


class Module(models.Model):
    _name = 'mcmacademy.module'
    _description = "Description de module"

    name = fields.Char('Nom du module', required=True)
    product_id = fields.Many2one('product.template', string="Formation", required=True)
    prix_normal = fields.Monetary('Prix Normal',default=lambda self:self.product_id.list_price,store=True)
    prix_chpf = fields.Monetary('Prix CHPF', compute='_get_module_prices')
    date_debut = fields.Date('Du')
    date_fin = fields.Date('Au')
    duree = fields.Char('Durée')
    session_id = fields.Many2one('mcmacademy.session', 'Session',required=True,ondelete='cascade') #ondelete='cascade'  the module will be automatically deleted when the session to which it is attached is deleted
    module_details_ids = fields.One2many('mcmacademy.module.details', inverse_name='module_id', string='Détails')
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    sequence = fields.Integer(string='Sequence', default=10)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    display_duration = fields.Char('Durée ', compute='_get_display_duration', store=True)
    date_module = fields.Selection(selection=[
        ('interval', 'Entrer seulement un intervalle'),
        ('all', 'Ou bien entrer toutes les dates'),
    ], string='Type de date')
    method_calcul = fields.Selection(selection=[
        ('manual', 'Déclaration manuelle des durées réalisées'),
        ('e-learning', 'Relevé des connexions des séquences e-learning'),
    ], string="Méthode de calcul de l'assiduité des stagiaires", default='manual')
    reparties_sur = fields.Char('')
    duree_moyenne = fields.Char("durée moyenne d'un créneau", default="00:00")
    color = fields.Integer(string='Color Index')
    # tarif_by_client_type=fields.Boolean('Tarifs par type de client')
    particulier_price_untaxed = fields.Monetary('Prix Unitaire HT', compute='_compute_price_untaxed', store=True)
    chpf_price_untaxed = fields.Monetary('Prix CHPF ', compute='_compute_price_untaxed', store=True)
    heure_debut_matin = fields.Char('De (Matin)')
    heure_fin_matin = fields.Char('À (Matin) ')
    heure_debut_apres_midi = fields.Char('De (Aprés midi)')
    heure_fin_apres_midi= fields.Char('À (Aprés midi) ')
    lieu=fields.Many2one('res.country.state',string="Lieu")
    modalite_pedagogique=fields.Selection(selection=[
        ('presentiel', 'Présentiel'),
        ('e-learning', 'E-learning'),
        ('blended', 'Blended learning'),
        ('travail', 'En situation de travail'),
        ('stage', 'Stage'),
        ('conduite', 'Conduite'),
    ], string='Modalité Pédagogique')
    website_published = fields.Boolean('Publié en site web', default=True)
    contract_price=fields.Monetary('Ancien Tarif',default=lambda self: self.product_id.list_price)

    @api.depends('duree')
    def _get_display_duration(self):
        for rec in self:
            rec.display_duration = str(rec.duree) + ' heures'

    @api.onchange('product_id')
    def change_contract_price(self):
        if self.product_id:
            self.contract_price=self.product_id.list_price

    @api.depends('module_details_ids')
    def _get_module_prices(self):
        for rec in self:
            prix_chpf = 0
            for model in rec.module_details_ids:
                prix_chpf += model.prix_chpf
            rec.prix_chpf = prix_chpf
            rec.prix_normal = rec.product_id.list_price

    def _compute_price_untaxed(self):
        for rec in self:
            if (rec.contract_price and rec.duree):
                rec.particulier_price_untaxed = rec.contract_price / float(rec.duree)

            if (rec.prix_chpf and rec.duree):
                rec.chpf_price_untaxed = rec.prix_chpf / float(rec.duree)
    @api.model
    def create(self,vals):
        if vals.get('product_id') and vals.get('duree'):
            product = self.env['product.template'].search([('id', '=', vals.get('product_id'))])
            vals['particulier_price_untaxed']=product.list_price/float(vals.get('duree'))
        return super(Module,self).create(vals)

    def write(self,vals):
        module = super(Module, self).write(vals)
        if vals.get('product_id') and vals.get('duree'):
            product = self.env['product.template'].search([('id', '=', vals.get('product_id'))])
            self.particulier_price_untaxed = product.list_price / float(vals.get('duree'))
        if vals.get('product_id') and not vals.get('duree'):
            product = self.env['product.template'].search([('id', '=', vals.get('product_id'))])
            self.particulier_price_untaxed = product.list_price / float(self.duree)
        if not vals.get('product_id') and  vals.get('duree'):
            self.particulier_price_untaxed = self.contract_price / float(vals.get('duree'))
        return module


