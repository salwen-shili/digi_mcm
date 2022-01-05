#Ce programme est écrit par houssem pour la validation des liens des factures CPF par Zoe
#Ce code a été modifié par Seifeddinne dans l' ordre de changement de la process de facturation : application automatique de 25% pour les factures venant de ZoE
#On oublie pas qu on travaille avec la notion de multi_compagnie :
#Compagnie_id.id ==1  MCM_Academy
#Compagnie_id.id ==2  Digimoov

from odoo import http,SUPERUSER_ID,_
from odoo.http import request
import datetime
class ClientCPFController(http.Controller):


    @http.route(
        '/request_not_validated/<string:email>/<string:nom>/<string:prenom>/<string:tel>/<string:address>/<string:code_postal>/<string:ville>/<string:dossier>/<string:motif>',
        type="http", auth="user")
    def request_not_validated(self, email=None, nom=None, prenom=None, tel=None, address=None, code_postal=None, ville=None,
                   dossier=None, motif=None):
        email = email.replace("%", ".")
        email = email.replace(" ", "")
        email = str(email).lower()
        user = request.env['res.users'].sudo().search([('login', "=", email)])
        if not user:
            user = request.env['res.users'].sudo().create({
                'name': str(prenom) + " " + str(nom),
                'login': str(email),
                'groups_id': [(6, 0, [request.env.ref('base.group_portal').id])],
                'email': email,
                'notification_type': 'email',
            })
            client = request.env['res.partner'].sudo().search(
                [('id', '=', user.partner_id.id)])
            if client:
                client.mode_de_financement = 'cpf'
                client.numero_cpf = dossier
                client.phone = tel
                client.street = address
                client.zip = code_postal
                client.city = ville
                client.email = email
        partner = user.partner_id
        # Si Zoé n'a pas validé les dossiers cpf on classe
        # Chercher l'apprenant sur crm lead et classer sous etape non traité
        stage = request.env['crm.stage'].sudo().search([("name", "=", _("Non traité"))])
        print('stageeeee non traité', stage)
        if stage:
            lead = request.env['crm.lead'].sudo().search([('partner_id', '=', partner.id)], limit=1)
            if lead:
                print('if lead')
                lead.sudo().write({
                    'name': partner.name,
                    'partner_name': partner.name,
                    'num_dossier': dossier,
                    'email': partner.email,
                    'type': "opportunity",
                    'stage_id': stage.id,
                    'description': 'Motif : %s ' % (motif),
                    'mode_de_financement': 'cpf',
                    'module_id': partner.module_id,
                    'mcm_session_id': partner.mcm_session_id,

                })
            if not lead:
                print('if not lead')
                lead = request.env['crm.lead'].sudo().create({
                    'name': partner.name,
                    'partner_name': partner.name,
                    'num_dossier': dossier,
                    'email': partner.email,
                    'type': "opportunity",
                    'stage_id': stage.id,
                    'description': 'Motif : %s ' % (motif),
                    'mode_de_financement': 'cpf',
                    'module_id': partner.module_id,
                    'mcm_session_id': partner.mcm_session_id,
                })
                lead.partner_id = partner.id
        return request.render("mcm_cpf_validation.mcm_website_request_not_validated", {})

    # Ce programme a été modifié par seifeddinne le 24/03/2021
    # Modification du process de la facturation chez zoee
    # Elimination du 25 % account
    # Zoe traite le dossier s il est bien le CPF sera accepte et generation d'un devis

    @http.route('/cpf_accepted/<string:email>/<string:module>/', type="http", auth="user")
    def cpf_accepted(self,module=None, email=None):
        email = email.replace("%", ".")
        email = str(email).lower()
        email = email.replace(" ","")
        users = request.env['res.users'].sudo().search([('login', "=", email)])
        user = False
        if len(users) > 1:
            user = users[1]
            for utilisateur in users:
                if utilisateur.partner_id.id_edof and utilisateur.partner_id.date_examen_edof and utilisateur.partner_id.ville:
                    user = utilisateur
        else:
            user = users
        if user:
            user.partner_id.mode_de_financement = 'cpf'
            user.partner_id.statut_cpf = 'accepted'
            module_id=False
            product_id=False
            if 'digimoov' in str(module):
                product_id = request.env['product.template'].sudo().search([('id_edof', "=", str(module)),('company_id',"=",2)], limit=1)
            else:
                product_id = request.env['product.template'].sudo().search(
                    [('id_edof', "=", str(module)), ('company_id', "=", 1)], limit=1)

            if product_id and product_id.company_id.id==2 and user.partner_id.id_edof and user.partner_id.date_examen_edof and user.partner_id.session_ville_id:
                module_id = request.env['mcmacademy.module'].sudo().search(
                    [('company_id', "=", 2), ('session_ville_id', "=", user.partner_id.session_ville_id.id),
                     ('date_exam', "=", user.partner_id.date_examen_edof), ('product_id', "=", product_id.id),
                     ('session_id.number_places_available', '>', 0)], limit=1)
                if module_id:
                    user.partner_id.module_id = module_id
                    user.partner_id.mcm_session_id = module_id.session_id
                    product_id = request.env['product.product'].sudo().search(
                        [('product_tmpl_id', '=', module_id.product_id.id)])
                    user.partner_id.mcm_session_id = module_id.session_id
                    user.partner_id.module_id = module_id
                    request.env.user.company_id=2
                    invoice = request.env['account.move'].sudo().search(
                        [('module_id', "=", module_id.id), ('state', "=", 'posted'),
                         ('partner_id', "=", user.partner_id.id)])
                    if not invoice:
                        so = request.env['sale.order'].sudo().create({
                            'partner_id': user.partner_id.id,
                            'company_id':2,
                        })
                        so.module_id=module_id
                        so.session_id=module_id.session_id

                        so_line=request.env['sale.order.line'].sudo().create({
                            'name': product_id.name,
                            'product_id': product_id.id,
                            'product_uom_qty': 1,
                            'product_uom': product_id.uom_id.id,
                            'price_unit': product_id.list_price,
                            'order_id': so.id,
                            'tax_id': product_id.taxes_id,
                            'company_id':2,
                        })
                        #prix de la formation dans le devis
                        amount_before_instalment=so.amount_total
                        # so.amount_total = so.amount_total * 0.25
                        for line in so.order_line:
                            line.price_unit= so.amount_total
                        so.action_confirm()
                        ref=False
                        #Creation de la Facture Cpf
                        #Si la facture est de type CPF :  On parse le pourcentage qui est 25 %
                        # methode_payment prend la valeur CPF pour savoir bien qui est une facture CPF qui prend la valeur 25 % par default

                        if so.amount_total>0 and so.order_line:
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
                                move.price_unit =  so.amount_total
                                # move.cpf_acompte_invoice=True
                                # move.cpf_invoice = True
                                move.methodes_payment = 'cpf'
                                move.post()
                                ref=move.name
                        so.action_cancel()
                        so.unlink()
                        user.partner_id.statut = 'won'
                        return request.render("mcm_cpf_validation.mcm_website_cpf_accepted")
                    else:
                        return request.render("mcm_cpf_validation.mcm_website_contract_exist")
            elif product_id and product_id.company_id.id == 1 and user.partner_id.id_edof and user.partner_id.date_examen_edof and user.partner_id.session_ville_id:
                module_id = request.env['mcmacademy.module'].sudo().search(
                    [('company_id', "=", 1), ('session_ville_id', "=", user.partner_id.session_ville_id.id),
                     ('date_exam', "=", user.partner_id.date_examen_edof), ('product_id', "=", product_id.id),
                     ('session_id.number_places_available', '>', 0)], limit=1)
                if module_id:
                    user.partner_id.module_id = module_id
                    user.partner_id.mcm_session_id = module_id.session_id
                    product_id = request.env['product.product'].sudo().search(
                        [('product_tmpl_id', '=', module_id.product_id.id)])
                    user.partner_id.mcm_session_id = module_id.session_id
                    user.partner_id.module_id = module_id
                    request.env.user.company_id = 1
                    invoice = request.env['account.move'].sudo().search(
                        [('module_id', "=", module_id.id), ('state', "=", 'posted'),
                         ('partner_id', "=", user.partner_id.id)])
                    
                    if not invoice:
                        so = request.env['sale.order'].sudo().create({
                            'partner_id': user.partner_id.id,
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
                        user.partner_id.statut = 'won'
                        return request.render("mcm_cpf_validation.mcm_website_cpf_accepted")
                    else:
                        return request.render("mcm_cpf_validation.mcm_website_contract_exist")
            else:
                if 'digimoov' in str(module):
                    vals = {
                        'description': 'CPF: vérifier la date et ville de %s' % (user.name),
                        'name': 'CPF : Vérifier Date et Ville ',
                        'team_id': request.env['helpdesk.team'].sudo().search([('name', 'like', 'Client'),('company_id',"=",2)],
                                                                              limit=1).id,
                    }
                    description = "CPF: vérifier la date et ville de "+str(user.name)
                    ticket = request.env['helpdesk.ticket'].sudo().search([("description", "=", description)])
                    if not ticket:
                        new_ticket = request.env['helpdesk.ticket'].sudo().create(
                            vals)
                else:
                    vals = {
                        'partner_email': '',
                        'partner_id': False,
                        'description': 'CPF: id module edof %s non trouvé' % (module),
                        'name': 'CPF : ID module edof non trouvé ',
                        'team_id': request.env['helpdesk.team'].sudo().search([('name', "like", _('Client')),('company_id',"=",2)],
                                                                              limit=1).id,
                    }
                    description='CPF: id module edof '+str(module)+' non trouvé'
                    ticket = request.env['helpdesk.ticket'].sudo().search([('description', 'ilike', description)])
                    if not ticket:
                        new_ticket = request.env['helpdesk.ticket'].sudo().create(
                            vals)
                return request.render("mcm_cpf_validation.mcm_website_module_not_found", {})
        else:
            return request.render("mcm_cpf_validation.mcm_website_partner_not_found", {})

        # new cpf accepted link with all parametres of client
    @http.route(
        '/cpf_accepted/<string:email>/<string:nom>/<string:prenom>/<string:diplome>/<string:tel>/<string:address>/<string:code_postal>/<string:ville>/<string:dossier>/<string:session>/<string:module>/',
        type="http", auth="user", website=True, sitemap=False)
    def cpf_client_accepted(self, email=None, nom=None, prenom=None, diplome=None, tel=None, address=None,
                             code_postal=None, ville=None, dossier=None, session=None, module=None):
        email = email.replace("%", ".")
        email = str(email).lower()
        email = email.replace(" ", "")
        users = request.env['res.users'].sudo().search([('login', "=", email)])
        # redirect link to generate validate cpf link to create the client with all info of client
        if not users:
            if '+33' not in str(tel):
                users = request.env["res.users"].sudo().search(
                    [("phone", "=", str(tel).replace(' ', ''))], limit=1)
                if not users:
                    phone = str(tel)
                    phone = phone[1:]
                    phone = '+33' + str(phone)
                    users = request.env["res.users"].sudo().search(
                        [("phone", "=", phone.replace(' ', ''))], limit=1)
            else:
                users = request.env["res.users"].sudo().search(
                    [("phone", "=", str(tel).replace(' ', ''))], limit=1)
                if not users:
                    phone = str(tel)
                    phone = phone[3:]
                    phone = '0' + str(phone)
                    users = request.env["res.users"].sudo().search(
                        [("phone", "=", phone.replace(' ', ''))], limit=1)
            if not users:
                return request.redirect("/validate_cpf/%s/%s/%s/%s/%s/%s/%s/%s/%s/%s/%s/" % (
                    email, nom, prenom, diplome, tel, address, code_postal, ville, dossier, session, module))
        user = False
        if len(users) > 1:
            user = users[1]
            for utilisateur in users:
                if utilisateur.partner_id.id_edof and utilisateur.partner_id.date_examen_edof and utilisateur.partner_id.ville:
                    user = utilisateur
        else:
            user = users
        if user:
            user.partner_id.mode_de_financement = 'cpf'
            user.partner_id.statut_cpf = 'accepted'
            module_id = False
            product_id = False
            if 'digimoov' in str(module):
                product_id = request.env['product.template'].sudo().search(
                    [('id_edof', "=", str(module)), ('company_id', "=", 2)], limit=1)
            else:
                product_id = request.env['product.template'].sudo().search(
                    [('id_edof', "=", str(module)), ('company_id', "=", 1)], limit=1)

            if product_id and product_id.company_id.id == 2 and user.partner_id.id_edof and user.partner_id.date_examen_edof and user.partner_id.session_ville_id:
                module_id = request.env['mcmacademy.module'].sudo().search(
                    [('company_id', "=", 2), ('session_ville_id', "=", user.partner_id.session_ville_id.id),
                     ('date_exam', "=", user.partner_id.date_examen_edof), ('product_id', "=", product_id.id),
                     ('session_id.number_places_available', '>', 0)], limit=1)
                if module_id:
                    user.partner_id.module_id = module_id
                    user.partner_id.mcm_session_id = module_id.session_id
                    product_id = request.env['product.product'].sudo().search(
                        [('product_tmpl_id', '=', module_id.product_id.id)])
                    user.partner_id.mcm_session_id = module_id.session_id
                    user.partner_id.module_id = module_id
                    request.env.user.company_id = 2
                    invoice = request.env['account.move'].sudo().search(
                        [('module_id', "=", module_id.id), ('state', "=", 'posted'),
                         ('partner_id', "=", user.partner_id.id)])
                    if not invoice:
                        so = request.env['sale.order'].sudo().create({
                            'partner_id': user.partner_id.id,
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
                        user.partner_id.statut = 'won'
                        return request.render("mcm_cpf_validation.mcm_website_cpf_accepted")
                    else:
                        return request.render("mcm_cpf_validation.mcm_website_contract_exist")
            elif product_id and product_id.company_id.id == 1 and user.partner_id.id_edof and user.partner_id.date_examen_edof and user.partner_id.session_ville_id:
                module_id = request.env['mcmacademy.module'].sudo().search(
                    [('company_id', "=", 1), ('session_ville_id', "=", user.partner_id.session_ville_id.id),
                     ('date_exam', "=", user.partner_id.date_examen_edof), ('product_id', "=", product_id.id),
                     ('session_id.number_places_available', '>', 0)], limit=1)
                if module_id:
                    user.partner_id.module_id = module_id
                    user.partner_id.mcm_session_id = module_id.session_id
                    product_id = request.env['product.product'].sudo().search(
                        [('product_tmpl_id', '=', module_id.product_id.id)])
                    user.partner_id.mcm_session_id = module_id.session_id
                    user.partner_id.module_id = module_id
                    request.env.user.company_id = 1
                    invoice = request.env['account.move'].sudo().search(
                        [('module_id', "=", module_id.id), ('state', "=", 'posted'),
                         ('partner_id', "=", user.partner_id.id)])
                    if not invoice:
                        so = request.env['sale.order'].sudo().create({
                            'partner_id': user.partner_id.id,
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
                        user.partner_id.statut = 'won'
                        return request.render("mcm_cpf_validation.mcm_website_cpf_accepted")
                    else:
                        return request.render("mcm_cpf_validation.mcm_website_contract_exist")
            else:
                if 'digimoov' in str(module):
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
                        'description': 'CPF: id module edof %s non trouvé' % (module),
                        'name': 'CPF : ID module edof non trouvé ',
                        'team_id': request.env['helpdesk.team'].sudo().search(
                            [('name', "like", _('Client')), ('company_id', "=", 1)],
                            limit=1).id,
                    }
                    description = 'CPF: id module edof ' + str(module) + ' non trouvé'
                    ticket = request.env['helpdesk.ticket'].sudo().search([('description', 'ilike', description)])
                    if not ticket:
                        new_ticket = request.env['helpdesk.ticket'].sudo().create(
                            vals)
                return request.render("mcm_cpf_validation.mcm_website_module_not_found", {})
        else:
            return request.render("mcm_cpf_validation.mcm_website_partner_not_found", {})

    # new cpf validated  link with all parametres of client
    @http.route('/validate_cpf/<string:email>/<string:nom>/<string:prenom>/<string:diplome>/<string:tel>/<string:address>/<string:code_postal>/<string:ville>/<string:dossier>/<string:session>/<string:module>/', type="http", auth="user")
    def validate_cpf(self,email=None,nom=None,prenom=None,diplome=None,tel=None,address=None,code_postal=None,ville=None,dossier=None,session=None,module=None, **kw):
        email = email.replace("%", ".") # remplacer % par . dans l'email envoyé en paramètre
        email = email.replace(" ", "") # supprimer les espaces envoyés en paramètre email  pour éviter la création des deux comptes
        email = str(email).lower() # recupérer l'email en miniscule pour éviter la création des deux comptes
        user = request.env['res.users'].sudo().search([('login', "=", email)])
        exist=True
        if not user:
            if tel:
                user = request.env["res.users"].sudo().search(
                    [("phone", "=", str(tel))], limit=1)

                if not user:
                    phone_number = str(tel).replace(' ', '')
                    if '+33' not in str(phone_number):  # check if aircall api send the number of client with +33
                        phone = phone_number[0:2]
                        if str(phone) == '33' and ' ' not in str(
                                tel):  # check if aircall api send the number of client in this format (number_format: 33xxxxxxx)
                            phone = '+' + str(tel)
                            user = request.env["res.users"].sudo().search([("phone", "=", phone)], limit=1)
                            if not user:
                                phone = phone[0:3] + ' ' + phone[3:4] + ' ' + phone[4:6] + ' ' + phone[
                                                                                                 6:8] + ' ' + phone[
                                                                                                              8:10] + ' ' + phone[
                                                                                                                            10:]
                                user = request.env["res.users"].sudo().search([("phone", "=", phone)], limit=1)
                            if not user :
                                phone = '0' +str(phone[4:])
                                user = request.env["res.users"].sudo().search(['|',("phone", "=", phone),("phone", "=",phone.replace(' ',''))], limit=1)
                        phone = phone_number[0:2]
                        if str(phone) == '33' and ' ' in str(
                                tel):  # check if aircall api send the number of client in this format (number_format: 33 x xx xx xx)
                            phone = '+' + str(tel)
                            user = request.env["res.users"].sudo().search(
                                ['|', ("phone", "=", phone), ("phone", "=", phone.replace(' ', ''))], limit=1)
                            if not user:
                                phone = '0' + str(phone[4:])
                                user = request.env["res.users"].sudo().search(
                                    ['|', ("phone", "=", phone), ("phone", "=", phone.replace(' ', ''))], limit=1)
                        phone = phone_number[0:2]
                        if str(phone) in ['06', '07'] and ' ' not in str(
                                tel):  # check if aircall api send the number of client in this format (number_format: 07xxxxxx)
                            user = request.env["res.users"].sudo().search(['|',("phone", "=", str(tel)),("phone", "=", str('+33'+tel.replace(' ','')[-9:]))], limit=1)
                            if not user:

                                phone = phone[0:2] + ' ' + phone[2:4] + ' ' + phone[4:6] + ' ' + phone[
                                                                                                 6:8] + ' ' + phone[8:] # 07 xx xx xx

                                user = request.env["res.users"].sudo().search([("phone", "=", phone)], limit=1)
                                if not user :
                                    phone = '0' + str(phone[4:])
                                    user = request.env["res.users"].sudo().search(
                                        ['|', ("phone", "=", phone), ("phone", "=", phone.replace(' ', ''))], limit=1)
                        phone = phone_number[0:2]
                        if str(phone) in ['06', '07'] and ' ' in str(
                                tel):  # check if aircall api send the number of client in this format (number_format: 07 xx xx xx)
                            user = request.env["res.users"].sudo().search(
                                ['|', ("phone", "=", str(tel)), ("phone", "=",str(tel).replace(' ', ''))], limit=1)
                            if not user:
                                phone_number = str(tel[1:])
                                user = request.env["res.users"].sudo().search(
                                    ['|', ("phone", "=", str('+33'+phone_number)), ("phone", "=", ('+33'+phone_number.replace(' ', '')))], limit=1)
                    else:  # check if aircall api send the number of client with+33
                        if ' ' not in str(tel):
                            phone = str(tel)
                            phone = phone[0:3] + ' ' + phone[3:4] + ' ' + phone[4:6] + ' ' + phone[6:8] + ' ' + phone[
                                                                                                                8:10] + ' ' + phone[
                                                                                                                              10:]
                            user = request.env["res.users"].sudo().search(
                                [("phone", "=", phone)], limit=1)
                        if not user:
                            user = request.env["res.users"].sudo().search(
                                [("phone", "=", str(phone_number).replace(' ', ''))], limit=1)
                            if not user:
                                phone = str(phone_number)
                                phone = phone[3:]
                                phone = '0' + str(phone)
                                user = request.env["res.users"].sudo().search(
                                    [("phone", "like", phone.replace(' ', ''))], limit=1)
            if not user:
                exist = False
                if "digimoov" in str(module):
                    user = request.env['res.users'].sudo().create({
                        'name': str(prenom) + " " + str(nom),
                        'login': str(email),
                        'groups_id': [(6, 0, [request.env.ref('base.group_portal').id])],
                        'email': email,
                        'notification_type': 'email',
                        'website_id': 2,
                        'company_ids': [2],
                        'company_id': 2
                    })
                    user.company_id = 2
                    user.partner_id.company_id = 2
                else:
                    user = request.env['res.users'].sudo().create({
                        'name': str(prenom) + " " + str(nom),
                        'login': str(email),
                        'groups_id': [(6, 0, [request.env.ref('base.group_portal').id])],
                        'email': email,
                        'notification_type': 'email',
                        'website_id': 1,
                        'company_ids': [1],
                        'company_id': 1

                    })
                    user.company_id = 1
                    user.partner_id.company_id = 1
        # user = request.env['res.users'].sudo().search([('login', "=", email)])
        if user:
            client = request.env['res.partner'].sudo().search(
                [('id', '=', user.partner_id.id)])
            if client:
                client.mode_de_financement = 'cpf'
                client.funding_type = 'cpf'
                client.numero_cpf = dossier
                client.statut_cpf = 'validated'
                client.phone='0'+str(tel.replace(' ',''))[-9:]
                client.street=address
                client.zip=code_postal
                client.city=ville
                client.diplome=diplome
                module_id=False
                product_id=False

                template_id = int(request.env['ir.config_parameter'].sudo().get_param(
                    'mcm_cpf_validation.digimoov_email_template_exam_date_center'))
                template_id = request.env['mail.template'].search([('id', '=', template_id)]).id
                if not template_id:
                    template_id = request.env['ir.model.data'].xmlid_to_res_id(
                        'mcm_cpf_validation.digimoov_email_template_exam_date_center', raise_if_not_found=False)
                if not template_id:
                    template_id = request.env['ir.model.data'].xmlid_to_res_id(
                        'mcm_cpf_validation.digimoov_email_template_exam_date_center',
                        raise_if_not_found=False)
                if "digimoov" in str(module):
                    user.write({'company_ids': [1,2], 'company_id': 2})
                    product_id = request.env['product.template'].sudo().search([('id_edof', "=", str(module)),('company_id',"=",2)], limit=1)
                    if product_id:
                        client.id_edof=product_id.id_edof
                        # if template_id:
                        #     client.with_context(force_send=True).message_post_with_template(template_id,
                        #                                                                        composition_mode='comment')
                else:
                    user.write({'company_ids': [(4, 2)], 'company_id': 1})
                    product_id = request.env['product.template'].sudo().search(
                        [('id_edof', "=", str(module)), ('company_id', "=", 1)], limit=1)
                    if product_id:
                        client.id_edof = product_id.id_edof
            else:
                if not user.partner_id.renounce_request:
                    url = str(user.partner_id.get_base_url()) + '/my'
                    body = "Chere(e) %s félicitation pour votre inscription, votre formation commence dans 14 jours. Si vous souhaitez commencer dès maintenant cliquez sur le lien suivant : %s" % (
                        user.partner_id.name, url)
                    phone = str(tel.replace(' ', ''))[-9:]
                    phone = '+33' + ' ' + phone[0:1] + ' ' + phone[1:3] + ' ' + phone[3:5] + ' ' + phone[
                                                                                                   5:7] + ' ' + phone[
                                                                                                                7:]  # convert the number in this format : +33 x xx xx xx xx
                    client.phone = phone
                    if body:
                        composer = request.env['sms.composer'].with_context(
                            default_res_model='res.partner',
                            default_res_ids=user.partner_id.id,
                            default_composition_mode='mass',
                        ).sudo().create({
                            'body': body,
                            'mass_keep_log': True,
                            'mass_force_send': True, # force send sms True
                        })
                        composer.action_send_sms() # send sms
                    client.phone = '0'+str(tel.replace(' ',''))[-9:]
                return request.render("mcm_cpf_validation.mcm_website_partner_not_found", {})
        if not exist:
            return request.render("mcm_cpf_validation.mcm_website_new_partner_created", {})
        else:
            return request.render("mcm_cpf_validation.mcm_website_partner_updated", {})

    @http.route('/available_places/<string:email>/<string:module>', type="http", auth="user")
    def available_places(self,email=None,module=None):
        if 'digimoov' in str(module):
            user = request.env['res.users'].sudo().search([('login', "=", email)])
            if user:
                if not user.partner_id.ville or not user.partner_id.date_examen_edof or not user.partner_id.id_edof:
                    return request.render("mcm_cpf_validation.ko_places",{})
                else:
                    product_id = request.env['product.template'].sudo().search(
                        [('id_edof', "=", str(module)), ('company_id', "=", 2)], limit=1)
                    if product_id:
                        module_id = request.env['mcmacademy.module'].sudo().search(
                            [('company_id', "=", 2), ('session_ville_id', "=", user.partner_id.session_ville_id),
                             ('date_exam', "=", user.partner_id.date_examen_edof)], limit=1)
                        if not module_id:
                            return request.render("mcm_cpf_validation.ko_places", {})
                        else:
                            if module_id.session_id.number_places_available<=0:
                                return request.render("mcm_cpf_validation.ko_places", {})
                            else:
                                return request.render("mcm_cpf_validation.ok_places", {})
                    else:
                        return request.render("mcm_cpf_validation.ko_places", {})
        else:
            module_id = request.env['mcmacademy.module'].sudo().search(
                [('id_edof', "=", module),('company_id',"=",1)])
            if module_id:
                available_places=module_id.number_places_available
                places={
                    'available_places': available_places
                }
                if available_places<=0:
                    return request.render("mcm_cpf_validation.ko_places",{})
                else:
                    return request.render("mcm_cpf_validation.ok_places", {})
            else:
                vals = {
                    'partner_email': '',
                    'partner_id': False,
                    'description': 'CPF: id module edof %s non trouvé' % (module),
                    'name': 'CPF : ID module edof non trouvé ',
                    'team_id': request.env['helpdesk.team'].sudo().search([('name', 'like', 'Client'),('company_id',"=",1)],
                                                                          limit=1).id,
                }
                new_ticket = request.env['helpdesk.ticket'].sudo().create(
                    vals)
                return request.render("mcm_cpf_validation.mcm_website_module_not_found", {})
    #url of update state of cpf
    @http.route('/update_statut_cpf/<string:email>/<string:dossier>/<string:statut>/<string:date_cpf>', type="http", auth="user")
    def cpf_in_formation(self, email=None,dossier=None,statut=None,date_cpf=None):
        email = email.replace("%", ".")
        email = str(email).lower()
        email = email.replace(" ","") # replace space in mail
        users = request.env['res.users'].sudo().search([('login', "=", email)]) #search user with same email sended
        user=False
        if len(users) > 1 :
            user=users[1]
            for utilisateur in users:
                if utilisateur.partner_id.id_edof and utilisateur.partner_id.date_examen_edof and utilisateur.partner_id.session_ville_id: #if more than user ,check between them wich user is come from edof
                    user=utilisateur
        else:
            user=users
        if user: # if user finded
            user.partner_id.mode_de_financement = 'cpf' # update field mode de financement to cpf
            user.partner_id.funding_type = 'cpf' # update field funding type to cpf
            statut = statut.replace(" ","") # delete space from state
            statut = str(statut).lower() # convert state in lowercase
            if statut=="enformation": # if state in edof is in 'En formation'
                user.partner_id.statut_cpf = 'in_training' # update statut cpf to 'En formation'
            elif statut=="sortiedeformation":
                user.partner_id.statut_cpf = 'out_training' # if state in edof is in 'Sortie de formation'
            elif statut=="servicefaitdéclaré":  # update statut cpf to 'Sortie de formation'
                user.partner_id.statut_cpf = 'service_declared' # if state in edof is in 'Service fait declaré'
            elif statut=="servicefaitvalidé": # update statut cpf to 'Service fait validéé'
                user.partner_id.statut_cpf = 'service_validated' # if state in edof is in 'Service fait validé'
            elif statut=="facturé": # if state in edof is in 'facturé'
                user.partner_id.statut_cpf = 'bill'  # update statut cpf to 'facturé'
            elif statut=="annulé": # if state in edof is in 'annulé'
                user.partner_id.statut_cpf = 'canceled' # update statut cpf to 'annulé'
            else:
                return request.render("mcm_cpf_validation.ko_places", {})
            date_cpf = date_cpf.replace(" ","") #delete spaces if parametre date sended contains space(s)
            date_cpf = date_cpf
            date_cpf = date_cpf.replace("-","/")  # replace - in date sended by /
            date_cpf=datetime.datetime.strptime(date_cpf, '%d/%m/%Y')  #convert string date to datetime
            user.partner_id.numero_cpf = str(dossier) # update 'numero de dossier' of client
            user.partner_id.date_cpf = date_cpf # update cpf date of client
            return request.render("mcm_cpf_validation.ok_places", {})
        else:
            return request.render("mcm_cpf_validation.user_not_found", {})