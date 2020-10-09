# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models,api

class Module(models.Model):
    _inherit = "mcmacademy.module"

    id_edof=fields.Char("ID Formation EDOF")
    max_number_places=fields.Integer("Nombre des places maximales")
    number_places_available=fields.Integer("Nombre des places disponibles" , compute='get_number_places_available',store=True,default=0)
    published=fields.Boolean('publié',default=False)
    next_module=fields.Many2one('mcmacademy.module','Module suivant')

    @api.depends('max_number_places','session_id.client_ids')
    def get_number_places_available(self):
        for rec in self:
            count = 0
            if rec.max_number_places and rec.session_id:
                for client in rec.session_id.client_ids:
                    if client.module_id.id==rec.id and client.statut=='won':
                        count+=1
            rec.number_places_available=rec.max_number_places-count
            # if rec.number_places_available ==3:
            #     vals = {
            #         'partner_email': '',
            #         'partner_id': False,
            #         'description': 'Bonjour /n Le nombre des places du module %s de la session %s est assez petit /n  Veuillez créer une nouvelle session ' % (rec.name,rec.session_id.name),
            #         'name': '%s : Nombre des places assez petit pour  %s ' % (rec.session_id.name,rec.name),
            #         'team_id': self.env['helpdesk.team'].sudo().search([('name', 'like', 'Clientèle')],
            #                                                               limit=1).id,
            #     }
            #     new_ticket = self.env['helpdesk.ticket'].sudo().create(
            #         vals)
            if rec.number_places_available <= 3:
                rec.published=True
            else:
                rec.published = False
            if rec.number_places_available <= 0 :
                rec.website_published=False
            else:
                rec.website_published=True
            return rec.number_places_available
    def write(self,values):
        module=super(Module,self).write(values)
        if 'number_places_available' in values:
            if values['number_places_available'] <= 0:
                self.website_published=False
        return module
