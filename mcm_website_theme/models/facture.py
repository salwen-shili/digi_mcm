from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"
    stripe_sub_reference = fields.Char("Reference d'abonnement")

    
    """Quand la facture sera modifié on vérifie si le montant est totalement payé """

    def write(self, vals):
        print('vals %s' % str(vals))
        if 'amount_residual' in vals and vals['amount_residual'] == 0.0 and self.company_id.id == 2:
            _logger.info('paid invoice %s' % vals['amount_residual'])
            """si la facture est payé et montant du egal à zero on fait annuler l'abonnement sur stripe  """
            if self.stripe_sub_reference:
                acquirer_id = False
                for transaction in self.transaction_ids:
                    trans = self.env['payment.transaction'].sudo().search([('id', "=", transaction.id)])
                    if trans:
                        acquirer_id = trans.acquirer_id
                        print('acquirer_id ', acquirer_id)
                if acquirer_id:
                    url = "subscriptions/%s" % (self.stripe_sub_reference)
                    acquirer_id._stripe_request(url, method="DELETE")
            record = super(AccountMove, self).write(vals)
            return record
