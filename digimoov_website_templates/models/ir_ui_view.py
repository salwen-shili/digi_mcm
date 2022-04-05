# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import uuid
from itertools import groupby

from odoo import api, fields, models, _
from odoo import tools
from odoo.addons.http_routing.models.ir_http import url_for
from odoo.osv import expression
from odoo.http import request

_logger = logging.getLogger(__name__)


class View(models.Model):

    _inherit = "ir.ui.view"

    @api.model
    def _prepare_qcontext(self):
        """ Returns the qcontext : rendering context with website specific value (required
            to render website layout template)
        """
        qcontext = super(View, self)._prepare_qcontext()
        if 'main_object' in qcontext:
            view_id = qcontext['main_object']
            if view_id.first_page_id:
                qcontext['main_object'] = view_id.first_page_id
        return qcontext