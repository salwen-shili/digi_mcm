from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"
    stripe_sub_reference = fields.Char("Reference d'abonnement")

    def write(self, vals):
        print('vals %s' % str(vals))
        if 'amount_residual' in vals and vals['amount_residual'] == 0.0 and self.company_id.id == 2:
            _logger.info('paid invoice %s' % vals['amount_residual'])
            """si la facture est payé et montant du egal à zero on fait annuler l'abonnement sur stripe  """
            subscription = self.stripe_sub_reference
            print('subscr ', subscription)
            if subscription:
                acquirer_id = False
                for transaction in self.transaction_ids:
                    tx = self.env['payment.transaction'].sudo().search([('id', "=", transaction.id)])
                    if tx:
                        acquirer_id = tx.acquirer_id
                        print('acquirer_id ', acquirer_id)
                if acquirer_id:
                    url = "subscriptions/%s" % (subscription)
                    acquirer_id._stripe_request(url, method="DELETE")
        record = super(AccountMove, self).write(vals)
        return record