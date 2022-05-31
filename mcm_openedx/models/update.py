# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Update(models.Model):
    _name = 'mcm_openedx.update'


    email = fields.Char()
    coach = fields.Char()






