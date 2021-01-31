# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    mcm_paid_amount = fields.Monetary(string='Montant payé',compute='_get_mcm_paid_amount',store=True)
    acompte_invoice = fields.Boolean(default=False)
    pourcentage_acompte = fields.Integer("Pourcentage d'acompte")
    module_id=fields.Many2one('mcmacademy.module','Module')
    session_id=fields.Many2one('mcmacademy.session','Session')
    pricelist_id=fields.Many2one('product.pricelist','Liste de prix')
    cpf_solde_invoice = fields.Boolean(default=False)
    cpf_acompte_invoice=fields.Boolean(default=False)
    cpf_acompte_amount= fields.Monetary('Montant acompte')



    @api.depends('amount_total', 'amount_residual')
    def _get_mcm_paid_amount(self):
        for rec in self:
            payments = self.env['account.payment'].search(['|','&',('communication', "=", rec.name),('state', "=", 'posted'),('communication', 'like', rec.invoice_origin)])
            paid_amount = 0.0

            for payment in payments:
                paid_amount += payment.amount
            rec.mcm_paid_amount = paid_amount

    # def unlink(self):
    #     for move in self:
    #         move.line_ids.unlink()
    #     for rec in self:
    #         rec.unlink()
    #     return super(AccountMove, self).unlink()

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def unlink(self):
        moves = self.mapped('move_id')

        # Check the lines are not reconciled (partially or not).
        self._check_reconciliation()

        # Check the lock date.
        moves._check_fiscalyear_lock_date()

        # Check the tax lock date.
        self._check_tax_lock_date()

        res = super(AccountMoveLine, self).unlink()

        # Check total_debit == total_credit in the related moves.
        if self._context.get('check_move_validity', True):
            moves._check_balanced()

        return res