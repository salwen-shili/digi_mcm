# -*- coding: utf-8 -*-
# Copyright 2018 Pierre Faniel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class WebsiteConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    @api.depends("website_id")
    def has_hotjar_tracking(self):
        self.has_hotjar_tracking = bool(self.hotjar_tracking_key)

    def inverse_hotjar_tracking(self):
        if not self.has_hotjar_tracking:
            self.hotjar_tracking_key = False

    has_hotjar_tracking = fields.Boolean(
        "Hotjar Tracking",
        compute=has_hotjar_tracking,
        inverse=inverse_hotjar_tracking,
    )
    hotjar_tracking_key = fields.Char(
        "Hotjar Tracking Key",
        help="Container ID",
        related="website_id.hotjar_tracking_key",
        readonly=False,
    )
