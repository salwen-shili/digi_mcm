from odoo import models, api
from odoo.tools import datetime


class BasePartnerMergeAutomaticWizard(models.TransientModel):
    _inherit = "base.partner.merge.automatic.wizard"

    @api.model
    def _get_ordered_partner(self, partner_ids):
        """ Helper : returns a `res.partner` recordset ordered by create_date/active fields
            :param partner_ids : list of partner ids to sort
        """
        a = self.env['res.partner'].browse(partner_ids).sorted(
            key=lambda p: (p.active, (p.create_date or datetime.datetime(1970, 1, 1))),
            reverse=True,
        ).filtered(lambda r: r.statut == "won")
        if a:
            print("a", a)
            return a
        elif not a:
            b = self.env['res.partner'].browse(partner_ids).sorted(
                key=lambda p: (p.active, (p.create_date or datetime.datetime(1970, 1, 1))),
                reverse=True,
            ).filtered(lambda r: r.statut != "won")
            print("b", b)
            return b
        else:
            c = self.env['res.partner'].browse(partner_ids).sorted(
                key=lambda p: (p.active, (p.create_date or datetime.datetime(1970, 1, 1))),
                reverse=True,
            ).filtered(lambda r: r.statut == None)
            print("c", c)
            return c
