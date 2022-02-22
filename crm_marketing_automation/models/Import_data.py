import base64
import binascii
import codecs
import collections
import unicodedata

import chardet
import datetime
import io
import itertools
import logging
import psycopg2
import operator
import os
import re
import requests
from datetime import date,datetime
from PIL import Image
from odoo import http,SUPERUSER_ID,_
from odoo import api, fields, models
from odoo.exceptions import AccessError
from odoo.tools.translate import _
from odoo.tools.mimetypes import guess_mimetype
from odoo.tools import config, DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, pycompat
import logging
_logger = logging.getLogger(__name__)

class Import(models.TransientModel):
    _inherit  ='base_import.import'
    # date_import=fields.datetime('Dernière mis à jour')
    """ heritage de methode d'importation pour mettre à jour les statuts cpf sur fiches clients  """
    def do(self, fields, columns, options, dryrun=False):
        date_import=date.today()
        result= super(Import, self).do(fields, columns, options, dryrun)
        _logger.info('Imporrrttttttttt %s ' %str(self.res_model))
        if "crm.lead" == self.res_model:

            leads = self.env['crm.lead'].search([('stage_id.name','!=',"Formation sur 360")])
            statut_cpf=['']
            for lead in leads:
                # if lead.stage_id.name!="Formation sur 360":
                    num_dossier = str(lead.num_dossier)
                    partners = self.env['res.partner'].search([('numero_cpf',"=",num_dossier)])
                    _logger.info('lead %s' %lead.name)
                    for partner in partners:
                        # if (partner.numero_cpf) and (partner.numero_cpf == lead.num_dossier):
                        #     print('lead',lead.num_dossier,'partner',partner.numero_cpf)
                        """Changer statut_cpf des fiches client selon
                                                  statut de dossier nsur edof"""
                        # partner.mode_de_financement = 'cpf'
                        # if lead.stage_id.name == "En formation":
                        #     partner.statut_cpf = "in_training"
                        if lead.stage_id.name == "Accepté":
                            partner.statut_cpf = "accepted"
                            if not partner.id_edof:
                                partner.id_edof=lead.numero_action
                            self.cpf_accpted(partner)
                        # if "Annulé" in lead.stage_id.name:
                        #     partner.statut_cpf = "canceled"
                        # if lead.stage_id.name == "Sortie de formation":
                        #     partner.statut_cpf = "out_training"
                        # if lead.stage_id.name == "Facturé":
                        #     partner.statut_cpf = "bill"
                        # if lead.stage_id.name == "Service fait déclaré":
                        #     partner.statut_cpf = "service_declared"
                        # if "Service fait validé" in lead.stage_id.name:
                        #     partner.statut_cpf = "service_validated"
                        # if lead.stage_id.name == "Annulation titulaire":
                        #     partner.statut_cpf = "canceled"

                        lead.sudo().write({
                                'nom': partner.firstName if firstName else "",
                                'prenom': partner.lastName if lastName else "",
                                'partner_id': partner,
                                'name': partner.name,
                                'mode_de_financement': 'cpf',
                                'module_id': partner.module_id ,
                                'mcm_session_id': partner.mcm_session_id,
                                'company_id':partner.company_id.id if partner.company_id else False

                            })


        return result

    def cpf_accpted(self,partner):
        if partner and partner.id_edof:
            if 'digimoov' in str(partner.id_edof):
                product_id = self.env['product.template'].sudo().search(
                    [('id_edof', "=", str(partner.id_edof)), ('company_id', "=", 2)], limit=1)
            else:
                product_id = self.env['product.template'].sudo().search(
                    [('id_edof', "=", str(partner.id_edof)), ('company_id', "=", 1)], limit=1)

            if product_id and product_id.company_id.id == 2 and partner.id_edof and partner.date_examen_edof and partner.session_ville_id:
                module_id = self.env['mcmacademy.module'].sudo().search(
                    [('company_id', "=", 2), ('session_ville_id', "=", partner.session_ville_id.id),
                     ('date_exam', "=", partner.date_examen_edof), ('product_id', "=", product_id.id),
                     ('session_id.number_places_available', '>', 0)], limit=1)
                if module_id:
                    partner.module_id = module_id
                    partner.mcm_session_id = module_id.session_id
                    product_id = self.env['product.product'].sudo().search(
                        [('product_tmpl_id', '=', module_id.product_id.id)])
                    partner.mcm_session_id = module_id.session_id
                    partner.module_id = module_id
                    order = self.env['sale.order'].sudo().search(
                        [('module_id', "=", module_id.id), ('state', 'in', ('sent', 'sale')),
                         ('partner_id', "=", partner.id)])
                    if not order:
                        so = self.env['sale.order'].sudo().create({
                            'partner_id': partner.id,
                            'company_id': 2,
                        })
                        so.module_id = module_id
                        so.session_id = module_id.session_id

                        so_line = self.env['sale.order.line'].sudo().create({
                            'name': product_id.name,
                            'product_id': product_id.id,
                            'product_uom_qty': 1,
                            'product_uom': product_id.uom_id.id,
                            'price_unit': product_id.list_price,
                            'order_id': so.id,
                            'tax_id': product_id.taxes_id,
                            'company_id': 2,
                        })
                        # prix de la formation dans le devis
                        amount_before_instalment = so.amount_total
                        # so.amount_total = so.amount_total * 0.25
                        for line in so.order_line:
                            line.price_unit = so.amount_total
                        so.action_confirm()
                        ref = False
                        # Creation de la Facture Cpf
                        # Si la facture est de type CPF :  On parse le pourcentage qui est 25 %
                        # methode_payment prend la valeur CPF pour savoir bien qui est une facture CPF qui prend la valeur 25 % par default

                        if so.amount_total > 0 and so.order_line:
                            moves = so._create_invoices(final=True)
                            for move in moves:
                                move.type_facture = 'interne'
                                # move.cpf_acompte_invoice= True
                                # move.cpf_invoice =True
                                move.methodes_payment = 'cpf'
                                move.pourcentage_acompte = 25
                                move.module_id = so.module_id
                                move.session_id = so.session_id
                                if so.pricelist_id.code:
                                    move.pricelist_id = so.pricelist_id
                                move.company_id = so.company_id
                                move.price_unit = so.amount_total
                                # move.cpf_acompte_invoice=True
                                # move.cpf_invoice = True
                                move.methodes_payment = 'cpf'
                                move.post()
                                ref = move.name
                        so.action_cancel()
                        for line in so.order_line:
                            line.price_unit = amount_before_instalment
                        so.sale_action_sent()
                        if so.env.su:
                            # sending mail in sudo was meant for it being sent from superuser
                            so = so.with_user(SUPERUSER_ID)

                        #
                        template_id = int(self.env['ir.config_parameter'].sudo().get_param(
                            'portal_contract.mcm_mail_template_sale_confirmation'))
                        template_id = self.env['mail.template'].sudo().search([('id', '=', template_id)]).id

                        if not template_id:
                            template_id = self.env['ir.model.data'].xmlid_to_res_id(
                                'portal_contract.mcm_mail_template_sale_confirmation', raise_if_not_found=False)
                        if not template_id:
                            template_id = self.env['ir.model.data'].xmlid_to_res_id(
                                'portal_contract.mcm_email_template_edi_sale', raise_if_not_found=False)
                        if template_id:
                            so.with_context(force_send=True).message_post_with_template(template_id,
                                                                                        composition_mode='comment',
                                                                                        email_layout_xmlid="portal_contract.mcm_mail_notification_paynow_online")

                        partner.statut = 'won'
                elif product_id and product_id.company_id.id == 1 and partner.id_edof and partner.date_examen_edof and partner.session_ville_id:
                    module_id = self.env['mcmacademy.module'].sudo().search(
                        [('company_id', "=", 1), ('session_ville_id', "=", partner.session_ville_id.id),
                         ('date_exam', "=", partner.date_examen_edof), ('product_id', "=", product_id.id),
                         ('session_id.number_places_available', '>', 0)], limit=1)
                    if module_id:
                        partner.module_id = module_id
                        partner.mcm_session_id = module_id.session_id
                        product_id = self.env['product.product'].sudo().search(
                            [('product_tmpl_id', '=', module_id.product_id.id)])
                        partner.mcm_session_id = module_id.session_id
                        partner.module_id = module_id
                        order = self.env['sale.order'].sudo().search(
                            [('module_id', "=", module_id.id), ('state', 'in', ('sent', 'sale')),
                             ('partner_id', "=", partner.id)])
                        if not order:
                            so = self.env['sale.order'].sudo().create({
                                'partner_id': partner.id,
                                'company_id': 1,
                            })
                            self.env['sale.order.line'].sudo().create({
                                'name': product_id.name,
                                'product_id': product_id.id,
                                'product_uom_qty': 1,
                                'product_uom': product_id.uom_id.id,
                                'price_unit': product_id.list_price,
                                'order_id': so.id,
                                'tax_id': product_id.taxes_id,
                                'company_id': 1
                            })
                            # Enreggistrement des valeurs de la facture
                            # Parser le pourcentage d'acompte
                            # Creation de la fcture étape Finale
                            # Facture comptabilisée
                            so.action_confirm()
                            so.module_id = module_id
                            so.session_id = module_id.session_id
                            moves = so._create_invoices(final=True)
                            for move in moves:
                                move.type_facture = 'interne'
                                move.module_id = so.module_id
                                # move.cpf_acompte_invoice=True
                                # move.cpf_invoice =True
                                move.methodes_payment = 'cpf'
                                move.pourcentage_acompte = 25
                                move.session_id = so.session_id
                                move.company_id = so.company_id
                                move.website_id = 1
                                for line in move.invoice_line_ids:
                                    if line.account_id != line.product_id.property_account_income_id and line.product_id.property_account_income_id:
                                        line.account_id = line.product_id.property_account_income_id
                                move.post()
                            so.action_cancel()
                            so.unlink()
                            partner.statut = 'won'
            else:
                if 'digimoov' in str(partner.id_edof):
                    vals = {
                        'description': 'CPF: vérifier la date et ville de %s' % (partner.name),
                        'name': 'CPF : Vérifier Date et Ville ',
                        'team_id': self.env['helpdesk.team'].sudo().search(
                            [('name', 'like', 'Client'), ('company_id', "=", 2)],
                            limit=1).id,
                    }
                    description = "CPF: vérifier la date et ville de " + str(partner.name)
                    ticket = self.env['helpdesk.ticket'].sudo().search([("description", "=", description)])
                    if not ticket:
                        new_ticket = self.env['helpdesk.ticket'].sudo().create(
                            vals)
                else:
                    vals = {
                        'partner_email': '',
                        'partner_id': False,
                        'description': 'CPF: id module edof %s non trouvé' % (partner.id_edof),
                        'name': 'CPF : ID module edof non trouvé ',
                        'team_id': self.env['helpdesk.team'].sudo().search(
                            [('name', "like", _('Client')), ('company_id', "=", 1)],
                            limit=1).id,
                    }
                    description = 'CPF: id module edof ' + str(partner.id_edof) + ' non trouvé'
                    ticket = self.env['helpdesk.ticket'].sudo().search([('description', 'ilike', description)])
                    if not ticket:
                        new_ticket = self.env['helpdesk.ticket'].sudo().create(
                            vals)