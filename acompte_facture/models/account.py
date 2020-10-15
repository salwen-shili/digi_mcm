
from odoo import api, fields, models, _

class AccountMove(models.Model):
    _inherit = "account.move"


    def action_create_acompte(self):
        for record in self:
            print('montant total')
            print(self.amount_total)
            return {
                'name':"Créer une facture d'acompte",
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'account.invoice.acompte.wizard',
                'target': 'new',
                'context': {
                    'default_invoice_id': self.ids[0],
                    'default_pourcentage': 100,
                },
            }

    def _compute_amount(self):
        invoice=super(AccountMove,self)._compute_amount()
        for rec in self:
            if rec.acompte_invoice and rec.pourcentage_acompte:
                rec.amount_untaxed=(rec.amount_untaxed*rec.pourcentage_acompte)/100
                rec.amount_total=(rec.amount_total*rec.pourcentage_acompte)/100
        return invoice
class resPartnerWizard(models.TransientModel):
    _name = 'account.invoice.acompte.wizard'
    _description = 'wizard to change total amount and invoice line (acompte invoice)'

    invoice_id=fields.Many2one('account.move','Facture')
    amount=fields.Monetary("Montant d'Acompte",default=lambda self:self.invoice_id.amount_total)
    pourcentage=fields.Integer("Pourcentage d'Acompte")
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True, default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    def action_create_acompte(self):
        self.invoice_id.button_draft()
        lines = self.invoice_id.line_ids.sorted('debit')
        self.invoice_id.write({
            'amount_total':self.amount,
            'pourcentage_acompte':self.pourcentage,
            'acompte_invoice':True,
        })
        # for line in self.invoice_id.invoice_line_ids:
        #     balance=line.debit-self.amount
        #     debit=0.0
        #     credit=self.amount
        #     price_unit=self.amount
        #     line.write({
        #     'price_unit': price_unit,
        #     'debit': debit,
        #     'credit': credit,
        #     'balance': balance,
        #     })
        self.invoice_id.post()

    @api.onchange('pourcentage')
    def change_amount(self):
        for rec in self:
            rec.amount=(rec.amount*rec.pourcentage)/100




