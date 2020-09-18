from odoo import http,SUPERUSER_ID
from odoo.http import request


class ClientCPFController(http.Controller):

    @http.route(
        '/request_not_validated/<string:email>/<string:nom>/<string:prenom>/<string:tel>/<string:address>/<string:code_postal>/<string:ville>/<string:dossier>/<string:motif>',
        type="http", auth="user")
    def request_not_validated(self, email=None, nom=None, prenom=None, tel=None, address=None, code_postal=None, ville=None,
                   dossier=None, motif=None):
        email = email.replace("%", ".")
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
                client.mobile = tel
                client.street = address
                client.zip = code_postal
                client.city = ville
                client.email = email
        partner = user.partner_id
        vals = {
            'partner_email': partner.email,
            'partner_id': partner.id,
            'description': ' N°Dossier : %s \n Motif : %s ' % (dossier, motif),
            'name': 'CPF : Dossier non validé ',
            'team_id': request.env['helpdesk.team'].sudo().search([('name', 'like', 'Client')],
                                                                  limit=1).id,

        }
        new_ticket = request.env['helpdesk.ticket'].sudo().create(
            vals)
        return request.render("mcm_cpf_validation.mcm_website_request_not_validated", {})

    @http.route('/cpf_accepted/<string:email>', type="http", auth="user")
    def cpf_accepted(self, email=None):
        email = email.replace("%", ".")
        user = request.env['res.users'].sudo().search([('login', "=", email)])
        if user:
            user.partner_id.statut_cpf = 'accepted'
            user.partner_id.statut = 'won'
            return request.render("mcm_cpf_validation.mcm_website_cpf_accepted")
        else:
            return request.render("mcm_cpf_validation.mcm_website_partner_not_found", {})

    @http.route('/validate_cpf/<string:email>/<string:nom>/<string:prenom>/<string:diplome>/<string:tel>/<string:address>/<string:code_postal>/<string:ville>/<string:dossier>/<string:session>/<string:module>/', type="http", auth="user")
    def validate_cpf(self,email=None,nom=None,prenom=None,diplome=None,tel=None,address=None,code_postal=None,ville=None,dossier=None,session=None,module=None, **kw):
        email = email.replace("%", ".")
        user = request.env['res.users'].sudo().search([('login', "=", email)])
        if not user:
            user = request.env['res.users'].sudo().create({
                'name': str(prenom)+" "+str(nom),
                'login': str(email),
                'groups_id': [(6, 0, [request.env.ref('base.group_portal').id])],
                'email': email,
                'notification_type': 'email',

            })
        user = request.env['res.users'].sudo().search([('login', "=", email)])
        if user:
            client = request.env['res.partner'].sudo().search(
                [('id', '=', user.partner_id.id)])
            if client:
                client.mode_de_financement = 'cpf'
                client.statut_cpf = 'validated'
                client.numero_cpf = dossier
                client.mobile=tel
                client.street=address
                client.zip=code_postal
                client.city=ville
                client.email=email
                client.diplome=diplome
                session_id = request.env['mcmacademy.session'].sudo().search(
                    [('id_edof', '=', session)])
                if session_id:
                    client.mcm_session_id=session_id
                    module_id=request.env['mcmacademy.module'].sudo().search(
                    [('id_edof', '=', module),('session_id', '=', session_id.id)])
                    print('module')
                    print(module_id)
                    if module_id:
                        product_id = request.env['product.product'].sudo().search(
                            [('product_tmpl_id', '=', module_id.product_id.id)])
                        client.module_id=module_id
                        so = request.env['sale.order'].sudo().create({
                            'partner_id': client.id,
                        })
                        request.env['sale.order.line'].sudo().create({
                            'name': product_id.name,
                            'product_id': product_id.id,
                            'product_uom_qty': 1,
                            'product_uom': product_id.uom_id.id,
                            'price_unit': product_id.list_price,
                            'order_id': so.id,
                            'tax_id': False,
                        })
                        if so.env.su:
                            # sending mail in sudo was meant for it being sent from superuser
                            so = so.with_user(SUPERUSER_ID)
                        template_id = int(request.env['ir.config_parameter'].sudo().get_param(
                            'portal_contract.mcm_mail_template_sale_confirmation'))
                        template_id = request.env['mail.template'].sudo().search([('id', '=', template_id)]).id

                        if not template_id:
                            template_id = request.env['ir.model.data'].xmlid_to_res_id(
                                'portal_contract.mcm_mail_template_sale_confirmation', raise_if_not_found=False)
                        if not template_id:
                            template_id = request.env['ir.model.data'].xmlid_to_res_id(
                                'portal_contract.mcm_email_template_edi_sale', raise_if_not_found=False)
                        so.with_context(force_send=True).message_post_with_template(template_id,
                                                                                              composition_mode='comment',
                                                                                              email_layout_xmlid="portal_contract.mcm_mail_notification_paynow_online")
                        so.sudo().write({'state': 'sent'})

                        return request.render("mcm_cpf_validation.mcm_website_new_partner_created", {})
                    else:
                        vals = {
                            'partner_email': '',
                            'partner_id': False,
                            'description': 'CPF: id module edof %s non trouvé en session %s' % (module,session_id.name),
                            'name': 'CPF : ID module edof non trouvé ',
                            'team_id': request.env['helpdesk.team'].sudo().search([('name', 'like', 'Client')],
                                                                               limit=1).id,
                        }
                        new_ticket = request.env['helpdesk.ticket'].sudo().create(
                            vals)
                        return request.render("mcm_cpf_validation.mcm_website_module_not_found", {})
                else:
                    vals = {
                        'partner_email': '',
                        'partner_id': False,
                        'description': 'CPF: id session edof %s non trouvé' % (session),
                        'name': 'CPF : ID session edof non trouvé ',
                        'team_id': request.env['helpdesk.team'].sudo().search([('name', 'like', 'Client')],
                                                                           limit=1).id,

                    }
                    new_ticket = request.env['helpdesk.ticket'].sudo().create(
                        vals)
                    return request.render("mcm_cpf_validation.mcm_website_session_not_found", {})

            else:
                return request.render("mcm_cpf_validation.mcm_website_partner_not_found", {})
        return request.render("mcm_cpf_validation.mcm_website_new_partner_created", {})

    @http.route('/available_places/<string:module>', type="http", auth="user")
    def available_places(self,module=None):
            module_id = request.env['mcmacademy.module'].sudo().search(
                [('id_edof', "=", module)])
            if module_id:
                available_places=module_id.number_places_available
                places={
                    'available_places': available_places
                }
                return request.render("mcm_cpf_validation.available_module_places",places)
            else:
                vals = {
                    'partner_email': '',
                    'partner_id': False,
                    'description': 'CPF: id module edof %s non trouvé' % (module),
                    'name': 'CPF : ID module edof non trouvé ',
                    'team_id': request.env['helpdesk.team'].sudo().search([('name', 'like', 'Client')],
                                                                          limit=1).id,
                }
                new_ticket = request.env['helpdesk.ticket'].sudo().create(
                    vals)
                return request.render("mcm_cpf_validation.mcm_website_module_not_found", {})






