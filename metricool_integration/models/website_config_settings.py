# -*- coding: utf-8 -*-
# Copyright 2018 Pierre Faniel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class WebsiteConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    @api.depends("website_id")
    def has_metricool_tracking(self):
        self.has_metricool_tracking = bool(self.metricool_tracking_key)

    def inverse_metricool_tracking(self):
        if not self.has_metricool_tracking:
            self.metricool_tracking_key = False

    has_metricool_tracking = fields.Boolean(
        "Metricool Tracking",
        compute=has_metricool_tracking,
        inverse=inverse_metricool_tracking,
    )
    metricool_tracking_key = fields.Char(
        "metricool Tracking Key",
        help="Container ID",
        related="website_id.metricool_tracking_key",
        readonly=False,
    )
