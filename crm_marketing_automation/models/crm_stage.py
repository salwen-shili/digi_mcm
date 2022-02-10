from odoo import api, fields, models,_
import calendar
from datetime import date,datetime
import logging
_logger = logging.getLogger(__name__)
class CRM(models.Model):
    _inherit = "crm.stage"
    bolt=fields.Boolean('Etape Bolt')
    


