import logging
import werkzeug
import odoo.http as http
import base64
import werkzeug
import requests
from PIL import Image
import PIL
import os
import glob
from odoo.http import request
from odoo import _
from addons.portal.controllers.portal import _build_url_w_params
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.exceptions import AccessError
from bs4 import BeautifulSoup as BSHTML
import urllib3
from werkzeug import FileStorage as storage
import PIL
from PIL import Image
import os
import glob
from odoo.exceptions import UserError
import mimetypes
from odoo.tools.mimetypes import guess_mimetype


logger = logging.getLogger(__name__)



class CustomerPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        print('_prepare_portal_layout_values')
        user = request.env.user
        document_count = request.env['documents.document'].sudo().search_count(
            [('owner_id', '=', user.id)])
        values['document_count'] = document_count
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        invoice_count = request.env['account.move'].search_count([
            ('type', 'in', ('out_invoice', 'in_invoice', 'out_refund', 'in_refund', 'out_receipt', 'in_receipt')),
            ('type_facture', '=', 'web'), ('cpf_solde_invoice', '=', False), ('cpf_acompte_invoice', '=', False)])
        values['invoice_count'] = invoice_count
        print('invoice_count')
        print(invoice_count)
        partner_orders_signed = request.env['sale.order'].sudo().search([('partner_id', '=', request.env.user.partner_id.id),('company_id', '=', 1),('state',"=",'sale')])
        isSigned = "False"
        if partner_orders_signed :
            for order in partner_orders_signed :
                if order.order_line :
                    for line in order.order_line :
                        if (line.product_id.default_code=='vtc_bolt'):
                            isSigned = "True"
        bolt_order = False
        partner_orders_not_signed = request.env['sale.order'].sudo().search(
            [('partner_id', '=', request.env.user.partner_id.id), ('company_id', '=', 1), ('state', "=", 'sent')])
        if partner_orders_not_signed :
            for order in partner_orders_not_signed :
                if order.order_line :
                    for line in order.order_line :
                        if (line.product_id.default_code=='vtc_bolt'):
                            bolt_order = order
        bolt_contract_uri = "False"
        if bolt_order :
            bolt_contract_uri = "/my/orders/%s?access_token=%s" % (str(bolt_order.id), str(bolt_order.access_token))
        rdvIsBooked = "False"
        rendezvous = request.env['calendly.rendezvous'].sudo().search([('partner_id', '=', request.env.user.partner_id.id)],limit=1)
        if rendezvous :
            rdvIsBooked = "True"
        cartIsEmpty = "False"
        order = request.website.sale_get_order()
        if not order:
            cartIsEmpty = "True"
        if order and not order.order_line :
            cartIsEmpty = "True"
        values.update({
            'rdvIsBooked' : rdvIsBooked,
            'cartIsEmpty' : cartIsEmpty,
            'isSigned' : isSigned,
            'bolt_contract_uri':bolt_contract_uri
        })
        return values

    # def _document_check_access(self, document_id):
    #     document = request.env['documents.document'].browse([document_id])
    #     document_sudo = document.sudo()
    #     try:
    #         document.check_access_rights('read')
    #         document.check_access_rule('read')
    #     except AccessError:
    #         raise
    #     return document_sudo

    @http.route(
        ['/my/documents', '/my/documents/page/<int:page>'],
        type='http',
        auth="user",
        website=True,
    )
    def portal_my_tickets(
            self,
            page=1,
            date_begin=None,
            date_end=None,
            sortby=None,
            filterby=None,
            **kw):
        values = self._prepare_portal_layout_values()
        Document = request.env['documents.document']
        user = request.env.user
        website = request.website
        domain = [('owner_id', '=', user.id)]

        searchbar_sortings = {
            'date': {'label': _('Nouveau'), 'order': 'create_date desc'},
            'name': {'label': _('Nom'), 'order': 'name'},
            'stage': {'label': _('État'), 'order': 'state'},
        }
        searchbar_filters = {
            'all': {'label': _('Tous'), 'domain': []},
            'refused': {'label': _('Refuser'), 'domain': [("state", "=", "refused")]},
            'waiting': {'label': _('En Attente de validation'), 'domain': [("state", "=", "waiting")]},
            'validated': {'label': _('Valider'), 'domain': [("state", "=", "validated")]},
        }

        # default sort by order
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        # count for pager
        document_count = Document.sudo().search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/documents",
            url_args={},
            total=document_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        documents = Document.sudo().search(
            domain,
            order=order,
            limit=self._items_per_page,
            offset=pager['offset']
        )
        values.update({
            'date': date_begin,
            'documents': documents,
            'page_name': 'document',
            'website' : website,
            'pager': pager,
            'default_url': '/my/documents',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': searchbar_filters,
            'filterby': filterby,
        })
        return request.render("mcm_contact_documents.portal_my_documents", values)
# upload documents MCM-Academy
    # Retour en arrière pour la version précédente pour les mimetype à cause d un problème service clientèle le 06/09/2021
    @http.route(['/submitted/document'], type="http", auth="user", methods=['POST'], website=True, csrf=False)
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
            return request.redirect('/charger_mes_documents')
        if not files_identity:
            return request.redirect('/charger_mes_documents')
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
                         # ajout du champ mimetype  dans ir.attachement
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
                        # ajout du champ mimetype  dans ir.attachement
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
                    # ajout du champ mimetype  dans ir.attachement
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
        # suppression des documents qui ont mimetype de type octet_stream
        obj_attachment = request.env['ir.attachment']
        partner = http.request.env.user.partner_id
        partner.step = "financement"
        order = request.website.sale_get_order()
        if order:
            return request.redirect('/shop/cart')
        else:
            return request.redirect('/pricing')
# Upload documents digimoov
    # Retour en arrière pour la version précédente pour les mimetype à cause d un problème service clientèle le 06/09/2021
    @http.route('/upload_my_files', type="http", auth="user", methods=['POST'], website=True, csrf=False)
    def upload_my_files(self, **kw):
        # charger le dossier des documents clients appartenant a Digimoov
        folder_id = request.env['documents.folder'].sudo().search(
            [('name', "=", _('Documents Digimoov')), ('company_id', "=", 2)])
        if not folder_id:
            vals_list = []
            # charger les documents appartenant seulement a digimoov
            vals = {
                'name': "Documents Digimoov",
                'company_id': 2
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
            # Ce code  a été modifiée par Seif le 10/03/2021  (!datas!)

        files_identity = request.httprequest.files.getlist('identity')
        files_identity_verso = request.httprequest.files.getlist('identity2')


        if (len(files_identity) > 2 ):
            name = http.request.env.user.name
            email = http.request.env.user.email
            return request.redirect('/charger_mes_documents')
        if not files_identity:
            return request.redirect('/charger_mes_documents')
        try:
            try:
                files = request.httprequest.files.getlist('identity')
                files2 = request.httprequest.files.getlist('identity2')
                if files :
                    vals_list = []
                    # charge le modele de la carte d'identité [un seul modele pour deux attachements]
                    # on a pris les precaution au cas ou un client télécharge le recto et le verso avec le meme upload file
                    # on a supprimer datas=False
                    vals = {
                        'name': "Carte d'identité Recto",
                        'folder_id': int(folder_id),
                        'code_document': 'identity',
                        'confirmation': kw.get('confirm_identity'),
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
                    # En cas ou le candiadat charge deux piéces_jointe
                    #ajout du champ mimetype dans ir.attachement
                    #Retour en arrière pour la version précédente pour les mimetype à cause d un problème service clientèle le 06/09/2021
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
                        # ajout du champ mimetype dans ir.attachement
                        # Retour en arrière pour la version précédente pour les mimetype à cause d un problème service clientèle le 06/09/2021
                    elif len(files) == 1:
                        datas_carte_didentiterecto = base64.encodebytes(files[0].read())
                        request.env['ir.attachment'].sudo().create({
                            'name': "Carte d'identité recto",
                            'type': 'binary',
                            'datas': datas_carte_didentiterecto,
                            'res_model': 'documents.document',
                            'res_id': document.id
                        })
                        # ajout du champ mimetype dans ir.attachement
                        # Retour en arrière pour la version précédente pour les mimetype à cause d un problème service clientèle le 06/09/2021
                if files2 and document :
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
        except Exception as e:
            logger.exception("Fail to upload document Carte d'identité")
        partner = http.request.env.user.partner_id
        partner.step = "financement"
        order = request.website.sale_get_order()
        if order:
            return request.redirect('/shop/cart')
        else:
            return request.redirect('/pricing')

    @http.route('/upload_my_files1', type="http", auth="user", methods=['POST'], website=True, csrf=False)
    def upload_my_files1(self, **kw):
        # charger le dossier des documents clients appartenant à Digimoov
        # mcm-academy a l'id 1 et digimoov a l'id 2
        folder_id = request.env['documents.folder'].sudo().search(
            [('name', "=", _('Documents Digimoov')), ('company_id', "=", 2)])
        # Si le dossier Documents Digimoov n'existe pas, le créer
        if not folder_id:
            vals_list = []
            # mcm-academy a l'id 1 et digimoov a l'id 2
            vals = {
                'name': "Documents Digimoov",
                'company_id': 2
            }
            vals_list.append(vals)
            folder_id = request.env['documents.folder'].sudo().create(vals_list)

        try:
            # Récupérer le justificatif de domicile
            fichier_justificatif = request.httprequest.files.getlist('justificatif_domicile')
            fichier_cerfa = request.httprequest.files.getlist('cerfa')
            if fichier_justificatif:
                vals_list = []
                # Création du document justificatif de domicile
                vals = {
                    'name': "Jusitificatif de domicile",
                    'folder_id': int(folder_id),
                    'code_document': 'justificatif_domicile',
                    'type': 'binary',
                    'partner_id': False,
                    'owner_id': False
                }
                vals_list.append(vals)
                document_justificatif = request.env['documents.document'].sudo().create(vals_list)
                if document_justificatif:
                    # Ajouter le partner_id et le owner_id
                    uid = document_justificatif.create_uid
                    document_justificatif.sudo().write(
                        {'owner_id': uid, 'partner_id': uid.partner_id,
                         'name': document_justificatif.name + ' ' + str(uid.name)})
                    # Créer la pièce jointe
                    datas_justificatif = base64.encodebytes(fichier_justificatif[0].read())
                    request.env['ir.attachment'].sudo().create({
                        'name': "Jusitificatif de domicile",
                        'type': 'binary',
                        'datas': datas_justificatif,
                        'res_model': 'documents.document',
                        'res_id': document_justificatif.id
                    })
        except Exception as e:
            logger.exception("Erreur de chargement du fichier justificatif de domicile ")

        try:
            # Récupérer l'identité de l'hébergeur
            fichier_identite = request.httprequest.files.getlist('identite_hebergeur')
            if fichier_identite:
                # Création du document identité de l'hébergeur
                vals_list = []
                vals = {
                    'name': "Carte d'identité hébergeur",
                    'folder_id': int(folder_id),
                    'code_document': 'identite_hebergeur',
                    'type': 'binary',
                    'partner_id': False,
                    'owner_id': False
                }
                vals_list.append(vals)
                document_identite_hebergeur = request.env['documents.document'].sudo().create(vals_list)
                if document_identite_hebergeur:
                    # Ajouter le partner_id et le owner_id
                    uid = document_identite_hebergeur.create_uid
                    document_identite_hebergeur.sudo().write(
                        {'owner_id': uid, 'partner_id': uid.partner_id,
                         'name': document_identite_hebergeur.name + ' ' + str(uid.name)})
                    # Créer la pièce jointe
                    datas_identite_hebergeur = base64.encodebytes(fichier_identite[0].read())
                    request.env['ir.attachment'].sudo().create({
                        'name': "Carte d'identité de l'hébergeur",
                        'type': 'binary',
                        'datas': datas_identite_hebergeur,
                        'res_model': 'documents.document',
                        'res_id': document_identite_hebergeur.id
                    })
                if document_identite_hebergeur:
                    document_identite_hebergeur.sudo().write({'name': "Carte d'identité de l'hébergeur"})
        except Exception as e:
            logger.exception("Erreur de chargement du document: Carte d'identité de l'hébergeur")
        try:
            # charger l'attestation de l'hébergement
            fichier_attestation = request.httprequest.files.getlist('attestation_hebergement')
            if fichier_attestation:
                # Création du document
                vals_list = []
                vals = {
                    'name': "Attestation d'hébergement",
                    'folder_id': int(folder_id),
                    'code_document': 'attestation_hebergement',
                    'type': 'binary',
                    'partner_id': False,
                    'owner_id': False
                }
                vals_list.append(vals)
                document_attestation = request.env['documents.document'].sudo().create(vals_list)
                if document_attestation :
                    # Ajouter le partner_id et le owner_id
                    uid = document_attestation.create_uid
                    document_attestation.sudo().write(
                        {'owner_id': uid, 'partner_id': uid.partner_id,
                         'name': document_attestation.name + ' ' + str(uid.name)})
                    # Créer la pièce jointe
                    datas_attestation_hebergement = base64.encodebytes(fichier_attestation[0].read())
                    request.env['ir.attachment'].sudo().create({
                        'name': "Attestation d'hébergement",
                        'type': 'binary',
                        'datas': datas_attestation_hebergement,
                        'res_model': 'documents.document',
                        'res_id': document_attestation.id
                    })
        except Exception as e:
            logger.exception("Erreur de téléchargement du fichier: Attestation d'hébergement")

    # ce code  a été modifié par Seifeddinne le 26/10/2021


        try:
            # charger le document CERFA
            fichier_cerfa = request.httprequest.files.getlist('cerfa')
            datas_cerfa = base64.encodebytes(fichier_cerfa[0].read())
            if fichier_cerfa:
                # Création du document
                vals_list = []
                vals = {
                    'name': "CERFA",
                    'folder_id': int(folder_id),
                    'code_document': 'cerfa',
                    'confirmation': kw.get('confirm_cerfa'),
                    'datas': datas_cerfa,
                    'type': 'binary',
                    'partner_id': False,
                    'owner_id': False
                }
                vals_list.append(vals)
                document_cerfa = request.env['documents.document'].sudo().create(vals_list)
                if document_cerfa:
                    # Ajouter le partner_id et le owner_id
                    uid = document_cerfa.create_uid
                    # Créer la pièce jointe
                    document_cerfa.sudo().write(
                        {'owner_id': uid, 'partner_id': uid.partner_id,
                         'name': document_cerfa.name + ' ' + str(uid.name)})
        except Exception as e:
            logger.exception("Erreur de téléchargement du document: CERFA")
        return http.request.render('mcm_contact_documents.success_documents_1')

    @http.route('/new_documents', type="http", auth="user", website=True)
    def create_documents(self, **kw):
        return request.redirect('/charger_mes_documents')
        name = http.request.env.user.name
        email = http.request.env.user.email
        partner_id = http.request.env.user.partner_id
        print(partner_id.module_id.name)
        return http.request.render('mcm_contact_documents.mcm_contact_documents_new_documents', {
            'email': email, 'name': name, 'partner_id':partner_id ,'error_identity':'','error_permis':'','error_permis_number':'','error_domicile':'' })


    #Nouvelle page qui ressemble à la page précédente
    @http.route('/charger_mes_documents_1', type="http", auth="user", website=True)
    def create_documents_digimoov1(self, **kw):
        name = http.request.env.user.name
        email = http.request.env.user.email
        partner_id = http.request.env.user.partner_id
        return http.request.render('mcm_contact_documents.mcm_contact_document_charger_mes_documents1', {
            'email': email, 'name': name, 'partner_id': partner_id, 'error_identity': '', 'error_permis': '', 'error_permis_number': '', 'error_domicile': ''})

    @http.route('/charger_mes_documents', type="http", auth="user", website=True)
    def create_documents_digimoov(self, **kw):
        name = http.request.env.user.name
        email = http.request.env.user.email
        partner_id = http.request.env.user.partner_id
        if request.website.id==2: # id 2 of website in database means website DIGIMOOV
            return http.request.render('mcm_contact_documents.mcm_contact_document_charger_mes_documents', {
                'email': email, 'name': name, 'partner_id': partner_id, 'error_identity': '', 'error_permis': '', 'error_permis_number': '', 'error_domicile': ''})
        elif request.website.id==1: # id 1 of website in database means website MCM ACADEMY
            return http.request.render('mcm_contact_documents.mcm_contact_documents_charger_mes_documents_mcm', {
                'email': email, 'name': name, 'partner_id': partner_id, 'error_identity': '', 'error_permis': '', 'error_permis_number': '', 'error_domicile': ''})

    @http.route('/charger_mes_documents_manual', type="http", auth="user", website=True)
    def create_documents_manual(self, **kw):
        name = http.request.env.user.name
        email = http.request.env.user.email
        partner_id = http.request.env.user.partner_id
        if request.website.id==2: # id 2 of website in database means website DIGIMOOV
            return http.request.render('mcm_contact_documents.digimoov_documents_manual', {
                'email': email, 'name': name, 'partner_id': partner_id, 'error_identity': '', 'error_permis': '', 'error_permis_number': '', 'error_domicile': ''})
        elif request.website.id==1: # id 1 of website in database means website MCM ACADEMY
            return http.request.render('mcm_contact_documents.mcm_documents_manual', {
                'email': email, 'name': name, 'partner_id': partner_id, 'error_identity': '', 'error_permis': '', 'error_permis_number': '', 'error_domicile': ''})


    def _document_get_page_view_values(self, document, access_token, **kwargs):
        values = {
            'page_name': 'document',
            'document': document,
        }
        return self._get_page_view_values(document, access_token, values, 'my_documents_history', False, **kwargs)

    @http.route(['/my/document/<int:document_id>'], type='http', website=True)
    def portal_my_document(self, document_id=None,access_token=None, **kw):
        document=request.env['documents.document'].sudo().search(
            [('id', '=', document_id)],limit=1)
        #view portal of refused document
        if document:
            if document.state != 'refused':
                return request.redirect('/my/documents')
            document_sudo=document.sudo()
            if document.owner_id.id != http.request.env.user.id:
                return request.redirect('/my/documents')
        values = self._document_get_page_view_values(document_sudo, access_token, **kw)

        return request.render("mcm_contact_documents.portal_document_page",
                              values)

    @http.route(['/update/<int:document_id>'], type="http", auth="user", methods=['POST'], website=True, csrf=False)
    def update_document(self,document_id=None, **kw):
        document = request.env['documents.document'].sudo().search(
            [('id', '=', document_id)], limit=1)
        #search and get the refused document
        # # ce code  a été modifié par Seifeddinne le 26/10/2021
        # rectification de la partie Cerfa ajout de [ir.attachement]

        if document:
            try:
                files = request.httprequest.files.getlist('updated_document') #if the refused document is not CERFA
                if not files:
                    # if the refused document is CERFA
                    files = request.httprequest.files.getlist('updated_document_cerfa')
                files2 = request.httprequest.files.getlist('updated_document_cerfa2') # get the second page of cerfa if the client upload only one image in first upload zone
                files3 = request.httprequest.files.getlist('updated_document_cerfa3')  # get the third page of cerfa if the client upload only one image in first upload zone
                for ufile in files:
                    # mimetype = self._neuter_mimetype(ufile.content_type, http.request.env.user)
                    datas = base64.encodebytes(ufile.read())
                    if request.website.id==1: # if refused document is for a mcm academy client
                        vals = {
                            'state':'waiting', #set the state of the refused document to verification (MCM ACADEMY)
                        }
                        document.sudo().write(vals)
                        request.env['ir.attachment'].sudo().create({
                            'name': "Cerfa",
                            'type': 'binary',
                            'datas': datas,
                            'res_model': 'documents.document',
                            'res_id': document.id
                        })
                    else: # if refused document is for a digimoov client
                        vals = {
                            'state': 'waiting', #set the state of the refused document to verification (DIGIMOOV)
                            'datas':datas
                        }
                        document.sudo().write(vals)
                        request.env['ir.attachment'].sudo().create({
                            'name': "Cerfa",
                            'type': 'binary',
                            'datas': datas,
                            'res_model': 'documents.document',
                            'res_id': document.id
                        })
                if files2:
                    datas_cerfa = base64.encodebytes(files2[0].read()) #get the second page of cerfa
                    request.env['ir.attachment'].sudo().create({
                        'name': "Cerfa Page 3",
                        'type': 'binary',
                        'datas': datas_cerfa,
                        'res_model': 'documents.document',
                        'res_id': document.id
                    })
                if files3:
                    datas_cerfa = base64.encodebytes(files3[0].read()) #get the third page of cerfa
                    request.env['ir.attachment'].sudo().create({
                        'name': "Cerfa Page 3",
                        'type': 'binary',
                        'datas': datas_cerfa,
                        'res_model': 'documents.document',
                        'res_id': document.id
                    })
            except Exception as e:
                logger.exception("Fail to upload document %s" % ufile.filename)

        return request.redirect('/my/documents')

    @http.route(['/my/cerfa'], type='http', auth="user", website=True)
    def portal_cerfa(self):
        return request.render("mcm_contact_documents.cerfa_portal_template")


