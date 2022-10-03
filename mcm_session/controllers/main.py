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

PPG = 20  # Products Per Page
PPR = 4  # Products Per Row


class WebsiteSale(WebsiteSale):

    def _prepare_product_values(self, product, category, search, **kwargs):
        add_qty = int(kwargs.get('add_qty', 1))

        product_context = dict(request.env.context, quantity=add_qty,
                               active_id=product.id,
                               partner=request.env.user.partner_id)
        ProductCategory = request.env['product.public.category']

        if category:
            category = ProductCategory.browse(int(category)).exists()

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
        attrib_set = {v[1] for v in attrib_values}

        keep = QueryURL('/shop', category=category and category.id, search=search, attrib=attrib_list)

        categs = ProductCategory.search([('parent_id', '=', False)])

        pricelist = request.website.get_current_pricelist()
        if not product_context.get('pricelist'):
            product_context['pricelist'] = pricelist.id
            product = product.with_context(product_context)

        # Needed to trigger the recently viewed product rpc
        view_track = request.website.viewref("website_sale.product").track
        modules = request.env['mcmacademy.module'].sudo().search(
            [('product_id', '=', product.id)])
        list_module=[]
        for module in modules:
            if module.session_id.stage_id.name==_('Planifiées'):
                list_module.append(module)
        department=False
        if product.department:
            department=True
        print('departement1')
        print(product.department)
        print(department)
        return {
            'search': search,
            'category': category,
            'pricelist': pricelist,
            'attrib_values': attrib_values,
            'attrib_set': attrib_set,
            'keep': keep,
            'categories': categs,
            'main_object': product,
            'product': product,
            'add_qty': add_qty,
            'view_track': view_track,
            'modules':list_module,
            'department':department,
            'error_department':'',
            'error_session':''
        }

    @http.route(['/shop/cart/update'], type='http', auth="public", methods=['GET', 'POST'], website=True, csrf=False)
    def cart_update(self, product_id,module='', add_qty=1, set_qty=0,promo=None, **kw):
        """This route is called when adding a product to cart (no options)."""
        product =  request.env['product.product'].sudo().search(
                    [('id', '=', product_id)])
        order = request.website.sale_get_order()
        print('shop update')
        print(order)
        if order and product and order.company_id != product.company_id:
            order.sudo().unlink()
        sale_order = request.website.sale_get_order(force_create=True)
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
        if sale_order.partner_id.bolt == True :
            bolt_product = request.env['product.product'].sudo().search(
                [('company_id', '=', 1), ('default_code', "=", 'vtc_bolt')], order="list_price", limit=1)
            if bolt_product :
                product_id = bolt_product
        sale_order._cart_update(
            product_id=int(product_id),
            add_qty=1,
            set_qty=1,
            product_custom_attribute_values=product_custom_attribute_values,
            no_variant_attribute_values=no_variant_attribute_values
        )
        if(sale_order.partner_id.customer_rank==0):
            sale_order.partner_id.customer_rank=1
        if promo:
            print(promo)
        if sale_order :
            if sale_order.company_id.id == 1 and product:
                if 'taxi' not in str(product.name).lower() and sale_order.partner_id.statut != "won":
                    sale_order.partner_id.state_id = False 
        if product_id:
            if module != '' and module !='all':
                module = request.env['mcmacademy.module'].sudo().search(
                    [('id', '=', module)])
                session=module.session_id
                if session:
                    sale_order.session_id=session
                    sale_order.partner_id.mcm_session_id=session
                if module:
                    sale_order.module_id=module
                    sale_order.partner_id.module_id=module
                list=[]
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
                    sale_order.partner_id.statut='panier_perdu'
                    sale_order.partner_id.module_id=module

        if kw.get('express'):
            return request.redirect("/shop/checkout?express=1")

        return request.redirect("/shop/cart")
