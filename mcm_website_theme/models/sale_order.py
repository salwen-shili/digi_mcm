# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "sale.order"

    instalment_number=fields.Integer("Tranches",compute='get_instalment_number')
    amount_to_pay=fields.Monetary('Montant à Payer',compute='compute_amount_to_pay')
    instalment = fields.Boolean(default=False)
    conditions =fields.Boolean(default=False)
    failures = fields.Boolean(default=False)
    accompagnement = fields.Boolean(default=False)

    @api.depends('amount_total','pricelist_id')
    def get_instalment_number(self):
        for rec in self:
            if (rec.amount_total>=1000 and rec.company_id.id==1):
                rec.instalment_number = 3
            elif(rec.amount_total<1000 and rec.company_id.id==1):
                rec.instalment_number = 1
            elif(rec.company_id.id==2):
                default_code=False
                for line in rec.order_line:
                    default_code=line.product_id.default_code
                if default_code=='basique':
                    rec.instalment_number = 1
                elif default_code=='avancee':
                    rec.instalment_number = 2
                elif default_code=='premium':
                    rec.instalment_number = 3
                else:
                    rec.instalment_number = 1
            else:
                rec.instalment_number = 1
            print('instalment number')
            print(rec.instalment_number)

    @api.depends('amount_total','instalment_number')
    def compute_amount_to_pay(self):
        for rec in self:
           rec.amount_to_pay=rec.amount_total/rec.instalment_number

    def sale_action_sent(self):
        return self.write({'state': 'sent'})


