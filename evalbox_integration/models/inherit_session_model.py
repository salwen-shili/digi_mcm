from odoo import api, fields, models, _
from datetime import date


class InheritSaleOrder(models.Model):
    _inherit = 'mcmacademy.session'

    show_hide_button = fields.Boolean(compute='_get_visible')

    def _get_visible(self):
        date_today = date.today()
        if self.date_exam > date_today:
            self.show_hide_button = True
        else:
            self.show_hide_button = False