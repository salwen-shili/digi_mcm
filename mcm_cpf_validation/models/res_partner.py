# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models,api,_
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.http import request

class resPartner(models.Model):
    _inherit = "res.partner"

    diplome=fields.Char("Diplôme")


    @api.model
    def create(self, values):
        partner= super(resPartner, self).create(values)
        if partner.mcm_session_id:
            check_portal = False
            if partner.user_ids:
                for user in self.partner_id.user_ids:
                    groups = user.groups_id
                    for group in groups:
                        if (group.name == _('Portail')):
                            check_portal = True
            if check_portal:
                if partner.statut == 'won' or partner.statut == 'finalized':
                    list = []
                    for client in partner.mcm_session_id.client_ids:
                        list.append(client.id)
                    list.append(partner.id)
                    partner.mcm_session_id.write({'client_ids': [(6, 0, list)]})

                    list = []
                    for client in partner.mcm_session_id.prospect_ids:
                        if client.id != partner.id:
                            list.append(client.id)
                    partner.mcm_session_id.write({'prospect_ids': [(6, 0, list)]})

                    list = []
                    for client in partner.mcm_session_id.canceled_prospect_ids:
                        if client.id != partner.id:
                            list.append(client.id)
                    partner.mcm_session_id.write({'canceled_prospect_ids': [(6, 0, list)]})

                    list = []
                    for client in partner.mcm_session_id.panier_perdu_ids:
                        if client.id != partner.id:
                            list.append(client.id)
                    partner.mcm_session_id.write({'panier_perdu_ids': [(6, 0, list)]})

                if partner.statut == 'indecis':
                    list = []
                    for client in partner.mcm_session_id.prospect_ids:
                        list.append(client.id)
                    list.append(partner.id)
                    partner.mcm_session_id.write({'prospect_ids': [(6, 0, list)]})

                    list = []
                    for client in partner.mcm_session_id.client_ids:
                        if client.id != partner.id:
                            list.append(client.id)
                    partner.mcm_session_id.write({'client_ids': [(6, 0, list)]})

                    list = []
                    for client in partner.mcm_session_id.canceled_prospect_ids:
                        if client.id != partner.id:
                            list.append(client.id)
                    partner.mcm_session_id.write({'canceled_prospect_ids': [(6, 0, list)]})

                    list = []
                    for client in partner.mcm_session_id.panier_perdu_ids:
                        if client.id != partner.id:
                            list.append(client.id)
                    partner.mcm_session_id.write({'panier_perdu_ids': [(6, 0, list)]})

                if partner.statut == 'panier_perdu':
                    list = []
                    for client in partner.mcm_session_id.panier_perdu_ids:
                        list.append(client.id)
                    list.append(partner.id)
                    partner.mcm_session_id.write({'panier_perdu_ids': [(6, 0, list)]})

                    list = []
                    for client in partner.mcm_session_id.client_ids:
                        if client.id != partner.id:
                            list.append(client.id)
                    partner.mcm_session_id.write({'client_ids': [(6, 0, list)]})

                    list = []
                    for client in partner.mcm_session_id.canceled_prospect_ids:
                        if client.id != partner.id:
                            list.append(client.id)
                    partner.mcm_session_id.write({'canceled_prospect_ids': [(6, 0, list)]})

                    list = []
                    for client in partner.mcm_session_id.prospect_ids:
                        if client.id != partner.id:
                            list.append(client.id)
                    partner.mcm_session_id.write({'prospect_ids': [(6, 0, list)]})

                if partner.statut == 'perdu' or partner.statut == 'canceled':
                    list = []
                    for client in partner.mcm_session_id.canceled_prospect_ids:
                        list.append(client.id)
                    list.append(partner.id)
                    partner.mcm_session_id.write({'canceled_prospect_ids': [(6, 0, list)]})
                    list = []
                    for client in partner.mcm_session_id.client_ids:
                        if client.id != partner.id:
                            list.append(client.id)
                    partner.mcm_session_id.write({'client_ids': [(6, 0, list)]})

                    list = []
                    for client in partner.mcm_session_id.panier_perdu_ids:
                        if client.id != partner.id:
                            list.append(client.id)
                    partner.mcm_session_id.write({'panier_perdu_ids': [(6, 0, list)]})

                    list = []
                    for client in partner.mcm_session_id.panier_perdu_ids:
                        if client.id != partner.id:
                            list.append(client.id)
                    partner.mcm_session_id.write({'panier_perdu_ids': [(6, 0, list)]})
        return partner

    def write(self, vals):
        User = self.env.user
        check_portal = False
        group_portal = self.env.ref('base.group_portal')
        if User.user_has_groups('base.group_portal'):
            check_portal = True
        if 'statut' in vals and 'module_id' not in vals:
            if check_portal == False:
                if vals['statut'] == 'won':
                    if (self.module_id.number_places_available <= 0):
                        raise ValidationError(_(
                            'Le nombre de places disponibles est atteint, basculer le condidat vers la prochaine session.'))
        if 'module_id' in vals and 'statut' not in vals:
            if check_portal == False:
                # if self.statut == 'won' and self.statut == 'finalized':
                module = self.env['mcmacademy.module'].sudo().search([('id', '=', vals['module_id'])])
                if module:
                    if (self.module_id.id != module.id):
                        if (module.number_places_available <= 0):
                            raise ValidationError(_(
                                'Le nombre de places disponibles est atteint, basculer le condidat vers la prochaine session.'))
        if 'module_id' in vals and 'statut' in vals:
            print('test3')
            if check_portal == False:
                module = self.env['mcmacademy.module'].sudo().search([('id', '=', vals['module_id'])])
                if module:
                    if ((vals['statut'] == 'won') and (module.number_places_available <= 0)):
                        raise ValidationError(_(
                            'Le nombre de places disponibles est atteint, basculer le condidat vers la prochaine session.'))
        check_report = False
        if 'report' in vals:
            if vals['report']==True:
                check_report=True
        previous_client_session = False
        if self.mcm_session_id:
            previous_client_session=self.mcm_session_id
        previous_client_module = False
        if self.module_id:
            previous_client_module = self.module_id
        partner = super(resPartner, self).write(vals)
        if self.mcm_session_id:
            check_portal = False
            if self.user_ids:
                for user in self.user_ids:
                    groups = user.groups_id
                    for group in groups:
                        if (group.name == _('Portail')):
                            check_portal = True
            if check_portal:
                sale = False
                move = False
                if self.statut == 'won' or self.statut == 'finalized':
                    if check_report and self.mcm_session_id != previous_client_session:
                        list= []
                        if previous_client_session :
                            for client in previous_client_session.client_ids:
                                if client.id != self.id:
                                    list.append(client.id)
                            previous_client_session.write({'client_ids': [(6, 0, list)]})
                        if previous_client_session:
                            sale = self.env['sale.order'].sudo().search([('session_id', "=", previous_client_session.id)])
                            if sale:
                                sale.session_id = self.mcm_session_id
                                sale.module_id = self.module_id
                        else:
                            sales = self.env['sale.order'].sudo().search([('session_id', "=", False)])
                            for sale in sales :
                                sale.session_id = self.mcm_session_id
                                sale.module_id = self.module_id
                        if previous_client_session:
                            move = self.env['account.move'].sudo().search([('session_id', "=", previous_client_session.id)])
                            if move:
                                move.session_id = self.mcm_session_id
                                move.module_id = self.module_id
                        else:
                            moves = self.env['account.move'].sudo().search([('session_id', "=", False)])
                            for move in moves :
                                move.session_id = self.mcm_session_id
                                move.module_id = self.module_id
                        product_of_module = previous_client_module.product_id
                        module = self.env['mcmacademy.module'].sudo().search([('product_id', "=", product_of_module.id),('session_id',"=",self.mcm_session_id.id)],limit=1)
                        if module :
                            self.module_id=module
                        if move :
                            move.module_id = module
                        if sale :
                            sale.module_id = module
                    list = []
                    for client in self.mcm_session_id.client_ids:
                        list.append(client.id)
                    list.append(self.id)
                    self.mcm_session_id.write({'client_ids': [(6, 0, list)]})
                    if self.module_id:
                        compteur = 0
                        for client in self.mcm_session_id.client_ids:
                            if client.module_id == self.module_id:
                                compteur += 1
                        self.module_id.number_places_available = self.module_id.max_number_places - compteur

                    list = []
                    for client in self.mcm_session_id.prospect_ids:
                        if client.id != self.id:
                            list.append(client.id)
                    self.mcm_session_id.write({'prospect_ids': [(6, 0, list)]})

                    list = []
                    for client in self.mcm_session_id.canceled_prospect_ids:
                        if client.id != self.id:
                            list.append(client.id)
                    self.mcm_session_id.write({'canceled_prospect_ids': [(6, 0, list)]})

                    list = []
                    for client in self.mcm_session_id.panier_perdu_ids:
                        if client.id != self.id:
                            list.append(client.id)
                    self.mcm_session_id.write({'panier_perdu_ids': [(6, 0, list)]})

                if self.statut == 'indecis':
                    list = []
                    for client in self.mcm_session_id.prospect_ids:
                        list.append(client.id)
                    list.append(self.id)
                    self.mcm_session_id.write({'prospect_ids': [(6, 0, list)]})

                    list = []
                    for client in self.mcm_session_id.client_ids:
                        if client.id != self.id:
                            list.append(client.id)
                    self.mcm_session_id.write({'client_ids': [(6, 0, list)]})

                    list = []
                    for client in self.mcm_session_id.canceled_prospect_ids:
                        if client.id != self.id:
                            list.append(client.id)
                    self.mcm_session_id.write({'canceled_prospect_ids': [(6, 0, list)]})

                    list = []
                    for client in self.mcm_session_id.panier_perdu_ids:
                        if client.id != self.id:
                            list.append(client.id)
                    self.mcm_session_id.write({'panier_perdu_ids': [(6, 0, list)]})

                if self.statut == 'panier_perdu':
                    list = []
                    for client in self.mcm_session_id.panier_perdu_ids:
                        list.append(client.id)
                    list.append(self.id)
                    self.mcm_session_id.write({'panier_perdu_ids': [(6, 0, list)]})

                    list = []
                    for client in self.mcm_session_id.client_ids:
                        if client.id != self.id:
                            list.append(client.id)
                    self.mcm_session_id.write({'client_ids': [(6, 0, list)]})

                    list = []
                    for client in self.mcm_session_id.canceled_prospect_ids:
                        if client.id != self.id:
                            list.append(client.id)
                    self.mcm_session_id.write({'canceled_prospect_ids': [(6, 0, list)]})

                    list = []
                    for client in self.mcm_session_id.prospect_ids:
                        if client.id != self.id:
                            list.append(client.id)
                    self.mcm_session_id.write({'prospect_ids': [(6, 0, list)]})
                if self.statut == 'perdu' or self.statut == 'canceled':
                    list = []
                    for client in self.mcm_session_id.canceled_prospect_ids:
                        list.append(client.id)
                    list.append(self.id)
                    self.mcm_session_id.write({'canceled_prospect_ids': [(6, 0, list)]})

                    list = []
                    for client in self.mcm_session_id.client_ids:
                        if client.id != self.id:
                            list.append(client.id)
                    self.mcm_session_id.write({'client_ids': [(6, 0, list)]})

                    list = []
                    for client in self.mcm_session_id.prospect_ids:
                        if client.id != self.id:
                            list.append(client.id)
                    self.mcm_session_id.write({'prospect_ids': [(6, 0, list)]})

                    list = []
                    for client in self.mcm_session_id.panier_perdu_ids:
                        if client.id != self.id:
                            list.append(client.id)
                    self.mcm_session_id.write({'panier_perdu_ids': [(6, 0, list)]})
        return partner