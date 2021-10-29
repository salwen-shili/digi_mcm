# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class Questionnaire(models.Model):
    _name = "questionnaire"

    partner_id = fields.Many2one('res.partner', 'Customer Name')
    product_id = fields.Many2one('product.product','Formation')
    besoins_particuliers = fields.Selection([('Oui','Oui'),('Non','Non')])
    type_besoins = fields.Text()
    raison_choix = fields.Selection([
        ('En chômage', 'Je suis en chômage et je suis en recherche d\'emploi'),
        ('Monter sa propre entreprise', 'Je veux monter ma propre entreprise et être indépendant'),
        ('Passionné par le métier', 'Je suis passionné par le métier de chauffeur'),
        ('En reconversion professionnelle','Je suis en reconversion professionnelle pour être chauffeur'),
        ('Mettre à jour ses connaissances','Pour mettre à jour mes connaissances et compétences du métier'),
        ('Arrondir ses fins du mois','Pour arrondir mes fins du mois')])
    support_formation = fields.Selection([
        ('Vidéos préenregistrées', 'En visualisant des vidéos préenregistrées '),
        ('Documents en ligne', 'En lisant des documents PDF en ligne'),
        ('En mode audio', 'En écoutant les cours en mode audio'),
        ('Alternance entre tous ces modes', 'En alternant entre tous ces modes d’apprentissage')])
    attentes = fields.Text()
    company_id = fields.Many2one('res.company', string='Société', default=lambda self: self.env.company)

class search(models.Model):
    _inherit = 'res.partner'
    questionnaires_count = fields.Integer(compute='compute_count')

    def get_questionnaires(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Questionnaires',
            'view_mode': 'tree',
            'res_model': 'questionnaire',
            'domain': [('partner_id', '=', self.id)],
            'context': "{'create': False}"
        }

    def compute_count(self):
        for record in self:
            record.questionnaires_count = self.env['questionnaire'].search_count(
                [('partner_id', '=', self.id)])

