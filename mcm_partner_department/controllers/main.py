# -*- coding: utf-8 -*-
from odoo import http,_
import json
from odoo.http import request
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website_sale.controllers.main import TableCompute
from odoo.addons.website_sale.controllers.main import QueryURL
from odoo.addons.portal.controllers.web import Home
from werkzeug.exceptions import Forbidden, NotFound
from odoo.addons.website.models.ir_http import sitemap_qs2dom
from odoo.addons.payment.controllers.portal import PaymentProcessing
from odoo.osv import expression
from odoo.exceptions import ValidationError,Warning,UserError,RedirectWarning
import logging
import base64

logger = logging.getLogger(__name__)

PPG = 20  # Products Per Page
PPR = 4  # Products Per Row


class WebsiteSale(WebsiteSale):

    def submit_documents(self, **kw):
        partner_id = http.request.env.user.partner_id
        folder_id = request.env['documents.folder'].sudo().search(
            [('name', "=", _('Documents MCM ACADEMY')), ('company_id', "=", 1)])
        if not folder_id:
            vals_list = []
            vals = {
                'name': "Documents MCM ACADEMY"
            }
            vals_list.append(vals)
            folder_id = request.env['documents.folder'].sudo().create(vals_list)
            vals_list = []
            vals = {
                'name': "Statut document",
                'folder_id': folder_id.id,
            }
            vals_list.append(vals)
            facet = request.env['documents.facet'].sudo().create(vals_list)
        files_identity = request.httprequest.files.getlist('identity')
        files_identity_verso = request.httprequest.files.getlist('identity2')
        files_permis = request.httprequest.files.getlist('permis')
        files_permis_verso = request.httprequest.files.getlist('permis1')
        if (len(files_identity) > 2 or len(files_permis) > 2):
            name = http.request.env.user.name
            email = http.request.env.user.email
            return request.redirect('/new_documents')
        if not files_identity:
            return request.redirect('/new_documents')
        try:
            try:
                files = request.httprequest.files.getlist('identity')
                files2 = request.httprequest.files.getlist('identity2')
                if files:
                    vals_list = []
                    # charge le modele de la carte d'identité [un seul modele pour deux attachements]
                    # on a pris les precaution au cas ou un client télécharge le recto et le verso avec le meme upload file
                    # on a supprimer datas=False
                    vals = {
                        'name': "Carte d'identité Recto",
                        'folder_id': int(folder_id),
                        'code_document': 'identity',
                        'confirmation': kw.get('confirm_identity'),
                        'attachment_number': kw.get('identity_number'),
                        'type': 'binary',
                        'partner_id': False,
                        'owner_id': False}
                    vals_list.append(vals)
                    document = request.env['documents.document'].sudo().create(vals_list)
                    if document:
                        uid = document.create_uid
                        document.sudo().write(
                            {'owner_id': uid, 'partner_id': uid.partner_id,
                             'name': document.name + ' ' + str(uid.name)})
                    if len(files) == 2:
                        datas_Carte_didentité_Recto = base64.encodebytes(files[0].read())
                        datas_Carte_didentité_Verso = base64.encodebytes(files[1].read())
                        # Attachement Carte d'identité Recto
                        request.env['ir.attachment'].sudo().create({
                            'name': "Carte d'identité recto",
                            'type': 'binary',
                            'datas': datas_Carte_didentité_Recto,
                            'res_model': 'documents.document',
                            'res_id': document.id
                        })
                        # Attachement Carte d'identité Verso
                        request.env['ir.attachment'].sudo().create({
                            'name': "Carte d'identité Verso",
                            'type': 'binary',
                            'datas': datas_Carte_didentité_Verso,
                            'res_model': 'documents.document',
                            'res_id': document.id
                        })
                        # Attachement Carte d'identité recto
                    elif len(files) == 1:
                        datas_carte_didentiterecto = base64.encodebytes(files[0].read())
                        request.env['ir.attachment'].sudo().create({
                            'name': "Carte d'identité recto",
                            'type': 'binary',
                            'datas': datas_carte_didentiterecto,
                            'res_model': 'documents.document',
                            'res_id': document.id
                        })
                if files2 and document:
                    datas_carte_didentite = base64.encodebytes(files2[0].read())

                    request.env['ir.attachment'].sudo().create({
                        'name': "Carte d'identité Verso",
                        'type': 'binary',
                        'datas': datas_carte_didentite,
                        'res_model': 'documents.document',
                        'res_id': document.id
                    })
                document.sudo().write({'name': "Carte d'identité Recto/Verso"})
            except Exception as e:
                logger.exception("Fail to upload document Carte d'identité ")

            try:
                files = request.httprequest.files.getlist('permis')
                files2 = request.httprequest.files.getlist('permis1')
                if files:
                    vals_list = []
                    # charge le modele de la carte d'identité [un seul modele pour deux attachements]
                    # on a pris les precaution au cas ou un client télécharge le recto et le verso avec le meme upload file
                    # on a supprimer datas=False
                    vals = {
                        'name': "Permis de conduire Recto",
                        'folder_id': int(folder_id),
                        'code_document': 'permis',
                        'confirmation': kw.get('confirm_permis'),
                        'attachment_number': '',
                        'type': 'binary',
                        'partner_id': False,
                        'owner_id': False}
                    vals_list.append(vals)
                    document = request.env['documents.document'].sudo().create(vals_list)
                    if document:
                        uid = document.create_uid
                        document.sudo().write(
                            {'owner_id': uid, 'partner_id': uid.partner_id,
                             'name': document.name + ' ' + str(uid.name)})
                    if len(files) == 2:
                        datas_permis_Recto = base64.encodebytes(files[0].read())
                        datas_permis_Verso = base64.encodebytes(files[1].read())
                        # Attachement Carte d'identité Recto
                        request.env['ir.attachment'].sudo().create({
                            'name': "Carte d'identité recto",
                            'type': 'binary',
                            'datas': datas_permis_Recto,
                            'res_model': 'documents.document',
                            'res_id': document.id
                        })
                        # Attachement Carte d'identité Verso
                        request.env['ir.attachment'].sudo().create({
                            'name': "Permis de conduire Verso",
                            'type': 'binary',
                            'datas': datas_permis_Verso,
                            'res_model': 'documents.document',
                            'res_id': document.id
                        })
                        # Attachement Carte d'identité recto
                    elif len(files) == 1:
                        datas_permis_recto = base64.encodebytes(files[0].read())
                        request.env['ir.attachment'].sudo().create({
                            'name': "Permis de conduire Recto",
                            'type': 'binary',
                            'datas': datas_permis_recto,
                            'res_model': 'documents.document',
                            'res_id': document.id
                        })
                if files2 and document:
                    datas_permis = base64.encodebytes(files2[0].read())

                    request.env['ir.attachment'].sudo().create({
                        'name': "Carte d'identité Verso",
                        'type': 'binary',
                        'datas': datas_permis,
                        'res_model': 'documents.document',
                        'res_id': document.id
                    })
                document.sudo().write({'name': "Permis de conduire Recto/Verso"})
            except Exception as e:
                logger.exception("Fail to upload document Carte d'identité ")
        except:
            logger.exception("Fail to upload documents")
        partner = http.request.env.user.partner_id

    @http.route(['/shop/cart/update'], type='http', auth="public", methods=['GET', 'POST'], website=True, csrf=False)
    def cart_update(self, product_id, module='', departement='', add_qty=1, set_qty=0, promo=None, **kw):
        """This route is called when adding a product to cart (no options)."""
        error_message = ''
        sale_order = request.website.sale_get_order(force_create=True)
        if not product_id:
            partner =http.request.env.user.partner_id
            if partner.choosed_product and partner.choosed_product != 0:
                product_id = partner.choosed_product
        if sale_order.order_line:
            list = []
            sale_order.write({'order_line': [(6, 0, list)]})
        if sale_order.state != 'draft':
            request.session['sale_order_id'] = None
            sale_order = request.website.sale_get_order(force_create=True)
        product_custom_attribute_values = None
        if kw.get('product_custom_attribute_values'):
            product_custom_attribute_values = json.loads(kw.get('product_custom_attribute_values'))

        no_variant_attribute_values = None
        if kw.get('no_variant_attribute_values'):
            no_variant_attribute_values = json.loads(kw.get('no_variant_attribute_values'))
        print('promo 1')
        if promo:
            print(promo)
        if product_id:
            sale_order._cart_update(
                product_id=int(product_id),
                add_qty=1,
                set_qty=1,
                product_custom_attribute_values=product_custom_attribute_values,
                no_variant_attribute_values=no_variant_attribute_values
            )
        if promo:
            pricelist = request.env['product.pricelist'].sudo().search(
                [('id', "=", promo)]) #search priclist in all companies
            if pricelist:
                request.website.sale_get_order(code=pricelist.code)
        else:
            request.website.sale_get_order(code='')
        if (sale_order.partner_id.customer_rank == 0):
            sale_order.partner_id.customer_rank = 1
        if product_id:
            if module == 'all':
                product = request.env['product.template'].sudo().search(
                    [('id', '=', product_id)])
                error_session = "error"
                url = "/shop/product/" + str(slug(product))
                values = self._prepare_product_values(product, category='', search='', **kw)
                values['error_session'] = "error"
                return request.redirect("/#pricing")

            if module != '' and module != 'all':
                module = request.env['mcmacademy.module'].sudo().search(
                    [('id', '=', module)])
                session = module.session_id
                if session:
                    sale_order.session_id = session
                    sale_order.partner_id.mcm_session_id = session
                if module:
                    sale_order.module_id = module
                    sale_order.partner_id.module_id = module
                list = []
                check_portal = False
                if sale_order.partner_id.user_ids:
                    for user in sale_order.partner_id.user_ids:
                        groups = user.groups_id
                        for group in groups:
                            if (group.name == _('Portail')):
                                check_portal = True
                if check_portal:
                    for partner in session.panier_perdu_ids:
                        list.append(partner.id)
                    list.append(sale_order.partner_id.id)
                    session.write({'panier_perdu_ids': [(6, 0, list)]})
                    sale_order.partner_id.statut = 'panier_perdu'
                    sale_order.partner_id.module_id = module
                    sale_order.partner_id.mcm_session_id = session
        if product_id:
            if departement != 'all':
                state = request.env['res.country.state'].sudo().search(
                    ['&', ('code', "=", str(departement)), ('country_id.code', 'ilike', 'FR')])
                if state:
                    sale_order.partner_id.state_id = state
                if departement == '59':
                    sale_order.partner_id.partner_departement = '59000'
                if departement == '62':
                    sale_order.partner_id.partner_departement = '62000'
            else:
                print('test false')
                product = request.env['product.template'].sudo().search(
                    [('id', '=', product_id)])
                error_message = "error"
                url = "/shop/product/" + str(slug(product))
                values = self._prepare_product_values(product, category='', search='', **kw)
                values['error_department'] = "error"
                return request.render("website_sale.product", values)

        if kw.get('express'):
            return request.redirect("/shop/checkout?express=1")
        if product_id:
            product = request.env['product.template'].sudo().search(
                [('id', '=', product_id)], limit=1)
            slugname = (product.name).strip().strip('-').replace(' ', '-').lower()
            if not promo and product and product.company_id.id == 2:
                return request.redirect("/%s/shop/cart" % (slugname))
            elif promo and product and product.company_id.id == 2:
                pricelist = request.env['product.pricelist'].sudo().search(
                    [('company_id', '=', 2), ('id', "=", promo)])
                if pricelist:
                    if pricelist.name in ['ubereats', 'deliveroo', 'coursierjob','box2home']:
                        return request.redirect("/%s/%s/shop/cart" % (slugname, pricelist.name))
            if not promo and product and product.company_id.id == 1:
                return request.redirect("/%s/shop/cart" % (slugname))
            elif promo and product and product.company_id.id == 1:
                pricelist = request.env['product.pricelist'].sudo().search(
                    [('company_id', '=', 1), ('id', "=", promo)])
                if pricelist:
                    if pricelist.name in ['bolt']:
                        return request.redirect("/%s/%s/shop/cart" % (slugname, pricelist.name))
        return request.redirect("/shop/cart")