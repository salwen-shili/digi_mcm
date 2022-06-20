# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError
from datetime import date,datetime


class resPartner(models.Model):
    _inherit = "res.partner"

    statut = fields.Selection(selection=[
        ('indecis', 'Indécis'),
        ('won', 'Gagné'),
        ('perdu', 'Perdu'),
        ('panier_perdu', 'Panier perdu'),
        ('canceled', 'Annulé'),
        ('finalized', 'Finalisé'),
    ], string='Statut Client', domain="[('customer_rank', '>', 0)]", default="indecis", track_visibility='always')
    module_id = fields.Many2one('mcmacademy.module', track_visibility='always')
    mcm_session_id = fields.Many2one('mcmacademy.session', track_visibility='always')
    mode_de_financement = fields.Selection(selection=[
        ('particulier', 'Personnel'),
        ('cpf', 'Mon Compte Formation, CPF'),
        ('chpf', 'Région Hauts-de-France, CHPF'),
        ('aif', 'Pôle emploi, AIF'),
    ], string='Mode de financement', domain="[('customer_rank', '>', 0)]", default="particulier", track_visibility='always')
    code_pole_emploi = fields.Char('Code Pôle Emploi')
    code_interne=fields.Char('Code Interne')
    nationality=fields.Char('Nationalité')
    birth_name=fields.Char('Nom de naissance')
    birth_state=fields.Char('Région de naissance')
    birth_city=fields.Char('Ville de naissance')
    numero_permis=fields.Char('Numéro de permis')
    numero_carte_identite = fields.Char("Numéro de Carte d'identité")
    lastName = fields.Char()
    # choosed_product=fields.Integer('Produit choisi')



    @api.constrains('code_pole_emploi')
    def _check_parent_id(self):
        for record in self:
            if record.code_pole_emploi:
                if len(record.code_pole_emploi) != 15:
                    raise ValidationError(_('le code pôle emploi doit être composé de 5 chiffres'))
                code = record.code_pole_emploi[10:]
                if code.isdigit() == False:
                    raise ValidationError(_('le code pôle emploi doit comporter que des chiffres'))

    @api.model
    def create(self, values):
        if values.get('code_pole_emploi'):
            values['code_pole_emploi'] = 'AIF41C4910' + str(values['code_pole_emploi'])
        return super(resPartner, self).create(values)

    def write(self, vals):
        result = True
        # To write in SUPERUSER on field is_company and avoid access rights problems.
        if 'code_pole_emploi' in vals:
            vals['code_pole_emploi'] = 'AIF41C4910' + str(vals['code_pole_emploi'])
        result = super(resPartner, self).write(vals)
        return result

    def action_validate(self):
        # self.write({'statut': 'won'})
        for record in self:
            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'res.partner.session.wizard',
                'target': 'new',
                'context': {
                    'default_partner_id': self.ids[0],
                    'default_session_id': record.mcm_session_id.id,
                    'default_module_id': record.module_id.id,
                    'default_statut': record.statut,
                },
            }
    def action_statut(self):
        for rec in self:
            self.write({'statut': 'indecis'})
            for record in self:
                if record.mcm_session_id:
                    list = []
                    for partner in record.mcm_session_id.prospect_ids:
                        list.append(partner.id)
                    list.append(record.id)
                    record.mcm_session_id.write({'prospect_ids': [(6, 0, list)]})
    def action_change_adress(self):
        for record in self:
            record.type=''

    def action_create_contract(self):

        product = self.env['product.product'].sudo().search(
            [('product_tmpl_id', '=', self.module_id.product_id.id)])

        so = self.env['sale.order'].sudo().create({
            'partner_id': self.id,
            'partner_invoice_id': self.id,
            'partner_shipping_id': self.id,
            'order_line': [(0, 0, {'name': product.name, 'product_id': product.id, 'product_uom_qty': 1,
                                   'price_unit': product.list_price})],
        })
        so.action_confirm()
        moves = so._create_invoices(final=True)
        for move in moves:
            move.action_post()
        so.action_cancel()
        so.sale_action_sent()
        if so.env.su:
            # sending mail in sudo was meant for it being sent from superuser
            so = so.with_user(SUPERUSER_ID)
        template_id = so._find_mail_template(force_confirmation_template=True)
        if template_id:
            print('envoi 2')
            so.with_context(force_send=True).message_post_with_template(template_id,
                                                                        composition_mode='comment',
                                                                        email_layout_xmlid="portal_contract.mcm_mail_notification_paynow_online"
                                                                       )

    def add_comment(self,**kw):
        for record in self:
            comment=kw.get('comment')
            print('aaaaa')
            print(comment)
            if record.comment:
                values = {
                    'record_name': self.name,
                    'model': 'res.partner',
                    'message_type': 'comment',
                    'subtype_id': self.env['mail.message.subtype'].search([('name', '=', 'Note')]).id,
                    'res_id': self.id,
                    'author_id': self.env.user.partner_id.id,
                    'date':datetime.now(),
                    'body':record.comment
                }
                self.env['mail.message'].sudo().create(values)
                record.comment=''
class resPartnerWizard(models.TransientModel):
    _name = 'res.partner.session.wizard'
    _description = 'wizard to change state,session & module of partner'

    partner_id=fields.Many2one('res.partner')
    statut = fields.Selection(selection=[
        ('indecis', 'Indécis'),
        ('won', 'Gagné'),
        ('perdu', 'Perdu'),
        ('panier_perdu', 'Panier perdu'),
        ('canceled', 'Annulé'),
        ('finalized', 'Finalisé'),
    ], string='Statut Client', domain="[('customer_rank', '>', 0)]", default="indecis")
    session_id=fields.Many2one('mcmacademy.session','Session')
    module_id=fields.Many2one('mcmacademy.module','Module')

    @api.model
    def create(self, vals):
        partner = super(resPartnerWizard, self).create(vals)
        if 'partner_id' in vals:
            print('client')
            print(vals['partner_id'])
        return partner

    def action_modify_partner(self):
        if self.partner_id:
            if not self.statut and not self.session_id and self.partner_id.mcm_session_id:
                list = []
                for partner in self.partner_id.mcm_session_id.client_ids:
                    if partner.id != self.partner_id.id:
                        list.append(partner.id)
                self.partner_id.mcm_session_id.write({'client_ids': [(6, 0, list)]})

                list = []
                for partner in self.partner_id.mcm_session_id.prospect_ids:
                    if partner.id != self.partner_id.id:
                        list.append(partner.id)
                self.partner_id.mcm_session_id.write({'prospect_ids': [(6, 0, list)]})

                list = []
                for partner in self.partner_id.mcm_session_id.canceled_prospect_ids:
                    if partner.id != self.partner_id.id:
                        list.append(partner.id)
                self.partner_id.mcm_session_id.write({'canceled_prospect_ids': [(6, 0, list)]})

                list = []
                for partner in self.partner_id.mcm_session_id.panier_perdu_ids:
                    if partner.id != self.partner_id.id:
                        list.append(partner.id)
                self.partner_id.mcm_session_id.write({'panier_perdu_ids': [(6, 0, list)]})
            self.partner_id.statut=self.statut
            self.partner_id.mcm_session_id=self.session_id
            self.partner_id.module_id = self.module_id
        check_portal=False
        if self.partner_id.user_ids:
            for user in self.partner_id.user_ids:
                groups=user.groups_id
                for group in groups:
                    if(group.name==_('Portail')):
                        check_portal=True
        # print('')
        # if check_portal:
        if self.statut=='won' or self.statut=='finalized':
            list = []
            for partner in self.session_id.client_ids:
                list.append(partner.id)
            list.append(self.partner_id.id)
            self.session_id.write({'client_ids': [(6, 0, list)]})

            list = []
            for partner in self.session_id.prospect_ids:
                if partner.id != self.partner_id.id:
                    list.append(partner.id)
            self.session_id.write({'prospect_ids': [(6, 0, list)]})

            list = []
            for partner in self.session_id.canceled_prospect_ids:
                if partner.id != self.partner_id.id:
                    list.append(partner.id)
            self.session_id.write({'canceled_prospect_ids': [(6, 0, list)]})

            list = []
            for partner in self.session_id.panier_perdu_ids:
                if partner.id != self.partner_id.id:
                    list.append(partner.id)
            self.session_id.write({'panier_perdu_ids': [(6, 0, list)]})
        if self.statut == 'indecis':
            if self.session_id:
                list = []
                for partner in self.session_id.prospect_ids:
                    list.append(partner.id)
                list.append(self.partner_id.id)
                self.session_id.write({'prospect_ids': [(6, 0, list)]})

                list = []
                for partner in self.session_id.client_ids:
                    if partner.id != self.partner_id.id:
                        list.append(partner.id)
                self.session_id.write({'client_ids': [(6, 0, list)]})

                list = []
                for partner in self.session_id.canceled_prospect_ids:
                    if partner.id != self.partner_id.id:
                        list.append(partner.id)
                self.session_id.write({'canceled_prospect_ids': [(6, 0, list)]})

                list = []
                for partner in self.session_id.panier_perdu_ids:
                    if partner.id != self.partner_id.id:
                        list.append(partner.id)
                self.session_id.write({'panier_perdu_ids': [(6, 0, list)]})
            else:
                if self.partner_id.date_examen_edof and self.partner_id.session_ville_id : #check if state of client is canceled and the client doesn't have a session so we get the date and the city choosed by the client
                    session = self.env['mcmacademy.session'].sudo().search(
                    [('date_exam', "=", self.partner_id.date_examen_edof),('session_ville_id',"=",self.partner_id.session_ville_id.id)],limit=1) #search for the session using the date and city choosed by client
                    if session :
                        list = []
                        for partner in session.prospect_ids:
                            list.append(partner.id)
                        list.append(self.partner_id.id)
                        session.write({'prospect_ids': [(6, 0, list)]})

                        list = []
                        for partner in session.client_ids:
                            if partner.id != self.partner_id.id:
                                list.append(partner.id)
                        session.write({'client_ids': [(6, 0, list)]})

                        list = []
                        for partner in session.canceled_prospect_ids:
                            if partner.id != self.partner_id.id:
                                list.append(partner.id)
                        session.write({'canceled_prospect_ids': [(6, 0, list)]})

                        list = []
                        for partner in session.panier_perdu_ids:
                            if partner.id != self.partner_id.id:
                                list.append(partner.id)
                        session.write({'panier_perdu_ids': [(6, 0, list)]})

        if self.statut == 'panier_perdu':
            list = []
            for partner in self.session_id.panier_perdu_ids:
                list.append(partner.id)
            list.append(self.partner_id.id)
            self.session_id.write({'panier_perdu_ids': [(6, 0, list)]})

            list = []
            for partner in self.session_id.client_ids:
                if partner.id != self.partner_id.id:
                    list.append(partner.id)
            self.session_id.write({'client_ids': [(6, 0, list)]})

            list = []
            for partner in self.session_id.canceled_prospect_ids:
                if partner.id != self.partner_id.id:
                    list.append(partner.id)
            self.session_id.write({'canceled_prospect_ids': [(6, 0, list)]})

            list = []
            for partner in self.session_id.prospect_ids:
                if partner.id != self.partner_id.id:
                    list.append(partner.id)
            self.session_id.write({'prospect_ids': [(6, 0, list)]})

        if self.statut == 'perdu' or self.statut == 'canceled' :
            """désactiver l'annulation de statut pour cpf"""
            if self.partner_id.mode_de_financement=="cpf" and self.partner_id.statut_cpf != "canceled" and self.partner_id.numero_cpf: #add possibilty to canceled a client if he doesn't cpf number
                raise UserError(_("L'apprenant doit annuler son inscription sur son compte cpf. Vous ne pouvez pas annuler manuellement un dossier cpf"))
            if self.session_id :
                list = []
                for partner in self.session_id.canceled_prospect_ids:
                    list.append(partner.id)
                list.append(self.partner_id.id)
                self.session_id.write({'canceled_prospect_ids': [(6, 0, list)]})

                list = []
                for partner in self.session_id.client_ids:
                    if partner.id != self.partner_id.id:
                        list.append(partner.id)
                self.session_id.write({'client_ids': [(6, 0, list)]})

                list = []
                for partner in self.session_id.panier_perdu_ids:
                    if partner.id != self.partner_id.id:
                        list.append(partner.id)
                self.session_id.write({'panier_perdu_ids': [(6, 0, list)]})

                list = []
                for partner in self.session_id.prospect_ids:
                    if partner.id != self.partner_id.id:
                        list.append(partner.id)
                self.session_id.write({'prospect_ids': [(6, 0, list)]})
            else :
                if self.partner_id.date_examen_edof and self.partner_id.session_ville_id : #check if state of client is canceled and the client doesn't have a session so we get the date and the city choosed by the client
                    session = self.env['mcmacademy.session'].sudo().search(
                    [('date_exam', "=", self.partner_id.date_examen_edof),('session_ville_id',"=",self.partner_id.session_ville_id.id)],limit=1) #search for the session using the date and city choosed by client
                    if session :
                        list = []
                        for partner in session.canceled_prospect_ids:
                            list.append(partner.id)
                        list.append(self.partner_id.id)
                        session.write({'canceled_prospect_ids': [(6, 0, list)]}) #append client to canceled list if we found the session

                        list = []
                        for partner in session.client_ids:
                            if partner.id != self.partner_id.id:
                                list.append(partner.id)
                        session.write({'client_ids': [(6, 0, list)]})

                        list = []
                        for partner in session.panier_perdu_ids:
                            if partner.id != self.partner_id.id:
                                list.append(partner.id)
                        session.write({'panier_perdu_ids': [(6, 0, list)]})

                        list = []
                        for partner in session.prospect_ids:
                            if partner.id != self.partner_id.id:
                                list.append(partner.id)
                        session.write({'prospect_ids': [(6, 0, list)]})

        # else:
        #     raise ValidationError(_('Vous pouvez pas modifier un utilisateur interne !'))