# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "sale.order"

    instalment_number = fields.Integer("Tranches", compute='get_instalment_number')
    amount_to_pay = fields.Monetary('Montant à Payer', compute='compute_amount_to_pay')
    instalment = fields.Boolean(default=False)
    conditions = fields.Boolean(default=False)
    failures = fields.Boolean(default=False)
    accompagnement = fields.Boolean(default=False)
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


    @ api.depends('amount_total', 'pricelist_id')
    def get_instalment_number(self):
        for rec in self:
            if (rec.amount_total >= 1000 and rec.company_id.id == 1):
                rec.instalment_number = 3
            elif (rec.amount_total < 1000 and rec.company_id.id == 1):
                rec.instalment_number = 1
            elif (rec.company_id.id == 2):
                default_code = False
                for line in rec.order_line:
                    default_code = line.product_id.default_code
                if default_code == 'basique':
                    rec.instalment_number = 1
                elif default_code == 'avancee':
                    rec.instalment_number = 2
                elif default_code == 'premium':
                    rec.instalment_number = 3
                else:
                    rec.instalment_number = 1
            else:
                rec.instalment_number = 1
            print('instalment number')
            print(rec.instalment_number)

    @api.depends('amount_total', 'instalment_number')
    def compute_amount_to_pay(self):
        for rec in self:
            rec.amount_to_pay = rec.amount_total / rec.instalment_number

    def sale_action_sent(self):
        return self.write({'state': 'sent'})