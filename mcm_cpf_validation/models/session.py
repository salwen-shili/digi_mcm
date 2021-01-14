# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models,api

class Session(models.Model):
    _inherit = "mcmacademy.session"

    id_edof=fields.Char("ID Sesssion EDOF")
    max_number_places = fields.Integer("Nombre des places maximales")
    number_places_available = fields.Integer("Nombre des places disponibles", compute='get_number_places_available',
                                             store=True, default=0)
    website_published=fields.Boolean('Publié en site web',default=True)

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
        if 'number_places_available' in values:
            if values['number_places_available'] <= 0:
                self.website_published=False
            else:
                self.website_published=True
        return session

    @api.depends('client_ids','max_number_places')
    def get_number_places_available(self):
        for rec in self:
            count = 0
            if rec.max_number_places:
                for client in rec.client_ids:
                    if client.statut == 'won':
                        count += 1
            rec.number_places_available = rec.max_number_places - count
            if rec.number_places_available <= 0:
                rec.website_published = False
            else:
                rec.website_published = True