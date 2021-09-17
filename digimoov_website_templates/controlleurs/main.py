from odoo import http
from odoo.http import request
from datetime import datetime, date
from odoo.addons.portal.controllers.web import Home
import werkzeug
import base64
from odoo.addons.website.controllers.main import Website  # import website controller


class Website(Website):
    # inherit sitemap route function
    @http.route('/sitemap.xml', type='http', auth="public", website=True, multilang=False, sitemap=False)
    def sitemap_xml_index(self, **kwargs):
        current_website = request.website
        Attachment = request.env['ir.attachment'].sudo()
        mimetype = 'application/xml;charset=utf-8'
        content = None
        dom = [('url', '=', '/sitemap-%d.xml' % current_website.id), ('type', '=', 'binary')]
        sitemap = Attachment.search(dom, limit=1)  # check existing of a sitemap attachment in database
        if sitemap and sitemap.datas:  # if sitemap exist get it from database and don't generate a new one
            content = base64.b64decode(sitemap.datas)
            return request.make_response(content, [('Content-Type', mimetype)])
        else:  # if doesn't exist in database generate new sitemap
            return super(Website, self).sitemap_xml_index(**kwargs)

    @http.route('/update_renonce', type='json', auth="public", methods=['POST'], website=True)
    def update_renonce(self, demande_renonce):
        user = request.env.user  # recuperer l'utilisateur connecté
        if demande_renonce:  # testé si l'utilisateur a cocher la demande de renonce dans son portal client
            user.partner_id.renounce_request = True  # mettre la demande de renonce cocher dans la fiche client


class FAQ(http.Controller):

    @http.route('/faq', type='http', auth='public', website=True)
    def faq(self, **kw, ):
        if request.website.id == 2:
            # recuperer la liste des villes pour l'afficher dans la page faq de siteweb digimoov
            last_ville = request.env['session.ville'].sudo().search(
                [], order='name_ville desc', limit=1)
            list_villes = request.env['session.ville'].sudo().search(
                [('id', "!=", last_ville.id)], order='name_ville asc')
            values = {
                'list_villes': list_villes,
                'last_ville': last_ville
            }
            return request.render("digimoov_website_templates.digimoov_template_faq", values)
        else:
            return request.render("mcm_website_theme.mcm_website_faq",{})


class FINANCEMENT(http.Controller):

    @http.route('/mon-compte-de-formation-cpf', type='http', auth='public', website=True)
    def financement(self, **kw, ):
        if request.website.id == 2:
            return request.render("digimoov_website_templates.digimoov_template_financement", {})
        elif request.website.id == 1:
            return request.render("mcm_website_theme.mcm_website_theme_cpf", {})

    @http.route('/completer-mon-dossier-cpf', type='http', auth='user', website=True)
    def completer_mon_dossier(self, **kw, ):
        partner = request.env.user.partner_id
        values = {}
        if partner and partner.id_edof:
            product_id = request.env['product.template'].sudo().search(
                [('id_edof', "=", str(partner.id_edof)), ('company_id', "=", 2)], limit=1)
            if product_id:
                all_digimoov_modules = False
                all_digimoov_modules = request.env['mcmacademy.module'].sudo().search(
                    [('product_id', '=', product_id.id),
                     ('company_id', '=', 2)])
                list_modules_digimoov = []
                today = date.today()
                if (all_digimoov_modules):
                    for module in all_digimoov_modules:
                        if module.date_exam:
                            print('interval days :' + str((module.date_exam - today).days))
                            if (module.date_exam - today).days > int(
                                    module.session_id.intervalle_jours) and module.session_id.website_published == True:
                                list_modules_digimoov.append(module)
                values.update({
                    'modules_digimoov': list_modules_digimoov,
                    'product': product_id,
                    'error_ville': False,
                    'error_exam_date': False,
                })
                list_villes = request.env['session.ville'].sudo().search([])
                if list_villes:
                    values.update({
                        'list_villes': list_villes,
                    })

        return request.render("digimoov_website_templates.completer_mon_dossier_cpf", values)

    @http.route('/cpf-complete', type='http', auth='user', website=True)
    def submit_cpf(self, **kw, ):
        ville = kw.get('centre_d_examen')
        date_examen = kw.get('date_d_examen')
        error_ville = False
        error_exam_date = False
        if ville == 'all' and date_examen != 'all':
            error_ville = True
        if date_examen == 'all' and ville != 'all':
            error_exam_date = True
        if date_examen == 'all' and ville == 'all':
            error_ville = True

        partner = request.env.user.partner_id
        if error_ville or error_exam_date:
            values = {}
            if partner and partner.id_edof:
                product_id = request.env['product.template'].sudo().search(
                    [('id_edof', "=", str(partner.id_edof)), ('company_id', "=", 2)], limit=1)
                if product_id:
                    all_digimoov_modules = False
                    all_digimoov_modules = request.env['mcmacademy.module'].sudo().search(
                        [('product_id', '=', product_id.id), ('website_published', "=", True),
                         ('company_id', '=', 2)])
                    list_modules_digimoov = []
                    today = date.today()
                    if (all_digimoov_modules):
                        for module in all_digimoov_modules:
                            if module.date_exam:
                                if (module.date_exam - today).days > int(module.session_id.intervalle_jours):
                                    list_modules_digimoov.append(module)
                    values.update({
                        'modules_digimoov': list_modules_digimoov,
                        'product': product_id,
                        'error_ville': error_ville,
                        'error_exam_date': error_exam_date,
                    })
                    partner.ville = ''
                    return request.render("digimoov_website_templates.completer_mon_dossier_cpf", values)
        else:
            centre_examen = request.env['session.ville'].sudo().search(
                [('name_ville', "=", ville)])
            if centre_examen:
                partner.session_ville_id = centre_examen
            return request.redirect("/cpf-thank-you")

    @http.route('/cpf-thank-you', type='http', auth='user', website=True)
    def cpf_thanks(self, **kw, ):
        return request.render("digimoov_website_templates.cpf_thank_you", {})

    @http.route('/pricing', type='http', auth='public', website=True)
    def pricing_table(self, **kw, ):
        user_connected = request.env.user
        if user_connected:
            if user_connected.partner_id.partner_from and user_connected.partner_id.partner_from in ['ubereats',
                                                                                                     'deliveroo',
                                                                                                     'coursierjob',
                                                                                                     'box2home']:
                return request.redirect("/%s#pricing" % str(user_connected.partner_id.partner_from))
            else:
                return request.redirect("/#pricing")


class DIGIEXAMEN(http.Controller):

    @http.route('/examen-capacite-transport-marchandises', type='http', auth='public', website=True)
    def exam(self, **kw, ):
        if request.website.id == 2:
            echec_examen = request.env['product.product'].sudo().search(
                [('company_id', '=', 2), ('default_code', "=", 'examen')])
            values = {
                'echec_examen': echec_examen,
            }
            return request.render("digimoov_website_templates.digimoov_template_examen", values)
        else:
            return request.redirect("/preparation-examen-taxi/vtc")


class QUISOMMESNOUS(http.Controller):

    @http.route('/qui-sommes-nous', type='http', auth='public', website=True)
    def quisommesnous(self, **kw, ):
        if request.website.id == 2:
            # recuperer la liste des villes pour l'afficher dans la page qui sommes nous de siteweb digimoov
            last_ville = request.env['session.ville'].sudo().search(
                [],order='name_ville desc',limit=1)
            list_villes = request.env['session.ville'].sudo().search(
                [('id',"!=",last_ville.id)],order='name_ville asc')
            values = {
                'list_villes': list_villes,
                'last_ville':last_ville
            }
            return request.render("digimoov_website_templates.digimoov_template_quisommesnous", values)
        elif request.website.id == 1:
            return request.render("mcm_website_theme.mcm_website_theme_qui_sommes_nous", {})


class NOSCENTRES(http.Controller):

    @http.route('/nos-centres-examen', type='http', auth='public', website=True)
    def noscentresdigimoov(self, **kw, ):
        if request.website.id == 2:
            # recuperer la liste des villes pour l'afficher dans la page nos centres examen de siteweb digimoov
            last_ville = request.env['session.ville'].sudo().search(
                [],order='name_ville desc',limit=1)
            list_villes = request.env['session.ville'].sudo().search(
                [('id',"!=",last_ville.id)],order='name_ville asc')
            values = {
                'list_villes': list_villes,
                'last_ville':last_ville
            }
            return request.render("digimoov_website_templates.digimoov_template_noscentre", values)
        else:
            return request.redirect("/nos-centres")

    @http.route('/nos-centres', type='http', auth='public', website=True)
    def noscentresmcm(self, **kw, ):
        if request.website.id == 1:
            return request.render("website.nos-centres-formation", {})
        else:
            return request.redirect("/nos-centres-examen")

    @http.route('/partenaires', type='http', auth='public', website=True)
    def partenaires(self, **kw, ):
        if request.website.id == 1:
            return request.render("website.partenaires-1", {})
        else:
            return request.redirect("/pricing")


class Conditions(http.Controller):

    @http.route('/conditions', type='http', auth='public', website=True)
    def conditions(self, **kw, ):
        return request.render("digimoov_website_templates.digimoov_template_conditions", {})

    @http.route('/politique-de-confidentialite', type='http', auth='public', website=True)
    def confidentialite(self, **kw, ):
        return request.render("digimoov_website_templates.digimoov_template_confidentialite", {})


class Services(http.Controller):

    @http.route('/service-clientele', type='http', auth='public', website=True)
    def clientele(self, **kw, ):
        public_user = http.request.env['res.users'].sudo().search([('id', '=', 4), ('active', '=', False)])

        if http.request.uid == public_user.id:
            email_from = ""
            nom = ""
            prenom = ""
            phone = ""
        else:
            phone = http.request.env.user.phone
            email_from = http.request.env.user.email
            name = http.request.env.user.name
            nom = ''
            prenom = ''
            if http.request.env.user.firstname:
                name = name.split(" ", 1)
                if ' ' in name:
                    nom = name[1] if name[1] else ''
                prenom = name[0] if name[0] else ''
        return request.render("digimoov_website_templates.digimoov_template_service_clientele",
                              {'email_from': email_from, 'phone': phone, 'contact_last_name': nom,
                               'contact_name': prenom})

    @http.route('/administration', type='http', auth='public', website=True)
    def administration(self, **kw, ):
        public_user = http.request.env['res.users'].sudo().search([('id', '=', 4), ('active', '=', False)])

        if http.request.uid == public_user.id:
            email_from = ""
            nom = ""
            prenom = ""
            phone = ""
        else:
            phone = http.request.env.user.phone
            email_from = http.request.env.user.email
            name = http.request.env.user.name
            nom = ''
            prenom = ''
            if http.request.env.user.firstname:
                name = name.split(" ", 1)
                if ' ' in name:
                    nom = name[1] if name[1] else ''
                prenom = name[0] if name[0] else ''
        return request.render("digimoov_website_templates.digimoov_template_service_administration",
                              {'email_from': email_from, 'phone': phone, 'contact_last_name': nom,
                               'contact_name': prenom})

    @http.route('/partenariat', type='http', auth='public', website=True)
    def partenariat(self, **kw, ):
        public_user = http.request.env['res.users'].sudo().search([('id', '=', 4), ('active', '=', False)])

        if http.request.uid == public_user.id:
            email_from = ""
            nom = ""
            prenom = ""
            phone = ""
        else:
            phone = http.request.env.user.phone
            email_from = http.request.env.user.email
            name = http.request.env.user.name
            nom = ''
            prenom = ''
            if http.request.env.user.firstname:
                name = name.split(" ", 1)
                if ' ' in name:
                    nom = name[1] if name[1] else ''
                prenom = name[0] if name[0] else ''
        return request.render("digimoov_website_templates.digimoov_template_service_partenariat",
                              {'email_from': email_from, 'phone': phone, 'contact_last_name': nom,
                               'contact_name': prenom})

    @http.route('/service-comptabilite', type='http', auth='user', website=True)
    def comptabilite(self, **kw, ):
        public_user = http.request.env['res.users'].sudo().search([('id', '=', 4), ('active', '=', False)])

        if http.request.uid == public_user.id:
            email_from = ""
            nom = ""
            prenom = ""
            phone = ""
        else:
            phone = http.request.env.user.phone
            email_from = http.request.env.user.email
            name = http.request.env.user.name
            nom = ''
            prenom = ''
            if http.request.env.user.firstname:
                name = name.split(" ", 1)
                if ' ' in name:
                    nom = name[1] if name[1] else ''
                prenom = name[0] if name[0] else ''
        return request.render("digimoov_website_templates.digimoov_template_service_comptabilite",
                              {'email_from': email_from, 'phone': phone, 'contact_last_name': nom,
                               'contact_name': prenom})

    @http.route('/service-pedagogique', type='http', auth='user', website=True)
    def pedagogique(self, **kw, ):
        public_user = http.request.env['res.users'].sudo().search([('id', '=', 4), ('active', '=', False)])
        if http.request.uid == public_user.id:
            email_from = ""
            nom = ""
            prenom = ""
            phone = ""
        else:
            phone = http.request.env.user.phone
            email_from = http.request.env.user.email
            name = http.request.env.user.name
            nom = ''
            prenom = ''
            if http.request.env.user.firstname:
                name = name.split(" ", 1)
                if ' ' in name:
                    nom = name[1] if name[1] else ''
                prenom = name[0] if name[0] else ''
        return request.render("digimoov_website_templates.digimoov_template_service_pedagogique",
                              {'email_from': email_from, 'phone': phone, 'contact_last_name': nom,
                               'contact_name': prenom})

    @http.route('/contact', type='http', auth='public', website=True)
    def contact1(self, **kw, ):
        if request.website.id == 2:
            # return request.redirect('/maintenance')
            return request.render("digimoov_website_templates.digimoov_template_contact", {})
        else:
            return request.render("mcm_website_theme.mcm_template_contact", {})


    @http.route('/maintenance', type='http', auth='public', website=True) # url of maintenance page 
    def maintenance(self, **kw, ):
        raise werkzeug.exceptions.NotFound()
        if request.website.id == 2:
            return request.render("digimoov_website_templates.support_maintenance", {}) # maintenance view
        else:
            raise werkzeug.exceptions.NotFound()

    @http.route('/helpdesk/submitted/',
                type="http", auth="public", website=True, csrf=False)
    def get_ticket(self, **kwargs):
        contact_last_name = kwargs.get('contact_lastname')
        contact_name = kwargs.get('contact_name')
        email_from = kwargs.get('email_from')
        phone = kwargs.get('phone')
        name = kwargs.get('name')
        description = kwargs.get('description')
        files = request.httprequest.files.getlist('attachment')
        name_company = False
        if kwargs.get('name_company'):
            name_company = kwargs.get('name_company')
        service = kwargs.get('service')
        user = http.request.env['res.users'].sudo().search([('login', "=", str(email_from))],
                                                           limit=1)  # get only one user if there is double account with same email
        if not user:
            user = request.env['res.users'].sudo().create({
                'name': str(contact_name) + " " + str(contact_last_name),
                'login': str(email_from),
                'groups_id': [(6, 0, [request.env.ref('base.group_portal').id])],
                'email': email_from,
                # 'phone': phone,
                'notification_type': 'email',
                # 'website_id': 2,
                # 'company_ids': [1, 2],
                # 'company_id': 2
            })
        if user and name_company:
            user.sudo().write({'company_id': 1, 'company_ids': [1, 2]})
            user.partner_id.sudo().write({'phone': phone, 'website_id': 2, 'email': email_from})

            user.partner_id.company_name = name_company
        if user:
            ticket_name = 'Digimoov : ' + str(name)
            ticket = request.env['helpdesk.ticket'].sudo().search(
                [('name', "=", ticket_name), ('partner_id', "=", user.partner_id.id),
                 ('description', "=", str(description),)], limit=1)
            if ticket:  # check if the customer has already sent a ticket with the same datas
                # if ticket has already created redirect client to contact page
                return request.redirect('/contact')
        if service == 'client':
            if request.website.id == 2 :
                vals = {
                    'partner_email': str(email_from),
                    'partner_id': user.partner_id.id,
                    'description': str(description),
                    'name': 'Digimoov : ' + str(name),
                    'team_id': request.env['helpdesk.team'].sudo().search(
                        [('name', 'like', 'Client'), ('company_id', "=", 2)],
                        limit=1).id,
                }
            elif request.website.id == 1 :
                vals = {
                    'partner_email': str(email_from),
                    'partner_id': user.partner_id.id,
                    'description': str(description),
                    'name': str(name),
                    'team_id': request.env['helpdesk.team'].sudo().search(
                        [('name', 'like', 'Client'), ('company_id', "=", 1)],
                        limit=1).id,
                }
            new_ticket = request.env['helpdesk.ticket'].sudo().create(
                vals)
            if files:
                for ufile in files:
                    datas = base64.encodebytes(ufile.read())
                    request.env['ir.attachment'].sudo().create({
                        'name': ufile.filename,
                        'type': 'binary',
                        'datas': datas,
                        'res_model': 'helpdesk.ticket',
                        'res_id': new_ticket.id
                    })
            return request.render("digimoov_website_templates.client_thank_you")
        elif service == 'Administration':
            if request.website.id == 2 :
                vals = {
                    'partner_email': str(email_from),
                    'partner_id': user.partner_id.id,
                    'description': str(description),
                    'name': 'Digimoov : ' + str(name),
                    'team_id': request.env['helpdesk.team'].sudo().search(
                        [('name', 'like', 'Admini'), ('company_id', "=", 2)],
                        limit=1).id,
                }
            elif request.website.id == 1 :
                vals = {
                    'partner_email': str(email_from),
                    'partner_id': user.partner_id.id,
                    'description': str(description),
                    'name': str(name),
                    'team_id': request.env['helpdesk.team'].sudo().search(
                        [('name', 'like', 'Admini'), ('company_id', "=", 1)],
                        limit=1).id,
                }
            new_ticket = request.env['helpdesk.ticket'].sudo().create(
                vals)
            return request.render("digimoov_website_templates.administration_thank_you")
        elif service == 'Partenariat':
            if request.website.id == 2 :
                vals = {
                    'partner_email': str(email_from),
                    'partner_id': user.partner_id.id,
                    'description': str(description),
                    'name': 'Digimoov : ' + str(name),
                    'team_id': request.env['helpdesk.team'].sudo().search(
                        [('name', 'like', 'Admini'), ('company_id', "=", 2)],
                        limit=1).id,
                }
            elif request.website.id == 1 :
                vals = {
                    'partner_email': str(email_from),
                    'partner_id': user.partner_id.id,
                    'description': str(description),
                    'name': str(name),
                    'team_id': request.env['helpdesk.team'].sudo().search(
                        [('name', 'like', 'Admini'), ('company_id', "=", 1)],
                        limit=1).id,
                }
            new_ticket = request.env['helpdesk.ticket'].sudo().create(
                vals)
            return request.render("digimoov_website_templates.administration_thank_you")
        elif service == 'Comptabilité':
            if request.website.id == 2 :
                vals = {
                    'partner_email': str(email_from),
                    'partner_id': user.partner_id.id,
                    'description': str(description),
                    'name': 'Digimoov : ' + str(name),
                    'team_id': request.env['helpdesk.team'].sudo().search(
                        [('name', 'like', 'Compta'), ('company_id', "=", 2)],
                        limit=1).id,
                }
            elif request.website.id == 1 :
                vals = {
                    'partner_email': str(email_from),
                    'partner_id': user.partner_id.id,
                    'description': str(description),
                    'name': str(name),
                    'team_id': request.env['helpdesk.team'].sudo().search(
                        [('name', 'like', 'Compta'), ('company_id', "=", 1)],
                        limit=1).id,
                }
            new_ticket = request.env['helpdesk.ticket'].sudo().create(
                vals)
            return request.render("digimoov_website_templates.comptabilite_thank_you")
        elif service == 'Pédagogique':
            if request.website.id == 2 :
                vals = {
                    'partner_email': str(email_from),
                    'partner_id': user.partner_id.id,
                    'description': str(description),
                    'name': 'Digimoov : ' + str(name),
                    'team_id': request.env['helpdesk.team'].sudo().search(
                        [('name', 'like', 'gogique'), ('company_id', "=", 2)],
                        limit=1).id,
                }
            elif request.website.id == 1 :
                vals = {
                    'partner_email': str(email_from),
                    'partner_id': user.partner_id.id,
                    'description': str(description),
                    'name': str(name),
                    'team_id': request.env['helpdesk.team'].sudo().search(
                        [('name', 'like', 'gogique'), ('company_id', "=", 1)],
                        limit=1).id,
                }
            new_ticket = request.env['helpdesk.ticket'].sudo().create(
                vals)
            if files:
                for ufile in files:
                    datas = base64.encodebytes(ufile.read())
                    request.env['ir.attachment'].sudo().create({
                        'name': ufile.filename,
                        'type': 'binary',
                        'datas': datas,
                        'res_model': 'helpdesk.ticket',
                        'res_id': new_ticket.id
                    })
            return request.render("digimoov_website_templates.pedagogique_thank_you")
