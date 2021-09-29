from odoo import models, api
from odoo.tools import datetime
import logging

_logger = logging.getLogger(__name__)

class BasePartnerMergeAutomaticWizard(models.TransientModel):
    _inherit = "base.partner.merge.automatic.wizard"

    @api.model
    def _get_ordered_partner(self, partner_ids):
        """ inherit this function to add conditions based on status of partner to use automatic partner merge,
        so the default field of dst_partner_id in wizard view will display as value from
        the list with state "won" if not "won" will choose to display other status different to "won"
        else if there is no state selected it will display the partner with no status
        """
        a = self.env['res.partner'].browse(partner_ids).sorted(
            key=lambda p: (p.active, (p.create_date or datetime.datetime(1970, 1, 1))),
            reverse=True,
        ).filtered(lambda r: r.statut == "won")
        if a:
            _logger.info("Duplicate partners a %s" % a)
            return a
        elif not a:
            b = self.env['res.partner'].browse(partner_ids).sorted(
                key=lambda p: (p.active, (p.create_date or datetime.datetime(1970, 1, 1))),
                reverse=True,
            ).filtered(lambda r: r.statut != "won")
            _logger.info("Duplicate partners b %s" % b)
            return b
        else:
            c = self.env['res.partner'].browse(partner_ids).sorted(
                key=lambda p: (p.active, (p.create_date or datetime.datetime(1970, 1, 1))),
                reverse=True,
            ).filtered(lambda r: r.statut == None)
            _logger.info("Duplicate partners c %s" % c)
            return c
