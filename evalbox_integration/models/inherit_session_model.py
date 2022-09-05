from odoo import api, fields, models, _
from datetime import date, timedelta


class InheritSaleOrder(models.Model):
    _inherit = 'mcmacademy.session'

    show_hide_button = fields.Boolean(compute='_get_visible_create_class_evalbox')
    hide_import_note_evalbox = fields.Boolean(compute='_get_visible_import_note_evalbox')

    def _get_visible_create_class_evalbox(self):
        """ Add fuction to control show and hide button in session view "Exporter une classe vers Evalbox" """
        date_today = date.today()
        if self.date_exam:
            if self.date_exam > date_today:
                self.show_hide_button = True
            else:
                self.show_hide_button = False

    def _get_visible_import_note_evalbox(self):
        """ Add fuction to control show and hide button in session view "Importer les notes depuis Evalbox" """
        date_today = date.today()
        if self.date_exam:
            if self.date_exam + timedelta(days=7) > date_today:
                self.hide_import_note_evalbox = True
            else:
                self.hide_import_note_evalbox = False
