# -*- coding: utf-8 -*-
# Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details

from odoo import models

class Themecentric(models.AbstractModel):
    _inherit = 'theme.utils'
    
    def _theme_centric_customize_modal(self, mod):
        self.enable_view('website_theme_install.customize_modal')
    
    def _theme_centric_affix(self, mod):
        self.disable_view('website.affix_top_menu')