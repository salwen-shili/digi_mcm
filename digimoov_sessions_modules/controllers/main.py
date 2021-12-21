from odoo import fields, http, SUPERUSER_ID, tools, _

PPG = 20  # Products Per Page
PPR = 4  # Products Per Row

from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from werkzeug.exceptions import Forbidden, NotFound
from datetime import datetime, date
import logging
import locale
import requests
import json
from requests.structures import CaseInsensitiveDict
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError
from unidecode import unidecode

PPG = 20  # Products Per Page
PPR = 4  # Products Per Row
_logger = logging.getLogger(__name__)

class WebsiteSale(WebsiteSale):

    @http.route(
        ['''/<string:product>/<string:partenaire>/shop/cart''', '''/<string:product>/shop/cart''', '''/shop/cart'''],
        type='http', auth="user", website=True, sitemap=False)
    def cart(self, access_token=None, product=None, revive='', partenaire=None, **post):
        """
        Main cart management + abandoned cart revival
        access_token: Abandoned cart SO access token
        revive: Revival method when abandoned cart. Can be 'merge' or 'squash'
        """
        statut ="False"
        if not request.env.user.lang:
            request.env.user.lang ='fr_FR'
        locale.setlocale(locale.LC_TIME, str(request.env.user.lang) + '.utf8') #get local time of partner
        order = request.website.sale_get_order()
        if order and order.state != 'draft':
            request.session['sale_order_id'] = None
            order = request.website.sale_get_order()
        values = {}
        if access_token:
            abandoned_order = request.env['sale.order'].sudo().search([('access_token', '=', access_token)], limit=1)
            if not abandoned_order:  # wrong token (or SO has been deleted)
                raise NotFound()
            if abandoned_order.state != 'draft':  # abandoned cart already finished
                values.update({'abandoned_proceed': True})
            elif revive == 'squash' or (revive == 'merge' and not request.session.get(
                    'sale_order_id')):  # restore old cart or merge with unexistant
                request.session['sale_order_id'] = abandoned_order.id
                return request.redirect('/shop/cart')
            elif revive == 'merge':
                abandoned_order.order_line.write({'order_id': request.session['sale_order_id']})
                abandoned_order.action_cancel()
            elif abandoned_order.id != request.session.get(
                    'sale_order_id'):  # abandoned cart found, user have to choose what to do
                values.update({'access_token': abandoned_order.access_token})
        values.update({
            'website_sale_order': order,
            'date': fields.Date.today(),
            'suggested_products': [],
        })
        if post.get('type') == 'popover':
            # force no-cache so IE11 doesn't cache this XHR
            return request.render("website_sale.cart_popover", values, headers={'Cache-Control': 'no-cache'})
        if not request.env.user.has_group('base.group_user'):
            documents = False
            if order.partner_id:
                documents = request.env['documents.document'].sudo().search([('partner_id', '=', order.partner_id.id)])
            if order and order.partner_id:
                product_id = False
                if order:
                    for line in order.order_line:
                        product_id = line.product_id
                if product_id:
                    questionnaire = request.env['questionnaire'].sudo().search(
                        [('partner_id', '=', order.partner_id.id), ('product_id', "=", product_id.id)])
                    if not questionnaire:
                        return request.redirect("/coordonnees")
            if order and not documents:
                return request.redirect("/charger_mes_documents")
        # if order.company_id.id == 1 and (partenaire or product):
        #     r eturn request.redirect("/shop/cart/")
        if order and order.company_id.id == 1:
            request.env.user.company_id = 1  # change default company
            request.env.user.company_ids = [1, 2]  # change default companies
            product_id = False
            if order:
                for line in order.order_line:
                    product_id = line.product_id

            if not product and not partenaire and product_id:
                product = True
                partenaire = True
            if product and not partenaire:
                if product_id:
                    slugname = (product_id.name).strip().strip('-').replace(' ', '-').lower()
                    if str(slugname) != str(product):
                        if order.pricelist_id and order.pricelist_id.name in ['bolt']:
                            return request.redirect("/%s/%s/shop/cart/" % (slugname, order.pricelist_id.name))
                        else:
                            return request.redirect("/%s/shop/cart/" % (slugname))
                    else:
                        if order.pricelist_id and order.pricelist_id.name in ['bolt']:
                            return request.redirect("/%s/%s/shop/cart/" % (slugname, order.pricelist_id.name))
                else:
                    return request.redirect("/pricing")
            elif product and partenaire:
                if product_id:
                    slugname = (product_id.name).strip().strip('-').replace(' ', '-').lower()
                    if str(slugname) != str(product):
                        pricelist = request.env['product.pricelist'].sudo().search(
                            [('company_id', '=', 1), ('name', "=", str(partenaire))])
                        if not pricelist:
                            pricelist_id = order.pricelist_id
                            if pricelist_id.name in ['bolt', ]:
                                return request.redirect("/%s/%s/shop/cart/" % (slugname, pricelist_id.name))
                            else:
                                return request.redirect("/%s/shop/cart/" % (slugname))
                        else:
                            if pricelist.name in ['bolt']:
                                return request.redirect("/%s/%s/shop/cart/" % (slugname, order.pricelist_id.name))
                            else:
                                return request.redirect("/%s/shop/cart/" % (slugname))
                    else:
                        pricelist = request.env['product.pricelist'].sudo().search(
                            [('company_id', '=', 1), ('name', "=", str(partenaire))])

                        if not pricelist:
                            pricelist_id = order.pricelist_id
                            if pricelist_id.name in ['bolt']:
                                return request.redirect("/%s/%s/shop/cart/" % (slugname, pricelist_id.name))
                            else:
                                return request.redirect("/%s/shop/cart/" % (slugname))
                        else:
                            if pricelist.name in ['bolt']:
                                if pricelist.name != order.pricelist_id.name:
                                    return request.redirect("/%s/%s/shop/cart/" % (slugname, order.pricelist_id.name))
                            else:
                                return request.redirect("/%s/shop/cart/" % (slugname))
                else:
                    pricelist = request.env['product.pricelist'].sudo().search(
                        [('company_id', '=', 1), ('name', "=", str(partenaire))])
                    if pricelist and pricelist.name in ['bolt']:
                        return request.redirect("/%s" % (pricelist.name))
                    else:
                        return request.redirect("/pricing")

        if order and order.company_id.id == 2:
            request.env.user.company_id = 2  # change default company
            request.env.user.company_ids = [1, 2]  # change default companies
            product_id = False
            if order:
                for line in order.order_line:
                    product_id = line.product_id

            if not product and not partenaire and product_id:
                product = True
                partenaire = True
            if product and not partenaire:
                if product_id:
                    slugname = (product_id.name).strip().strip('-').replace(' ', '-').lower()
                    if str(slugname) != str(product):
                        if order.pricelist_id and order.pricelist_id.name in ['ubereats', 'deliveroo', 'coursierjob','box2home','coursier2roues', 'habilitation-electrique', 'eco-conduite', 'transport-routier']:
                            return request.redirect("/%s/%s/shop/cart/" % (slugname, order.pricelist_id.name))
                        else:
                            return request.redirect("/%s/shop/cart/" % (slugname))
                    else:
                        if order.pricelist_id and order.pricelist_id.name in ['ubereats', 'deliveroo', 'coursierjob','box2home','coursier2roues', 'habilitation-electrique', 'eco-conduite', 'transport-routier']:
                            return request.redirect("/%s/%s/shop/cart/" % (slugname, order.pricelist_id.name))
                else:
                    return request.redirect("/pricing")
            elif product and partenaire:
                if product_id:
                    slugname = (product_id.name).strip().strip('-').replace(' ', '-').lower()
                    if str(slugname) != str(product):
                        pricelist = request.env['product.pricelist'].sudo().search(
                            [('company_id', '=', 2), ('name', "=", str(partenaire))])
                        if not pricelist:
                            pricelist_id = order.pricelist_id
                            if pricelist_id.name in ['ubereats', 'deliveroo', 'coursierjob','box2home','coursier2roues', 'habilitation-electrique', 'eco-conduite', 'transport-routier']:
                                return request.redirect("/%s/%s/shop/cart/" % (slugname, pricelist_id.name))
                            else:
                                return request.redirect("/%s/shop/cart/" % (slugname))
                        else:
                            if pricelist.name in ['ubereats', 'deliveroo', 'coursierjob','box2home','coursier2roues', 'habilitation-electrique', 'eco-conduite', 'transport-routier']:
                                return request.redirect("/%s/%s/shop/cart/" % (slugname, order.pricelist_id.name))
                            else:
                                return request.redirect("/%s/shop/cart/" % (slugname))
                    else:
                        pricelist = request.env['product.pricelist'].sudo().search(
                            [('company_id', '=', 2), ('name', "=", str(partenaire))])

                        if not pricelist:
                            pricelist_id = order.pricelist_id
                            if pricelist_id.name in ['ubereats', 'deliveroo', 'coursierjob','box2home','coursier2roues', 'habilitation-electrique', 'eco-conduite', 'transport-routier']:
                                return request.redirect("/%s/%s/shop/cart/" % (slugname, pricelist_id.name))
                            else:
                                return request.redirect("/%s/shop/cart/" % (slugname))
                        else:
                            if pricelist.name in ['ubereats', 'deliveroo', 'coursierjob','box2home','coursier2roues', 'habilitation-electrique', 'eco-conduite', 'transport-routier']:
                                if pricelist.name != order.pricelist_id.name:
                                    return request.redirect("/%s/%s/shop/cart/" % (slugname, order.pricelist_id.name))
                            else:
                                return request.redirect("/%s/shop/cart/" % (slugname))
                else:
                    pricelist = request.env['product.pricelist'].sudo().search(
                        [('company_id', '=', 2), ('name', "=", str(partenaire))])
                    if pricelist and pricelist.name in ['ubereats', 'deliveroo', 'coursierjob','box2home','coursier2roues', 'habilitation-electrique', 'eco-conduite', 'transport-routier']:
                        return request.redirect("/%s" % (pricelist.name))
                    else:
                        return request.redirect("/pricing")
        list_products = []
        if order:
            for line in order.order_line:
                list_products.append(line.product_id)
        all_mcm_modules = False
        all_digimoov_modules = False
        for product in list_products:
            all_mcm_modules = request.env['mcmacademy.module'].sudo().search(
                [('product_id', '=', product.product_tmpl_id.id),
                 ('company_id', '=', 1)],order='date_exam asc')
            all_digimoov_modules = request.env['mcmacademy.module'].sudo().search(
                [('product_id', '=', product.product_tmpl_id.id),
                 ('company_id', '=', 2)],order='date_exam asc')
        list_modules_digimoov = []
        list_modules_mcm = []
        today = date.today()
        if (all_digimoov_modules):
            for module in all_digimoov_modules:
                if module.date_exam:
                    if (module.date_exam - today).days > int(
                            module.session_id.intervalle_jours) and module.session_id.website_published == True:
                        list_modules_digimoov.append(module)
        if (all_mcm_modules):
            for module in all_mcm_modules:
                if module.date_exam:
                    if (module.date_exam - today).days > int(
                            module.session_id.intervalle_jours) and module.session_id.website_published == True:
                        list_modules_mcm.append(module)
        if order:
            order.order_line.filtered(lambda l: not l.product_id.active).unlink()
            _order = order
            if not request.env.context.get('pricelist'):
                _order = order.with_context(pricelist=order.pricelist_id.id)
            values['suggested_products'] = _order._cart_accessories()
        for module in list_modules_digimoov:
            print(module.ville)
            print(module.date_exam)
        """Récuperer num_cpf et vérifier l'etat de dossier sur edof via api"""
        if order and order.partner_id and order.partner_id.numero_cpf:
            numero_cpf =order.partner_id.numero_cpf
            params_wedof = (
                ('order', 'desc'),
                ('type', 'all'),
                ('state', 'all'),
                ('billingState', 'all'),
                ('certificationState', 'all'),
                ('sort', 'lastUpdate'),
                ('limit', '100')
            )

            headers = {
                'accept': 'application/json',
                'Content-Type': 'application/json',
                'X-API-KEY': '026514d6bc7d880515a27eae4947bccef4fbbf03',
            }
            response = requests.get('https://www.wedof.fr/api/registrationFolders/'+numero_cpf, headers=headers,
                                    params=params_wedof)
            registration = response.json()
            print('registration',registration['state'],registration['externalId'])
            state =registration['state']
            
            if state=="validated":
                statut='https://www.moncompteformation.gouv.fr/espace-prive/html/#/dossiers/v2/'+numero_cpf+'/detail/financement'
            if state=="accepted":
                statut="accepted"
            

        values.update({
            'modules_digimoov': list_modules_digimoov,
            'modules_mcm': list_modules_mcm,
            'state':statut,
            'error_ville': '',
            'error_exam_date': '',
            'error_condition': '',
        })
        # recuperer la liste des villes pour l'afficher dans la vue panier de siteweb digimoov pour que le client peut choisir une ville parmis la liste
        list_villes = request.env['session.ville'].sudo().search([('company_id', '=', 2)])
        if list_villes:
            values.update({
                'list_villes': list_villes,
            })

            # recuperer la liste des villes pour l'afficher dans la vue panier de siteweb mcm pour que le client peut choisir une ville parmis la liste
            list_villes_mcm = []

        list_villes_mcm = request.env['session.ville'].sudo().search([('company_id', '=', 1)])
        if list_villes_mcm:
            values.update({
                'list_villes_mcm': list_villes_mcm,
            })
        print('valuuuuuuuue',values)
        return request.render("website_sale.cart", values)

    # def checkout_redirection(self, order):
    #     redirection=super(WebsiteSale,self).checkout_redirection(order)
    #     if order:
    #         if (order.company_id.id==2):
    #             check=False
    #             if not order.session_ville_id:
    #                 order.exam_center_error='error'
    #                 check=True
    #             else:
    #                 order.exam_center_error = ''
    #             if not order.module_id:
    #                 order.exam_date_error='error'
    #                 check = True
    #             else:
    #                 order.exam_date_error=''
    #             #remove verify conditions in shop cart
    #             # if not order.conditions:
    #             #     order.conditions_error='error'
    #             #     check = True
    #             if check:
    #                 return request.redirect('/shop/cart')
    #     return redirection
    """Changer statut cpf vers accepté selon l'etat récupéré avec api wedof"""
    @http.route(['/shop/cpf_accepted'], type='json', auth="user", methods=['POST'], website=True)
    def accepted_cpf(self):
        partner = request.env.user.partner_id
        if partner.numero_cpf:
            params_wedof = (
                ('order', 'desc'),
                ('type', 'all'),
                ('state', 'accepted'),
                ('billingState', 'all'),
                ('certificationState', 'all'),
                ('sort', 'lastUpdate'),
                ('limit', '100')
            )

            headers = {
                'accept': 'application/json',
                'Content-Type': 'application/json',
                'X-API-KEY': '026514d6bc7d880515a27eae4947bccef4fbbf03',
            }
            response = requests.get('https://www.wedof.fr/api/registrationFolders/' + partner.numero_cpf,
                                    headers=headers,
                                    params=params_wedof)
            dossier = response.json()
            print('controller cpf accepted', dossier['state'], dossier['externalId'])
            diplome = dossier['trainingActionInfo']['title']
            idform = dossier['trainingActionInfo']['externalId']
            training_id = ""
            if "_" in idform:
                idforma = idform.split("_", 1)
                if idforma:
                    training_id = idforma[1]

            lastupdatestr = str(dossier['lastUpdate'])
            lastupdate = datetime.strptime(lastupdatestr, '%Y-%m-%dT%H:%M:%S.%fz')
            newformat = "%d/%m/%Y %H:%M:%S"
            lastupdateform = lastupdate.strftime(newformat)
            lastupd = datetime.strptime(lastupdateform, "%d/%m/%Y %H:%M:%S")
            partner.mode_de_financement = 'cpf'
            partner.statut_cpf = 'accepted'
            partner.date_cpf = lastupd
            partner.diplome = diplome
            module_id = False
            product_id = False
            if 'digimoov' in str(training_id):

                product_id = request.env['product.template'].sudo().search(
                    [('id_edof', "=", str(training_id)), ('company_id', "=", 2)], limit=1)
                if product_id:
                    partner.id_edof = product_id.id_edof
            else:
                product_id = request.env['product.template'].sudo().search(
                    [('id_edof', "=", str(training_id)), ('company_id', "=", 1)], limit=1)
                if product_id:
                    partner.id_edof = product_id.id_edof
            print('if digi ', product_id)
            if product_id and product_id.company_id.id == 2 and partner.id_edof and partner.date_examen_edof and partner.session_ville_id:

                print('if product_id digimoov', product_id.id_edof)
                module_id = request.env['mcmacademy.module'].sudo().search(
                    [('company_id', "=", 2), ('session_ville_id', "=", partner.session_ville_id.id),
                     ('date_exam', "=", partner.date_examen_edof), ('product_id', "=", product_id.id),
                     ('session_id.number_places_available', '>', 0)], limit=1)
                print('before if modulee', module_id)
                if module_id:
                    print('if modulee', module_id)
                    partner.module_id = module_id
                    partner.mcm_session_id = module_id.session_id
                    product_id = request.env['product.product'].sudo().search(
                        [('product_tmpl_id', '=', module_id.product_id.id)])
                    partner.mcm_session_id = module_id.session_id
                    partner.module_id = module_id
                    request.env.user.company_id = 2
                    invoice = request.env['account.move'].sudo().search(
                        [('module_id', "=", module_id.id), ('state', "=", 'posted'),
                         ('partner_id', "=", partner.id)])
                    if not invoice:
                        so = request.env['sale.order'].sudo().create({
                            'partner_id': partner.id,
                            'company_id': 2,
                        })
                        so.module_id = module_id
                        so.session_id = module_id.session_id

                        so_line = request.env['sale.order.line'].sudo().create({
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
                        so.unlink()
                        partner.statut = 'won'

                    """Créer un historique de ssession pour cet apprenant """
                    session = request.env['partner.sessions'].search([('client_id', '=', partner.id),
                                                                      ('session_id', '=', module_id.session_id.id)])
                    if not session:
                        new_history = request.env['partner.sessions'].sudo().create({
                            'client_id': partner.id,
                            'session_id': module_id.session_id.id,
                            'company_id': 2,
                        })

            elif product_id and product_id.company_id.id == 1 and partner.id_edof and partner.date_examen_edof and partner.session_ville_id:
                print('if product_id mcm', product_id, user.login)
                partner.id_edof = product_id.id_edof
                module_id = request.env['mcmacademy.module'].sudo().search(
                    [('company_id', "=", 1), ('session_ville_id', "=", partner.session_ville_id.id),
                     ('date_exam', "=", partner.date_examen_edof), ('product_id', "=", product_id.id),
                     ('session_id.number_places_available', '>', 0)], limit=1)
                if module_id:
                    partner.module_id = module_id
                    partner.mcm_session_id = module_id.session_id
                    product_id = request.env['product.product'].sudo().search(
                        [('product_tmpl_id', '=', module_id.product_id.id)])
                    partner.mcm_session_id = module_id.session_id
                    partner.module_id = module_id
                    request.env.user.company_id = 1
                    invoice = request.env['account.move'].sudo().search(
                        [('module_id', "=", module_id.id), ('state', "=", 'posted'),
                         ('partner_id', "=", partner.id)])
                    if not invoice:
                        so = request.env['sale.order'].sudo().create({
                            'partner_id': partner.id,
                            'company_id': 1,
                        })
                        request.env['sale.order.line'].sudo().create({
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
                    """Créer un historique de ssession pour cet apprenant """
                    session = request.env['partner.sessions'].search([('client_id', '=', partner.id),
                                                                      ('session_id', '=', module_id.session_id.id)])
                    if not session:
                        new_history = request.env['partner.sessions'].sudo().create({
                            'client_id': partner.id,
                            'session_id': module_id.session_id.id,
                            'company_id': 1,
                        })

            else:
                if 'digimoov' in str(training_id):
                    vals = {
                        'description': 'CPF: vérifier la date et ville de %s' % (user.name),
                        'name': 'CPF : Vérifier Date et Ville ',
                        'team_id': request.env['helpdesk.team'].sudo().search(
                            [('name', 'like', 'Client'), ('company_id', "=", 2)],
                            limit=1).id,
                    }
                    description = "CPF: vérifier la date et ville de " + str(user.name)
                    ticket = request.env['helpdesk.ticket'].sudo().search([("description", "=", description)])
                    if not ticket:
                        new_ticket = request.env['helpdesk.ticket'].sudo().create(
                            vals)
                else:
                    vals = {
                        'partner_email': '',
                        'partner_id': False,
                        'description': 'CPF: id module edof %s non trouvé' % (training_id),
                        'name': 'CPF : ID module edof non trouvé ',
                        'team_id': request.env['helpdesk.team'].sudo().search(
                            [('name', "like", _('Client')), ('company_id', "=", 1)],
                            limit=1).id,
                    }
                    description = 'CPF: id module edof ' + str(training_id) + ' non trouvé'
                    ticket = request.env['helpdesk.ticket'].sudo().search([('description', 'ilike', description)])
                    if not ticket:
                        new_ticket = request.env['helpdesk.ticket'].sudo().create(
                            vals)
        return {'state':'finished'}

    """ajouter l'apprenant sur 360 par api360"""
    @http.route(['/shop/adduser_plateform'], type='json', auth="user",methods=['POST'], website=True)
    def add_partner_plateforme(self): 
       
        
       
        user = request.env.user
        partner = user.partner_id
        if partner.statut == "won" and partner.statut_cpf != "canceled" and user.company_id.id == 2:
            print('if parnter adddddddddd')
            # chercher son contrat
            sale_order = request.env['sale.order'].sudo().search([('partner_id', '=', partner.id),
                                                                  ('session_id', '=', partner.mcm_session_id.id),
                                                                  ('module_id', '=', partner.module_id.id),
                                                                  ('state', '=', 'sale'),
                                                                  ('session_id.date_exam', '>', date.today())
                                                                  ], limit=1, order="id desc")
            # Pour chaque apprenant chercher sa facture
            facture = request.env['account.move'].sudo().search([('session_id', '=', partner.mcm_session_id.id),
                                                                 ('module_id', '=', partner.module_id.id),
                                                                 ('state', '=', 'posted')
                                                                 ], order="invoice_date desc", limit=1)
            date_facture = facture.invoice_date
            today = date.today()
            _logger.info('sale order %s ' % sale_order.name)
            # Récupérer les documents et vérifier si ils sont validés ou non
            documents = request.env['documents.document'].sudo().search([('partner_id', '=', partner.id)])
            document_valide = False
            count = 0
            for document in documents:
                if (document.state == "validated"):
                    count = count + 1
            if (count == len(documents) and count != 0):
                document_valide = True
            # Cas particulier on doit Vérifier si partner a choisi une formation et si ses documents sont validés
            # if partner.mode_de_financement == "particulier":
            #     if ((sale_order) and (document_valide)):
            #         statut = partner.statut
            #         # Vérifier si contrat signé ou non
            #         if (sale_order.state == 'sale') and (sale_order.signature):
            #             # Si demande de renonce est coché donc l'apprenant est ajouté sans attendre 14jours
            #             if partner.renounce_request:
            #                 self.ajouter_iOne(partner)
            #             # si non il doit attendre 14jours pour etre ajouté
            #             # if not partner.renounce_request and date_facture and (date_facture + timedelta(days=14)) <= today:
            #             #     self.ajouter_iOne(partner)
            """cas de cpf on vérifie la validation des document , la case de renonciation et la date d'examen qui doit etre au future """
            if partner.mode_de_financement == "cpf":
                if document_valide and partner.mcm_session_id.date_exam and (
                        partner.mcm_session_id.date_exam > date.today()):
                    if partner.renounce_request:
                        print("****************************************ajouterrrr ione")
                        return self.ajouter_iOne(partner)
                    if not partner.renounce_request:
                        print("Renonce")
                        """créer ticket pour service client"""
                        vals = {
                            'description': 'CPF: Apprenant non ajouté sur 360 %s' % (partner.name),
                            'name': 'CPF : case de renonciation non coché  ',
                            'team_id': request.env['helpdesk.team'].sudo().search(
                                [('name', 'like', 'Client'), ('company_id', "=", 2)],
                                limit=1).id,
                        }
                        description = "CPF: Apprenant non ajouté sur 360 " + str(partner.name)
                        ticket = request.env['helpdesk.ticket'].sudo().search([("description", "=", description)])
                        if not ticket:
                            new_ticket = request.env['helpdesk.ticket'].sudo().create(
                                vals)
                        return {'ajout': 'Vous devez attendre 14 jours pour commencer  votre formation'}

                    # if not partner.renounce_request and date_facture and (date_facture + timedelta(days=14)) <= today:
                    #     self.ajouter_iOne(partner)
                if not document_valide:
                    print("Documents")
                    
                    """créer ticket pour service client"""
                    vals = {
                        'description': 'CPF: Apprenant non ajouté sur 360 %s' % (partner.name),
                        'name': 'CPF : Valider les documents ',
                        'team_id': request.env['helpdesk.team'].sudo().search(
                            [('name', 'like', 'Client'), ('company_id', "=", 2)],
                            limit=1).id,
                    }
                    description = "CPF: Apprenant non ajouté sur 360 " + str(partner.name)
                    ticket = request.env['helpdesk.ticket'].sudo().search([("description", "=", description)])
                    if not ticket:
                        new_ticket = request.env['helpdesk.ticket'].sudo().create(
                            vals)
                    return {'ajout': 'Vous devez attendre la validation de vos documents pour commencer la formation'}
    
    def ajouter_iOne(self, partner):
        params = (
            ('company', '56f5520e11d423f46884d593'),
            ('apiKey', 'cnkcbrhHKyfzKLx4zI7Ub2P5'),
        )
        company_id = '56f5520e11d423f46884d593'
        api_key = 'cnkcbrhHKyfzKLx4zI7Ub2P5'
        headers = CaseInsensitiveDict()
        headers["Content-Type"] = "application/json"

        """Vérifier la presence d'apprenant sur 360 """
        url_user = 'https://staging.360learning-dev.com/api/v1/users/' + partner.email + '?company=' + company_id + '&apiKey=' + api_key
        resp = requests.get(url_user, headers=headers)
        """s'il est présent on lui envoie le lien pour se connecter si non on lui ajoute """
        print('get user', resp.status_code)
        if resp.status_code == 200:
            
            return {'ajout': 'Vous êtes déja sur la plateforme, cliquez sur continuer pour se connecter','url':'https://digimoov.360learning.com'}

        else :
            if not request.env.user.lang:
                request.env.user.lang = 'fr_FR'  # Remplacez les paramètres régionaux de l'heure par le paramètre de langue actuel
                                             # du compte dans odoo
            locale.setlocale(locale.LC_TIME, str(request.env.user.lang) + '.utf8')
            company = str(partner.module_id.company_id.id)
            product_name = partner.module_id.product_id.name
            if (not (product_name)):
                product_name = ''
            if not (partner.phone):
                partner.phone = ''
            # Extraire firstName et lastName à partir du champs name
            self.diviser_nom(partner)

            new_format = '%d %B %Y'
            if (partner.mcm_session_id.date_exam) and (partner.mcm_session_id.session_ville_id.name_ville):
                ville = str(partner.mcm_session_id.session_ville_id.name_ville).upper()
                _logger.info('----ville %s' % ville)
                date_exam = partner.mcm_session_id.date_exam
                # Changer format de date et la mettre en majuscule
                datesession = str(date_exam.strftime(new_format).upper())
                date_session = unidecode(datesession)

                #Récuperer le mot de passe à partir de res.users
                user = request.env.user
                _logger.info('avant if login user %s' % user.login)
                _logger.info('avant if partner email %s' % partner.email)
                if user.password360 == False:
                    _logger.info(' if password  %s ' % user.password360)

                if user:
                    print('iffff userrrrrr')
                    id_Digimoov_bienvenue = '56f5520e11d423f46884d594'
                    id_Digimoov_Examen_Attestation = '5f9af8dae5769d1a2c9d5047'
                    urluser = 'https://staging.360learning-dev.com/api/v1/users?company=' + company_id + '&apiKey=' + api_key
                    urlgroup_Bienvenue = 'https://staging.360learning-dev.com/api/v1/groups/' + id_Digimoov_bienvenue + '/users/' + partner.email + '?company=' + company_id + '&apiKey=' + api_key
                    url_groups = 'https://staging.360learning-dev.com/api/v1/groups'
                    url_unsubscribeToEmailNotifications = 'https://staging.360learning-dev.com/api/v1/users/unsubscribeToEmailNotifications?company=' + company_id + '&apiKey=' + api_key
                    invit = False
                    create = False
                    responce_api =False
                    # Si le mot de passe n'est pas récupérée au moment d'inscrit on invite l'apprennant
                    # if user.password360==False:
                    # data_user ='{"mail":"' + partner.email + '"}'
                    # resp_invit = requests.post(urluser, headers=headers, data=data_user)
                    # if(resp_invit.status_code == 200):
                    #     invit=True
                    # Si non si mot de passe récupéré on l'ajoute sur la plateforme avec le meme mot de passe
                    if (user.password360) and (company == '2'):
                        partner.password360 = user.password360

                        # Ajouter i-One to table user
                        data_user = '{"mail":"' + partner.email + '" , "password":"' + user.password360 + '", "firstName":"' + partner.firstName + '", "lastName":"' + partner.lastName + '", "phone":"' + partner.phone + '", "lang":"fr","sendCredentials":"true"}'
                        resp = requests.post(urluser, headers=headers, data=data_user)
                        print(data_user, 'user', resp.status_code)
                        responce_api=json.loads(resp.text)
                        if (resp.status_code == 200):
                            create = True
                    data_group = {}
                    # Désactiver les notifications par email
                    data_email = json.dumps({
                        "usersEmails": [
                            partner.email
                        ]
                    })
                    resp_unsub_email = requests.put(url_unsubscribeToEmailNotifications, headers=headers, data=data_email)
                    # Si l'apprenant a été ajouté sur table user on l'affecte aux autres groupes
                    if (create):
                        _logger.info('create %s' % user.login)
                        today = date.today()
                        new_format = '%d %B %Y'
                        # Changer format de date et la mettre en majuscule
                        date_ajout = today.strftime(new_format)
                        partner.date_creation = date_ajout
                        # Affecter i-One to groupe digimoov-bienvenue
                        respgroupe = requests.put(urlgroup_Bienvenue, headers=headers, data=data_group)
                        print('bienvenue ', respgroupe.status_code, partner.date_creation)
                        partner.apprenant = True
                        # Affecter i-One à un pack et session choisi
                        response_grps = requests.get(url_groups, params=params)
                        existe = False
                        groupes = response_grps.json()
                        # print(response_grps.json())
                        company = str(partner.module_id.company_id.id)
                        for groupe in groupes:
                            # Convertir le nom en majuscule
                            nom_groupe = str(groupe['name']).upper()
                            print('nom groupe', groupe)
                            id_groupe = groupe['_id']
                            # affecter à groupe digimoov
                            digimoov_examen = "Digimoov - Attestation de capacité de transport de marchandises de moins de 3.5t"
                            # Si la company est digimoov on ajoute i-One sur 360
                            if (company == '2'):
                                if (nom_groupe == digimoov_examen.upper()):
                                    id_Digimoov_Examen_Attestation = id_groupe
                                    urlsession = 'https://staging.360learning-dev.com/api/v1/groups/' + id_groupe + '/users/' + partner.email + '?company=' + company_id + '&apiKey=' + api_key
                                    respsession = requests.put(urlsession, headers=headers, data=data_group)
                                    if respsession.status_code==200:
                                        ajout_exam =True

                                    # Affecter à un pack solo
                                packsolo = "Digimoov - Pack Solo"
                                if (("solo" in product_name) and (nom_groupe == packsolo.upper())):
                                    print(partner.module_id.name)
                                    urlgrp_solo = 'https://staging.360learning-dev.com/api/v1/groups/' + id_groupe + '/users/' + partner.email + '?company=' + company_id + '&apiKey=' + api_key
                                    respgrp_solo = requests.put(urlgrp_solo, headers=headers, data=data_group)
                                    print('affecté à solo', respgrp_solo.status_code)

                                # Affecter à un pack pro
                                pack_pro = "Digimoov - Pack Pro"
                                if (("pro" in product_name) and (nom_groupe == pack_pro.upper())):
                                    print(partner.module_id.name)
                                    urlgrp_pro = 'https://staging.360learning-dev.com/api/v1/groups/' + id_groupe + '/users/' + partner.email + '?company=' + company_id + '&apiKey=' + api_key
                                    respgrp_pro = requests.put(urlgrp_pro, headers=headers, data=data_group)
                                # Affecter à unpremium
                                packprem = "Digimoov - Pack Premium"
                                if (("premium" in product_name) and (nom_groupe == packprem.upper())):
                                    print(partner.module_id.name)
                                    urlgrp_prim = 'https://staging.360learning-dev.com/api/v1/groups/' + id_groupe + '/users/' + partner.email + '?company=' + company_id + '&apiKey=' + api_key
                                    respgrp_prim = requests.put(urlgrp_prim, headers=headers, data=data_group)

                                # Affecter apprenant à Digimoov-Révision
                                revision = "Digimoov - Pack Repassage Examen"
                                if (("Repassage d'examen" in product_name) and (nom_groupe == revision.upper())):
                                    urlgrp_revision = 'https://staging.360learning-dev.com/api/v1/groups/' + id_groupe + '/users/' + partner.email + '?company=' + company_id + '&apiKey=' + api_key
                                    respgrp_revision = requests.put(urlgrp_revision, headers=headers, data=data_group)

                                # Affecter apprenant à une session d'examen
                                print('date, ville', ville, date_session)
                                if (ville in nom_groupe) and (date_session in nom_groupe):
                                    existe = True
                                    urlsession = 'https://staging.360learning-dev.com/api/v1/groups/' + id_groupe + '/users/' + partner.email + '?company=' + company_id + '&apiKey=' + api_key
                                    respsession = requests.put(urlsession, headers=headers, data=data_group)

                        # Si la session n'est pas trouvée sur 360 on l'ajoute
                        print('exist', existe)
                        if not (existe):
                            nom = ville + ' - ' + date_session
                            nomgroupe = unidecode(nom)
                            print(nomgroupe)
                            urlgroups = 'https://staging.360learning-dev.com/api/v1/groups?company=' + company_id + '&apiKey=' + api_key
                            data_session = '{"name":"' + nomgroupe + '","parent":"' + id_Digimoov_Examen_Attestation + '"  , "public":"false" }'
                            create_session = requests.post(urlgroups, headers=headers, data=data_session)
                            print('creer  une session', create_session.status_code)
                            response_grpss = requests.get(url_groups, params=params)
                            groupess = response_grpss.json()
                            for groupe in groupess:
                                # Convertir le nom en majuscule
                                nom_groupe = str(groupe['name']).upper()
                                id_groupe = groupe['_id']
                                # Affecter apprenant à la nouvelle session d'examen
                                if (ville in nom_groupe) and (date_session in nom_groupe):
                                    existe = True
                                    urlsession = 'https://staging.360learning-dev.com/api/v1/groups/' + id_groupe + '/users/' + partner.email + '?company=' + company_id + '&apiKey=' + api_key
                                    respsession = requests.put(urlsession, headers=headers, data=data_group)
                                    print(existe, 'ajouter à son session', respsession.status_code)
                        "si créer envoyer le lien de la plateforme si non false"
                        return {'ajout':'Cliquez sur continuer pour commencer la formation. Vous devez utiliser les même identifiants pour accéder à la plateforme','url': 'https://digimoov.360learning.com'}
                    if not (create):
                            if str(responce_api)=="{'error': 'unavailableEmails'}":
                               

                                vals = {
                                    'description': 'CPF: Apprenant non ajouté sur 360 %s' % (partner.name) ,
                                    'name': 'CPF : Email non valide ',
                                    'team_id': request.env['helpdesk.team'].sudo().search(
                                        [('name', 'like', 'Client'), ('company_id', "=", 2)],
                                        limit=1).id,
                                }
                                description = "CPF: Apprenant non ajouté sur 360 " + str(partner.name)
                                ticket = request.env['helpdesk.ticket'].sudo().search([("description", "=", description),
                                                                                       ("team_id.name", 'like', 'Client')])
                                if not ticket:
                                    new_ticket = request.env['helpdesk.ticket'].sudo().create(
                                        vals)
                                return {'ajout': 'Email non valide.'}

                            else :

                                vals = {
                                    'description': 'CPF: Apprenant non ajouté sur 360 %s %s' % (partner.name ,responce_api),
                                    'name': 'CPF : Apprenant non ajouté sur 360 ',
                                    'team_id': request.env['helpdesk.team'].sudo().search(
                                        [('name', 'like', 'IT'), ('company_id', "=", 2)],
                                        limit=1).id,
                                }
                                description = "CPF: Apprenant non ajouté sur 360 " + str(partner.name) + str(responce_api)
                                ticket = request.env['helpdesk.ticket'].sudo().search([("description", "=", description),
                                                                                    ("team_id.name",'like', 'IT')])
                                
                                if not ticket:
                                    new_ticket = request.env['helpdesk.ticket'].sudo().create(
                                        vals)
                                vals_client = {
                                    'description': 'CPF: Apprenant non ajouté sur 360 %s %s' % (partner.name, responce_api),
                                    'name': 'CPF : Apprenant non ajouté sur 360 ',
                                    'team_id': request.env['helpdesk.team'].sudo().search(
                                        [('name', 'like', 'Client'), ('company_id', "=", 2)],
                                        limit=1).id,
                                }
                                description_client = "CPF: Apprenant non ajouté sur 360 " + str(partner.name) + str(responce_api)
                                ticket_client = request.env['helpdesk.ticket'].sudo().search([("description", "=", description_client),
                                                                                           ("team_id.name",'like', 'Client')])
                                if not ticket_client:
                                    new_ticket_client = request.env['helpdesk.ticket'].sudo().create(
                                        vals_client)
                                return {'ajout': 'Vous allez bientôt recevoir une invitation à la plateforme par courrier.'}




    # Extraire firstName et lastName à partir du champs name
    def diviser_nom(self, partner):
        # _logger.info('name au debut  %s' %partner.name)
        if partner.name == '':
            partner.firstName = partner.name
            partner.lastName = partner.name
        # Cas d'un nom composé
        else:
            if " " in partner.name:
                name = partner.name.split(" ", 1)
                if name:
                    partner.firstName = name[0]
                    partner.lastName = name[1]
            # Cas d'un seul nom
            else:
                partner.firstName = partner.name
                partner.lastName = partner.name
                print('first', partner.firstName)

    @http.route(['''/<string:product>/<string:partenaire>/shop/payment''', '''/<string:product>/shop/payment''',
                 '''/shop/payment'''], type='http', auth="user", website=True)
    def payment(self, partenaire=None, product=None, **post):
        order = request.website.sale_get_order()
        # if order.company_id.id == 1 and (partenaire or product):
        #     return request.redirect("/shop/payment/")
        if order and order.company_id.id == 1:
            product_id = False
            if order:
                for line in order.order_line:
                    product_id = line.product_id

            if not product and not partenaire and product_id:
                product = True
                partenaire = True
            if product and not partenaire:
                if product_id:
                    slugname = (product_id.name).strip().strip('-').replace(' ', '-').lower()
                    if str(slugname) != str(product):
                        if order.pricelist_id and order.pricelist_id.name in ['bolt']:
                            return request.redirect("/%s/%s/shop/payment/" % (slugname, order.pricelist_id.name))
                        else:
                            return request.redirect("/%s/shop/payment/" % (slugname))
                    else:
                        if order.pricelist_id and order.pricelist_id.name in ['bolt']:
                            return request.redirect("/%s/%s/shop/payment/" % (slugname, order.pricelist_id.name))
                else:
                    return request.redirect("/pricing")
            elif product and partenaire:
                if product_id:
                    slugname = (product_id.name).strip().strip('-').replace(' ', '-').lower()
                    if str(slugname) != str(product):
                        pricelist = request.env['product.pricelist'].sudo().search(
                            [('company_id', '=', 1), ('name', "=", str(partenaire))])
                        if not pricelist:
                            pricelist_id = order.pricelist_id
                            if pricelist_id.name in ['bolt']:
                                return request.redirect("/%s/%s/shop/payment/" % (slugname, pricelist_id.name))
                            else:
                                return request.redirect("/%s/shop/payment/" % (slugname))
                        else:
                            if pricelist.name in ['bolt']:
                                return request.redirect("/%s/%s/shop/payment/" % (slugname, order.pricelist_id.name))
                            else:
                                return request.redirect("/%s/shop/payment/" % (slugname))
                    else:
                        pricelist = request.env['product.pricelist'].sudo().search(
                            [('company_id', '=', 1), ('name', "=", str(partenaire))])

                        if not pricelist:
                            pricelist_id = order.pricelist_id
                            if pricelist_id.name in ['bolt']:
                                return request.redirect("/%s/%s/shop/payment/" % (slugname, pricelist_id.name))
                            else:
                                return request.redirect("/%s/shop/payment/" % (slugname))
                        else:
                            if pricelist.name in ['bolt']:
                                if pricelist.name != order.pricelist_id.name:
                                    return request.redirect(
                                        "/%s/%s/shop/payment/" % (slugname, order.pricelist_id.name))
                            else:
                                return request.redirect("/%s/shop/payment/" % (slugname))
                else:
                    pricelist = request.env['product.pricelist'].sudo().search(
                        [('company_id', '=', 1), ('name', "=", str(partenaire))])
                    if pricelist and pricelist.name in ['bolt']:
                        return request.redirect("/%s" % (pricelist.name))
                    else:
                        return request.redirect("/pricing")
        if order and order.company_id.id == 2:
            product_id = False
            if order:
                for line in order.order_line:
                    product_id = line.product_id

            if not product and not partenaire and product_id:
                product = True
                partenaire = True
            if product and not partenaire:
                if product_id:
                    slugname = (product_id.name).strip().strip('-').replace(' ', '-').lower()
                    if str(slugname) != str(product):
                        if order.pricelist_id and order.pricelist_id.name in ['ubereats', 'deliveroo', 'coursierjob','box2home','coursier2roues', 'habilitation-electrique', 'eco-conduite', 'transport-routier']:
                            return request.redirect("/%s/%s/shop/payment/" % (slugname, order.pricelist_id.name))
                        else:
                            return request.redirect("/%s/shop/payment/" % (slugname))
                    else:
                        if order.pricelist_id and order.pricelist_id.name in ['ubereats', 'deliveroo', 'coursierjob','box2home','coursier2roues', 'habilitation-electrique', 'eco-conduite', 'transport-routier']:
                            return request.redirect("/%s/%s/shop/payment/" % (slugname, order.pricelist_id.name))
                else:
                    return request.redirect("/pricing")
            elif product and partenaire:
                if product_id:
                    slugname = (product_id.name).strip().strip('-').replace(' ', '-').lower()
                    if str(slugname) != str(product):
                        pricelist = request.env['product.pricelist'].sudo().search(
                            [('company_id', '=', 2), ('name', "=", str(partenaire))])
                        if not pricelist:
                            pricelist_id = order.pricelist_id
                            if pricelist_id.name in ['ubereats', 'deliveroo', 'coursierjob','box2home','coursier2roues', 'habilitation-electrique', 'eco-conduite', 'transport-routier']:
                                return request.redirect("/%s/%s/shop/payment/" % (slugname, pricelist_id.name))
                            else:
                                return request.redirect("/%s/shop/payment/" % (slugname))
                        else:
                            if pricelist.name in ['ubereats', 'deliveroo', 'coursierjob','box2home','coursier2roues', 'habilitation-electrique', 'eco-conduite', 'transport-routier']:
                                return request.redirect("/%s/%s/shop/payment/" % (slugname, order.pricelist_id.name))
                            else:
                                return request.redirect("/%s/shop/payment/" % (slugname))
                    else:
                        pricelist = request.env['product.pricelist'].sudo().search(
                            [('company_id', '=', 2), ('name', "=", str(partenaire))])

                        if not pricelist:
                            pricelist_id = order.pricelist_id
                            if pricelist_id.name in ['ubereats', 'deliveroo', 'coursierjob','box2home','coursier2roues', 'habilitation-electrique', 'eco-conduite', 'transport-routier']:
                                return request.redirect("/%s/%s/shop/payment/" % (slugname, pricelist_id.name))
                            else:
                                return request.redirect("/%s/shop/payment/" % (slugname))
                        else:
                            if pricelist.name in ['ubereats', 'deliveroo', 'coursierjob', 'box2home', 'coursier2roues', 'habilitation-electrique', 'eco-conduite', 'transport-routier']:
                                if pricelist.name != order.pricelist_id.name:
                                    return request.redirect(
                                        "/%s/%s/shop/payment/" % (slugname, order.pricelist_id.name))
                            else:
                                return request.redirect("/%s/shop/payment/" % (slugname))
                else:
                    pricelist = request.env['product.pricelist'].sudo().search(
                        [('company_id', '=', 2), ('name', "=", str(partenaire))])
                    if pricelist and pricelist.name in ['ubereats', 'deliveroo', 'coursierjob', 'box2home',
                                                        'coursier2roues', 'habilitation-electrique', 'eco-conduite', 'transport-routier']:
                        return request.redirect("/%s" % (pricelist.name))
                    else:
                        return request.redirect("/pricing")
        return super(WebsiteSale, self).payment(**post)

    @http.route(['''/<string:product>/<string:partenaire>/shop/confirmation/<string:state>''',
                 '''/<string:product>/<string:partenaire>/shop/confirmation''',
                 '''/<string:product>/shop/confirmation/<string:state>''', '''/<string:product>/shop/confirmation''',
                 '''/shop/confirmation'''], type='http', auth="user", website=True, sitemap=False)
    def payment_confirmation(self, partenaire=None, product=None, state=None, **post):
        order_id = request.session.get('sale_last_order_id')
        order = request.env['sale.order'].sudo().search([('id', '=', order_id)], limit=1)
        if order:
            if order and order.company_id.id == 1:
                product_id = False
                if order:
                    for line in order.order_line:
                        product_id = line.product_id

                if not product and not partenaire and product_id:
                    product = True
                    partenaire = True
                if product and not partenaire:
                    if product_id:
                        slugname = (product_id.name).strip().strip('-').replace(' ', '-').lower()
                        if str(slugname) != str(product):
                            if order.pricelist_id and order.pricelist_id.name in ['bolt']:
                                return request.redirect(
                                    "/%s/%s/shop/confirmation/" % (slugname, order.pricelist_id.name))
                            else:
                                return request.redirect("/%s/shop/confirmation/" % (slugname))
                        else:
                            if order.pricelist_id and order.pricelist_id.name in ['bolt']:
                                return request.redirect(
                                    "/%s/%s/shop/confirmation/" % (slugname, order.pricelist_id.name))
                    else:
                        return request.redirect("/pricing")
                elif product and partenaire:
                    if product_id:
                        slugname = (product_id.name).strip().strip('-').replace(' ', '-').lower()
                        if str(slugname) != str(product):
                            pricelist = request.env['product.pricelist'].sudo().search(
                                [('company_id', '=', 1), ('name', "=", str(partenaire))])
                            if not pricelist:
                                pricelist_id = order.pricelist_id
                                if pricelist_id.name in ['bolt']:
                                    return request.redirect("/%s/%s/shop/confirmation/" % (slugname, pricelist_id.name))
                                else:
                                    return request.redirect("/%s/shop/confirmation/" % (slugname))
                            else:
                                if pricelist.name in ['bolt']:
                                    return request.redirect(
                                        "/%s/%s/shop/confirmation/" % (slugname, order.pricelist_id.name))
                                else:
                                    return request.redirect("/%s/shop/confirmation/" % (slugname))
                        else:
                            pricelist = request.env['product.pricelist'].sudo().search(
                                [('company_id', '=', 1), ('name', "=", str(partenaire))])

                            if not pricelist:
                                pricelist_id = order.pricelist_id
                                if pricelist_id.name in ['bolt']:
                                    return request.redirect("/%s/%s/shop/confirmation/" % (slugname, pricelist_id.name))
                                else:
                                    return request.redirect("/%s/shop/confirmation/" % (slugname))
                            else:
                                if pricelist.name in ['bolt']:
                                    if pricelist.name != order.pricelist_id.name:
                                        return request.redirect(
                                            "/%s/%s/shop/confirmation/" % (slugname, order.pricelist_id.name))
                                else:
                                    return request.redirect("/%s/shop/confirmation/" % (slugname))
                    else:
                        pricelist = request.env['product.pricelist'].sudo().search(
                            [('company_id', '=', 1), ('name', "=", str(partenaire))])
                        if pricelist and pricelist.name in ['bolt']:
                            return request.redirect("/%s" % (pricelist.name))
                        else:
                            return request.redirect("/pricing")
                check_transaction = True
                for transaction in order.transaction_ids:
                    if transaction.state != 'done':
                        check_transaction = False
                if check_transaction and order.state == 'sent':
                    return request.redirect("/my/orders/%s?access_token=%s" % (order.id, order.access_token))
            if order and order.company_id.id == 2:
                product_id = False
                if order:
                    for line in order.order_line:
                        product_id = line.product_id

                if not product and not partenaire and product_id:
                    product = True
                    partenaire = True
                if product and not partenaire:
                    if product_id:
                        slugname = (product_id.name).strip().strip('-').replace(' ', '-').lower()
                        if str(slugname) != str(product):
                            if order.pricelist_id and order.pricelist_id.name in ['ubereats', 'deliveroo',
                                                                                  'coursierjob','box2home','coursier2roues', 'habilitation-electrique', 'eco-conduite', 'transport-routier']:
                                return request.redirect(
                                    "/%s/%s/shop/confirmation/" % (slugname, order.pricelist_id.name))
                            else:
                                return request.redirect("/%s/shop/confirmation/" % (slugname))
                        else:
                            if order.pricelist_id and order.pricelist_id.name in ['ubereats', 'deliveroo',
                                                                                  'coursierjob','box2home','coursier2roues', 'habilitation-electrique', 'eco-conduite', 'transport-routier']:
                                return request.redirect(
                                    "/%s/%s/shop/confirmation/" % (slugname, order.pricelist_id.name))
                    else:
                        return request.redirect("/pricing")
                elif product and partenaire:
                    if product_id:
                        slugname = (product_id.name).strip().strip('-').replace(' ', '-').lower()
                        if str(slugname) != str(product):
                            pricelist = request.env['product.pricelist'].sudo().search(
                                [('company_id', '=', 2), ('name', "=", str(partenaire))])
                            if not pricelist:
                                pricelist_id = order.pricelist_id
                                if pricelist_id.name in ['ubereats', 'deliveroo', 'coursierjob','box2home','coursier2roues', 'habilitation-electrique', 'eco-conduite', 'transport-routier']:
                                    return request.redirect("/%s/%s/shop/confirmation/" % (slugname, pricelist_id.name))
                                else:
                                    return request.redirect("/%s/shop/confirmation/" % (slugname))
                            else:
                                if pricelist.name in ['ubereats', 'deliveroo', 'coursierjob','box2home','coursier2roues', 'habilitation-electrique', 'eco-conduite', 'transport-routier']:
                                    return request.redirect(
                                        "/%s/%s/shop/confirmation/" % (slugname, order.pricelist_id.name))
                                else:
                                    return request.redirect("/%s/shop/confirmation/" % (slugname))
                        else:
                            pricelist = request.env['product.pricelist'].sudo().search(
                                [('company_id', '=', 2), ('name', "=", str(partenaire))])

                            if not pricelist:
                                pricelist_id = order.pricelist_id
                                if pricelist_id.name in ['ubereats', 'deliveroo', 'coursierjob','box2home','coursier2roues', 'habilitation-electrique', 'eco-conduite', 'transport-routier']:
                                    return request.redirect("/%s/%s/shop/confirmation/" % (slugname, pricelist_id.name))
                                else:
                                    return request.redirect("/%s/shop/confirmation/" % (slugname))
                            else:
                                if pricelist.name in ['ubereats', 'deliveroo', 'coursierjob','box2home','coursier2roues', 'habilitation-electrique', 'eco-conduite', 'transport-routier']:
                                    if pricelist.name != order.pricelist_id.name:
                                        return request.redirect(
                                            "/%s/%s/shop/confirmation/" % (slugname, order.pricelist_id.name))
                                else:
                                    return request.redirect("/%s/shop/confirmation/" % (slugname))
                    else:
                        pricelist = request.env['product.pricelist'].sudo().search(
                            [('company_id', '=', 2), ('name', "=", str(partenaire))])
                        if pricelist and pricelist.name in ['ubereats', 'deliveroo', 'coursierjob','box2home','coursier2roues', 'habilitation-electrique', 'eco-conduite', 'transport-routier']:
                            return request.redirect("/%s" % (pricelist.name))
                        else:
                            return request.redirect("/pricing")
                check_transaction = True
                for transaction in order.transaction_ids:
                    if transaction.state != 'done':
                        check_transaction = False
                if check_transaction and order.state == 'sent':
                    return request.redirect("/my/orders/%s?access_token=%s" % (order.id, order.access_token))
        return super(WebsiteSale, self).payment_confirmation(**post)


class Centre_Examen(http.Controller):
    @http.route(['/shop/cart/update_exam_center'], type='json', auth="public", methods=['POST'], website=True)
    def cart_update_exam_center(self, center):
        """This route is called when changing exam center from the cart."""
        order = request.website.sale_get_order()
        print("center")
        print(center)
        ville = request.env['session.ville'].sudo().search([('name_ville', "=", center)], limit=1)
        if center and center != 'all':
            order.sudo().write({
                'session_ville_id': ville,
                'module_id': False,
                'session_id': False,
            })
        else:
            order.sudo().write({
                'session_ville_id': False
            })
        return order.session_ville_id

    @http.route(['/cpf/update_exam_center'], type='json', auth="public", methods=['POST'], website=True)
    def partner_update_exam_center(self, center):
        return True


class Date_Examen(http.Controller):
    @http.route(['/shop/cart/update_exam_date'], type='json', auth="public", methods=['POST'], website=True)
    def cart_update_exam_center(self, exam_date_id):
        order = request.website.sale_get_order()
        if exam_date_id and exam_date_id != 'all':
            module = request.env['mcmacademy.module'].sudo().search([('id', '=', exam_date_id)], limit=1)
            if module and order:
                check_partner_in_future_session = False
                futures_sessions = request.env['mcmacademy.session'].sudo().search(
                    [('date_exam', '>=', date.today())])
                if futures_sessions:
                    for session in futures_sessions:
                        for client in session.client_ids:
                            if client.id == order.partner_id.id:
                                check_partner_in_future_session = True
                if not check_partner_in_future_session:
                    order.partner_id.statut = 'indecis'
                    if futures_sessions:
                        for session in futures_sessions:
                            list_prospect = []
                            for prospect in session.prospect_ids:
                                if prospect.id != order.partner_id.id:
                                    list_prospect.append(prospect.id)
                            session.write({'prospect_ids': [(6, 0, list_prospect)]})
                    list = []
                    for prospect in module.session_id.prospect_ids:
                        list.append(prospect.id)
                    list.append(order.partner_id.id)
                    module.session_id.write({'prospect_ids': [(6, 0, list)]})
                order.module_id = module
                order.session_id = module.session_id
                # if order.company_id.id == 1:
                order.partner_id.date_examen_edof = module.date_exam
                order.partner_id.session_ville_id = module.session_ville_id

        if exam_date_id and exam_date_id == 'all':
            if order:
                order.module_id = False
                order.session_id = False
                order.partner_id.date_examen_edof = False
                order.partner_id.session_ville_id = False

    @http.route(['/cpf/update_exam_date'], type='json', auth="public", methods=['POST'], website=True)
    def partner_update_exam_center(self, exam_date_id):
        partner = request.env.user.partner_id
        if exam_date_id and exam_date_id != 'all':
            module = request.env['mcmacademy.module'].sudo().search([('id', '=', exam_date_id)], limit=1)
            if module and partner:
                partner.date_examen_edof = module.date_exam
        return True




            
            
