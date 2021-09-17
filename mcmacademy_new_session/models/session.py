# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

import logging
_logger = logging.getLogger(__name__)

class handle_install_uninstall(models.Model):
    _name = "handle.install.uninstall"

    name = fields.Char('Name')

    #@api.model
    #def create(self, vals):
    #query = """update mcmacademy_session ses set stage_id = (select mcmacademy_stage.id from mcmacademy_stage where mcmacademy_stage.name=ses.ville) where company_id=1;"""
    #cr = self._cr
    #cr.execute(query)
    #return super(handle_install_uninstall,self).create(vals)

class Session(models.Model):
    _inherit = 'mcmacademy.session'
    _order = 'date_debut desc'


class Module(models.Model):
    _inherit = 'mcmacademy.module'

    prix_normal = fields.Monetary('Tarif',default=lambda self:self.product_id.list_price,store=True)
    lieu = fields.Many2one('res.country.state', string="Ville")




