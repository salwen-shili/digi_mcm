# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
import werkzeug
import itertools
import pytz
import babel.dates
from collections import OrderedDict

from odoo import http, fields
from odoo.addons.http_routing.models.ir_http import slug, unslug
from odoo.addons.website.controllers.main import QueryURL
from odoo.http import request
from odoo.osv import expression
from odoo.tools import html2plaintext
from odoo.tools.misc import get_lang
from odoo.addons.website_blog.controllers.main import WebsiteBlog


class CustomWebsiteBlog(WebsiteBlog):

    @http.route([
        '/blog',
        '/blog/page/<int:page>',
        '/blog/tag/<string:tag>',
        '/blog/tag/<string:tag>/page/<int:page>',
        '''/blog/<model("blog.blog", "[('website_id', 'in', (False, current_website_id))]"):blog>''',
        '''/blog/<model("blog.blog"):blog>/page/<int:page>''',
        '''/blog/<model("blog.blog"):blog>/tag/<string:tag>''',
        '''/blog/<model("blog.blog"):blog>/tag/<string:tag>/page/<int:page>''',
    ], type='http', auth="public", website=True)
    def blog(self, blog=None, tag=None, page=1, **opt):
        Blog = request.env['blog.blog']
        blogs = Blog.search(request.website.website_domain(), order="create_date asc, id asc")
        if blog and len(blogs) == 1: #check if the website has only one category and the url contains the website_url of this category to redirect the client to /blog using the code 301 of redirection
            return werkzeug.utils.redirect('/blog',301)
        elif blog and len(blogs) > 1 :
            if blog.name =="DIGIMOOV" : #check if the name of category is DIGIMOOV to redirect it to /blog
                return werkzeug.utils.redirect('/blog', 301)
        if blog and not blog.can_access_from_current_website(): # redirect client to /blog
            raise werkzeug.exceptions.NotFound()

        blogs = Blog.search(request.website.website_domain(), order="create_date asc, id asc")

        date_begin, date_end, state = opt.get('date_begin'), opt.get('date_end'), opt.get('state')

        values = self._prepare_blog_values(blogs=blogs, blog=blog, date_begin=date_begin, date_end=date_end, tags=tag, state=state, page=page)

        if blog:
            values['main_object'] = blog
            values['edit_in_backend'] = True
            values['blog_url'] = QueryURL('', ['blog', 'tag'], blog=blog, tag=tag, date_begin=date_begin, date_end=date_end)
        else:
            values['blog_url'] = QueryURL('/blog', ['tag'], date_begin=date_begin, date_end=date_end)
        return request.render("website_blog.blog_post_short", values)

    #prepare website route for blog post /blog/blog_post_website_url
    @http.route([
        '''/blog/<string:blog_post>''',
    ], type='http', auth="public", website=True)
    def custom_blog_post(self, blog=None, blog_post=None, tag_id=None, page=1, enable_editor=None, **post):
        blog = False
        blog_post = '/blog/' + str(blog_post)
        if blog_post:
            blog_post = request.env['blog.post'].sudo().search([('blog_post_website_url', "=", str(blog_post))], limit=1)
            if blog_post:
                if not blog_post.is_published:
                    blog_post_rewrite = request.env['website.rewrite'].sudo().search(
                        [('url_from', "=", blog_post.blog_post_website_url)], limit=1)
                    if blog_post_rewrite and blog_post_rewrite.url_to:
                        return werkzeug.utils.redirect(blog_post_rewrite.url_to, blog_post_rewrite.redirect_type)
                    elif blog_post_rewrite.redirect_type == '404':
                        raise werkzeug.exceptions.NotFound()
                blog_post = blog_post
                blog = blog_post.blog_id
            else:
                raise werkzeug.exceptions.NotFound()
        if blog:
            if not blog.can_access_from_current_website():
                raise werkzeug.exceptions.NotFound()
        BlogPost = request.env['blog.post']
        date_begin, date_end = post.get('date_begin'), post.get('date_end')

        pager_url = "/blog_post/%s" % blog_post.id

        pager = request.website.pager(
            url=pager_url,
            total=len(blog_post.website_message_ids),
            page=page,
            step=self._post_comment_per_page,
            scope=7
        )
        pager_begin = (page - 1) * self._post_comment_per_page
        pager_end = page * self._post_comment_per_page
        comments = blog_post.website_message_ids[pager_begin:pager_end]

        domain = request.website.website_domain()
        blogs = blog.search(domain, order="create_date, id asc")

        tag = None
        if tag_id:
            tag = request.env['blog.tag'].browse(int(tag_id))
        blog_url = QueryURL('', ['blog', 'tag'], blog=blog_post.blog_id, tag=tag, date_begin=date_begin,
                            date_end=date_end)

        tags = request.env['blog.tag'].search([])

        # Find next Post
        blog_post_domain = [('blog_id', '=', blog.id)]
        if not request.env.user.has_group('website.group_website_designer'):
            blog_post_domain += [('post_date', '<=', fields.Datetime.now())]

        all_post = BlogPost.search(blog_post_domain)

        if blog_post not in all_post:
            return request.redirect("/blog/%s" % (slug(blog)))

        # should always return at least the current post
        all_post_ids = all_post.ids
        current_blog_post_index = all_post_ids.index(blog_post.id)
        nb_posts = len(all_post_ids)
        next_post_id = all_post_ids[(current_blog_post_index + 1) % nb_posts] if nb_posts > 1 else None
        next_post = next_post_id and BlogPost.browse(next_post_id) or False

        values = {
            'tags': tags,
            'tag': tag,
            'blog': blog,
            'blog_post': blog_post,
            'blogs': blogs,
            'main_object': blog_post,
            'nav_list': self.nav_list(blog),
            'enable_editor': enable_editor,
            'next_post': next_post,
            'date': date_begin,
            'blog_url': blog_url,
            'pager': pager,
            'comments': comments,
        }
        response = request.render("website_blog.blog_post_complete", values)
        return response
    #redirect old blog post website url to the new url
    @http.route([
        '''/blog/<model("blog.blog", "[('website_id', 'in', (False, current_website_id))]"):blog>/post/<model("blog.post", "[('blog_id','=',blog[0])]"):blog_post>''',
    ], type='http', auth="public", website=True)
    def blog_post(self, blog, blog_post, tag_id=None, page=1, enable_editor=None, **post):
        if blog_post:
            return werkzeug.utils.redirect(blog_post.blog_post_website_url, 301)
        return super(CustomWebsiteBlog, self).blog_post(blog, blog_post, tag_id, page, enable_editor)