# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
import datetime
import json
import os
import logging
import pytz
import requests
import werkzeug.utils
import werkzeug.wrappers

from itertools import islice
from xml.etree import ElementTree as ET

import odoo

from odoo import http, models, fields, _
from odoo.http import request
from odoo.tools import OrderedSet
from odoo.addons.http_routing.models.ir_http import slug, _guess_mimetype
from odoo.addons.web.controllers.main import Binary
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.addons.portal.controllers.web import Home

logger = logging.getLogger(__name__)

# Completely arbitrary limits
MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT = IMAGE_LIMITS = (1024, 768)
LOC_PER_SITEMAP = 45000
SITEMAP_CACHE_TIME = datetime.timedelta(hours=12)

from odoo.addons.website.controllers.main import Website

class Website(Website):
    
    @http.route(['/robots.txt'], type='http',website=True, auth="public")
    def robots(self, **kwargs):
        #personalize robots txt of website
        if request.website.id == 2 :
            return request.render('website_no_crawler.digi_robots', {'url_root': request.httprequest.url_root}, mimetype='text/plain')
        else:
            return request.render('website_no_crawler.mcm_academy_robots', {'url_root': request.httprequest.url_root},
                                  mimetype='text/plain')