# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class resPartner(models.Model):
    _inherit = "res.partner"

    from_digiforma=fields.Boolean('De digiforma',default=False)
    digiforma_sessions=fields.Text('Liste des sessions')
    note_digiforma = fields.Text('Notes sur digiforma')