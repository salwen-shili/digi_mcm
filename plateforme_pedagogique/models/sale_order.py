# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    def write(self, values):
        res = super(SaleOrder, self).write(values)
        if values.get('state') == 'sale':
            _logger.info('write******** %s' %str(values))
            self.partner_id.ajouter_iOne_manuelle(self.partner_id)
        return res