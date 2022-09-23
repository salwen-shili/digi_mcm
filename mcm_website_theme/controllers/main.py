from odoo import http
from odoo.http import request
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website_sale.controllers.main import TableCompute
from odoo.addons.website_sale.controllers.main import QueryURL
from odoo.addons.portal.controllers.web import Home
from werkzeug.exceptions import Forbidden, NotFound
from odoo.addons.website.models.ir_http import sitemap_qs2dom
from odoo.addons.payment.controllers.portal import PaymentProcessing
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.tools import groupby as groupbyelem
from odoo.osv.expression import OR
from collections import OrderedDict
from operator import itemgetter
from odoo.exceptions import ValidationError
from odoo import fields, http, SUPERUSER_ID, tools, _
from odoo.osv import expression
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import werkzeug
import locale
import json
import logging
import requests
import random
import string
import odoo
import pandas as pd  # import library pandas to manage excel files
import xlrd  # import library xlrd for excel files
from odoo.addons.auth_signup.controllers.main import AuthSignupHome

_logger = logging.getLogger(__name__)
PPG = 20  # Products Per Page
PPR = 4  # Products Per Row


class Website(Home):
    @http.route(
        [
            """/""",
            """/<string:partenaire>""",
        ],
        type="http",
        auth="public",
        website=True,
    )
    def index(
        self,
        state="",
        partenaire="",
        **kw,
    ):
        # homepage=super(Website, self).index()
        print("partenaire:", partenaire)
        if not request.env.user.lang:
            request.env.user.lang = "fr_FR"
        locale.setlocale(locale.LC_TIME, str(request.env.user.lang) + ".utf8")
        all_categs = request.env["product.public.category"].sudo().search([("parent_id", "=", False)])
        all_states = (
            request.env["res.country.state"].sudo().search([("country_id.code", "ilike", "FR")], order="id asc")
        )
        taxi_category = request.env["product.public.category"].sudo().search([("name", "ilike", "Formation TAXI")])
        vtc_category = request.env["product.public.category"].sudo().search([("name", "ilike", "Formation VTC")])
        vmdtr_category = request.env["product.public.category"].sudo().search([("name", "ilike", "Formation VMDTR")])

        digimoov_products = request.env["product.product"].sudo().search([("company_id", "=", 2)], order="list_price")
        basic_price = False
        avancee_price = False
        premium_price = False
        # get all exam centers to show them in digimoov website homepage
        last_ville = (
            request.env["session.ville"]
            .sudo()
            .search([("company_id", "=", 2), ("ville_formation", "=", False)], order="name_ville desc", limit=1)
        )
        list_villes = (
            request.env["session.ville"]
            .sudo()
            .search(
                [("id", "!=", last_ville.id), ("company_id", "=", 2), ("ville_formation", "=", False)],
                order="name_ville asc",
            )
        )
        values = {"list_villes": list_villes, "last_ville": last_ville}
        if digimoov_products:
            for product in digimoov_products:
                if product.default_code == "basic":
                    basic_price = round(product.list_price)
                if product.default_code == "avancée":
                    avancee_price = round(product.list_price)
                if product.default_code == "premium":
                    premium_price = round(product.list_price)
        promo = False
        user_connected = request.env.user
        user_connected.partner_from = False
        if request.website.id == 2 and partenaire in [
            "ubereats",
            "deliveroo",
            "coursierjob",
            "box2home",
            "coursier2roues",
        ]:
            user_connected.partner_from = str(partenaire)
            promo = (
                request.env["product.pricelist"]
                .sudo()
                .search([("company_id", "=", 2), ("code", "ilike", partenaire.upper())])
            )
        if state:
            kw["search"] = state

        # Tarifs mcm
        mcm_products = request.env["product.product"].sudo().search([("company_id", "=", 1)], order="list_price")
        taxi_price = False
        vtc_price = False
        vmdtr_price = False
        if mcm_products:
            for product in mcm_products:
                if product.default_code == "taxi":
                    taxi_price = round(product.list_price)
                if product.default_code == "vmdtr":
                    vmdtr_price = round(product.list_price)
                if product.default_code == "vtc":
                    vtc_price = round(product.list_price)

        # Send values to digimoov and mcm websites

        values = {
            "all_categories": all_categs,
            "state": state,
            "all_states": all_states,
            "taxi": taxi_category,
            "vtc": vtc_category,
            "vmdtr": vmdtr_category,
            "digimoov_products": digimoov_products,
            "basic_price": basic_price if basic_price else "",
            "avancee_price": avancee_price if avancee_price else "",
            "premium_price": premium_price if premium_price else "",
            "taxi_price": taxi_price if taxi_price else "",
            "vtc_price": vtc_price if vtc_price else "",
            "vmdtr_price": vmdtr_price if vmdtr_price else "",
            "mcm_products": mcm_products,  # send mcm product to homepage
        }

        # send all exam centers to digimoov website homepage
        if last_ville:
            values["last_ville"] = last_ville
        if list_villes:
            values["list_villes"] = list_villes
        if (
            partenaire in ["", "ubereats", "deliveroo", "coursierjob", "box2home", "coursier2roues"]
            and request.website.id == 2
        ):
            values["partenaire"] = partenaire
            if promo:
                values["promo"] = promo
            else:
                values["promo"] = False
            return request.render("website.homepage", values)
        elif request.website.id == 2:
            website_page = (
                request.env["website.page"]
                .sudo()
                .search([("url", "=", "/" + str(partenaire)), ("website_id", "=", 2)])
            )
            if website_page:
                return request.render(str(website_page.view_id.key), values)
            else:
                # raise 404 not found if the url was not found
                raise werkzeug.exceptions.NotFound()
        if request.website.id == 1:
            user = http.request.env.user
            partner = user.partner_id
            documents = False
            promo = False
            user_connected = request.env.user
            user_connected.partner_from = False
            if request.website.id == 1 and partenaire in ["bolt"]:
                user_connected.partner_from = str(partenaire)
                promo = (
                    request.env["product.pricelist"]
                    .sudo()
                    .search([("company_id", "=", 1), ("code", "ilike", partenaire.upper())])
                )
            if partner:
                documents = request.env["documents.document"].sudo().search([("partner_id", "=", partner.id)])
            values["documents"] = documents
            if partenaire in [""] and request.website.id == 1:
                values["partenaire"] = partenaire
                if promo:
                    values["promo"] = promo
                else:
                    values["promo"] = False
                return request.render("website.homepage", values)
            else:
                website_page = request.env["website.page"].search(
                    [("url", "=", "/" + str(partenaire)), ("website_id", "=", 1)]
                )
                if website_page:
                    return request.render(str(website_page.view_id.key), values)
                else:
                    # raise 404 not found if the url was not found
                    raise werkzeug.exceptions.NotFound()
        return request.render("website.homepage", values)
        # --------------------------------------------------------------------------
        # states Search Bar
        # --------------------------------------------------------------------------

    @http.route("/states/autocomplete", type="json", auth="public", website=True)
    def states_autocomplete(self, term, options={}, **kwargs):
        states = (
            request.env["res.country.state"]
            .sudo()
            .search(["&", ("name", "ilike", term), ("country_id.code", "ilike", "FR")])
        )
        fields = ["id", "name"]
        res = {
            "states": states.read(fields),
        }
        return res


class Routes_Site(http.Controller):
    @http.route("/continue_signup", type="http", auth="user", website=True)
    def get_form_values(self, **kw):
        order = request.website.sale_get_order()
        if request.website.id == 2:
            if order:
                return request.redirect("/coordonnees")
            else:
                return request.redirect("/#pricing")
        elif request.website.id == 1:
            if order:
                return request.redirect("/coordonnees")
            else:
                return werkzeug.utils.redirect("/#pricing")

    @http.route("/update_partner", type="http", auth="user", website=True)
    def update_partner(self, **kw):

        # Bouton submit de la page edit_info pour modifier les coordonnées du client

        vals = {}
        vals["lastName"] = kw.get("lastName")
        vals["firstname"] = kw.get("firstname")
        vals["zip"] = kw.get("zip")
        vals["city"] = kw.get("city")
        vals["street2"] = kw.get("street2")
        vals["phone"] = kw.get("phone")
        vals["street"] = kw.get("num_voie") + " " + kw.get("voie") + " " + kw.get("nom_voie")
        user_id = request.uid
        partner = request.env["res.users"].sudo().search([("id", "=", user_id)]).partner_id
        partner.sudo().write(vals)
        order = request.website.sale_get_order()
        if partner:
            documents = request.env["documents.document"].sudo().search([("partner_id", "=", partner.id)])
        if not documents:
            return request.redirect("/charger_mes_documents")
        if documents and order:
            return request.redirect("/shop/cart")
        if not order:
            return request.redirect("/pricing")

    @http.route("/edit_info", type="http", auth="user", website=True)
    def editInfo(self):
        if request.website.id == 2:
            return request.render("digimoov_website_templates.digimoov_website_templates_edit_info", {})
        elif request.website.id == 1:
            return request.render("mcm_website_theme.mcm_website_theme_edit_info", {})

    @http.route("/formation-taxi", type="http", auth="public", website=True)
    def taxi(self):

        taxi_category = request.env["product.public.category"].sudo().search([("name", "ilike", "Formation TAXI")])
        vtc_category = request.env["product.public.category"].sudo().search([("name", "ilike", "Formation VTC")])
        vmdtr_category = request.env["product.public.category"].sudo().search([("name", "ilike", "Formation VMDTR")])

        # Pricelist sur la page formation chauffeur taxi
        mcm_products = request.env["product.product"].sudo().search([("company_id", "=", 1)], order="list_price")
        print(mcm_products)
        taxi_price = False
        vtc_price = False
        vmdtr_price = False
        if mcm_products:
            for product in mcm_products:
                if product.default_code == "taxi":
                    taxi_price = round(product.list_price)
                if product.default_code == "vmdtr":
                    vmdtr_price = round(product.list_price)
                if product.default_code == "vtc":
                    vtc_price = round(product.list_price)

        values = {
            "taxi": taxi_category,
            "vtc": vtc_category,
            "vmdtr": vmdtr_category,
            "taxi_price": taxi_price if taxi_price else "",
            "vtc_price": vtc_price if vtc_price else "",
            "vmdtr_price": vmdtr_price if vmdtr_price else "",
            "mcm_products": mcm_products,  # send mcm product to homepage
        }

        if request.website.id == 2:
            raise werkzeug.exceptions.NotFound()
        elif request.website.id == 1:
            return request.render("mcm_website_theme.mcm_template_taxi", values)

    @http.route("/formation-chauffeur-taxi", type="http", auth="public", website=True)
    def chauffeur_taxi(self):
        if request.website.id == 1:
            return werkzeug.utils.redirect("/formation-taxi", 301)
        else:
            raise werkzeug.exceptions.NotFound()

    @http.route("/formation-vtc", type="http", auth="public", website=True)
    def vtc(self):

        taxi_category = request.env["product.public.category"].sudo().search([("name", "ilike", "Formation TAXI")])
        vtc_category = request.env["product.public.category"].sudo().search([("name", "ilike", "Formation VTC")])
        vmdtr_category = request.env["product.public.category"].sudo().search([("name", "ilike", "Formation VMDTR")])

        # Pricelists sur la page formation chauffeur vtc
        mcm_products = request.env["product.product"].sudo().search([("company_id", "=", 1)], order="list_price")
        print(mcm_products)
        taxi_price = False
        vtc_price = False
        vmdtr_price = False
        if mcm_products:
            for product in mcm_products:
                if product.default_code == "taxi":
                    taxi_price = round(product.list_price)
                if product.default_code == "vmdtr":
                    vmdtr_price = round(product.list_price)
                if product.default_code == "vtc":
                    vtc_price = round(product.list_price)

        values = {
            "taxi": taxi_category,
            "vtc": vtc_category,
            "vmdtr": vmdtr_category,
            "taxi_price": taxi_price if taxi_price else "",
            "vtc_price": vtc_price if vtc_price else "",
            "vmdtr_price": vmdtr_price if vmdtr_price else "",
            "mcm_products": mcm_products,  # send mcm product to homepage
        }

        if request.website.id == 2:
            raise werkzeug.exceptions.NotFound()
        elif request.website.id == 1:
            return request.render("mcm_website_theme.mcm_website_theme_vtc", values)

    @http.route("/formation-chauffeur-vtc", type="http", auth="public", website=True)
    def chauffeur_vtc(self):
        if request.website.id == 1:
            return werkzeug.utils.redirect("/formation-vtc", 301)
        else:
            raise werkzeug.exceptions.NotFound()

    @http.route("/formation-moto-taxi", type="http", auth="public", website=True)
    def vmdtr(self):

        taxi_category = request.env["product.public.category"].sudo().search([("name", "ilike", "Formation TAXI")])
        vtc_category = request.env["product.public.category"].sudo().search([("name", "ilike", "Formation VTC")])
        vmdtr_category = request.env["product.public.category"].sudo().search([("name", "ilike", "Formation VMDTR")])

        # Pricelist de la page formation vmdtr
        mcm_products = request.env["product.product"].sudo().search([("company_id", "=", 1)], order="list_price")
        print(mcm_products)
        taxi_price = False
        vtc_price = False
        vmdtr_price = False
        if mcm_products:
            for product in mcm_products:
                if product.default_code == "taxi":
                    taxi_price = round(product.list_price)
                if product.default_code == "vmdtr":
                    vmdtr_price = round(product.list_price)
                if product.default_code == "vtc":
                    vtc_price = round(product.list_price)

        values = {
            "taxi": taxi_category,
            "vtc": vtc_category,
            "vmdtr": vmdtr_category,
            "taxi_price": taxi_price if taxi_price else "",
            "vtc_price": vtc_price if vtc_price else "",
            "vmdtr_price": vmdtr_price if vmdtr_price else "",
            "mcm_products": mcm_products,  # send mcm product to homepage
        }

        if request.website.id == 2:
            raise werkzeug.exceptions.NotFound()
        elif request.website.id == 1:
            return request.render("mcm_website_theme.mcm_template_vmdtr", values)

    @http.route("/formation-taximoto-vmtdr", type="http", auth="public", website=True)
    def chauffeur_vmdtr(self):
        if request.website.id == 1:
            return werkzeug.utils.redirect("/formation-moto-taxi", 301)
        else:
            raise werkzeug.exceptions.NotFound()

    @http.route("/examen-vtc-taxi-moto-taxi", type="http", auth="public", website=True)
    def examen(self):

        # La page n'est affichée que sur le site mcm
        taxi_category = request.env["product.public.category"].sudo().search([("name", "ilike", "Formation TAXI")])
        vtc_category = request.env["product.public.category"].sudo().search([("name", "ilike", "Formation VTC")])
        vmdtr_category = request.env["product.public.category"].sudo().search([("name", "ilike", "Formation VMDTR")])

        # Pricelist sur la page financement
        mcm_products = request.env["product.product"].sudo().search([("company_id", "=", 1)], order="list_price")
        print(mcm_products)
        taxi_price = False
        vtc_price = False
        vmdtr_price = False
        if mcm_products:
            for product in mcm_products:
                if product.default_code == "taxi":
                    taxi_price = round(product.list_price)
                if product.default_code == "vmdtr":
                    vmdtr_price = round(product.list_price)
                if product.default_code == "vtc":
                    vtc_price = round(product.list_price)

        values = {
            "taxi": taxi_category,
            "vtc": vtc_category,
            "vmdtr": vmdtr_category,
            "taxi_price": taxi_price if taxi_price else "",
            "vtc_price": vtc_price if vtc_price else "",
            "vmdtr_price": vmdtr_price if vmdtr_price else "",
            "mcm_products": mcm_products,  # send mcm product to homepage
        }
        if request.website.id == 2:
            raise werkzeug.exceptions.NotFound()
        elif request.website.id == 1:
            return request.render("mcm_website_theme.mcm_website_examen", values)

        # La page n'est affichée que sur le site mcm

        if request.website.id == 2:
            raise werkzeug.exceptions.NotFound()
        elif request.website.id == 1:
            return request.render("mcm_website_theme.mcm_website_examen", {})

    @http.route("/coordonnees", type="http", auth="user", website=True, csrf=False)
    def validation_questionnaires(self, **kw):
        order = request.website.sale_get_order()
        if not order:
            return request.redirect("/pricing")
        else:
            default_code_bolt = False
            if order.company_id.id == 1:
                if order.order_line:
                    for line in order.order_line:
                        if line.product_id.default_code == "vtc_bolt":
                            default_code_bolt = True
                    if default_code_bolt:
                        survey = (
                            request.env["survey.survey"]
                            .sudo()
                            .search([("title", "=", "Examen blanc Français")], limit=1)
                        )
                        if survey:
                            print(survey)
                            survey_user = (
                                request.env["survey.user_input"]
                                .sudo()
                                .search(
                                    [
                                        ("partner_id", "=", request.env.user.partner_id.id),
                                        ("survey_id", "=", survey.id),
                                    ],
                                    order="create_date asc",
                                    limit=1,
                                )
                            )
                            if not survey_user:
                                url = "/survey/start/" + str(survey.access_token)
                                return werkzeug.utils.redirect(url, 301)
                            if survey_user and survey_user.state == "new":
                                url = "/survey/start/" + str(survey.access_token)
                                return werkzeug.utils.redirect(url, 301)
                            if survey_user and survey_user.state == "skip":
                                return werkzeug.utils.redirect(
                                    str("survey/fill/%s/%s" % (str(survey.access_token), str(survey_user.token))), 301
                                )
                            if survey_user and survey_user.state == "done":
                                if not survey_user.quizz_passed:
                                    return werkzeug.utils.redirect("/bolt", 301)

        partner_has_documents = False
        if order.partner_id:
            documents = request.env["documents.document"].sudo().search([("partner_id", "=", order.partner_id.id)])
            if documents:
                partner_has_documents = True
        values = {
            "partner_has_documents": partner_has_documents,
        }
        if request.website.id == 2:
            return request.render("digimoov_website_templates.digimoov_template_validation", values)
        elif request.website.id == 1:
            return request.render("mcm_website_theme.mcm_website_theme_validation", values)

    @http.route(
        [
            """/<string:product>/<string:partenaire>/felicitations""",
            """/<string:product>/felicitations""",
            """/felicitations""",
        ],
        type="http",
        auth="user",
        website=True,
    )
    def felicitations(
        self,
        product=None,
        partenaire=None,
        **kw,
    ):
        # dynamic felicitations url
        if request.website.id == 1:
            order = request.website.sale_get_order()
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
                        slugname = (product_id.name).strip().strip("-").replace(" ", "-").lower()
                        if str(slugname) != str(product):
                            if order.pricelist_id and order.pricelist_id.name in ["bolt"]:
                                return request.redirect("/%s/%s/felicitations/" % (slugname, order.pricelist_id.name))
                            else:
                                return request.redirect("/%s/felicitations/" % (slugname))
                        else:
                            if order.pricelist_id and order.pricelist_id.name in ["bolt"]:
                                return request.redirect("/%s/%s/felicitations/" % (slugname, order.pricelist_id.name))
                    else:
                        return request.redirect("/felicitations")
                elif product and partenaire:
                    if product_id:
                        slugname = (product_id.name).strip().strip("-").replace(" ", "-").lower()
                        if str(slugname) != str(product):
                            pricelist = (
                                request.env["product.pricelist"]
                                .sudo()
                                .search([("company_id", "=", 1), ("name", "=", str(partenaire))])
                            )
                            if not pricelist:
                                pricelist_id = order.pricelist_id
                                if pricelist_id.name in [
                                    "bolt",
                                ]:
                                    return request.redirect("/%s/%s/felicitations/" % (slugname, pricelist_id.name))
                                else:
                                    return request.redirect("/%s/felicitations/" % (slugname))
                            else:
                                if pricelist.name in ["bolt"]:
                                    return request.redirect(
                                        "/%s/%s/felicitations/" % (slugname, order.pricelist_id.name)
                                    )
                                else:
                                    return request.redirect("/%s/felicitations/" % (slugname))
                        else:
                            pricelist = (
                                request.env["product.pricelist"]
                                .sudo()
                                .search([("company_id", "=", 1), ("name", "=", str(partenaire))])
                            )

                            if not pricelist:
                                pricelist_id = order.pricelist_id
                                if pricelist_id.name in ["bolt"]:
                                    return request.redirect("/%s/%s/felicitations/" % (slugname, pricelist_id.name))
                                else:
                                    return request.redirect("/%s/felicitations/" % (slugname))
                            else:
                                if pricelist.name in ["bolt"]:
                                    if pricelist.name != order.pricelist_id.name:
                                        return request.redirect(
                                            "/%s/%s/felicitations/" % (slugname, order.pricelist_id.name)
                                        )
                                else:
                                    return request.redirect("/%s/felicitations/" % (slugname))
                    else:
                        pricelist = (
                            request.env["product.pricelist"]
                            .sudo()
                            .search([("company_id", "=", 1), ("name", "=", str(partenaire))])
                        )
                        if pricelist and pricelist.name in ["bolt"]:
                            return request.redirect("/%s" % (pricelist.name))
                        else:
                            return request.redirect("/felicitations")
            return request.render("mcm_website_theme.mcm_template_felicitations", {})
        elif request.website.id == 2:
            order = request.website.sale_get_order()
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
                        slugname = (product_id.name).strip().strip("-").replace(" ", "-").lower()
                        if str(slugname) != str(product):
                            if order.pricelist_id and order.pricelist_id.name in [
                                "ubereats",
                                "deliveroo",
                                "coursierjob",
                                "box2home",
                                "coursier2roues",
                            ]:
                                return request.redirect("/%s/%s/felicitations/" % (slugname, order.pricelist_id.name))
                            else:
                                return request.redirect("/%s/felicitations/" % (slugname))
                        else:
                            if order.pricelist_id and order.pricelist_id.name in [
                                "ubereats",
                                "deliveroo",
                                "coursierjob",
                                "box2home",
                                "coursier2roues",
                            ]:
                                return request.redirect("/%s/%s/felicitations/" % (slugname, order.pricelist_id.name))
                    else:
                        return request.redirect("/felicitations")
                elif product and partenaire:
                    if product_id:
                        slugname = (product_id.name).strip().strip("-").replace(" ", "-").lower()
                        if str(slugname) != str(product):
                            pricelist = (
                                request.env["product.pricelist"]
                                .sudo()
                                .search([("company_id", "=", 2), ("name", "=", str(partenaire))])
                            )
                            if not pricelist:
                                pricelist_id = order.pricelist_id
                                if pricelist_id.name in [
                                    "ubereats",
                                    "deliveroo",
                                    "coursierjob",
                                    "box2home",
                                    "coursier2roues",
                                ]:
                                    return request.redirect("/%s/%s/felicitations/" % (slugname, pricelist_id.name))
                                else:
                                    return request.redirect("/%s/felicitations/" % (slugname))
                            else:
                                if pricelist.name in [
                                    "ubereats",
                                    "deliveroo",
                                    "coursierjob",
                                    "box2home",
                                    "coursier2roues",
                                ]:
                                    return request.redirect(
                                        "/%s/%s/felicitations/" % (slugname, order.pricelist_id.name)
                                    )
                                else:
                                    return request.redirect("/%s/felicitations/" % (slugname))
                        else:
                            pricelist = (
                                request.env["product.pricelist"]
                                .sudo()
                                .search([("company_id", "=", 2), ("name", "=", str(partenaire))])
                            )

                            if not pricelist:
                                pricelist_id = order.pricelist_id
                                if pricelist_id.name in ["bolt"]:
                                    return request.redirect("/%s/%s/felicitations/" % (slugname, pricelist_id.name))
                                else:
                                    return request.redirect("/%s/felicitations/" % (slugname))
                            else:
                                if pricelist.name in [
                                    "ubereats",
                                    "deliveroo",
                                    "coursierjob",
                                    "box2home",
                                    "coursier2roues",
                                ]:
                                    if pricelist.name != order.pricelist_id.name:
                                        return request.redirect(
                                            "/%s/%s/felicitations/" % (slugname, order.pricelist_id.name)
                                        )
                                else:
                                    return request.redirect("/%s/felicitations/" % (slugname))
                    else:
                        pricelist = (
                            request.env["product.pricelist"]
                            .sudo()
                            .search([("company_id", "=", 2), ("name", "=", str(partenaire))])
                        )
                        if pricelist and pricelist.name in [
                            "ubereats",
                            "deliveroo",
                            "coursierjob",
                            "box2home",
                            "coursier2roues",
                        ]:
                            return request.redirect("/%s" % (pricelist.name))
                        else:
                            return request.redirect("/felicitations")
            return request.render("digimoov_website_templates.digimoov_template_felicitations", {})

    @http.route(["/validation/submit"], type="http", auth="user", website=True, csrf=False)
    def validation_submit(self, **kw):
        # Méthode qui s'exécute au clic sur le bouton submit du questionnaire
        vals = {}
        vals["besoins_particuliers"] = kw.get("group1")
        vals["type_besoins"] = kw.get("type_besoins")
        vals["raison_choix"] = kw.get("group2")
        vals["support_formation"] = kw.get("group3")
        vals["availability"] = kw.get("group4")

        vals["attentes"] = kw.get("attentes")
        partner = http.request.env.user.partner_id
        # Étape suivante est documents
        documents = request.env["documents.document"].sudo().search([("partner_id", "=", partner.id)])
        if not documents:
            partner.step = "document"
        else:
            partner.step = "financement"
        partner = request.env["res.partner"].sudo().search([("id", "=", partner.id)])[-1]
        vals["partner_id"] = partner.id
        # Récupérer la commande liée au client
        order = request.website.sale_get_order()
        if order.order_line:
            # Récupérer le produit
            product = order.order_line[0].product_id.id
        else:
            product = False
        vals["product_id"] = product
        vals["company_id"] = partner.company_id.id
        # get the value of redirection sent from a form of questionnaire
        redirection = kw.get("redirection")
        new_quetionnaire = request.env["questionnaire"].sudo().create(vals)
        # Si le client a choisi un pack
        if order:
            # order.sudo().write(vals)
            documents = False
            # Si le client a déjà chargé ses documents, aller directement au panier
            if order.partner_id:
                documents = request.env["documents.document"].sudo().search([("partner_id", "=", order.partner_id.id)])
                if order and not documents:
                    if (
                        redirection == "automatique"
                    ):  # check if the value of redirection is auto to redirect the client to upload his documents using idenfy
                        return werkzeug.utils.redirect("/charger_mes_documents", 301)
                    elif (
                        redirection == "manuelle"
                    ):  # check if the value of redirection is manual to redirect the client to upload his documents manually
                        return werkzeug.utils.redirect("/charger_mes_documents_manual", 301)
                    else:
                        # if no redirection sended we redirect the client to shop cart
                        return werkzeug.utils.redirect("/shop/cart", 301)
            return werkzeug.utils.redirect("/shop/cart", 301)
        return http.request.render("mcm_contact_documents.portal_my_home", {"step": "document"})

    @http.route(
        ["/bolt-no-won"],
        type="http",
        auth="public",
        website=True,
    )
    def boltnowon(self):
        # ville = 'Île-de-France'
        # date_exam = '28/06/2022'
        # date_exam = datetime.strptime(
        #     date_exam, '%d/%m/%Y').date()
        # _logger.info("date_exam : %s" % (str(date_exam)))
        # ville_id = request.env['session.ville'].sudo().search(
        #     [('name_ville', "=", ville), ('company_id', "=", 1)],
        #     limit=1)  # search session ville
        # _logger.info("ville_id: %s" % (str(ville_id)))
        # product_id = request.env['product.product'].sudo().search(
        #     [('default_code', "=", 'vtc_bolt')], limit=1)
        # module_id = False
        # if ville_id and date_exam and product_id:
        #     _logger.info("aaaaaaaaaaaaaaaaaaaaaaaaaa")
        #     module_id = request.env['mcmacademy.module'].sudo().search(
        #         [('company_id', "=", 1), ('session_ville_id', "=", ville_id.id),
        #          ('date_exam', "=", date_exam), ('product_id',
        #                                          "=", product_id.id),
        #          ('session_id.number_places_available', '>', 0)],
        #         limit=1)  # search module in mcmacademy module using ville_id date_exam and product_id of bolt and session has available places
        # _logger.info("module_id: %s" % (str(module_id)))
        # if module_id :
        #     partners = request.env['res.partner'].sudo().search([('statut', "=", 'won'),('mcm_session_id',"=",module_id.session_id.id)])
        #     list = []
        #     _logger.info("compteurrrrrrrrrr : %s" %(str(len(partners))))
        #     for partner in partners :
        #         list.append(partner.id)
        #     module_id.session_id.sudo().write({'client_ids': [(6, 0, list)]})

        # promo = request.env['product.pricelist'].sudo().search(
        #     [('company_id', '=', 1), ('name', "=", 'bolt')], limit=1)
        loc = "/home/odoo/src/user/mcm_website_theme/static/res_partner_bolt.xlsx"
        wb = xlrd.open_workbook(loc)  # read excel file using xlrd open_workbook function
        list_user_won_or_have_session = []
        list_user_no_session_no_won = []
        list_not_found_user = []
        sheet = wb.sheet_by_index(0)
        for i in range(sheet.nrows):  # range rows of excel files
            row = sheet.row_values(i)
            _logger.info("email : %s" % (str(row[0])))
            email = str(row[0]).lower().replace(" ", "")
            users = request.env["res.users"].sudo().search([("login", "=", email)])

            #     list_dep = []
            if users:
                for user in users:
                    if user:
                        if user.statut == "won" or user.mcm_session_id:
                            list_user_won_or_have_session.append(user.email)
                        else:
                            list_user_no_session_no_won.append(user)
            else:
                list_not_found_user.append(email)
        _logger.info("list_user_won_or_have_session : %s" % (str(list_user_won_or_have_session)))
        _logger.info("list_user_no_session_no_won : %s" % (str(list_user_no_session_no_won)))
        _logger.info("list_not_found_user : %s" % (str(list_not_found_user)))
        for user in list_user_no_session_no_won:
            subtype_id = request.env["ir.model.data"].xmlid_to_res_id("mt_note")
            message = (
                request.env["mail.message"]
                .sudo()
                .create(
                    {
                        "subject": "Session supprimé",
                        "model": "res.partner",
                        "res_id": user.partner_id.id,
                        "message_type": "notification",
                        "subtype_id": subtype_id,
                        "body": "supprimé de la session du mois de juin suite à la demande de kawther dhmiri",
                    }
                )
            )

        #                 if not user.numero_evalbox:  # check if user has already an evalbox_number
        #                     if num_dossier:
        #                         _logger.info("num_dossier : %s" % (str(state)))
        #                         user.numero_evalbox = num_dossier  # fill field numero_evalbox with the number obtained from excel
        #                         list_evalbox.append(user.email)
        #                 if not user.state_id:  # check if user has already a state
        #                     if department:
        #                         state_id = department[:2]
        #                         _logger.info("state_id : %s" % (str(state_id)))
        #                         state = request.env['res.country.state'].sudo().search(
        #                             [('code', "=", state_id), ('country_id.code', "=", 'FR')])
        #                         if len(state) > 1:
        #                             state_id = False
        #                             for s in state:
        #                                 if (s.country_id.code == 'FR'):
        #                                     state_id = s
        #                             if state_id:
        #                                 state = state_id
        #                             else:
        #                                 state = False
        #                         if state:
        #                             _logger.info("state : %s" % (str(state)))
        #                             user.state_id = state  # fill field state with the state obtained from excel
        #                             list_dep.append(user.email)
        #     _logger.info("list_evalbox : %s" % (str(list_evalbox)))
        #     _logger.info("list_dep : %s" % (str(list_dep)))
        # data = pd.read_excel(
        #     r'/home/odoo/src/user/mcm_website_theme/static/res_partner_bolt.xlsx')  # read excel file using pandas read_excel function
        # df = pd.DataFrame(data, columns=['Email'])
        # compteur = 0
        # list = []
        # list_evalbox = []
        # list_user_no_evalbox = []
        # list_won = []
        # for x in data['Email']:  # read email column from excel file
        #     email = x
        #     email = str(email).lower().replace(' ', '')
        #     users = request.env['res.users'].sudo().search([('login', "=", email)])
        #     if users:
        #         for user in users:
        #             if user:
        #                 if user.statut != 'won' and user.statut != 'canceled':
        #                     compteur += 1
        #                     if user.numero_evalbox:
        #                         list_evalbox.append(
        #                             user.email)  # Add to the list of customers that have an evalbox number but do not have a won status.
        #                     else:
        #                         list_user_no_evalbox.append(
        #                             user)  # Add to the list of customers thatnot have an account on database
        #                 else:
        #                     list_won.append(user)
        #                 _logger.info("email : %s" % (str(email)))
        #
        #
        #     else:
        #         compteur += 1
        #         list.append(email)
        # _logger.info("list evalbox %s compteur : %s" % (str(list_evalbox), str(len(list_evalbox))))
        # _logger.info("email_not_found : %s compteur : %s" % (str(list), str(len(list))))
        # _logger.info("list won : %s compteur : %s" % (str(list_won), str(len(list_won))))
        # _logger.info("compteur: %s" % (str(compteur)))
        #
        # evalbox_no_facture = []
        # evalbox_facture = []
        # for email in list_evalbox:
        #     user = request.env['res.users'].sudo().search([('login', "=", email)], limit=1)
        #     if user and user.statut != 'canceled':
        #         invoice = request.env['account.move'].sudo().search(
        #             [('partner_id', "=", user.partner_id.id), ('amount_total', "=", 20)], limit=1)
        #         if not invoice:
        #             evalbox_no_facture.append(user)
        #         else:
        #             evalbox_facture.append(user)
        # _logger.info(
        #     "evalbox_no_facture_no_won: %s compteur %s" % (str(evalbox_no_facture), str(len(evalbox_no_facture))))
        # _logger.info("evalbox_facture_no_won: %s compteur %s" % (str(evalbox_facture), str(len(evalbox_facture))))
        # _logger.info(
        #     "-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
        # _logger.info(
        #     "-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
        # no_evalbox_no_facture = []
        # no_evalbox_facture = []
        # for user in list_user_no_evalbox:
        #     if user.statut != 'canceled':
        #         invoice = request.env['account.move'].sudo().search(
        #             [('partner_id', "=", user.partner_id.id), ('amount_total', "=", 20)], limit=1)
        #         if not invoice:
        #             no_evalbox_no_facture.append(user.email)
        #         else:
        #             no_evalbox_facture.append(user.email)
        # _logger.info("no_evalbox_no_facture_no_won: %s compteur %s" % (
        #     str(no_evalbox_no_facture), str(len(no_evalbox_no_facture))))
        # _logger.info(
        #     "no_evalbox_facture_no_won: %s compteur %s" % (str(no_evalbox_facture), str(len(no_evalbox_facture))))
        #
        # ville = 'Hauts-de-France'
        # date_exam = '28/06/2022'
        # date_exam = datetime.strptime(
        #     date_exam, '%d/%m/%Y').date()
        # _logger.info("date_exam : %s" % (str(date_exam)))
        # ville_id = request.env['session.ville'].sudo().search(
        #     [('name_ville', "=", ville), ('company_id', "=", 1)],
        #     limit=1)  # search session ville
        # _logger.info("ville_id: %s" % (str(ville_id)))
        # product_id = request.env['product.product'].sudo().search(
        #     [('default_code', "=", 'vtc_bolt')], limit=1)
        # module_id = False
        # if ville_id and date_exam and product_id:
        #     _logger.info("aaaaaaaaaaaaaaaaaaaaaaaaaa")
        #     module_id = request.env['mcmacademy.module'].sudo().search(
        #         [('company_id', "=", 1), ('session_ville_id', "=", ville_id.id),
        #          ('date_exam', "=", date_exam), ('product_id',
        #                                          "=", product_id.id),
        #          ('session_id.number_places_available', '>', 0)],
        #         limit=1)  # search module in mcmacademy module using ville_id date_exam and product_id of bolt and session has available places
        # _logger.info("module_id: %s" % (str(module_id)))
        # if module_id:
        #     for user in evalbox_no_facture:
        #         partner = user.partner_id
        #         _logger.info("partneeeeeeeeeeeerr: %s" % (str(partner)))
        #         so = request.env['sale.order'].sudo().create({
        #             'partner_id': partner.id,
        #             'company_id': 1,
        #             'website_id': 1,
        #         })  # create sale order ( contract ) if payment is succeed
        #         request.env['sale.order.line'].sudo().create({
        #             'name': product_id.name,
        #             'product_id': product_id.id,
        #             'product_uom_qty': 1,
        #             'product_uom': product_id.uom_id.id,
        #             'price_unit': product_id.list_price,
        #             'order_id': so.id,
        #             'tax_id': product_id.taxes_id,
        #             'company_id': 1
        #         })
        #         pricelist = request.env['product.pricelist'].sudo().search(
        #             [('company_id', '=', 1), ('name', "=", 'bolt')])  # search the pricelist bolt
        #         if pricelist:
        #             so.pricelist_id = pricelist.id
        #         _logger.info("soooooooooooooo: %s" % (str(so)))
        #         so.action_confirm()
        #         if module_id:
        #             so.partner_id.session_ville_id = module_id.session_ville_id
        #             so.partner_id.date_examen_edof = module_id.date_exam
        #             so.module_id = module_id.id
        #             so.session_id = module_id.session_id.id
        #         # create invoice from sale_order
        #         moves = so._create_invoices(final=True)
        #         for move in moves:
        #             _logger.info(
        #                 "webhook_stripe_move : %s" % (str(move)))
        #             move.type_facture = 'web'
        #             move.module_id = so.module_id.id
        #             move.session_id = so.session_id.id
        #             move.post()  # post the created invoice
        #             journal_id = move.journal_id.id
        #             acquirer = request.env['payment.acquirer'].sudo().search(
        #                 [('name', "=", _('stripe')), ('company_id', '=', 1)], limit=1)
        #             if acquirer:
        #                 journal_id = acquirer.journal_id.id
        #             payment_method = request.env['account.payment.method'].sudo().search(
        #                 [('code', 'ilike', 'electronic')], limit=1)
        #             payment = request.env['account.payment'].sudo().create(
        #                 {'payment_type': 'inbound',
        #                  'payment_method_id': payment_method.id,
        #                  'partner_type': 'customer',
        #                  'partner_id': move.partner_id.id,
        #                  'amount': so.amount_total,
        #                  'currency_id': move.currency_id.id,
        #                  'payment_date': move.create_date,
        #                  'journal_id': journal_id,
        #                  'communication': False,
        #                  'payment_token_id': False,
        #                  'invoice_ids': [(6, 0, move.ids)],
        #                  })  # create payment for invoice
        #         so.action_cancel()  # cancel contract
        #         so.sale_action_sent()  # resend contract
        #         so.partner_id.sudo().write({
        #             'mcm_session_id': module_id.session_id.id,
        #             'module_id': module_id.id,
        #         })
        #         so.partner_id.statut = 'won'  # change state of client to won
        #         list = []
        #         for partner in module_id.session_id.client_ids:
        #             list.append(partner.id)
        #             list.append(so.partner_id.id)
        #             module_id.session_id.write(
        #                 {'client_ids': [(6, 0, list)]})
        #         _logger.info("so : %s" % (str(so.id)))
        #         if so.env.su:
        #             # sending mail in sudo was meant for it being sent from superuser
        #             so = so.with_user(SUPERUSER_ID)
        #         template_id = so._find_mail_template(
        #             force_confirmation_template=True)
        #         if template_id and so:
        #             so.with_context(force_send=True).message_post_with_template(template_id,
        #                                                                         composition_mode='comment',
        #                                                                         email_layout_xmlid="portal_contract.mcm_mail_notification_paynow_online")
        #     for user in evalbox_facture:
        #         partner = user.partner_id
        #         _logger.info("partneeeeeeeeeeeerr1: %s" % (str(partner)))
        #         user.partner_id.sudo().write({
        #             'mcm_session_id': module_id.session_id.id,
        #             'module_id': module_id.id,
        #         })
        #         user.partner_id.statut = 'won'
        #         list = []
        #         for partner in module_id.session_id.client_ids:
        #             list.append(partner.id)
        #         list.append(user.partner_id.id)
        #         module_id.session_id.write(
        #             {'client_ids': [(6, 0, list)]})
        #     _logger.info("list won1 : %s" % (str(list_won)))
        #     for user in list_won:
        #         partner = user.partner_id
        #         if partner.module_id.session_ville_id.name_ville != 'Hauts-de-France':
        #             _logger.info("email of user : %s" % (str(partner.email)))
        #             module = partner.module_id
        #             list = []
        #             for res_partner in module.session_id.client_ids:
        #                 if res_partner.id != partner.id:
        #                     list.append(partner.id)
        #             module.session_id.sudo().write(
        #                 {'client_ids': [(6, 0, list)]})
        #             list_haut_de_france = []
        #             if module_id:
        #                 for res in module_id.session_id.client_ids:
        #                     list_haut_de_france.append(res.id)
        #                 list_haut_de_france.append(partner.id)
        #                 module_id.session_id.write(
        #                     {'client_ids': [(6, 0, list_haut_de_france)]})
        #             partner.mcm_session_id = module_id.session_id
        #             partner.module_id = module_id
        #         invoices = request.env['account.move'].sudo().search(
        #             [('partner_id', "=", user.partner_id.id), ('amount_total', "=", 20)], limit=1)
        #         for invoice in invoices:
        #             invoice.session_id = module_id.session_id
        #             invoice.module_id = module_id
        #
        #         orders = request.env['sale.order'].sudo().search(
        #             [('partner_id', "=", user.partner_id.id), ('amount_total', "=", 20)])
        #         for order in orders:
        #             order.session_id = module_id.session_id
        #             order.module_id = module_id
        # _logger.info("aaaaaaaaaaa")

        return request.render("mcm_website_theme.mcm_bolt_no_won", {})

    @http.route(
        ["""/bolt""", """/BOLT""", """/Bolt"""],
        type="http",
        auth="public",
        website=True,
    )
    def bolttest(self):
        return werkzeug.utils.redirect("/inscription-bolt", 301)

        bolt_product = (
            request.env["product.product"]
            .sudo()
            .search([("company_id", "=", 1), ("default_code", "=", "vtc_bolt")], order="list_price", limit=1)
        )
        vtc_product = (
            request.env["product.product"]
            .sudo()
            .search([("company_id", "=", 1), ("default_code", "=", "vtc")], order="list_price", limit=1)
        )

        promo = (
            request.env["product.pricelist"].sudo().search([("company_id", "=", 1), ("name", "=", "bolt")], limit=1)
        )
        #
        # res['exam_not_passed'] = 'False'
        # res['exam_success'] = 'False'
        # if order:
        #     if order.company_id.id == 1:
        #         if order.order_line:
        #             for line in order.order_line:
        #                 if (line.product_id.default_code == 'vtc_bolt'):
        #                     default_code_bolt = True
        #             if default_code_bolt:
        #                 survey = request.env['survey.survey'].sudo().search([('title', "=", 'Examen blanc Français')],
        #                                                                     limit=1)
        #                 if survey:
        #                     survey_user = request.env['survey.user_input'].sudo().search(
        #                         [('partner_id', "=", request.env.user.partner_id.id), ('survey_id', '=', survey.id)],
        #                         order='create_date asc', limit=1)
        #                     if not survey_user:
        #                         res['exam_not_passed'] = 'True'
        #                     if survey_user and survey_user.state == 'new':
        #                         res['exam_not_passed'] = 'True'
        #
        #                     if survey_user and survey_user.state == 'done':
        #                         if survey_user.quizz_passed:
        #                             res['exam_success'] = 'True'
        exam_state = "False"
        if not request.website.is_public_user():
            survey = request.env["survey.survey"].sudo().search([("title", "=", "Examen blanc Français")], limit=1)
            if survey:
                survey_user = (
                    request.env["survey.user_input"]
                    .sudo()
                    .search(
                        [
                            ("partner_id", "=", request.env.user.partner_id.id),
                            ("survey_id", "=", survey.id),
                            ("state", "=", "done"),
                        ],
                        order="create_date asc",
                        limit=1,
                    )
                )
                if not survey_user:
                    exam_state = "exam_not_passed"
                if survey_user and survey_user.state == "new":
                    exam_state = "exam_not_passed"

                if survey_user and survey_user.state == "done":
                    if not survey_user.quizz_corrected:
                        exam_state = "in_process"
                    else:
                        if survey_user.quizz_passed:
                            exam_state = "success"
                        else:
                            exam_state = "failed"
            if request.env.user.partner_id.bolt:
                if not request.env.user.partner_id.note_exam:
                    exam_state = "exam_not_passed"
                else:
                    note_exam = request.env.user.partner_id.note_exam
                    if int(note_exam) < 40:
                        exam_state = "failed"
                    else:
                        exam_state = "success"
        cartIsEmpty = "False"
        order = request.website.sale_get_order()
        if not order:
            cartIsEmpty = "True"
        if order and not order.order_line:
            cartIsEmpty = "True"
        boltWrongProduct = "False"
        if not request.website.is_public_user():
            request.env.user.partner_id.bolt = True
        if order and order.order_line:
            for line in order.order_line:
                if order.partner_id.bolt == True and line.product_id.default_code != "vtc_bolt":
                    boltWrongProduct = "True"
        partner = request.env.user.partner_id
        values = {
            "bolt_product": bolt_product,
            "vtc_product": vtc_product,
            "promo": promo,
            "exam_state": exam_state,
            "cartIsEmpty": cartIsEmpty,
            "boltWrongProduct": boltWrongProduct,
            "partner": partner,
        }

        if request.website.id == 2:
            raise werkzeug.exceptions.NotFound()
        elif request.website.id == 1:
            return request.render("mcm_website_theme.mcm_bolt", values)

    @http.route("/get_data_user_connected", type="json", auth="user", methods=["POST"], website=True)
    def get_data_user_connected(self):
        partner = request.env.user.partner_id
        res = {"response": []}
        exam_state = False
        if partner.bolt and partner.note_exam:
            note = float(partner.note_exam)
            note = note / 5
            if note >= 8:
                exam_state = "success"
            else:
                exam_state = "failed"
        res["response"] += [
            {
                "id": partner.id,
                "name": partner.name,
                "fisrtname": partner.firstname,
                "lastName": partner.lastName,
                "email": partner.email,
                "phone": partner.phone,
                "street": partner.street,
                "city": partner.city,
                "zip": partner.zip,
                "email": partner.email,
                "note_exam": partner.note_exam,
                "exam_state": exam_state,
                "ipJotForm": partner.ipjotform,
                "evalbox": partner.numero_evalbox,
            }
        ]
        partner = json.dumps(res)
        return partner

    @http.route("/formation-taxi-Paris", type="http", auth="public", website=True)
    def taxi_paris(self):

        taxi_category = request.env["product.public.category"].sudo().search([("name", "ilike", "Formation TAXI")])
        vtc_category = request.env["product.public.category"].sudo().search([("name", "ilike", "Formation VTC")])
        vmdtr_category = request.env["product.public.category"].sudo().search([("name", "ilike", "Formation VMDTR")])

        # Pricelist sur la page formation chauffeur taxi
        mcm_products = request.env["product.product"].sudo().search([("company_id", "=", 1)], order="list_price")
        print(mcm_products)
        taxi_price = False
        vtc_price = False
        vmdtr_price = False
        if mcm_products:
            for product in mcm_products:
                if product.default_code == "taxi":
                    taxi_price = round(product.list_price)
                if product.default_code == "vmdtr":
                    vmdtr_price = round(product.list_price)
                if product.default_code == "vtc":
                    vtc_price = round(product.list_price)

        values = {
            "taxi": taxi_category,
            "vtc": vtc_category,
            "vmdtr": vmdtr_category,
            "taxi_price": taxi_price if taxi_price else "",
            "vtc_price": vtc_price if vtc_price else "",
            "vmdtr_price": vmdtr_price if vmdtr_price else "",
            "mcm_products": mcm_products,  # send mcm product to homepage
        }

        if request.website.id == 2:
            raise werkzeug.exceptions.NotFound()
        elif request.website.id == 1:
            return request.render("mcm_website_theme.formation-taxi-Paris", values)

    @http.route("/formation-taxi-Lille", type="http", auth="public", website=True)
    def taxi_lille(self):

        taxi_category = request.env["product.public.category"].sudo().search([("name", "ilike", "Formation TAXI")])
        vtc_category = request.env["product.public.category"].sudo().search([("name", "ilike", "Formation VTC")])
        vmdtr_category = request.env["product.public.category"].sudo().search([("name", "ilike", "Formation VMDTR")])

        # Pricelist sur la page formation chauffeur taxi
        mcm_products = request.env["product.product"].sudo().search([("company_id", "=", 1)], order="list_price")
        print(mcm_products)
        taxi_price = False
        vtc_price = False
        vmdtr_price = False
        if mcm_products:
            for product in mcm_products:
                if product.default_code == "taxi":
                    taxi_price = round(product.list_price)
                if product.default_code == "vmdtr":
                    vmdtr_price = round(product.list_price)
                if product.default_code == "vtc":
                    vtc_price = round(product.list_price)

        values = {
            "taxi": taxi_category,
            "vtc": vtc_category,
            "vmdtr": vmdtr_category,
            "taxi_price": taxi_price if taxi_price else "",
            "vtc_price": vtc_price if vtc_price else "",
            "vmdtr_price": vmdtr_price if vmdtr_price else "",
            "mcm_products": mcm_products,  # send mcm product to homepage
        }

        if request.website.id == 2:
            raise werkzeug.exceptions.NotFound()
        elif request.website.id == 1:
            return request.render("mcm_website_theme.formation-taxi-Lille", values)

    @http.route("/formation-taxi-Lyon", type="http", auth="public", website=True)
    def taxi_lyon(self):

        taxi_category = request.env["product.public.category"].sudo().search([("name", "ilike", "Formation TAXI")])
        vtc_category = request.env["product.public.category"].sudo().search([("name", "ilike", "Formation VTC")])
        vmdtr_category = request.env["product.public.category"].sudo().search([("name", "ilike", "Formation VMDTR")])

        # Pricelist sur la page formation chauffeur taxi
        mcm_products = request.env["product.product"].sudo().search([("company_id", "=", 1)], order="list_price")
        print(mcm_products)
        taxi_price = False
        vtc_price = False
        vmdtr_price = False
        if mcm_products:
            for product in mcm_products:
                if product.default_code == "taxi":
                    taxi_price = round(product.list_price)
                if product.default_code == "vmdtr":
                    vmdtr_price = round(product.list_price)
                if product.default_code == "vtc":
                    vtc_price = round(product.list_price)

        values = {
            "taxi": taxi_category,
            "vtc": vtc_category,
            "vmdtr": vmdtr_category,
            "taxi_price": taxi_price if taxi_price else "",
            "vtc_price": vtc_price if vtc_price else "",
            "vmdtr_price": vmdtr_price if vmdtr_price else "",
            "mcm_products": mcm_products,  # send mcm product to homepage
        }

        if request.website.id == 2:
            raise werkzeug.exceptions.NotFound()
        elif request.website.id == 1:
            return request.render("mcm_website_theme.formation-taxi-Lyon", values)

    @http.route("/evalbox_registration/<string:email>/<string:state>/", type="http", auth="public")
    def evalbox_registration(self, email=None, **kw):
        email = email.replace("%", ".")  # remplacer % par . dans l'email envoyé en paramètre
        email = email.replace(
            " ", ""
        )  # supprimer les espaces envoyés en paramètre email  pour éviter la création des deux comptes
        email = str(email).lower()  # recupérer l'email en miniscule pour éviter la création des deux comptes
        users = request.env["res.users"].sudo().search([("login", "=", email)])
        if users:
            for user in users:
                subtype_id = request.env.ref("mail.mt_note")
                print("subtypeeeeee:", subtype_id)
                if state and state == "succeed" and subtype_id:
                    message = (
                        request.env["mail.message"]
                        .sudo()
                        .create(
                            {
                                "subject": "Nouvelle inscription evalbox pour %s" % (user.partner_id.name),
                                "model": "res.partner",
                                "res_id": user.partner_id.id,
                                "message_type": "notification",
                                "subtype_id": int(subtype_id),
                                "body": "Compte Evalbox créé ",
                            }
                        )
                    )  # créer une note avec un contenu Compte Evalbox créé
                elif state and state == "null" and subtype_id:
                    message = (
                        request.env["mail.message"]
                        .sudo()
                        .create(
                            {
                                "subject": "Compte Evalbox déjà existant %s" % (user.partner_id.name),
                                "model": "res.partner",
                                "res_id": user.partner_id.id,
                                "message_type": "notification",
                                "subtype_id": int(subtype_id),
                                "body": "Compte Evalbox déjà existant",
                            }
                        )
                    )  # créer une note avec un contenu Compte Evalbox déjà existant
            if state == "succeed":
                return request.render("mcm_website_theme.evalbox_account_created", {})
            elif state == "null":
                return request.render("mcm_website_theme.evalbox_account_existant", {})
            else:
                description = "le statut %s envoyé n'est pas valide pour l'email %s" % (state, email)
                vals = {
                    "description": description,
                    "name": "Statut non validé",
                    "team_id": request.env["helpdesk.team"]
                    .sudo()
                    .search([("name", "like", "IT"), ("company_id", "=", 2)], limit=1)
                    .id,
                }

                ticket = (
                    request.env["helpdesk.ticket"]
                    .sudo()
                    .search([("description", "=", description), ("team_id.name", "like", "IT")])
                )

                if not ticket:
                    new_ticket = (
                        request.env["helpdesk.ticket"].sudo().create(vals)
                    )  # create ticket if the sended state is wrong
                return request.render("mcm_website_theme.evalbox_state_not_valid", {})
        else:
            _logger.info(" le compte utilisateur de %s non trouvé " % (str(email)))
            description = "l'email envoyé %s n'est pas lié à un compte utilisateur" % (email)
            vals = {
                "description": description,
                "name": "Compte utilisateur non trouvé",
                "team_id": request.env["helpdesk.team"]
                .sudo()
                .search([("name", "like", "IT"), ("company_id", "=", 2)], limit=1)
                .id,
            }

            ticket = (
                request.env["helpdesk.ticket"]
                .sudo()
                .search([("description", "=", description), ("team_id.name", "like", "IT")])
            )

            if not ticket:
                new_ticket = (
                    request.env["helpdesk.ticket"].sudo().create(vals)
                )  # create ticket if we don't found user using email
            return request.render("mcm_website_theme.evalbox_account_not_found", {})

    @http.route("/evalbox_registration_error/<string:email>", type="http", auth="public")
    def evalbox_registration_error(self, email=None, **kw):
        email = email.replace("%", ".")  # remplacer % par . dans l'email envoyé en paramètre
        email = email.replace(
            " ", ""
        )  # supprimer les espaces envoyés en paramètre email  pour éviter la création des deux comptes
        email = str(email).lower()  # recupérer l'email en minuscule
        user = request.env["res.users"].sudo().search([("login", "=", email)], limit=1)
        description = (
            "Zoé n'a pas pu créer un compte Evalbox pour %s en raison de l'absence d'un mot de passe contenant les critères requis ou d'une autre raison. merci de contacter le client afin de l'accompagner dans la création de son compte. "
            % (str(user.name) if user else str(email))
        )
        name = "Evalbox : Erreur lors de la création du compte de %s" % (str(user.name) if user else str(email))
        vals = {
            "partner_email": "",
            "partner_id": False,
            "description": description,
            "name": name,
            "team_id": request.env["helpdesk.team"]
            .sudo()
            .search([("name", "like", _("Examen")), ("company_id", "=", 1)], limit=1)
            .id,
        }
        ticket = (
            request.env["helpdesk.ticket"]
            .sudo()
            .search(["|", ("description", "ilike", description), ("name", "=", name)])
        )  # search for ticket with same description or same name already created
        if not ticket:  # create new ticket if we didn't find a ticket already created
            new_ticket = request.env["helpdesk.ticket"].sudo().create(vals)
            return request.render("mcm_website_theme.evalbox_ticket_created", {})
        else:
            return request.render("mcm_website_theme.evalbox_ticket_exist", {})


class WebsiteSale(WebsiteSale):
    def sitemap_shop(env, rule, qs):
        if not qs or qs.lower() in "/shop":
            yield {"loc": "/shop"}

        Category = env["product.public.category"]
        dom = sitemap_qs2dom(qs, "/shop/category", Category._rec_name)
        dom += env["website"].get_current_website().website_domain()
        for cat in Category.sudo().search(dom):
            loc = "/shop/category/%s" % slug(cat)
            if not qs or qs.lower() in loc:
                yield {"loc": loc}

    @http.route(
        [
            """/shop""",
            """/shop/page/<int:page>""",
            """/shop/category/<model("product.public.category"):category>""",
            """/shop/category/<model("product.public.category"):category>/page/<int:page>""",
        ],
        type="http",
        auth="public",
        website=True,
        sitemap=False,
    )
    def shop(
        self,
        page=0,
        category=None,
        state="",
        taxi_state="",
        vmdtr_state="",
        vtc_state="",
        search="",
        ppg=False,
        **post,
    ):
        if 'product.public.category' not in str(type(category)):
            return werkzeug.utils.redirect("/#pricing", 301)
        if category and category.website_id and category.website_id.id == 1:
            if any(taxi in category.name for taxi in ["TAXI", "Taxi", "taxi"]):
                return werkzeug.utils.redirect("/formation-taxi#pricing", 301)
            elif any(vtc in category.name for vtc in ["VTC", "Vtc", "vtc"]):
                return werkzeug.utils.redirect("/formation-vtc#pricing", 301)
            elif any(vmdtr in category.name for vmdtr in ["VMDTR", "Vmdtr", "vmdtr"]):
                return werkzeug.utils.redirect("/formation-moto-taxi#pricing", 301)
            else:
                return werkzeug.utils.redirect("/#pricing", 301)
        else:
            return werkzeug.utils.redirect("/#pricing", 301)
        add_qty = int(post.get("add_qty", 1))
        Category = request.env["product.public.category"]
        if category and category != "all":
            category = Category.sudo().search([("id", "=", int(category))], limit=1)
            if not category or not category.can_access_from_current_website():
                raise NotFound()
        else:
            category = Category
        if ppg:
            try:
                ppg = int(ppg)
                post["ppg"] = ppg
            except ValueError:
                ppg = False
        if not ppg:
            ppg = request.env["website"].get_current_website().shop_ppg or 20

        ppr = request.env["website"].get_current_website().shop_ppr or 4

        attrib_list = request.httprequest.args.getlist("attrib")
        attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
        attributes_ids = {v[0] for v in attrib_values}
        attrib_set = {v[1] for v in attrib_values}

        domain = self._get_search_domain(search, category, attrib_values)

        keep = QueryURL(
            "/shop", category=category and int(category), search=search, attrib=attrib_list, order=post.get("order")
        )

        pricelist_context, pricelist = self._get_pricelist_context()

        request.context = dict(request.context, pricelist=pricelist.id, partner=request.env.user.partner_id)

        url = "/shop"
        if search:
            post["search"] = search
        if attrib_list:
            post["attrib"] = attrib_list

        Product = request.env["product.template"].with_context(bin_size=True)

        search_product = Product.sudo().search(domain)
        website_domain = request.website.website_domain()
        categs_domain = [("parent_id", "=", False)] + website_domain
        if search:
            search_categories = (
                Category.sudo()
                .search([("product_tmpl_ids", "in", search_product.ids)] + website_domain)
                .parents_and_self
            )
            categs_domain.append(("id", "in", search_categories.ids))
        else:
            search_categories = Category
        categs = Category.sudo().search(categs_domain)

        if category:
            url = "/shop/category/%s" % slug(category)

        product_count = len(search_product)
        pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
        products = Product.sudo().search(domain, limit=ppg, offset=pager["offset"], order=self._get_search_order(post))
        final_products = []
        if state and state != "all" and category != "all":
            states = (
                request.env["res.country.state"]
                .sudo()
                .search(["&", ("name", "ilike", state), ("country_id.code", "ilike", "FR")])
            )
            for product in products:
                if states:
                    for state in states:
                        sql_query = """ select * from product_template_state_rel where product_template_id=%s and state_id=%s """
                        request.cr.execute(sql_query, (product.id, state.id))
                        result = request.cr.fetchall()
                        if result:
                            final_products.append(product)
            products = final_products

        # get products where category is taxi and search using state
        if taxi_state and taxi_state != "":
            states = (
                request.env["res.country.state"]
                .sudo()
                .search(["&", ("name", "ilike", taxi_state), ("country_id.code", "ilike", "FR")])
            )
            category = request.env["product.public.category"].sudo().search([("code", "ilike", "taxi")], limit=1)
            domain = self._get_search_domain(search, category.id, attrib_values)
            products = Product.sudo().search(
                domain, limit=ppg, offset=pager["offset"], order=self._get_search_order(post)
            )
            for product in products:
                if states:
                    for state in states:
                        sql_query = """ select * from product_template_state_rel where product_template_id=%s and state_id=%s """
                        request.cr.execute(sql_query, (product.id, state.id))
                        result = request.cr.fetchall()
                        if result:
                            final_products.append(product)
            products = final_products

        # get products where category is vmdtr and search using state
        if vmdtr_state and vmdtr_state != "":
            states = (
                request.env["res.country.state"]
                .sudo()
                .search(["&", ("name", "ilike", vmdtr_state), ("country_id.code", "ilike", "FR")])
            )
            category = request.env["product.public.category"].sudo().search([("code", "ilike", "vmdtr")], limit=1)
            domain = self._get_search_domain(search, category.id, attrib_values)
            products = Product.sudo().search(
                domain, limit=ppg, offset=pager["offset"], order=self._get_search_order(post)
            )
            for product in products:
                if states:
                    for state in states:
                        sql_query = """ select * from product_template_state_rel where product_template_id=%s and state_id=%s """
                        request.cr.execute(sql_query, (product.id, state.id))
                        result = request.cr.fetchall()
                        if result:
                            final_products.append(product)
            products = final_products

        # get products where category is vtc and search using state
        if vtc_state and vtc_state != "":
            states = (
                request.env["res.country.state"]
                .sudo()
                .search(["&", ("name", "ilike", vtc_state), ("country_id.code", "ilike", "FR")])
            )
            category = request.env["product.public.category"].sudo().search([("code", "ilike", "vtc")], limit=1)
            domain = self._get_search_domain(search, category.id, attrib_values)
            products = Product.sudo().search(
                domain, limit=ppg, offset=pager["offset"], order=self._get_search_order(post)
            )
            for product in products:
                if states:
                    for state in states:
                        sql_query = """ select * from product_template_state_rel where product_template_id=%s and state_id=%s """
                        request.cr.execute(sql_query, (product.id, state.id))
                        result = request.cr.fetchall()
                        if result:
                            final_products.append(product)
            products = final_products

        # get products where category is vtc

        if state and state != "all" and category == "all":
            states = (
                request.env["res.country.state"]
                .sudo()
                .search(["&", ("name", "ilike", state), ("country_id.code", "ilike", "FR")])
            )

            for product in products:
                if states:
                    for state in states:
                        sql_query = """ select * from product_template_state_rel where state_id=%s """
                        request.cr.execute(sql_query, (state.id))
                        result = request.cr.fetchall()
                        if result:
                            final_products.append(product)
            products = final_products

        ProductAttribute = request.env["product.attribute"]
        if products:
            # get all products without limit
            attributes = ProductAttribute.sudo().search([("product_tmpl_ids", "in", search_product.ids)])
        else:
            attributes = ProductAttribute.browse(attributes_ids)

        layout_mode = request.session.get("website_sale_shop_layout_mode")
        if not layout_mode:
            if request.website.viewref("website_sale.products_list_view").active:
                layout_mode = "list"
            else:
                layout_mode = "grid"

        values = {
            "search": search,
            "category": category,
            "attrib_values": attrib_values,
            "attrib_set": attrib_set,
            "pager": pager,
            "pricelist": pricelist,
            "add_qty": add_qty,
            "products": products,
            "search_count": product_count,  # common for all searchbox
            "bins": TableCompute().process(products, ppg, ppr),
            "ppg": ppg,
            "ppr": ppr,
            "categories": categs,
            "attributes": attributes,
            "keep": keep,
            "search_categories_ids": search_categories.ids,
            "layout_mode": layout_mode,
        }
        if category:
            values["main_object"] = category
        return request.render("website_sale.products", values)

    @http.route("/shop/payment/validate", type="http", auth="public", website=True, sitemap=False)
    def payment_validate(self, transaction_id=None, sale_order_id=None, **post):
        """Method that should be called by the server when receiving an update
        for a transaction. State at this point :

         - UDPATE ME
        """
        if sale_order_id is None:
            order = request.website.sale_get_order()
        else:
            order = request.env["sale.order"].sudo().browse(sale_order_id)
            assert order.id == request.session.get("sale_last_order_id")

        if transaction_id:
            tx = request.env["payment.transaction"].sudo().browse(transaction_id)
            assert tx in order.transaction_ids()
        elif order:
            tx = order.get_portal_last_transaction()
        else:
            tx = None

        if not order or (order.amount_total and not tx):
            return request.redirect("/shop")

        if order and not order.amount_total and not tx:
            order.with_context(send_email=True).action_confirm()
            return request.redirect(order.get_portal_url())

        # clean context and session, then redirect to the confirmation page
        request.website.sale_reset()
        if tx and tx.state == "draft":
            return request.redirect("/shop")
        if tx and tx.state == "done" and tx.amount > 0 and order.state != "sale":
            order.sale_action_sent()
        PaymentProcessing.remove_payment_transaction(tx)
        if order.company_id.id == 1:
            product_id = False
            pricelist = False
            if order:
                for line in order.order_line:
                    product_id = line.product_id
            if tx:
                state = str(tx.state)
                if product_id:
                    slugname = (product_id.name).strip().strip("-").replace(" ", "-").lower()
                    if order.pricelist_id and order.pricelist_id.name in ["bolt"]:
                        return request.redirect(
                            "/%s/%s/shop/confirmation/%s" % (slugname, order.pricelist_id.name, state)
                        )
                    else:
                        return request.redirect("/%s/shop/confirmation/%s" % (slugname, state))
                else:
                    return request.redirect("/shop/confirmation")
            else:
                return request.redirect("/shop/confirmation")
        else:
            product_id = False
            pricelist = False
            if order:
                for line in order.order_line:
                    product_id = line.product_id
            if tx:
                state = str(tx.state)
                if product_id:
                    slugname = (product_id.name).strip().strip("-").replace(" ", "-").lower()
                    if order.pricelist_id and order.pricelist_id.name in [
                        "ubereats",
                        "deliveroo",
                        "coursierjob",
                        "box2home",
                    ]:
                        return request.redirect(
                            "/%s/%s/shop/confirmation/%s" % (slugname, order.pricelist_id.name, state)
                        )
                    else:
                        return request.redirect("/%s/shop/confirmation/%s" % (slugname, state))
                else:
                    return request.redirect("/shop/confirmation")
            else:
                return request.redirect("/shop/confirmation")

    @http.route(
        [
            """/<string:product>/<string:partenaire>/shop/address""",
            """/<string:product>/shop/address""",
            """/shop/address""",
        ],
        type="http",
        methods=["GET", "POST"],
        auth="user",
        website=True,
        sitemap=False,
    )
    def address(self, partenaire=None, product=None, **kw):
        return request.redirect("/shop/payment")
        Partner = request.env["res.partner"].with_context(show_address=1).sudo()
        if request.website.id == 1:
            return request.redirect("/edit_info")
        order = request.website.sale_get_order()
        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        mode = (False, False)
        can_edit_vat = False
        def_country_id = order.partner_id.country_id
        values, errors = {}, {}

        partner_id = int(kw.get("partner_id", -1))
        partner = Partner.browse(partner_id)

        # IF PUBLIC ORDER
        if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
            mode = ("new", "billing")
            can_edit_vat = True
            country_code = request.session["geoip"].get("country_code")
            if country_code:
                def_country_id = request.env["res.country"].search([("code", "=", country_code)], limit=1)
            else:
                def_country_id = request.website.user_id.sudo().country_id
        # IF ORDER LINKED TO A PARTNER
        else:
            if partner_id > 0:
                if partner_id == order.partner_id.id:
                    mode = ("edit", "billing")
                    can_edit_vat = order.partner_id.can_edit_vat()
                else:
                    shippings = Partner.search([("id", "child_of", order.partner_id.commercial_partner_id.ids)])
                    if partner_id in shippings.mapped("id"):
                        mode = ("edit", "shipping")
                    else:
                        return Forbidden()
                if mode:
                    values = Partner.browse(partner_id)
            elif partner_id == -1:
                mode = ("new", "shipping")
            else:  # no mode - refresh without post?
                return request.redirect("/shop/checkout")

        # IF POSTED
        if "submitted" in kw:
            partner.addresse_facturation = str(kw.get("adresse_facturation")) if kw.get("adresse_facturation") else ""
            partner.numero_permis = str(kw.get("numero_permis")) if kw.get("numero_permis") else ""
            partner.siret = str(kw.get("siret")) if kw.get("siret") else ""
            pre_values = self.values_preprocess(order, mode, kw)
            errors, error_msg = self.checkout_form_validate(mode, kw, pre_values)
            post, errors, error_msg = self.values_postprocess(order, mode, pre_values, errors, error_msg)
            if errors:
                errors["error_message"] = error_msg
                values = kw
            else:
                partner_id = self._checkout_form_save(mode, post, kw)
                if kw.get("adresse_facturation") and kw.get("adresse_facturation") == "societe":
                    if not partner.parent_id:
                        company = Partner.sudo().create(
                            {
                                "name": kw.get("company_name"),
                                "siret": kw.get("siret"),
                                "company_type": "company",
                                "phone": partner.phone,
                                "street": partner.street,
                            }
                        )
                        partner.parent_id = company.id
                if mode[1] == "billing":
                    order.partner_id = partner_id
                    order.onchange_partner_id()
                    # This is the *only* thing that the front end user will see/edit anyway when choosing billing address
                    order.partner_invoice_id = partner_id
                    if not kw.get("use_same"):
                        kw["callback"] = kw.get("callback") or (
                            not order.only_services and (mode[0] == "edit" and "/shop/checkout" or "/shop/address")
                        )
                elif mode[1] == "shipping":
                    order.partner_shipping_id = partner_id

                order.message_partner_ids = [(4, partner_id), (3, request.website.partner_id.id)]
                if not errors:
                    return request.redirect(kw.get("callback") or "/shop/confirm_order")

        country = (
            "country_id" in values
            and values["country_id"] != ""
            and request.env["res.country"].browse(int(values["country_id"]))
        )
        country = country and country.exists() or def_country_id
        fr_country = request.env["res.country"].sudo().search([("code", "ilike", "FR")], limit=1)
        if partner:
            values["addresse_facturation"] = order.partner_id.addresse_facturation
            values["siret"] = order.partner_id.siret
            values["name"] = order.partner_id.name
            values["phone"] = order.partner_id.phone
        render_values = {
            "website_sale_order": order,
            "partner_id": partner_id,
            "mode": mode,
            "checkout": values,
            "fact": order.partner_id.addresse_facturation,
            "can_edit_vat": can_edit_vat,
            "country": country,
            "fr_country": fr_country,
            "countries": country.get_website_sale_countries(mode=mode[1]),
            "states": country.get_website_sale_states(mode=mode[1]),
            "error": errors,
            "callback": kw.get("callback"),
            "only_services": order and order.only_services,
        }
        return request.render("website_sale.address", render_values)

    def checkout_form_validate(self, mode, all_form_values, data):
        # mode: tuple ('new|edit', 'billing|shipping')
        # all_form_values: all values before preprocess
        # data: values after preprocess
        error = dict()
        error_message = []

        # Required fields from form
        required_fields = [f for f in (all_form_values.get("field_required") or "").split(",") if f]
        # Required fields from mandatory field function
        required_fields += (
            mode[1] == "shipping" and self._get_mandatory_shipping_fields() or self._get_mandatory_billing_fields()
        )
        # Check if state required
        country = request.env["res.country"]
        if data.get("country_id"):
            country = country.browse(int(data.get("country_id")))
            if "state_code" in country.get_address_fields() and country.state_ids:
                required_fields += ["state_id"]

        # error message for empty required fields
        for field_name in required_fields:
            if not data.get(field_name):
                error[field_name] = "missing"

        if not data.get("numero_permis") and request.website.id == 1:
            error["numero_permis"] = "error"
            error_message.append(_("Numéro de permis doit être rempli"))
        if not data.get("adresse_facturation"):
            error["adresse_facturation"] = "error"
            error_message.append(_("l'Adresse de facturation doit être rempli"))
        if "adresse_facturation" in data:
            if str(data["adresse_facturation"]) == "societe":
                if not data.get("company_name"):
                    error["company_name"] = "error"
                    error_message.append(_("Nom de la société doit être rempli"))
                if not data.get("siret"):
                    error["siret"] = "error"
                    error_message.append(_("Numéro Siret doit être rempli"))

        # email validation
        if data.get("email") and not tools.single_email_re.match(data.get("email")):
            error["email"] = "error"
            error_message.append(_("Invalid Email! Please enter a valid email address."))
        # vat validation
        Partner = request.env["res.partner"]
        # if data.get("vat") and hasattr(Partner, "check_vat"):
        #     if data.get("country_id"):
        #         data["vat"] = Partner.fix_eu_vat_number(data.get("country_id"), data.get("vat"))
        #     partner_dummy = Partner.new({
        #         'vat': data['vat'],
        #         'country_id': (int(data['country_id'])
        #                        if data.get('country_id') else False),
        #     })
        #     try:
        #         partner_dummy.check_vat()
        #     except ValidationError:
        #         error["vat"] = 'error'

        if [err for err in error.values() if err == "missing"]:
            error_message.append(_("Some required fields are empty."))

        return error, error_message

    @http.route(['/shop/product/<model("product.template"):product>'], type="http", auth="public", website=True)
    def product(self, product, category="", search="", **kwargs):
        res = super(WebsiteSale, self).product(product, category, search)
        if product and product.website_id and product.website_id.id == 1:
            if product.default_code == "vtc_bolt":
                return werkzeug.utils.redirect("/bolt#pricing", 301)
            elif any(taxi in product.name for taxi in ["TAXI", "Taxi", "taxi"]):
                return werkzeug.utils.redirect("/formation-taxi#pricing", 301)
            elif any(vtc in product.name for vtc in ["VTC", "Vtc", "vtc"]):
                return werkzeug.utils.redirect("/formation-vtc#pricing", 301)
            elif any(vmdtr in product.name for vmdtr in ["VMDTR", "Vmdtr", "vmdtr"]):
                return werkzeug.utils.redirect("/formation-moto-taxi#pricing", 301)
            else:
                return werkzeug.utils.redirect("/#pricing", 301)
        elif product and product.website_id and product.website_id.id == 2:
            if product.default_code == "examen":
                return werkzeug.utils.redirect("/examen-capacite-transport-marchandises#nouvelle-tentative", 301)
            elif product.default_code == "habilitation-electrique":
                return werkzeug.utils.redirect("/habilitation-electrique#pricing", 301)
            elif product.default_code == "transport-routier":
                return werkzeug.utils.redirect("/formation-capacite-transport-lourd-marchandise#pricing", 301)
            else:
                return werkzeug.utils.redirect("/#pricing", 301)
        return res


class Payment3x(http.Controller):
    @http.route(["/shop/payment/update_amount"], type="json", auth="public", methods=["POST"], website=True)
    def cart_update_amount(self, instalment):
        """This route is called when changing quantity from the cart or adding
        a product from the wishlist."""
        order = request.website.sale_get_order(force_create=1)
        payment = (
            request.env["payment.acquirer"]
            .sudo()
            .search([("name", "ilike", "stripe"), ("company_id", "=", request.website.company_id.id)])
        )
        if instalment:
            if payment:
                order.instalment = True
                payment.instalment = True
                if order.company_id.id == 2 and order.pricelist_id.name == "ubereats":
                    for line in order.order_line:
                        if line.product_id.default_code == "access":
                            order.amount_total = 450
                            line.price_unit = 450
        else:
            payment.instalment = False
            order.instalment = False
            if order.company_id.id == 2 and order.pricelist_id.name == "ubereats":
                for line in order.order_line:
                    if line.product_id.default_code == "access":
                        order.amount_total = 380
                        line.price_unit = 380
        return True

    @http.route(["/shop/payment/update_cpf"], type="json", auth="public", methods=["POST"], website=True, csrf=False)
    def cart_update_cpf(self, cpf):
        order = request.website.sale_get_order(force_create=1)
        if cpf and order.partner_id.statut != "won":
            # order.partner_id.date_cpf = datetime.now()
            order.partner_id.mode_de_financement = "cpf"
            # order.partner_id.statut_cpf = 'untreated'
            # Si mode de financement est cpf, le champ pole emploi sur fiche client sera décoché
            order.partner_id.is_pole_emploi = False
        return True

    """Route est appelé quand Pole emploi dans panier est coché """

    @http.route(
        ["/shop/cart/update_pole_emploi"], type="json", auth="public", methods=["POST"], website=True, csrf=False
    )
    def cart_update_pole_emploi(self, pole_emploi_state):
        order = request.website.sale_get_order(force_create=1)
        print("order:", order, "pole_emploi_state:", pole_emploi_state)
        if pole_emploi_state and order.partner_id.statut != "won":
            # order.partner_id.date_cpf = datetime.now()
            order.partner_id.mode_de_financement = "cpf"
            # Si mode de financement est pole emploi, le champ pole emploi sur fiche client sera coché
            order.partner_id.is_pole_emploi = pole_emploi_state
        return pole_emploi_state

    @http.route(
        ["/shop/payment/update_cartebleu"], type="json", auth="public", methods=["POST"], website=True, csrf=False
    )
    def cart_update_cartebleu(self, cartebleu):
        order = request.website.sale_get_order(force_create=1)
        if cartebleu and order.partner_id.statut != "won":
            order.partner_id.mode_de_financement = "particulier"
            order.partner_id.is_pole_emploi = False
        return True


class Conditions(http.Controller):
    @http.route(["/shop/payment/update_condition"], type="json", auth="public", methods=["POST"], website=True)
    def cart_update_condition(self, condition):
        """This route is called when changing conditions in shop cart"""
        print("POST request @ /shop/payment/update_condition")
        order = request.website.sale_get_order(force_create=0)
        if order:
            if condition:
                order.conditions = True
            else:
                order.conditions = False
        return True

    @http.route(["/shop/payment/update_failures"], type="json", auth="public", methods=["POST"], website=True)
    def cart_update_failures(self, failures):
        """This route is called when changing failures in shop cart."""
        print(failures)

        order = request.website.sale_get_order(force_create=0)
        print(order)
        if order:
            if failures:
                order.failures = True
                order.partner_id.renounce_request = True
            else:
                order.failures = False
                order.partner_id.renounce_request = False
        return True

    @http.route(
        ["/shop/payment/update_failures_not_signed"], type="json", auth="public", methods=["POST"], website=True
    )
    def cart_update_failures_not_signed(self, failures, token):
        """This route is called when changing failures in contract not signed."""
        order = request.env["sale.order"].sudo().search([("access_token", "=", str(token))], limit=1)
        print("/shop/payment/update_failures_not_signed", failures, token, order)
        if order:
            if failures:
                order.failures = True
                order.partner_id.renounce_request = True
            else:
                order.failures = False
                order.partner_id.renounce_request = False
        return (token, failures)

    @http.route(["/shop/update_driver_licence"], type="json", auth="public", methods=["POST"], website=True)
    def cart_update_driver_licence(self, driver_licence):
        """This route is called when changing driver_licence in shop cart."""
        order = request.website.sale_get_order(force_create=0)
        if order:
            if order.order_line:
                for line in order.order_line:
                    if line.product_id.default_code == "vtc_bolt":
                        if driver_licence:
                            order.partner_id.driver_licence = True
                        else:
                            order.partner_id.driver_licence = False
        return True

    @http.route(["/shop/update_license_suspension"], type="json", auth="public", methods=["POST"], website=True)
    def cart_update_license_suspension(self, license_suspension):
        """This route is called when changing license_suspension in shop cart."""
        order = request.website.sale_get_order(force_create=0)
        if order:
            if order.order_line:
                for line in order.order_line:
                    if line.product_id.default_code == "vtc_bolt":
                        if license_suspension:
                            order.partner_id.license_suspension = True
                        else:
                            order.partner_id.license_suspension = False
        return True

    @http.route(["/shop/update_criminal_record"], type="json", auth="public", methods=["POST"], website=True)
    def cart_update_criminal_record(self, criminal_record):
        """This route is called when changing criminal_record in shop cart."""
        order = request.website.sale_get_order(force_create=0)
        if order:
            if order.order_line:
                for line in order.order_line:
                    if line.product_id.default_code == "vtc_bolt":
                        if criminal_record:
                            order.partner_id.criminal_record = True
                        else:
                            order.partner_id.criminal_record = False
        return True

    @http.route(["/shop/payment/update_accompagnement"], type="json", auth="public", methods=["POST"], website=True)
    def cart_update_accompagnement(self, accompagnement):
        """This route is called when changing quantity from the cart or adding
        a product from the wishlist."""
        order = request.website.sale_get_order(force_create=0)
        if order:
            if accompagnement:
                order.accompagnement = True
            else:
                order.accompagnement = False
        return True


class CustomerPortal(CustomerPortal):
    """
    @override function 'portal_my_tasks' to add domain
    'users_tasks_domain' to restrict users to display tasks
    assigned to them.
    """

    # @http.route(['/my/tasks', '/my/tasks/page/<int:page>'], type='http', auth="user", website=True)
    # def portal_my_tasks(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None,
    #                     search_in='content', groupby='project', **kw):
    #     values = self._prepare_portal_layout_values()
    #     searchbar_sortings = {
    #         'date': {'label': _('Newest'), 'order': 'create_date desc'},
    #         'name': {'label': _('Title'), 'order': 'name'},
    #         'stage': {'label': _('Stage'), 'order': 'stage_id'},
    #         'update': {'label': _('Last Stage Update'), 'order': 'date_last_stage_update desc'},
    #     }
    #     searchbar_filters = {
    #         'all': {'label': _('All'), 'domain': []},
    #     }
    #     searchbar_inputs = {
    #         'content': {'input': 'content', 'label': _('Search <span class="nolabel"> (in Content)</span>')},
    #         'message': {'input': 'message', 'label': _('Search in Messages')},
    #         'customer': {'input': 'customer', 'label': _('Search in Customer')},
    #         'stage': {'input': 'stage', 'label': _('Search in Stages')},
    #         'all': {'input': 'all', 'label': _('Search in All')},
    #     }
    #     searchbar_groupby = {
    #         'none': {'input': 'none', 'label': _('None')},
    #         'project': {'input': 'project', 'label': _('Project')},
    #     }
    #
    #     # extends filterby criteria with project the customer has access to
    #     projects = request.env['project.project'].search([])
    #     print(projects)
    #     for project in projects:
    #         searchbar_filters.update({
    #             str(project.id): {'label': project.name, 'domain': [('project_id', '=', project.id)]}
    #         })
    #
    #     # extends filterby criteria with project (criteria name is the project id)
    #     # Note: portal users can't view projects they don't follow
    #     project_groups = request.env['project.task'].read_group([('project_id', 'not in', projects.ids)],
    #                                                             ['project_id'], ['project_id'])
    #     for group in project_groups:
    #         proj_id = group['project_id'][0] if group['project_id'] else False
    #         proj_name = group['project_id'][1] if group['project_id'] else _(
    #             'Others')
    #         searchbar_filters.update({
    #             str(proj_id): {'label': proj_name, 'domain': [('project_id', '=', proj_id)]}
    #         })
    #
    #     # default sort by value
    #     if not sortby:
    #         sortby = 'date'
    #     order = searchbar_sortings[sortby]['order']
    #     # default filter by value
    #     if not filterby:
    #         filterby = 'all'
    #     domain = searchbar_filters[filterby]['domain']
    #
    #     # archive groups - Default Group By 'create_date'
    #     archive_groups = self._get_archive_groups('project.task', domain)
    #     if date_begin and date_end:
    #         domain += [('create_date', '>', date_begin),
    #                    ('create_date', '<=', date_end)]
    #
    #     # search
    #     if search and search_in:
    #         search_domain = []
    #         if search_in in ('content', 'all'):
    #             search_domain = OR(
    #                 [search_domain, ['|', ('name', 'ilike', search), ('description', 'ilike', search)]])
    #         if search_in in ('customer', 'all'):
    #             search_domain = OR(
    #                 [search_domain, [('partner_id', 'ilike', search)]])
    #         if search_in in ('message', 'all'):
    #             search_domain = OR(
    #                 [search_domain, [('message_ids.body', 'ilike', search)]])
    #         if search_in in ('stage', 'all'):
    #             search_domain = OR(
    #                 [search_domain, [('stage_id', 'ilike', search)]])
    #         domain += search_domain
    #
    #     # Display tasks of active user
    #     users = request.env.user
    #     users_tasks_domain = [
    #         '|', ('parent_id.user_id', '=', users.id), ('user_id', '=', users.id)]
    #     # task count
    #     task_count = request.env['project.task'].search_count(
    #         users_tasks_domain)
    #     # pager
    #     pager = portal_pager(
    #         url="/my/tasks",
    #         url_args={'date_begin': date_begin},
    #         total=task_count,
    #         page=page,
    #         step=self._items_per_page
    #     )
    #     # content according to pager and archive selected
    #     if groupby == 'project_id':
    #         # force sort on project first to group by project in view
    #         order = "project_id, %s" % order
    #     tasks = request.env['project.task'].search(users_tasks_domain, order=order, limit=self._items_per_page,
    #                                                offset=(page - 1) * self._items_per_page)
    #     request.session['my_tasks_history'] = tasks.ids[:100]
    #     if groupby == 'project':
    #         grouped_tasks = [request.env['project.task'].concat(*g) for k, g in
    #                          groupbyelem(tasks, itemgetter('project_id'))]
    #     else:
    #         grouped_tasks = [tasks]
    #     values.update({
    #         'date': date_begin,
    #         'date_end': date_end,
    #         'grouped_tasks': grouped_tasks,
    #         'page_name': 'task',
    #         'archive_groups': archive_groups,
    #         'default_url': '/my/tasks',
    #         'pager': pager,
    #         'searchbar_sortings': [],
    #         'searchbar_groupby': [],
    #         'searchbar_inputs': searchbar_inputs,
    #         'search_in': search_in,
    #         'sortby': False,
    #         'groupby': False,
    #         'searchbar_filters': False,
    #         'filterby': False,
    #     })
    #     return request.render("project.portal_my_tasks", values)

    # @override Function to Add Filter to invoice_count in portal invoice view
    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        invoice_count = request.env["account.move"].search_count(
            [
                ("type", "in", ("out_invoice", "in_invoice", "out_refund", "in_refund", "out_receipt", "in_receipt")),
                ("type_facture", "=", "web"),
            ]
        )
        values["invoice_count"] = invoice_count
        # add users_tasks_domain to filter tasks in portal view
        users = request.env.user
        return values

    # @override Second Function to Add Filter to invoice_count in portal invoice view
    def _prepare_home_portal_values(self):
        values = super(CustomerPortal, self)._prepare_home_portal_values()
        invoice_count = (
            request.env["account.move"].search_count(
                [
                    (
                        "type",
                        "in",
                        ("out_invoice", "in_invoice", "out_refund", "in_refund", "out_receipt", "in_receipt"),
                    ),
                    ("type_facture", "=", "web"),
                ]
            )
            if request.env["account.move"].check_access_rights("read", raise_exception=False)
            else 0
        )
        values["invoice_count"] = invoice_count
        # add users_tasks_domain to filter tasks in portal view
        users = request.env.user
        # users_tasks_domain = [
        #     '|', ('parent_id.user_id', '=', users.id), ('user_id', '=', users.id)]
        # values['task_count'] = request.env['project.task'].search_count(
        #     users_tasks_domain)
        return values

    """@override this function to add filter can display 
    all invoices Not CPF type linked to specific portal"""

    @http.route(["/my/invoices", "/my/invoices/page/<int:page>"], type="http", auth="user", website=True)
    def portal_my_invoices(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        AccountInvoice = request.env["account.move"]

        domain = [
            ("type", "in", ("out_invoice", "out_refund", "in_invoice", "in_refund", "out_receipt", "in_receipt")),
            ("type_facture", "=", "web"),
        ]

        searchbar_sortings = {
            "date": {"label": _("Invoice Date"), "order": "invoice_date desc"},
            "duedate": {"label": _("Due Date"), "order": "invoice_date_due desc"},
            "name": {"label": _("Reference"), "order": "name desc"},
            "state": {"label": _("Status"), "order": "state"},
        }
        # default sort by order
        if not sortby:
            sortby = "date"
        order = searchbar_sortings[sortby]["order"]

        archive_groups = self._get_archive_groups("account.move", domain)
        if date_begin and date_end:
            domain += [("create_date", ">", date_begin), ("create_date", "<=", date_end)]

        # count for pager
        invoice_count = AccountInvoice.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/invoices",
            url_args={"date_begin": date_begin, "date_end": date_end, "sortby": sortby},
            total=invoice_count,
            page=page,
            step=self._items_per_page,
        )
        # content according to pager and archive selected

        """ Add filter to client view to display all invoices 
        contains type WEB also the cpf_solde_invoice, cpf_acompte_invoice
        should be not ckecked using lambda """

        invoices = AccountInvoice.search(
            domain, order=order, limit=self._items_per_page, offset=pager["offset"]
        ).filtered(lambda facture: facture.type_facture == "web")
        request.session["my_invoices_history"] = invoices.ids[:100]
        values.update(
            {
                "date": date_begin,
                "invoices": invoices,
                "page_name": "invoice",
                "pager": pager,
                "archive_groups": archive_groups,
                "default_url": "/my/invoices",
                "searchbar_sortings": searchbar_sortings,
                "sortby": sortby,
            }
        )
        return request.render("account.portal_my_invoices", values)


# class MCMFORMATION(http.Controller):

#     # @http.route('/formation-theorique-et-pratique-vtc', type='http', auth='public', website=True)
#     # def formvtc(self, **kw, ):
#     #     if request.website.id == 2:
#     #         return 0
#     #     elif request.website.id == 1:
#     #         return request.render("mcm_website_theme.mcm_website_formation_vtc")

#     @http.route('/formation-moto-taxi', type='http', auth='public', website=True)
#     def formvmdtr(self, **kw, ):

#         #Si site Digimoov, ne renvoie rien
#         if request.website.id == 2:
#             return 0
#         elif request.website.id == 1:
#             return request.render("mcm_website_theme.mcm_website_theme_vmdtr")


class MCM_SIGNUP(http.Controller):
    @http.route("/sign_up", type="http", auth="public", website=True)
    def formvtc(
        self,
        **kw,
    ):
        if request.website.id == 2:
            return 0
        elif request.website.id == 1:
            return request.render("mcm_website_theme.mcm_website_register_form")


class MCM_SIGNUP(http.Controller):
    @http.route("/sign_up", type="http", auth="public", website=True)
    def formvtc(
        self,
        **kw,
    ):
        if request.website.id == 2:
            return 0
        elif request.website.id == 1:
            return request.render("mcm_website_theme.mcm_website_register_form")

    """Récupérer le paiement de stripe en cas de succès"""

    @http.route(["/webhook_testing"], type="json", auth="public", methods=["POST"])
    def stripe_event(self):
        event = None
        request.uid = odoo.SUPERUSER_ID
        dataa = json.loads(request.httprequest.data)
        _logger.info("webhoooooooooook %s" % str(dataa))
        event = dataa.get("type")
        object = dataa.get("data", []).get("object")
        _logger.info("event : %s" % str(event))
        charges = False
        if event == "payment_intent.payment_failed": #check if the event sended from webhook is payment_intent.payment_failed
            failure_message = False
            if object and 'charges' in object: #check if charges in response
                charges = object['charges']
            if charges:
                datas = charges['data'] #check if data in charges of response
                if datas:
                    for data in datas:
                        if 'failure_message' in data: # get failure message of payment
                            _logger.info("failure_message : %s" % str(data['failure_message']))
                            failure_message = str(data['failure_message'])
            amount = int(object["amount"] / 100)
            receipt_email = object["receipt_email"]
            user = request.env['res.users'].sudo().search(
                [('login', "=", str(receipt_email).replace(' ', '').lower())])
            _logger.info("receipt_email : %s" % str(receipt_email))
            _logger.info("user : %s" % str(user))
            subtype_id = request.env['ir.model.data'].xmlid_to_res_id('mail.mt_note')
            if not subtype_id:
                subtype_id = request.env.ref('mail.mt_note')
            _logger.info("subtype_id : %s" % str(subtype_id))
            if user:
                message = request.env['mail.message'].sudo().create({ #create note in client record contains payment failure message
                    'subject': 'Échec de paiement',
                    'model': 'res.partner',
                    'res_id': user.partner_id.id,
                    'message_type': 'notification',
                    'subtype_id': subtype_id,
                    'body': 'Échec de réalisation de la tentative de paiement de %s € : %s' % (str(amount),
                                                                                               failure_message) if failure_message else 'Échec de réalisation de la tentative de paiement de %s € : %s' % (
                        str(amount)),
                })
            _logger.info("message : %s" % str(message))
            return True
        if event == "invoice.payment_failed": #check if the event sended from webhook is invoice.payment_failed
            receipt_email = object["customer_email"]
            user = request.env['res.users'].sudo().search(
                [('login', "=", str(receipt_email).replace(' ', '').lower())])
            lines = False
            prod_id = False
            product = False
            amount = False
            if object and 'lines' in object: #check if object in response contains lines
                lines = object['lines']
            if lines:
                datas = lines['data'] # get data from lines of response object
                if datas:
                    for data in datas:
                        if 'amount' in data:
                            amount = int(data["amount"] / 100) # get amount of payment
                        if 'plan' in data:
                            _logger.info("plan : %s" % str(data['plan'])) #get plan from response
                            plan = data['plan']
                            if plan and 'product' in plan: #get stripe product_id
                                prod_id = plan['product']
            _logger.info("prod_id : %s" % str(prod_id))
            _logger.info("amount : %s" % str(amount))
            if prod_id:
                product = request.env['product.template'].sudo().search(
                    [('id_stripe', "=", str(prod_id).replace(' ', ''))]) #search product in odoo with same stripe product_id
            subtype_id = request.env['ir.model.data'].xmlid_to_res_id('mail.mt_note')
            if not subtype_id:
                subtype_id = request.env.ref('mail.mt_note')
            _logger.info("subtype_id : %s" % str(subtype_id))
            _logger.info("product : %s" % str(product))
            if user:
                message = request.env['mail.message'].sudo().create({#create note in client record contains invoice failure message
                    'subject': 'Échec de paiement',
                    'model': 'res.partner',
                    'res_id': user.partner_id.id,
                    'message_type': 'notification',
                    'subtype_id': subtype_id,
                    'body': "Échec du paiement d'une facture de %s € relatif à la formation : %s" % (str(amount),
                                                                                                     str(product.name)) if amount and product else "Échec du paiement d'une facture de %s €" % (
                        str(amount)),
                })
            _logger.info("message : %s" % str(message))
            return True
        if event == "charge.succeeded": #check if the event sended from webhook is charge.succeeded
            receipt_email = object["receipt_email"]  #get receipt_email
            amount = int(object["amount"] / 100)
            user = request.env['res.users'].sudo().search(
                [('login', "=", str(receipt_email).replace(' ', '').lower())])
            _logger.info("receipt_email : %s" % str(receipt_email))
            _logger.info("user : %s" % str(user))
            subtype_id = request.env['ir.model.data'].xmlid_to_res_id('mail.mt_note')
            if not subtype_id:
                subtype_id = request.env.ref('mail.mt_note')
            _logger.info("subtype_id : %s" % str(subtype_id))
            if user:
                message = request.env['mail.message'].sudo().create({ #create note in client record contains amount charge succeeded
                    'subject': 'Montant débité',
                    'model': 'res.partner',
                    'res_id': user.partner_id.id,
                    'message_type': 'notification',
                    'subtype_id': subtype_id,
                    'body': 'Un montant de %s € a été débité' % (str(amount)),
                })
                _logger.info("message : %s" % str(message))
            return True
        if event == "customer.subscription.created": #check if the event sended from webhook is customer.subscription.created
            customer_id = object["customer"] if 'customer' in object else False #get stripe customer_id from webhook
            product = False
            prod_id = False
            items = object['items'] #get items from response webhook
            acquirer = False
            email = False
            user = False
            items = False
            if object and 'items' in object:
                items = object['items']
            if items:
                datas = items['data']
                if datas:
                    for data in datas:
                        plan = data['plan'] #get plan from items of response
                        _logger.info("plan : %s" % str(plan))
                        if plan and 'product' in plan:
                            prod_id = plan['product'] #get stripe product_id from response
            _logger.info("prod_id : %s" % str(prod_id))
            if prod_id:
                product = request.env['product.template'].sudo().search(
                    [('id_stripe', "=", str(prod_id).replace(' ', ''))]) #search product in odoo using stripe_product_id
            _logger.info("product : %s" % str(product))
            acquirer = request.env["payment.acquirer"].sudo().search(
                [("name", "ilike", 'Stripe'), ("company_id", "=", 2)], limit=1)
            _logger.info("acquirer : %s" % str(acquirer))
            if customer_id and acquirer:
                response = requests.get('https://api.stripe.com/v1/customers/%s' % (str(customer_id)),
                                        auth=(str(acquirer.stripe_secret_key), '')) #using stripe api search customer email using stripe customer id
                json_data = json.loads(response.text)
                _logger.info("json_data : %s" % (json_data))
                if 'email' in json_data:
                    email = json_data['email']
            _logger.info("email : %s" % str(email))
            if email:
                user = request.env['res.users'].sudo().search(
                    [('login', "=", str(email).replace(' ', '').lower())])
            _logger.info("user : %s" % str(user))
            if user and product:
                subtype_id = request.env['ir.model.data'].xmlid_to_res_id('mail.mt_note')
                if not subtype_id:
                    subtype_id = request.env.ref('mail.mt_note')
                _logger.info("subtype_id : %s" % str(subtype_id))
                if user:
                    message = request.env['mail.message'].sudo().create({  #create note in client record contains subscription created info
                        'subject': 'Abonnement créé',
                        'model': 'res.partner',
                        'res_id': user.partner_id.id,
                        'message_type': 'notification',
                        'subtype_id': subtype_id,
                        'body': "Le client vient de s'abonner à la %s" % (str(product.name)),
                    })
                    _logger.info("message : %s" % str(message))
            return True
        if event == "customer.subscription.deleted": #check if the event sended from webhook is customer.subscription.deleted
            customer_id = object["customer"] if 'customer' in object else False
            product = False
            prod_id = False
            items = object['items'] #get items from response webhook
            acquirer = False
            email = False
            user = False
            items = False
            if object and 'items' in object:
                items = object['items']
            if items:
                datas = items['data']
                if datas:
                    for data in datas:
                        plan = data['plan'] #get plan from items of response
                        _logger.info("plan : %s" % str(plan))
                        if plan and 'product' in plan:
                            prod_id = plan['product'] #get stripe product_id from response
            _logger.info("prod_id : %s" % str(prod_id))
            if prod_id:
                product = request.env['product.template'].sudo().search(
                    [('id_stripe', "=", str(prod_id).replace(' ', ''))])  #search product in odoo using stripe_product_id
            _logger.info("product : %s" % str(product))
            acquirer = request.env["payment.acquirer"].sudo().search(
                [("name", "ilike", 'Stripe'), ("company_id", "=", 2)], limit=1)
            _logger.info("acquirer : %s" % str(acquirer))
            if customer_id and acquirer:
                response = requests.get('https://api.stripe.com/v1/customers/%s' % (str(customer_id)),
                                        auth=(str(acquirer.stripe_secret_key), '')) #using stripe api search customer email using stripe customer id
                json_data = json.loads(response.text)
                _logger.info("json_data : %s" % (json_data))
                if 'email' in json_data:
                    email = json_data['email']
            _logger.info("email : %s" % str(email))
            if email:
                user = request.env['res.users'].sudo().search(
                    [('login', "=", str(email).replace(' ', '').lower())])
            _logger.info("user : %s" % str(user))
            if user and product:
                subtype_id = request.env['ir.model.data'].xmlid_to_res_id('mail.mt_note')
                if not subtype_id:
                    subtype_id = request.env.ref('mail.mt_note')
                _logger.info("subtype_id : %s" % str(subtype_id))
                if user:
                    message = request.env['mail.message'].sudo().create({ #create note in client record contains subscription canceled info
                        'subject': 'Abonnement Annulé',
                        'model': 'res.partner',
                        'res_id': user.partner_id.id,
                        'message_type': 'notification',
                        'subtype_id': subtype_id,
                        'body': "L'abonnement relatif à la %s a été annulé" % (str(product.name)),
                    })
                    _logger.info("message : %s" % str(message))
            return True
        if event == "payment_intent.succeeded":
            _logger.info("teeeeeeest %s" % str(object))
            """Cas de paiement une seule fois : créer une facture lié à ce paiement """
            acquirer = object["id"]
            receipt_email = object["receipt_email"]
            invoice_id = object["invoice"]
            description = str(object["description"])
            amount = int(object["amount"] / 100)
            user = request.env['res.users'].sudo().search(
                [('login', "=", str(receipt_email).replace(' ', '').lower())])
            _logger.info("invoice_id : %s" % str(invoice_id))
            _logger.info("description : %s" % str(description))
            _logger.info("receipt_email : %s" % str(receipt_email))
            _logger.info("user : %s" % str(user))
            if user:
                if not (description.startswith('S') and '-' in description):
                    moves = request.env['account.move'].sudo().search(
                        [('stripe_sub_reference', "!=", ''), ('partner_id', '=', user.partner_id.id),
                         ('amount_residual', '>', 0)], limit=1)
                    _logger.info("moves : %s" % str(moves))
                    if moves:
                        for move in moves:
                            acquirer = request.env['payment.acquirer'].sudo().search(
                                [('name', 'ilike', 'Stripe'), ('company_id', "=", move.company_id.id)])
                            _logger.info("acquirer : %s" % str(acquirer))
                            payment_method = request.env["account.payment.method"].sudo().search(
                                [("code", "ilike", "electronic")], limit=1)
                            _logger.info("payment_method : %s" % str(payment_method))
                            check_sale = False
                            sales = request.env['sale.order'].sudo().search([('partner_id', '=', user.partner_id.id)])
                            _logger.info("sales : %s" % str(sales))
                            if sales:
                                for sale in sales:
                                    if int(sale.amount_total) == amount:
                                        check_sale = True
                            _logger.info("check_sale : %s" % str(check_sale))
                            if not check_sale:
                                payment = request.env["account.payment"].sudo().create(
                                    {
                                        "payment_type": "inbound",
                                        "payment_method_id": payment_method.id,
                                        "partner_type": "customer",
                                        "partner_id": move.partner_id.id,
                                        "amount": amount,
                                        "currency_id": move.currency_id.id,
                                        "payment_date": datetime.now(),
                                        "journal_id": acquirer.journal_id.id if acquirer else move.journal_id.id,
                                        "communication": False,
                                        "payment_token_id": False,
                                        "invoice_ids": [(6, 0, move.ids)],
                                    }
                                )
                                _logger.info("payment : %s" % str(payment))
                                payment.post()
            return True

            #     _logger.info("if not invoice")
        if event == "invoice.paid":
            _logger.info("teeeeeeest invoice %s" % str(object))
            subsciption = object.get("subscription")
            customer_email = object["customer_email"]
            if subsciption:
                customer = object.get("customer")
                amount = int(object.get("amount_paid") / 100)
                """Cas de paiement sur plusieur fois : Mettre à jour la facture lié à l'abonnement sur stripe """
                # partner=request.env['res.partner'].sudo().search([('email',"=",receipt_email)],limit=1)
                invoice = request.env["account.move"].sudo().search([("stripe_sub_reference", "=", subsciption),
                                                                     ("partner_id.email", "=", customer_email)], limit=1)
                _logger.info("invoice %s" % str(invoice.name))
                _logger.info("invoice ************* %s" % str(invoice.stripe_sub_reference))
                payment_method = request.env["account.payment.method"].sudo().search([("code", "ilike", "electronic")],
                                                                                     limit=1)
                journal_id = invoice.journal_id.id
                acquirer = False
                if invoice:
                    acquirer = (
                        request.env["payment.acquirer"]
                        .sudo()
                        .search([("name", "ilike", _("Stripe")), ("company_id", "=", invoice.company_id.id)], limit=1)
                    )
                else:
                    acquirer = (
                        request.env["payment.acquirer"]
                        .sudo()
                        .search([("name", "ilike", _("Stripe")), ("company_id", "=", 2)], limit=1)
                    )
                if acquirer:
                    journal_id = acquirer.journal_id.id
                if invoice:
                    payment = (
                        request.env["account.payment"]
                        .sudo()
                        .create(
                            {
                                "payment_type": "inbound",
                                "payment_method_id": payment_method.id,
                                "partner_type": "customer",
                                "partner_id": invoice.partner_id.id,
                                "amount": amount,
                                "currency_id": invoice.currency_id.id,
                                "payment_date": datetime.now(),
                                "journal_id": acquirer.journal_id.id if acquirer else invoice.journal_id.id,
                                "communication": False,
                                "payment_token_id": False,
                                "invoice_ids": [(6, 0, invoice.ids)],
                            }
                        )
                    )

                    payment.post()

                    return True
        return True

    @http.route("/inscription-bolt", type="http", auth="public", website=True)
    def inscription_bolt_jotform(
        self,
        **kw,
    ):
    
        if request.website.id == 1:
            return request.render("mcm_website_theme.mcm_bolt_documents_new_process")
        else:
            raise werkzeug.exceptions.NotFound()

    @http.route("/examen-blanc", type="http", auth="public", website=True)
    def examen_bolt_jotform(
        self,
        **kw,
    ):
        return werkzeug.utils.redirect("/bolt", 301)
        if request.website.id == 1:
            return request.render("mcm_website_theme.mcm_bolt_documents")
        else:
            raise werkzeug.exceptions.NotFound()

    @http.route("/contrat-mcm-bolt", type="http", auth="public", website=True)
    def contrat_bolt_jotform(
        self,
        **kw,
    ):
        if request.website.id == 1:
            return request.render("mcm_website_theme.mcm_bolt_contract")
        else:
            raise werkzeug.exceptions.NotFound()

    @http.route("/get-resetPassword-token", type="http", auth="public", website=True)
    def get_link_of_reset(self, **kw):
        qcontext = request.params.copy()
        _logger.info("qcontext %s" % str(qcontext))
        if not qcontext.get("email"):
            raise werkzeug.exceptions.NotFound()
        else:
            email = qcontext.get("email")
            user_sudo = (
                request.env["res.users"].sudo().search([("login", "=", email.replace(" ", "").lower())], limit=1)
            )
            if user_sudo:
                if user_sudo.login_date:
                    raise werkzeug.exceptions.NotFound()
                else:
                    if user_sudo.signup_url and "reset_password" in user_sudo.signup_url:
                        return werkzeug.utils.redirect(user_sudo.signup_url, 301)
                    else:
                        raise werkzeug.exceptions.NotFound()
            else:
                raise werkzeug.exceptions.NotFound()
        raise werkzeug.exceptions.NotFound()


class AuthSignupHome(AuthSignupHome):

    # generate random password with letters and digits
    def get_random_string(self, length):
        letters = list(string.ascii_letters + string.digits)
        result_str = "".join(random.choice(letters) for i in range(length))
        return result_str

    @http.route(['/webhook_contact_form'], type='http', auth="public", csrf=False)
    def create_contact_from_jotform_webhook(self, **kw):
        _logger.info("webhoook contact jotform %s" % (kw))
        rawRequest = kw['rawRequest']
        _logger.info("rawRequest : %s" % (rawRequest))
        # convert response of webhook to json format
        rawRequest = json.loads(rawRequest)
        _logger.info("rawRequest1 : %s" % (rawRequest))
        firstname = rawRequest['q5_prenom']
        lastName = rawRequest['q6_nom']
        tel = str(rawRequest['q41_numeroDe41'])
        email = str(rawRequest['q7_email']).replace(' ', '').lower()
        street = rawRequest['q25_adresse']
        street2 = rawRequest['q26_complementDadresse']
        city = rawRequest['q27_ville']
        zipcode = str(rawRequest['q29_codePostal'])
        department = str(rawRequest['q38_dansQuel'])
        department_id = request.env['res.country.state'].sudo().search([('code', "=", str(
            department)), ('country_id.code', 'ilike', 'FR')], limit=1)
        _logger.info("department : %s" % (str(department_id)))
        res_user = request.env['res.users']
        odoo_contact = res_user.sudo().search([('login', "=", str(
            email).lower().replace(' ', ''))], limit=1)  # search contact using email
        _logger.info("user founded using email : %s" % (odoo_contact))
        request.uid = odoo.SUPERUSER_ID
        if not odoo_contact:
            odoo_contact = res_user.find_user_with_phone(tel)
            _logger.info("user founded using tel : %s" % (odoo_contact))
        if not odoo_contact:
            _logger.info("user not created using do signup")
            name = str(firstname) + ' ' + str(lastName) if firstname and lastName else False
            odoo_contact = request.env['res.users'].sudo().create({
                'name': name,
                'login': email,
                'groups_id': [(6, 0, [request.env.ref('base.group_portal').id])],
                'email': email,  # set email in create user instead of False
                'phone': tel,
                'notification_type': 'email',
                'step': "financement",
                'website_id': 1,
                'company_ids': [1, 2],
                'company_id': 1,
            })
            odoo_contact.bolt = True
            # odoo_contact.action_reset_password() comment action reset password
            if odoo_contact:
                _logger.info("user created using create user")
                odoo_contact.street = street if street else False
                odoo_contact.zip = zipcode if zipcode else False
                odoo_contact.city = city if city else False
                odoo_contact.firstname = firstname if firstname else False
                odoo_contact.lastName = lastName if lastName else False
                odoo_contact.email = email
                odoo_contact.lang = 'fr_FR'
                odoo_contact.state_id = department_id if department_id else False
        return True

    @http.route(['/contact-examen-blanc'], type='http', auth="public", csrf=False)
    def webhook_integration_examen(self, **kw):
        """ Récuprer et multiplier * 5 la note de l'examen blanc de jotform.
            Afficher la note multiplier sur la fiche client apres une recherche basé sur email"""
        rawRequest = json.loads(kw['rawRequest'])
        _logger.info("rawRequest /contact-examen-blanc: %s" % (str(rawRequest)))
        email = str(rawRequest['q54_email'])
        tel = str(rawRequest['q93_numeroDe93'])
        firstname = rawRequest['q53_nom']['first']
        lastName = rawRequest['q53_nom']['last']
        name = str(firstname) + ' ' + str(lastName)
        street = rawRequest['q115_adresse115']
        street2 = rawRequest['q116_complementDadresse']
        city = rawRequest['q117_ville']
        zipcode = str(rawRequest['q118_codePostal'])
        result = str(rawRequest['q107_resultatExamen'])
        res_user = request.env['res.users']
        if email:
            odoo_contact = res_user.sudo().search([('login', "=", str(
                email).lower().replace(' ', ''))], limit=1)  # search contact using email
            _logger.info("user founded using email : %s" % (odoo_contact))
        else:
            if 'jfFormUserSCL_emailSentTo' in rawRequest :
                email = str(rawRequest['jfFormUserSCL_emailSentTo'])
                odoo_contact = res_user.sudo().search([('login', "=", str(
                    email).lower().replace(' ', ''))], limit=1)  # search contact using email
                _logger.info("user founded using jfFormUserSCL_emailSentTo : %s" % (odoo_contact))
        request.uid = odoo.SUPERUSER_ID
        if not odoo_contact and tel:
            odoo_contact = res_user.find_user_with_phone(tel)
            _logger.info("user founded using tel : %s" % (odoo_contact))
        if odoo_contact and not odoo_contact.login_date:
            odoo_contact.action_reset_password()
            if odoo_contact.phone:
                phone = str(odoo_contact.phone.replace(' ', ''))[
                        -9:]  # change phone to this format to be accepted in sms +33XXXXXXXXX
                phone = '+33' + phone
                # ' ' + phone[0:1] + ' ' + phone[1:3] + ' ' + phone[
                #                                             3:5] + ' ' + phone[
                #                                                          5:7] + ' ' + phone[
                #                                                                       7:]
                odoo_contact.phone = phone
                url = odoo_contact.signup_url
                base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
                # Define base_url according to partner company
                if odoo_contact.company_id.id == 1:
                    base_url = 'https://www.mcm-academy.fr'

                elif odoo_contact.company_id.id == 2:
                    base_url = 'https://www.digimoov.fr'

                link_tracker = request.env['link.tracker'].sudo().search([('url', "=", url)])
                if not link_tracker:
                    # generate short link using module of link tracker
                    link_tracker = request.env['link.tracker'].sudo().create({
                        'title': 'Rénitialisation de mot de passe de %s' % (odoo_contact.name),
                        'url': url,
                    })
                    link_tracker.sudo().write({
                        'short_url': base_url + '/r/%(code)s' % {'code': link_tracker.code}
                        # change the short url of link tracker based on base url
                    })
                if not link_tracker:
                    short_url = pyshorteners.Shortener(api_key=bitly_access_token)  # api key of bitly
                    short_url = short_url.bitly.short(
                        url)
                else:
                    short_url = link_tracker.short_url
                body = 'Chere(e) %s , Vous avez été invité par %s  à compléter votre inscription : %s . Votre courriel de connection est: %s' % (
                    odoo_contact.partner_id.name, odoo_contact.partner_id.company_id.name, short_url,
                    odoo_contact.partner_id.email)  # content of sms
                if body:
                    composer = request.env['sms.composer'].with_context(
                        default_res_model='res.partner',
                        default_res_id=odoo_contact.partner_id.id,
                        default_composition_mode='comment',
                    ).sudo().create({
                        'body': body,
                        'mass_keep_log': True,
                        'mass_force_send': False,
                        'use_active_domain': True,
                        'active_domain': [('id', 'in', odoo_contact.partner_id.ids)]
                    })
                    if (odoo_contact.bolt and odoo_contact.login_date) or (not odoo_contact.bolt):
                        composer = composer.with_user(SUPERUSER_ID)
                        composer._action_send_sms()  # we send sms to client contains link of reset password.
                    if odoo_contact.phone:
                        odoo_contact.phone = '0' + str(odoo_contact.phone.replace(' ', ''))[
                                                   -9:]
        elif odoo_contact and odoo_contact.login_date and not odoo_contact.password_evalbox:
            _logger.info(
                "remplir les champs evalbox : %s %s" % (str(odoo_contact.email), str(odoo_contact.password360)))
            odoo_contact.id_evalbox = odoo_contact.email
            odoo_contact.password_evalbox = odoo_contact.password360

        if not odoo_contact:
            _logger.info("user not created using do signup")
            name = str(firstname) + ' ' + str(lastName) if firstname and lastName else False
            odoo_contact = request.env['res.users'].sudo().create({
                'name': name,
                'login': email,
                'groups_id': [(6, 0, [request.env.ref('base.group_portal').id])],
                'email': email,  # set email in create user instead of False
                'phone': tel,
                'notification_type': 'email',
                'step': "financement",
                'website_id': 1,
                'company_ids': [1, 2],
                'company_id': 1,
            })
            odoo_contact.bolt = True
            # odoo_contact.action_reset_password() comment action reset password
            if odoo_contact:
                _logger.info("user created using create user")
                odoo_contact.street = street if street else False
                odoo_contact.zip = zipcode if zipcode else False
                odoo_contact.city = city if city else False
                odoo_contact.firstname = firstname if firstname else False
                odoo_contact.lastName = lastName if lastName else False
                odoo_contact.email = email
                odoo_contact.lang = 'fr_FR'
        if odoo_contact:
            if 'transactionId' in rawRequest:
                _logger.info("rawrequest with transaction_id : %s" %
                             (rawRequest['transactionId']))
                intent_id = str(
                    rawRequest['transactionId'])
                acquirer = request.env['payment.acquirer'].sudo().search(
                    [('name', 'ilike', 'stripe'), ('company_id', "=", 1)])
                _logger.info("acquirer : %s" % (str(acquirer)))
                if acquirer:
                    _logger.info("acquirer : %s" %
                                 (str(acquirer.stripe_secret_key)))
                    response = requests.get("https://api.stripe.com/v1/payment_intents/%s" % (intent_id),
                                            auth=(str(acquirer.stripe_secret_key),
                                                  ''))  # get response of payment intent using stripe api
                    json_data = json.loads(response.text)
                    _logger.info("json_data : %s" % (json_data))
                    succeed = False
                    if 'status' in json_data:
                        # check if the payment state is succeeded
                        if json_data['status'] == 'succeeded':
                            succeed = True
                    if odoo_contact.partner_id.password_evalbox and odoo_contact.note_exam and succeed:
                        if float(odoo_contact.note_exam) >= 40:
                            res_user.send_email_create_account_evalbox(odoo_contact,
                                                                       odoo_contact.partner_id.password_evalbox)
                    ville = 'Île-de-France'
                    ville_id = request.env['session.ville'].sudo().search(
                        [('name_ville', "=", ville), ('company_id', "=", 1)], limit=1)
                    date_exam = '27/09/2022'
                    date_exam = datetime.strptime(
                        date_exam, '%d/%m/%Y').date()
                    product_id = request.env['product.product'].sudo().search(
                        [('default_code', "=", 'vtc_bolt')], limit=1)
                    module_id = False
                    _logger.info("ville_id : %s and product_id : %s and date_exam : %s" % (
                    str(ville_id), str(product_id), str(date_exam)))
                    if ville_id and date_exam and product_id:
                        module_id = request.env['mcmacademy.module'].sudo().search(
                            [('company_id', "=", 1), ('session_ville_id', "=", ville_id.id),
                             ('date_exam', "=", date_exam), ('product_id',
                                                             "=", product_id.id),
                             ('session_id.number_places_available', '>', 0)], limit=1)
                    _logger.info("module_id : %s" % (str(module_id)))
                    if succeed:
                        partner = odoo_contact.partner_id
                        so = request.env['sale.order'].sudo().create({
                            'partner_id': partner.id,
                            'company_id': 1,
                            'website_id': 1,
                        })  # create sale order ( contract ) if payment is succeed
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
                        pricelist = request.env['product.pricelist'].sudo().search(
                            [('company_id', '=', 1), ('name', "=", 'bolt')])  # search the pricelist bolt
                        if pricelist:
                            so.pricelist_id = pricelist.id
                        so.action_confirm()
                        if module_id:
                            so.partner_id.session_ville_id = module_id.session_ville_id
                            so.partner_id.date_examen_edof = module_id.date_exam
                            so.module_id = module_id.id
                            so.session_id = module_id.session_id.id

                            # create invoice from sale_order
                            moves = so._create_invoices(final=True)
                            for move in moves:
                                _logger.info(
                                    "webhook_stripe_move : %s" % (str(move)))
                                move.type_facture = 'web'
                                move.module_id = so.module_id.id
                                move.session_id = so.session_id.id
                                move.post()  # post the created invoice
                                journal_id = move.journal_id.id
                                acquirer = request.env['payment.acquirer'].sudo().search(
                                    [('name', "=", _('stripe')), ('company_id', '=', 1)], limit=1)
                                if acquirer:
                                    journal_id = acquirer.journal_id.id
                                payment_method = request.env['account.payment.method'].sudo().search(
                                    [('code', 'ilike', 'electronic')], limit=1)
                                payment = request.env['account.payment'].sudo().create(
                                    {'payment_type': 'inbound',
                                     'payment_method_id': payment_method.id,
                                     'partner_type': 'customer',
                                     'partner_id': move.partner_id.id,
                                     'amount': so.amount_total,
                                     'currency_id': move.currency_id.id,
                                     'payment_date': move.create_date,
                                     'journal_id': journal_id,
                                     'communication': False,
                                     'payment_token_id': False,
                                     'invoice_ids': [(6, 0, move.ids)],
                                     })  # create payment for invoice
                            so.partner_id.sudo().write({
                                'mcm_session_id': module_id.session_id.id,
                                'module_id': module_id.id,
                            })
                            so.partner_id.statut = 'won'  # change state of client to won
                            list = []
                            for partner in module_id.session_id.client_ids:
                                list.append(partner.id)
                                list.append(so.partner_id.id)
                                module_id.session_id.write(
                                    {'client_ids': [(6, 0, list)]})
                        so.action_cancel()  # cancel contract
                        so.sudo().unlink()  # unlink contract
        return True

    @http.route(['/contact-examen-blanc-resultat'], type='http', auth="public", csrf=False)
    def webhook_resultat_examen(self, **kw):
        _logger.info("webhoook contact jotform %s" % (kw))
        rawRequest = json.loads(kw['rawRequest'])
        _logger.info("rawRequest contact-examen-blanc-resultat: %s" % (str(rawRequest)))
        email = str(rawRequest['q169_email'])
        tel = str(rawRequest['q172_numeroDe172'])
        firstname = rawRequest['q176_nom']['first']
        lastName = rawRequest['q176_nom']['last']
        name = str(firstname) + ' ' + str(lastName)
        street = rawRequest['q180_adresse']
        street2 = rawRequest['q181_complementDadresse']
        city = rawRequest['q182_ville']
        zipcode = str(rawRequest['q183_codePostal'])
        result = str(rawRequest['q114_resultatExamen'])
        res_user = request.env['res.users']
        odoo_contact = res_user.sudo().search([('login', "=", str(
            email).lower().replace(' ', ''))], limit=1)  # search contact using email
        _logger.info("user founded using email : %s" % (odoo_contact))
        request.uid = odoo.SUPERUSER_ID
        if not odoo_contact:
            odoo_contact = res_user.find_user_with_phone(tel)
            _logger.info("user founded using tel : %s" % (odoo_contact))
        if not odoo_contact:
            _logger.info("user not created using do signup")
            name = str(firstname) + ' ' + str(lastName) if firstname and lastName else False
            odoo_contact = request.env['res.users'].sudo().create({
                'name': name,
                'login': email,
                'groups_id': [(6, 0, [request.env.ref('base.group_portal').id])],
                'email': email,  # set email in create user instead of False
                'phone': tel,
                'notification_type': 'email',
                'step': "financement",
                'website_id': 1,
                'company_ids': [1, 2],
                'company_id': 1,
            })
            odoo_contact.bolt = True
            # odoo_contact.action_reset_password() comment action reset password
            if odoo_contact:
                _logger.info("user created using create user")
                odoo_contact.street = street if street else False
                odoo_contact.zip = zipcode if zipcode else False
                odoo_contact.city = city if city else False
                odoo_contact.firstname = firstname if firstname else False
                odoo_contact.lastName = lastName if lastName else False
                odoo_contact.email = email
                odoo_contact.lang = 'fr_FR'
        if odoo_contact:
            if 'q114_resultatExamen' in rawRequest:  # check if the result in the response of webhook
                _logger.info("q114_resultatExamen of %s est %s" % (
                str(odoo_contact.name), str(rawRequest['q114_resultatExamen'])))
                result = str(rawRequest['q114_resultatExamen'])
                if result and result != '':
                    note_exam = float(result)
                    note_exam = note_exam * 5
                    odoo_contact.note_exam = str(note_exam)  # save the result of exam into client record
        return True
