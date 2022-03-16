# Copyright 2022 Salwen SHILI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Optimisation blog/blog post SEO',
    'category': 'Website',
    'summary': 'Optimisation blog/blog post SEO',
    'version': '1.0.0',
    'license': 'AGPL-3',
    'description': '''
    optimize blog post url to /blog/slug(blog post name)
    ''',
    'author': 'Houssem Ben mbarek',
    'depends': [
        'website_blog',
    ],
    'data': [
        #page de blog
        'views/website_blog_posts.xml',
    ],
    'images': [
    ],
    'installable': True,
    'application': False,
}