# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
import random
import json
import re
from odoo.exceptions import ValidationError, UserError
from odoo import api, models, fields, _
from odoo.addons.http_routing.models.ir_http import slug
from odoo.tools.translate import html_translate
from odoo.tools import html2plaintext


class WebsitePublishedMixin(models.AbstractModel):
    _inherit = "website.published.mixin"

    website_url = fields.Char('Website URL', compute='_compute_website_url',
                              help='The full URL to access the document through the website.', store=True)


class BlogPost(models.Model):
    _inherit = "blog.post"

    _sql_constraints = [
        ('code_uniq', 'unique (name)', "Nom de l'article existe dèjàaaaa"),
    ]

    def _compute_website_url(self):
        super(BlogPost, self)._compute_website_url()
        for blog_post in self:
            blog_posts = self.env['blog.post'].sudo().search([('id', '!=', blog_post.id)])
            for post in blog_posts:
                if post.name == blog_post.name:
                    raise UserError("'Nom de l'article existe dèjà")
            blog_post.website_url = "/blog/%s" % str(blog_post.name).replace(' ?', '').replace('?', '').replace(' !',
                                                                                                                '').replace(
                ' : ', '-').replace(' - ', '-').replace(' ', '-').lower()