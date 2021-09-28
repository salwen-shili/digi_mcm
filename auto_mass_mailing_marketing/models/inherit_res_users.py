from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class InheritResUsers(models.Model):
    _inherit = "res.users"

    def remove_double_users(self):
        """ Add this function to remove duplicate
        users in res.users interface based on condition if state = new"""
        duplicate_users = []
        for users in self:
            if users.partner_id.id and users.id not in duplicate_users:
                duplicates = self.env['res.users'].search(
                    [('name', '=', users.partner_id.display_name), ('id', '!=', users.id),
                     ('login', 'ilike', users.partner_id.email), ('state', '=', 'new')])
                _logger.info("Duplicates users %s" % duplicates.name)
                for dup in duplicates:
                    _logger.info("////////////////////DUP////////////// %s" % dup)
                    duplicate_users.append(dup.id)
                    _logger.info("Duplicates users ////// duplicate_users /////////////////// %s" % duplicate_users)
        self.browse(duplicate_users).unlink()