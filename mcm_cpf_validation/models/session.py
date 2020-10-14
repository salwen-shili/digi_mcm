# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models

class Session(models.Model):
    _inherit = "mcmacademy.session"

    id_edof=fields.Char("ID Sesssion EDOF")

    #compute available places for every module in session
    def write(self,values):
        session=super(Session,self).write(values)
        if self.module_ids:
            for module in self.module_ids:
                count=0
                for partner in self.client_ids:
                    if partner.module_id==module and partner.statut=='won':
                        count+=1
                module.number_places_available=module.max_number_places-count
        return session