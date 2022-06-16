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


class LoadDocument(Website):

    @http.route('/upload_document', type='http', auth='public', website=True)
    def create_applicant(self, **kw):
        partner=request.env['res.partner'].sudo().search([('id','=',request.env.user.partner_id.id)])
        values = {
            'sdk_token': '',
        }
        if partner:
            id_applicant=partner.create_applicant(partner)
            sdk_token=partner.generateSdktoken(id_applicant)
            
        # if request.website.id == 2:
        #     digimoov_products = request.env['product.product'].sudo().search([('company_id', '=', 2)],
        #                                                                      order="list_price")
            values = {
                'sdk_token': sdk_token,
            }

        return request.render("onfido_api_integration.load_document",
                              values)
        # else:
        #     raise werkzeug.exceptions.NotFound()

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

