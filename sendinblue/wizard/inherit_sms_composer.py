
from odoo import api, fields, models, tools
import logging

_logger = logging.getLogger(__name__)


class InheritSmsComposer(models.TransientModel):
    _inherit = 'sms.composer'

    def _action_send_sms(self):
        _logger.info("_____________SMS.COMPoSER___________ %s")
        records = self._get_records()
        if self.composition_mode == 'numbers':
            return self._action_send_sms_numbers()
        elif self.composition_mode == 'comment':
            if records is not None and issubclass(type(records), self.pool['mail.thread']):
                return self._action_send_sms_comment(records)
            return self._action_send_sms_numbers()
        else:
            return self._action_send_sms_mass(records)