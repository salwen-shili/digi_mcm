import dateutil
from odoo import http
from odoo.http import request
from datetime import datetime, date
from odoo.addons.portal.controllers.web import Home
import werkzeug
import base64
from odoo.addons.website.controllers.main import Website  # import website controller
import locale
import logging

_logger = logging.getLogger(__name__)


class Website(Website):
    # inherit sitemap route function
    @http.route('/sitemap.xml', type='http', auth="public", website=True, multilang=False, sitemap=False)
    def sitemap_xml_index(self, **kwargs):
        current_website = request.website
        Attachment = request.env['ir.attachment'].sudo()
        mimetype = 'application/xml;charset=utf-8'
        content = None
        dom = [('url', '=', '/sitemap-%d.xml' %
                current_website.id), ('type', '=', 'binary')]
        # check existing of a sitemap attachment in database
        sitemap = Attachment.search(dom, limit=1)
        if sitemap and sitemap.datas:  # if sitemap exist get it from database and don't generate a new one
            content = base64.b64decode(sitemap.datas)
            return request.make_response(content, [('Content-Type', mimetype)])
        else:  # if doesn't exist in database generate new sitemap
            return super(Website, self).sitemap_xml_index(**kwargs)

    @http.route('/update_renonce', type='json', auth="public", methods=['POST'], website=True)
    def update_renonce(self, demande_renonce):
        user = request.env.user  # recuperer l'utilisateur connecté
        if demande_renonce:  # testé si l'utilisateur a cocher la demande de renonce dans son portal client
            # mettre la demande de renonce cocher dans la fiche client
            user.partner_id.renounce_request = True

    @http.route('/attestation-transport-leger-marchandises', type='http', auth='public', website=True)
    def attestation_transport_leger_marchandises(self, **kw, ):
        if request.website.id == 2:
            digimoov_products = request.env['product.product'].sudo().search([('company_id', '=', 2)],
                                                                             order="list_price")
            values = {
                'digimoov_products': digimoov_products,
            }
            return request.render("digimoov_website_templates.digimoov_template_transport_leger_marchandises", values)
        else:
            raise werkzeug.exceptions.NotFound()

    # Page de destination Paris

    @http.route('/devenir-coursier-paris', type='http', auth='public', website=True)
    def attestation_transport_leger_marchandises_destination_paris(self, **kw, ):

        if request.website.id == 2:
            digimoov_products = request.env['product.product'].sudo().search([('company_id', '=', 2)],
                                                                             order="list_price")
            values = {
                'digimoov_products': digimoov_products,
            }

            return request.render("digimoov_website_templates.devenir_coursier_paris",
                                  values)
        else:
            raise werkzeug.exceptions.NotFound()

    # Route nos formations

    @http.route('/nos-formations', type='http', auth='public', website=True)
    def nos_formations_digimoov(self, **kw, ):

        if request.website.id == 2:
            digimoov_products = request.env['product.product'].sudo().search([('company_id', '=', 2)],
                                                                             order="list_price")
            values = {
                'digimoov_products': digimoov_products,
            }

            return request.render("digimoov_website_templates.nos_formations",
                                  values)
        else:
            raise werkzeug.exceptions.NotFound()

    # Page de destination Lyon

    @http.route('/devenir-coursier-lyon', type='http', auth='public', website=True)
    def attestation_transport_leger_marchandises_destination_lyon(self, **kw, ):
        if request.website.id == 2:
            digimoov_products = request.env['product.product'].sudo().search([('company_id', '=', 2)],
                                                                             order="list_price")
            values = {
                'digimoov_products': digimoov_products,
            }
            return request.render("digimoov_website_templates.devenir_coursier_lyon",
                                  values)
        else:
            raise werkzeug.exceptions.NotFound()

    # Page de destination nantes
    @http.route('/livreur-de-colis-nantes', type='http', auth='public', website=True)
    def attestation_transport_leger_marchandises_destination_nantes(self, **kw, ):
        if request.website.id == 2:
            digimoov_products = request.env['product.product'].sudo().search([('company_id', '=', 2)],
                                                                             order="list_price")
            values = {
                'digimoov_products': digimoov_products,
            }
            return request.render("digimoov_website_templates.livreur_de_colis_nantes",
                                  values)
        else:
            raise werkzeug.exceptions.NotFound()

    # Page de destination bordeaux

    @http.route('/capacitaire-transport-bordeaux', type='http', auth='public', website=True)
    def attestation_transport_leger_marchandises_destination_bordeaux(self, **kw, ):
        if request.website.id == 2:
            digimoov_products = request.env['product.product'].sudo().search([('company_id', '=', 2)],
                                                                             order="list_price")
            values = {
                'digimoov_products': digimoov_products,
            }
            return request.render("digimoov_website_templates.capacitaire_transport_bordeaux",
                                  values)
        else:
            raise werkzeug.exceptions.NotFound()

    # Page de destination Marseille

    @http.route('/inscription-surveillants-examen-capacite-de-transport', type='http', auth='public', website=True)
    def inscription_surveillants_examen_capacite_de_transport(self, **kw, ):
        if request.website.id == 2:
            digimoov_products = request.env['product.product'].sudo().search([('company_id', '=', 2)],
                                                                             order="list_price")
            values = {
                'digimoov_products': digimoov_products,
            }
            return request.render("digimoov_website_templates.inscription_surveillants_examen_capacite_de_transport",
                                  values)
        else:
            raise werkzeug.exceptions.NotFound()


    # Page de destination Marseille

    @http.route('/capacite-de-transport-marseille', type='http', auth='public', website=True)
    def attestation_transport_leger_marchandises_destination_marseille(self, **kw, ):
        if request.website.id == 2:
            digimoov_products = request.env['product.product'].sudo().search([('company_id', '=', 2)],
                                                                             order="list_price")
            values = {
                'digimoov_products': digimoov_products,
            }
            return request.render("digimoov_website_templates.capacité_de_transport_marseille",
                                  values)
        else:
            raise werkzeug.exceptions.NotFound()

    @http.route('/capacité-de-transport-marseille', type='http', auth='public', website=True)
    def attestation_transport_leger_marchandises_destination_marseille_old_url(self, **kw, ):
        if request.website.id == 2:
            # redirect old url /capacité-de-transport-marseille to new url /capacite-de-transport-marseille
            return werkzeug.utils.redirect('/capacite-de-transport-marseille', 301)
        else:
            raise werkzeug.exceptions.NotFound()
    #redirection to cpf => reste a charge lourd
    @http.route('/redirection_to_cpf', type='http', auth='public', website=True)
    def redirection_to_cpf(self, **kw, ):
        if request.website.id == 2:
            return request.render("digimoov_website_templates.reste_a_charge")                                 v)
        else:
            raise werkzeug.exceptions.NotFound()



class FAQ(http.Controller):

    @http.route('/faq', type='http', auth='public', website=True)
    def faq(self, **kw, ):
        if request.website.id == 2:
            # recuperer la liste des villes pour l'afficher dans la page faq de siteweb digimoov
            last_ville = request.env['session.ville'].sudo().search(
                [('company_id', '=', 2), ('ville_formation', "=", False)], order='name_ville desc', limit=1)
            list_villes = request.env['session.ville'].sudo().search(
                [('id', "!=", last_ville.id), ('company_id', '=', 2),
                 ('ville_formation', "=", False)],
                order='name_ville asc')
            values = {
                'list_villes': list_villes,
                'last_ville': last_ville
            }
            return request.render("digimoov_website_templates.digimoov_template_faq", values)
        else:
            return request.render("mcm_website_theme.mcm_website_faq", {})


class FINANCEMENT(http.Controller):

    @http.route('/mon-compte-de-formation-cpf', type='http', auth='public', website=True)
    def financement(self, **kw, ):
        taxi_category = request.env['product.public.category'].sudo().search(
            [('name', 'ilike', 'Formation TAXI')])
        vtc_category = request.env['product.public.category'].sudo().search(
            [('name', 'ilike', 'Formation VTC')])
        vmdtr_category = request.env['product.public.category'].sudo().search(
            [('name', 'ilike', 'Formation VMDTR')])

        # Pricelist sur la page financement
        mcm_products = request.env['product.product'].sudo().search(
            [('company_id', '=', 1)], order="list_price")
        print(mcm_products)
        taxi_price = False
        vtc_price = False
        vmdtr_price = False
        if mcm_products:
            for product in mcm_products:
                if (product.default_code == 'taxi'):
                    taxi_price = round(product.list_price)
                if (product.default_code == 'vmdtr'):
                    vmdtr_price = round(product.list_price)
                if (product.default_code == 'vtc'):
                    vtc_price = round(product.list_price)

        values = {
            'taxi': taxi_category,
            'vtc': vtc_category,
            'vmdtr': vmdtr_category,
            'taxi_price': taxi_price if taxi_price else '',
            'vtc_price': vtc_price if vtc_price else '',
            'vmdtr_price': vmdtr_price if vmdtr_price else '',
            'mcm_products': mcm_products,  # send mcm product to homepage
        }
        if request.website.id == 2:
            # get digimoov products to send them to pricing table
            digimoov_products = request.env['product.product'].sudo().search([('company_id', '=', 2)],
                                                                             order="list_price")
            values = {
                'digimoov_products': digimoov_products,
            }
            return request.render("digimoov_website_templates.digimoov_template_financement", values)
        elif request.website.id == 1:
            return request.render("mcm_website_theme.mcm_website_theme_cpf", values)

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
                            print('interval days :' +
                                  str((module.date_exam - today).days))
                            if (module.date_exam - today).days > int(
                                    module.session_id.intervalle_jours) and module.session_id.website_published == True:
                                list_modules_digimoov.append(module)
                values.update({
                    'modules_digimoov': list_modules_digimoov,
                    'product': product_id,
                    'error_ville': False,
                    'error_exam_date': False,
                })
                list_villes = request.env['session.ville'].sudo().search(
                    [('company_id', '=', 2), ('ville_formation', "=", False)])
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
                                                                                                     'box2home',
                                                                                                     'coursier2roues']:
                return werkzeug.utils.redirect("/%s#pricing" % str(user_connected.partner_id.partner_from),301)
            
            else:
                return werkzeug.utils.redirect("/#pricing",301)


class DIGIEXAMEN(http.Controller):

    @http.route('/examen-capacite-transport-marchandises', type='http', auth='public', website=True)
    def exam(self, **kw, ):
        """ Ajouter les conditions suivant au niveau de la page examen dans le Site Web,
        lorsque un utulisateur clique sur le bouton de Tentative de repassage
        :param request.website.id: Si siteweb = digimoov alors :
        I- :param : is_public_user: Si l'utilisateur est un visiteur (False)
            1- Redirection: /web/signup
        II- :param: is_public_user: Si l'utilisateur n'est pas un visiteur (True)
            2- Si date examen != 0 : redirection:/#pricing
            3- Sinon si date examen existe, nombre de passage < 3 et date_dateutil(1er date_examen + 6 mois)
                Redirection: /shop/cart/update
            4- Si nombre de passage > 3: Redirection : /#pricing """
        if request.website.id == 2:
            partner = request.env.user.partner_id  # Récupérer id de l'apprenant connecté
            session_filtered = request.env['info.examen'].sudo().search(
                [('partner_id', "=", partner.id), ('nombre_de_passage', "=", 'premier')], order='date_exam desc',
                limit=1)
            # Récupérer date d'examen à partir de la première session
            date_exam = session_filtered.session_id.date_exam
            # PUBLIC USER = VISITOR OR USER ODOO NOT CONNECTED, return true or false
            is_public_user = request.website.is_public_user()
            echec_examen = request.env['product.product'].sudo().search(
                [('company_id', '=', 2), ('default_code', "=", 'examen')])
            if is_public_user is False:
                if date_exam:  # Si date examen exist
                    now = date.today()  # Date d'aujourd'hui
                    date_dateutil = date_exam + dateutil.relativedelta.relativedelta(
                        months=6)  # Calcule la durée de temps à partir de la ligne d'examen qui contient premier de l'apprenant en ajoutant 6 mois
                    exam_count = request.env['info.examen'].sudo().search_count(
                        [('partner_id', "=", partner.id), ('date_exam', ">=",
                                                           date_exam)])  # Calculer le nombre des examens a partir de la ligne qui contient un premier repassage
                    if exam_count < 3:  # Si nombre de passage < 3
                        logging.info(
                            'Si nombre de passage < 3 °°°°°°°°°°°°°°°°°°°°')
                        # Comparer si date d'aujourd'hui inférieur à date d'examen + 6 mois
                        if now < date_dateutil and is_public_user is not True:
                            values = {
                                'date_dateutil': date_dateutil,  # Date de 1ere inscription + 6 mois
                                'now': now,  # Date aujourd'hui
                                'echec_examen': echec_examen,
                                'url': '/shop/cart/update',
                                'default': 'True',
                            }
                            return request.render("digimoov_website_templates.digimoov_template_examen",
                                                  values)  # Envoyer les données vers xml dans la page examen
                        else:
                            values = {
                                'echec_examen': echec_examen,
                                'url': '/#pricing',
                                'default': 'False',
                                'message': "Vous avez dépassé la limite de 6 mois pour réserver votre nouvelle date d'examen."
                                           "Vous devez à présent vous réinscrire à la formation pour retenter votre chance de nouveau.",
                            }
                            return request.render("digimoov_website_templates.digimoov_template_examen",
                                                  values)  # Envoyer les données vers xml dans la page examen
                    elif exam_count >= 3:
                        logging.info(
                            'Si nombre de passage > 3 °°°°°°°°°°°°°°°°°°')
                        values = {
                            'default': 'False',
                            'echec_examen': echec_examen,
                            'url': '/#pricing',
                            'message': "Vous avez atteint le nombre maximum autorisé de repassages d'examen."
                                       "Vous devez à présent vous réinscrire à la formation pour retenter votre chance de nouveau.",
                        }
                        return request.render('digimoov_website_templates.digimoov_template_examen', values)
                else:
                    values = {
                        'echec_examen': echec_examen,
                        'is_public_user': is_public_user,
                        'default': 'False',
                        'url': '/#pricing',
                        'message': "Oups ! Vous ne pouvez pas accéder à cette option. Vous devez vous inscrire à la formation pour pouvoir choisir la date de votre examen."
                                   "Si vous avez déjà passé un examen, veuillez saisir les identifiants utilisés lors de la première inscription.<br/>"
                                   "Pour en savoir plus, veuillez contacter notre <a href='/service-clientele'>service clientèle</a>",

                    }
                    return request.render("digimoov_website_templates.digimoov_template_examen", values)

            else:
                values = {
                    'echec_examen': echec_examen,
                    'is_public_user': is_public_user,
                    'default': 'False',
                    'url': '/web/signup',
                    'message': 'Pour réserver votre nouvelle tentative, '
                               'merci de vous connecter ou de créer votre compte client.',
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
                [('company_id', '=', 2), ('ville_formation', "=", False)], order='name_ville desc', limit=1)
            list_villes = request.env['session.ville'].sudo().search(
                [('id', "!=", last_ville.id), ('company_id', '=', 2),
                 ('ville_formation', "=", False)],
                order='name_ville asc')
            values = {
                'list_villes': list_villes,
                'last_ville': last_ville
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
                [('company_id', '=', 2), ('ville_formation', "=", False)], order='name_ville desc', limit=1)
            list_villes = request.env['session.ville'].sudo().search(
                [('id', "!=", last_ville.id), ('company_id', '=', 2),
                 ('ville_formation', "=", False)],
                order='name_ville asc')
            values = {
                'list_villes': list_villes,
                'last_ville': last_ville
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

    # @http.route('/partenaires', type='http', auth='public', website=True)
    # def partenaires(self, **kw, ):
    #     if request.website.id == 1:
    #         return request.render("website.partenaires-1", {})
    #     else:
    #         return request.redirect("/pricing")


class Conditions(http.Controller):
    @http.route('/conditions', type='http', auth='public', website=True)
    def conditions(self, **kw, ):
        if request.website.id == 1:
            return request.render("mcm_website_theme.mcm_template_conditions", {})
        elif request.website.id == 2:
            return request.render("digimoov_website_templates.digimoov_template_conditions", {})

    @http.route('/politique-de-confidentialite', type='http', auth='public', website=True)
    def confidentialite(self, **kw, ):
        return request.render("digimoov_website_templates.digimoov_template_confidentialite", {})


class Services(http.Controller):

    @http.route('/service-clientele', type='http', auth='public', website=True)
    def clientele(self, **kw, ):
        if not http.request.env.user.active:
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
        if not http.request.env.user.active:
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

        if not http.request.env.user.active:
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

    @http.route('/service-presse', type='http', auth='public', website=True)
    def presse(self, **kw, ):
        if request.website.is_public_user():
            values = {
                'partner_id': False
            }
        else:
            values = {
                'partner_id': http.request.env.user.partner_id
            }
        return request.render("digimoov_website_templates.digimoov_template_service_presse",
                              values)

    @http.route('/service-comptabilite', type='http', auth='user', website=True)
    def comptabilite(self, **kw, ):
        if not http.request.env.user.active:
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
        raise werkzeug.exceptions.NotFound()
        # return request.render("digimoov_website_templates.digimoov_template_service_comptabilite",
        #                       {'email_from': email_from, 'phone': phone, 'contact_last_name': nom,
        #                        'contact_name': prenom})

    @http.route('/service-pedagogique', type='http', auth='user', website=True)
    def pedagogique(self, **kw, ):
        if not http.request.env.user.active:
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

    # url of maintenance page
    @http.route('/maintenance', type='http', auth='public', website=True)
    def maintenance(self, **kw, ):
        raise werkzeug.exceptions.NotFound()
        if request.website.id == 2:
            # maintenance view
            return request.render("digimoov_website_templates.support_maintenance", {})
        else:
            raise werkzeug.exceptions.NotFound()

    @http.route('/helpdesk/submitted/',
                type="http", auth="public", website=True, csrf=False)
    def get_ticket(self, **kwargs):
        contact_last_name = kwargs.get('contact_lastname')
        contact_name = kwargs.get('contact_name')
        email_from = str(kwargs.get('email_from')).replace(' ', '').lower()
        phone = kwargs.get('phone')
        _logger.info("phone : %s" %(str(kwargs.get('phone'))))
        _logger.info("phone_origin : %s" %(str(kwargs.get('phone_origin'))))
        name = kwargs.get('subject')
        description = kwargs.get('description')
        files = request.httprequest.files.getlist('attachment')
        name_company = False
        if kwargs.get('name_company'):
            name_company = kwargs.get('name_company')
        service = kwargs.get('service') #get value of service sended from frontend form
        user = http.request.env['res.users'].sudo().search([('login', "=", str(email_from).replace(' ', '').lower()), '|', ('active', '=', True), ('active', '=', False)], #search for active and not active users
                                                           limit=1)  # get only one user if there is double account with same email 
        if not user:
            user = request.env['res.users'].sudo().create({
                'name': str(contact_name) + " " + str(contact_last_name).upper(),
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
            user.partner_id.company_name = name_company
        if user and phone:
            if request.website.id == 1:
                user.sudo().write({'company_id': 1, 'company_ids': [1, 2]})
                user.partner_id.sudo().write(
                {'phone': phone, 'website_id': 1, 'email': email_from})
            elif request.website.id == 2:
                user.sudo().write({'company_id': 2, 'company_ids': [1, 2]})
                #fill fileds of the client ( phone , firstname , lastname )
                user.partner_id.sudo().write(
                    {'phone': phone, 'website_id': 2, 'email': email_from,'firstname':str(contact_name),'lastName':str(contact_last_name).upper(),'lastname':str(contact_last_name).upper()})
        if user:
            ticket_name = 'Digimoov : ' + str(name)
            ticket = request.env['helpdesk.ticket'].sudo().search(
                [('name', "=", ticket_name), ('partner_id', "=", user.partner_id.id),
                 ('description', "=", str(description),)], limit=1)
            if ticket:  # check if the customer has already sent a ticket with the same datas
                # if ticket has already created redirect client to contact page
                return request.redirect('/contact')
        #redirect ticket to the concerned team
        if service == 'client':
            if request.website.id == 2:
                vals = {
                    'partner_email': str(email_from),
                    'partner_id': user.partner_id.id,
                    'description': str(description),
                    'name': 'Digimoov : ' + str(name),
                    'team_id': request.env['helpdesk.team'].sudo().search(
                        [('name', 'ilike', 'Client'), ('company_id', "=", 2)],
                        limit=1).id,
                }
            elif request.website.id == 1:
                vals = {
                    'partner_email': str(email_from),
                    'partner_id': user.partner_id.id,
                    'description': str(description),
                    'name': str(name),
                    'team_id': request.env['helpdesk.team'].sudo().search(
                        [('name', 'ilike', 'client'), ('company_id', "=", 1)],
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
            if request.website.id == 2:
                vals = {
                    'partner_email': str(email_from),
                    'partner_id': user.partner_id.id,
                    'description': str(description),
                    'name': 'Digimoov : ' + str(name),
                    'team_id': request.env['helpdesk.team'].sudo().search(
                        [('name', 'like', 'Admini'), ('company_id', "=", 2)],
                        limit=1).id,
                }
            elif request.website.id == 1:
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
            if request.website.id == 2:
                vals = {
                    'partner_email': str(email_from),
                    'partner_id': user.partner_id.id,
                    'description': str(description),
                    'name': 'Digimoov : ' + str(name),
                    'team_id': request.env['helpdesk.team'].sudo().search(
                        [('name', 'like', 'Admini'), ('company_id', "=", 2)],
                        limit=1).id,
                }
            elif request.website.id == 1:
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
        elif service == 'presse':
            if request.website.id == 2:
                vals = {
                    'partner_email': str(email_from),
                    'partner_id': user.partner_id.id,
                    'description': str(description),
                    'name': 'Digimoov : ' + str(name),
                    'team_id': request.env['helpdesk.team'].sudo().search(
                        [('name', 'like', 'Presse'), ('company_id', "=", 2)],
                        limit=1).id,
                }
            elif request.website.id == 1:
                vals = {
                    'partner_email': str(email_from),
                    'partner_id': user.partner_id.id,
                    'description': str(description),
                    'name': str(name),
                    'team_id': request.env['helpdesk.team'].sudo().search(
                        [('name', 'like', 'Presse'), ('company_id', "=", 1)],
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
            return request.render("digimoov_website_templates.presse_thank_you")
        elif service == 'Comptabilité':
            if request.website.id == 2:
                vals = {
                    'partner_email': str(email_from),
                    'partner_id': user.partner_id.id,
                    'description': str(description),
                    'name': 'Digimoov : ' + str(name),
                    'team_id': request.env['helpdesk.team'].sudo().search(
                        [('name', 'like', 'Compta'), ('company_id', "=", 1)],
                        limit=1).id,
                }
            elif request.website.id == 1:
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
        elif service == 'coaching':
            if request.website.id == 2:
                vals = {
                    'partner_email': str(email_from),
                    'partner_id': user.partner_id.id,
                    'description': str(description),
                    'name': 'Digimoov : ' + str(name),
                    'team_id': request.env['helpdesk.team'].sudo().search(
                        [('name', 'like', 'coaching'), ('company_id', "=", 2)],
                        limit=1).id,
                }
            elif request.website.id == 1:
                vals = {
                    'partner_email': str(email_from),
                    'partner_id': user.partner_id.id,
                    'description': str(description),
                    'name': str(name),
                    'team_id': request.env['helpdesk.team'].sudo().search(
                        [('name', 'like', 'coaching'), ('company_id', "=", 1)],
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
        elif service == 'examen':
            if request.website.id == 2:
                vals = {
                    'partner_email': str(email_from),
                    'partner_id': user.partner_id.id,
                    'description': str(description),
                    'name': 'Digimoov : ' + str(name),
                    'team_id': request.env['helpdesk.team'].sudo().search(
                        [('name', 'like', 'Examen'), ('company_id', "=", 2)],
                        limit=1).id,
                }
            elif request.website.id == 1:
                vals = {
                    'partner_email': str(email_from),
                    'partner_id': user.partner_id.id,
                    'description': str(description),
                    'name': str(name),
                    'team_id': request.env['helpdesk.team'].sudo().search(
                        [('name', 'like', 'Examen'), ('company_id', "=", 1)],
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
        elif service == 'it':
            if request.website.id == 2:
                vals = {
                    'partner_email': str(email_from),
                    'partner_id': user.partner_id.id,
                    'description': str(description),
                    'name': 'Digimoov : ' + str(name),
                    'team_id': request.env['helpdesk.team'].sudo().search(
                        [('name', 'like', 'IT'), ('company_id', "=", 2)],
                        limit=1).id,
                }
            elif request.website.id == 1:
                vals = {
                    'partner_email': str(email_from),
                    'partner_id': user.partner_id.id,
                    'description': str(description),
                    'name': str(name),
                    'team_id': request.env['helpdesk.team'].sudo().search(
                        [('name', 'like', 'IT'), ('company_id', "=", 2)],
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
        else:
            if request.website.id == 2:
                vals = {
                    'partner_email': str(email_from),
                    'partner_id': user.partner_id.id,
                    'description': str(description),
                    'name': 'Digimoov : ' + str(name),
                    'team_id': request.env['helpdesk.team'].sudo().search(
                        [('name', 'ilike', 'Client'), ('company_id', "=", 2)],
                        limit=1).id,
                }
            elif request.website.id == 1:
                vals = {
                    'partner_email': str(email_from),
                    'partner_id': user.partner_id.id,
                    'description': str(description),
                    'name': str(name),
                    'team_id': request.env['helpdesk.team'].sudo().search(
                        [('name', 'ilike', 'client'), ('company_id', "=", 1)],
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


    # transport lourd


class Transport_Lourd(http.Controller):
    @http.route(['/formation-capacite-transport-lourd-marchandise'], type='http', auth='public', website=True)
    def transport_lourd(self, **kw, ):
        digimoov_products = False
        values = False
        if request.website.id == 2:

            # get digimoov products to send them to pricing table
            digimoov_products = request.env['product.product'].sudo().search([('company_id', '=', 2)],
                                                                             order="list_price")
            values = {
                'digimoov_products': digimoov_products,
            }
            return request.render("digimoov_website_templates.formation-capacité-transport-lourd-marchandise", values)
        else:
            raise werkzeug.exceptions.NotFound()


# habilitation electrique

class Habilitation_electrique(http.Controller):
    @http.route(['/habilitation-electrique'], type='http', auth='public', website=True)
    def habilitation_electrique(self, **kw, ):
        digimoov_products = False
        values = False
        if request.website.id == 2:
            # get digimoov products to send them to pricing table
            digimoov_products = request.env['product.product'].sudo().search([('company_id', '=', 2)],
                                                                             order="list_price")
            values = {
                'digimoov_products': digimoov_products,
            }
            return request.render("digimoov_website_templates.habilitation-electrique", values)
        else:
            raise werkzeug.exceptions.NotFound()

    @http.route(['/formation-habilitation-lyon'], type='http', auth='public', website=True)
    def habilitation_electrique_lyon(self, **kw, ):
        digimoov_products = False
        values = False
        if request.website.id == 2:
            # get digimoov products to send them to pricing table
            digimoov_products = request.env['product.product'].sudo().search([('company_id', '=', 2)],
                                                                             order="list_price")
            values = {
                'digimoov_products': digimoov_products,
            }
            return request.render("digimoov_website_templates.habilitation-electrique-lyon", values)
        else:
            raise werkzeug.exceptions.NotFound()

    @http.route(['/formation-habilitation-marseille'], type='http', auth='public', website=True)
    def habilitation_electrique_marseille(self, **kw, ):
        digimoov_products = False
        values = False
        if request.website.id == 2:
            # get digimoov products to send them to pricing table
            digimoov_products = request.env['product.product'].sudo().search([('company_id', '=', 2)],
                                                                             order="list_price")
            values = {
                'digimoov_products': digimoov_products,
            }
            return request.render("digimoov_website_templates.habilitation-electrique-marseille", values)
        else:
            raise werkzeug.exceptions.NotFound()

    @http.route(['/formation-habilitation-paris'], type='http', auth='public', website=True)
    def habilitation_electrique_paris(self, **kw, ):
        digimoov_products = False
        values = False
        if request.website.id == 2:
            # get digimoov products to send them to pricing table
            digimoov_products = request.env['product.product'].sudo().search([('company_id', '=', 2)],
                                                                             order="list_price")
            values = {
                'digimoov_products': digimoov_products,
            }
            return request.render("digimoov_website_templates.habilitation-electrique-paris", values)
        else:
            raise werkzeug.exceptions.NotFound()

    @http.route(['/page-vide'], type='http', auth='public', website=True)
    def page_vide(self, **kw, ):
        return request.render("digimoov_website_templates.page_vide", {})


class Uber_eats(http.Controller):
    @http.route(['/ubereats'], type='http', auth='public', website=True)
    def ubereats_landing_page(self, **kw, ):
        digimoov_products = False
        values = {}
        if request.website.id == 2:

            # get digimoov products to send them to pricing table
            digimoov_products = request.env['product.product'].sudo().search([('company_id', '=', 2)],
                                                                             order="list_price")
            partenaire = 'ubereats'
            promo = False
            # search for pricelist code UBEREATS
            promo = request.env['product.pricelist'].sudo().search(
                [('company_id', '=', 2), ('code', 'ilike', partenaire.upper())])
            values = {
                'digimoov_products': digimoov_products,
                'promo': promo,
            }
            return request.render("digimoov_website_templates.ubereats_landing_page", values)
        else:
            raise werkzeug.exceptions.NotFound()


class Deliveroo(http.Controller):
    @http.route(['/deliveroo'], type='http', auth='public', website=True)
    def deliveroo_landing_page(self, **kw, ):
        digimoov_products = False
        values = {}
        if request.website.id == 2:
            # get digimoov products to send them to pricing table
            digimoov_products = request.env['product.product'].sudo().search([('company_id', '=', 2)],
                                                                             order="list_price")

            partenaire = 'deliveroo'
            promo = False
            # search for pricelist code DELIVEROO
            promo = request.env['product.pricelist'].sudo().search(
                [('company_id', '=', 2), ('code', 'ilike', partenaire.upper())])
            values = {
                'digimoov_products': digimoov_products,
                'promo': promo,
            }
            return request.render("digimoov_website_templates.deliveroo_landing_page", values)
        else:
            raise werkzeug.exceptions.NotFound()


class Amazon(http.Controller):
    @http.route(['/amazon'], type='http', auth='public', website=True)
    def amazon_landing_page(self, **kw, ):
        digimoov_products = False
        values = {}
        if request.website.id == 2:
            # get digimoov products to send them to pricing table
            digimoov_products = request.env['product.product'].sudo().search([('company_id', '=', 2)],
                                                                             order="list_price")

            partenaire = 'amazon'
            promo = False
            # search for pricelist code amazon
            promo = request.env['product.pricelist'].sudo().search(
                [('company_id', '=', 2), ('code', 'ilike', partenaire.upper())])
            values = {
                'digimoov_products': digimoov_products,
                'promo': promo,
            }
            return request.render("digimoov_website_templates.digimoov_template_amazon_landing_page", values)
        else:
            raise werkzeug.exceptions.NotFound()
