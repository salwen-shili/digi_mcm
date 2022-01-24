from odoo import api, fields, models

import logging
_logger = logging.getLogger(__name__)
class AccountMove(models.Model):
    _inherit = "account.move"

    stripe_sub_reference = fields.Char("Reference d'abonnement")
    
    def write(self,vals):
        if 'invoice_payment_state' in vals and  vals['invoice_payment_state'] == 'paid':
            _logger.info('paid invoice %s' % vals['invoice_payment_state'])
            

        record = super(AccountMove, self).write(vals)
        return record