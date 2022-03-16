# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
import random
import json
import re
from odoo.exceptions import ValidationError, UserError
from odoo import api, models, fields, _
from odoo.addons.http_routing.models.ir_http import slug,slugify
from odoo.tools.translate import html_translate
from odoo.tools import html2plaintext


class BlogPost(models.Model):
    _inherit = "blog.post"

    _sql_constraints = [
        ('code_uniq', 'unique (blog_post_website_url)', "Nom de l'article existe dèjàaaaa"),
    ]
    blog_post_website_url = fields.Char('Website URL', compute='_compute_blog_post_website_url', help='The full URL to access the document through the website.',store=True) #add computed field stored in the database to use it in search function contains the blog post website url optimized
    def _compute_blog_post_website_url(self):
        for blog_post in self:
            blog_posts = self.env['blog.post'].sudo().search([('id', '!=', blog_post.id)])
            for post in blog_posts:
                if post.name == blog_post.name:
                    raise UserError("'Nom de l'article existe dèjà")
            blog_post.blog_post_website_url = "/blog/%s" % (slugify(blog_post.name or '').strip().strip('-')) #using slugify to change the website_url to be without special characters
