# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import binascii

from odoo import fields, http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.payment.controllers.portal import PaymentProcessing
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.osv import expression

class CustomerPortal(CustomerPortal):

    @http.route(['/my/quotes', '/my/quotes/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_quotes(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        SaleOrder = request.env['sale.order']
        domain = [
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['sent', 'cancel'])
        ]

        searchbar_sortings = {
            'date': {'label': _('Date de contrat'), 'order': 'date_order desc'},
            'name': {'label': _('Nom'), 'order': 'name'},
        }

        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        archive_groups = self._get_archive_groups('sale.order', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        quotation_count = SaleOrder.search_count(domain)
        # make pager
        pager = portal_pager(
            url="/my/quotes",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=quotation_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        quotations = SaleOrder.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_quotations_history'] = quotations.ids[:100]

        values.update({
            'date': date_begin,
            'quotations': quotations.sudo(),
            'page_name': 'Contrat',
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/quotes',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("sale.portal_my_quotations", values)

    @http.route(['/my/orders', '/my/orders/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_orders(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        SaleOrder = request.env['sale.order']

        domain = [
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['sale', 'done'])
        ]

        searchbar_sortings = {
            'date': {'label': _('Date de contrat'), 'order': 'date_order desc'},
            'name': {'label': _('Nom'), 'order': 'name'},
        }
        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        archive_groups = self._get_archive_groups('sale.order', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        order_count = SaleOrder.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/orders",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=order_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        orders = SaleOrder.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_orders_history'] = orders.ids[:100]

        values.update({
            'date': date_begin,
            'orders': orders.sudo(),
            'page_name': 'Contrat',
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/orders',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("sale.portal_my_orders", values)

    @http.route(['''/my/orders/<int:order_id>''','''/my/orders/<string:product>/<int:order_id>''','''/my/orders/<string:product>/<string:partenaire>/<int:order_id>'''], type='http', auth="public", website=True)
    def portal_order_page(self, order_id, report_type=None, access_token=None, message=False, download=False,product=None,partenaire=None, **kw):
        try:
            order_sudo = self._document_check_access('sale.order', order_id, access_token=access_token)
            order = order_sudo
            if message == "sign_ok" and access_token: # check if the contract is signed and have access token
                if order and order.company_id.id == 2 :
                    product_id = False
                    if order:
                        for line in order.order_line:
                            product_id = line.product_id

                    if not product and not partenaire and product_id:
                        product = True
                        partenaire = True
                    if product and not partenaire:
                        if product_id:
                            slugname = (product_id.name).strip().strip(
                                '-').replace(' ', '-').lower()
                            if str(slugname) != str(product):
                                if order.pricelist_id and order.pricelist_id.name in ['ubereats', 'deliveroo', 'coursierjob', 'box2home', 'coursier2roues']: # check if the client has paid with one of this pricelist ['ubereats', 'deliveroo', 'coursierjob', 'box2home', 'coursier2roues' ] for digimoov
                                    return request.redirect("/my/orders/%s/%s/%d?access_token=%s&message=%s" % (slugname, order.pricelist_id.name,order_id,access_token,message))
                                else:
                                    return request.redirect("/my/orders/%s/%d?access_token=%s&message=%s" % (slugname,order_id,access_token,message))
                            else:
                                if order.pricelist_id and order.pricelist_id.name in ['ubereats', 'deliveroo', 'coursierjob', 'box2home', 'coursier2roues']:
                                    return request.redirect("/my/orders/%s/%s/%d?access_token=%s&message=%s" % (slugname, order.pricelist_id.name,order_id,access_token,message))
                        else:
                            return request.redirect("/my/orders/%d?access_token=%s&message=%s" % (order_id,access_token,message))
                    elif product and partenaire:
                        if product_id:
                            slugname = (product_id.name).strip().strip(
                                '-').replace(' ', '-').lower()
                            if str(slugname) != str(product):
                                pricelist = request.env['product.pricelist'].sudo().search(
                                    [('company_id', '=', 2), ('name', "=", str(partenaire))])
                                if not pricelist:
                                    pricelist_id = order.pricelist_id
                                    if pricelist_id.name in ['ubereats', 'deliveroo', 'coursierjob', 'box2home', 'coursier2roues']:
                                        return request.redirect("/my/orders/%s/%s/%d?access_token=%s&message=%s" % (slugname, order.pricelist_id.name,order_id,access_token,message))
                                    else:
                                        return request.redirect("/my/orders/%s/%d?access_token=%s&message=%s" % (slugname,order_id,access_token,message))
                                else:
                                    if pricelist.name in ['ubereats', 'deliveroo', 'coursierjob', 'box2home', 'coursier2roues']:
                                        return request.redirect("/my/orders/%s/%s/%d?access_token=%s&message=%s" % (slugname, order.pricelist_id.name,order_id,access_token,message))
                                    else:
                                        return request.redirect("/my/orders/%s/%d?access_token=%s&message=%s" % (slugname,order_id,access_token,message))
                            else:
                                pricelist = request.env['product.pricelist'].sudo().search(
                                    [('company_id', '=', 2), ('name', "=", str(partenaire))])

                                if not pricelist:
                                    pricelist_id = order.pricelist_id
                                    if pricelist_id.name in ['bolt']:
                                        return request.redirect("/my/orders/%s/%s/%d?access_token=%s&message=%s" % (slugname, order.pricelist_id.name,order_id,access_token,message))
                                    else:
                                        return request.redirect("/my/orders/%s/%d?access_token=%s&message=%s" % (slugname,order_id,access_token,message))
                                else:
                                    if pricelist.name in ['ubereats', 'deliveroo', 'coursierjob', 'box2home', 'coursier2roues']:
                                        if pricelist.name != order.pricelist_id.name:
                                            return request.redirect("/my/orders/%s/%s/%d?access_token=%s&message=%s" % (slugname, order.pricelist_id.name,order_id,access_token,message))
                                    else:
                                        return request.redirect("/my/orders/%s/%d?access_token=%s&message=%s" % (slugname,order_id,access_token,message))
                        else:
                            pricelist = request.env['product.pricelist'].sudo().search(
                                [('company_id', '=', 2), ('name', "=", str(partenaire))])
                            if pricelist and pricelist.name in ['ubereats', 'deliveroo', 'coursierjob', 'box2home', 'coursier2roues']:
                                return request.redirect("/my/orders/%s/%d?access_token=%s&message=%s" % (pricelist.name,order_id,access_token,message))
                            else:
                                return request.redirect("/my/orders/%d?access_token=%s&message=%s" % (order_id,access_token,message))
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
                            slugname = (product_id.name).strip().strip(
                                '-').replace(' ', '-').lower()
                            if str(slugname) != str(product):
                                if order.pricelist_id and order.pricelist_id.name in ['bolt']: # check if the client has paid with one of this pricelist ['bolt'] for mcm academy
                                    return request.redirect("/my/orders/%s/%s/%d?access_token=%s&message=%s" % (slugname, order.pricelist_id.name,order_id,access_token,message)) # redirect the client to /my/orders/product_name/pricelist_name
                                else:
                                    return request.redirect("/my/orders/%s/%d?access_token=%s&message=%s/" % (slugname,order_id,access_token,message)) # redirect the client to /my/orders/product_name
                            else:
                                if order.pricelist_id and order.pricelist_id.name in ['bolt']:
                                    return request.redirect("/my/orders/%s/%s/%d?access_token=%s&message=%s" % (slugname, order.pricelist_id.name,order_id,access_token,message))
                        else:
                            return request.redirect("/my/orders/%d?access_token=%s&message=%s/" % (order_id,access_token,message)) #redirect the client to the default contract url
                    elif product and partenaire:
                        if product_id:
                            slugname = (product_id.name).strip().strip(
                                '-').replace(' ', '-').lower()
                            if str(slugname) != str(product):
                                pricelist = request.env['product.pricelist'].sudo().search(
                                    [('company_id', '=', 1), ('name', "=", str(partenaire))])
                                if not pricelist:
                                    pricelist_id = order.pricelist_id
                                    if pricelist_id.name in ['bolt', ]:
                                        return request.redirect("/my/orders/%s/%s/%d?access_token=%s&message=%s" % (slugname, order.pricelist_id.name,order_id,access_token,message))
                                    else:
                                        return request.redirect("/my/orders/%s/%d?access_token=%s&message=%s" % (slugname,order_id,access_token,message))
                                else:
                                    if pricelist.name in ['bolt']:
                                        return request.redirect("/my/orders/%s/%s/%d?access_token=%s&message=%s" % (slugname, order.pricelist_id.name,order_id,access_token,message))
                                    else:
                                        return request.redirect("/my/orders/%s/%d?access_token=%s&message=%s" % (slugname,order_id,access_token,message))
                            else:
                                pricelist = request.env['product.pricelist'].sudo().search(
                                    [('company_id', '=', 1), ('name', "=", str(partenaire))])

                                if not pricelist:
                                    pricelist_id = order.pricelist_id
                                    if pricelist_id.name in ['bolt']:
                                        return request.redirect("/my/orders/%s/%s/%d?access_token=%s&message=%s" % (slugname, order.pricelist_id.name,order_id,access_token,message))
                                    else:
                                        return request.redirect("/my/orders/%s/%d?access_token=%s&message=%s" % (slugname,order_id,access_token,message))
                                else:
                                    if pricelist.name in ['bolt']:
                                        if pricelist.name != order.pricelist_id.name:
                                            return request.redirect("/my/orders/%s/%s/%d?access_token=%s&message=%s" % (slugname, order.pricelist_id.name,order_id,access_token,message))
                                    else:
                                        return request.redirect("/my/orders/%s/%d?access_token=%s&message=%s" % (slugname,order_id,access_token,message))
                        else:
                            pricelist = request.env['product.pricelist'].sudo().search(
                                [('company_id', '=', 1), ('name', "=", str(partenaire))])
                            if pricelist and pricelist.name in ['bolt']:
                                return request.redirect("/my/orders/%s/%d?access_token=%s&message=%s" % (pricelist.name,order_id,access_token,message))
                            else:
                                return request.redirect("/my/orders/%d?access_token=%s&message=%s" % (order_id,access_token,message))
        except (AccessError, MissingError):
            return request.redirect('/my')
        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(model=order_sudo, report_type=report_type,
                                     report_ref='sale.action_report_saleorder', download=download)

        # use sudo to allow accessing/viewing orders for public user
        # only if he knows the private token
        now = fields.Date.today()

        # Log only once a day
        if order_sudo and request.session.get(
                'view_quote_%s' % order_sudo.id) != now and request.env.user.share and access_token:
            request.session['view_quote_%s' % order_sudo.id] = now
            body = _('Quotation viewed by customer %s') % order_sudo.partner_id.name
            _message_post_helper('sale.order', order_sudo.id, body, token=order_sudo.access_token,
                                 message_type='notification', subtype="mail.mt_note")

        values = {
            'sale_order': order_sudo,
            'message': message,
            'token': access_token,
            'return_url': '/shop/payment/validate',
            'bootstrap_formatting': True,
            'partner_id': order_sudo.partner_id.id,
            'report_type': 'html',
            'action': order_sudo._get_portal_return_action(),
        }
        if order_sudo.company_id:
            values['res_company'] = order_sudo.company_id

        if order_sudo.has_to_be_paid():
            domain = expression.AND([
                ['&', ('state', 'in', ['enabled', 'test']), ('company_id', '=', order_sudo.company_id.id)],
                ['|', ('country_ids', '=', False), ('country_ids', 'in', [order_sudo.partner_id.country_id.id])]
            ])
            acquirers = request.env['payment.acquirer'].sudo().search(domain)

            values['acquirers'] = acquirers.filtered(
                lambda acq: (acq.payment_flow == 'form' and acq.view_template_id) or
                            (acq.payment_flow == 's2s' and acq.registration_view_template_id))
            values['pms'] = request.env['payment.token'].search([('partner_id', '=', order_sudo.partner_id.id)])
            values['acq_extra_fees'] = acquirers.get_acquirer_extra_fees(order_sudo.amount_total,
                                                                         order_sudo.currency_id,
                                                                         order_sudo.partner_id.country_id.id)

        if order_sudo.state in ('draft', 'sent', 'cancel'):
            history = request.session.get('my_quotations_history', [])
        else:
            history = request.session.get('my_orders_history', [])
        values.update(get_records_pager(history, order_sudo))

        return request.render('sale.sale_order_portal_template', values)

    @http.route(['/my/orders/<int:order_id>/accept'], type='json', auth="public", website=True)
    def portal_quote_accept(self, order_id, access_token=None, name=None, signature=None):
        # get from query string if not on json param
        access_token = access_token or request.httprequest.args.get('access_token')
        try:
            order_sudo = self._document_check_access('sale.order', order_id, access_token=access_token)
        except (AccessError, MissingError):
            return {'error': _('Contrat invalide')}

        if not order_sudo.has_to_be_signed():
            return {'error': _("L'état de la contrat ne requiert pas de signature de la part du client.")}
        if not signature:
            return {'error': _('Signature is missing.')}

        try:
            order_sudo.write({
                'signed_by': name,
                'signed_on': fields.Datetime.now(),
                'signature': signature,
            })
        except (TypeError, binascii.Error) as e:
            return {'error': _('Données de signature invalides.')}

        if not order_sudo.has_to_be_paid():
            order_sudo.action_confirm()
            order_sudo._send_order_confirmation_mail()

        pdf = request.env.ref('sale.action_report_saleorder').sudo().render_qweb_pdf([order_sudo.id])[0]

        _message_post_helper(
            'sale.order', order_sudo.id, _('Contrat signé par %s') % (name,),
            attachments=[('Contrat -%s.pdf' % order_sudo.partner_id.name, pdf)],
            **({'token': access_token} if access_token else {}))

        query_string = '&message=sign_ok'
        if order_sudo.has_to_be_paid(True):
            query_string += '#allow_payment=yes'
        print('portal_quote_accept')
        return {
            'force_refresh': True,
            'redirect_url': order_sudo.get_portal_url(query_string=query_string),
        }