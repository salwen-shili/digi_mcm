from odoo import api, fields, models,_
import calendar
from datetime import date,datetime
import logging
_logger = logging.getLogger(__name__)
class CRMStage(models.Model):
    _inherit = "crm.stage"
    bolt=fields.Boolean('Etape Bolt')

    # @api.model
    # def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
    #     if self.user_has_groups('crm_marketing_automation.group_bolt'):
    #         domain += [('bolt', '=', True)]
    #
    #     res = super(CRMStage, self).search_read(domain, fields, offset, limit, order)
    #
    #     return res


