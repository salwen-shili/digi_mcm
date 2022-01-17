
import time
from odoo import api, fields, models, _, SUPERUSER_ID
class Product(models.Model):
    _inherit="product.template"

    id_stripe=fields.Char(string="Id produit en stripe")