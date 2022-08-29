from odoo import models, fields, api
import datetime
from odoo.exceptions import ValidationError

class KsChatDelete(models.Model):
    _inherit = 'mail.message'
    ks_msg_del = fields.Char()
    ks_msg_edit = fields.Boolean()
    ks_msg_edit_date = fields.Char(string="Date de modification de contenu de message")

    # Function to delete the message and changes the message to notification.
    @api.model
    def ks_delete_message(self, ks_message_id,ks_result):
        ks_admin_delete_access = self.env['ir.config_parameter'].sudo().get_param('ks_admin_delete_access')

        ks_date = self.browse(ks_message_id).create_date
        ks_present = datetime.datetime.now()
        ks_difference = ks_present - ks_date
        res = self.env['res.users'].search([("id", "=", self.browse(ks_message_id).create_uid.id)])
        if self.env.user.has_group('base.group_system') and ks_result:
            # if ks_difference.seconds <= 48 * 60 * 60:
            #     if res.has_group('base.group_system'):
            #         custom_message = "<p><i>This message was deleted.</i></p>"
            #     else:
            #         custom_message = "<p><i>Admin has deleted this message.</i></p>"

            # self.browse(ks_message_id).write({
            #     'message_type': "notification",
            #     'ks_msg_del': self.browse(ks_message_id).body,
            #     'body': custom_message
            # })
            self.browse(ks_message_id).attachment_ids.unlink()
            self.browse(ks_message_id).sudo().unlink()

        elif not self.env.user.has_group('base.group_system'):
            raise ValidationError(
                "Vous n'êtes pas autorisé à supprimer le message.Veuillez contacter l'administrateur")

    # Function to set the value of ks_msg_edit is true if message is updated.
    @api.model
    def ks_edit_message(self, ks_message_id, ks_state):
        ks_date = self.browse(ks_message_id).create_date
        ks_present = datetime.datetime.now()
        ks_difference = ks_present - ks_date
        self.write_date = datetime.datetime.now()
        self.browse(ks_message_id).ks_msg_edit_date = str(datetime.datetime.now())
        if ks_difference.seconds <= 600:
            self.browse(ks_message_id).ks_msg_edit = ks_state

    # @api.multi
    def read(self, fields=None, load='_classic_read'):
        """ Override to explicitely call check_access_rule, that is not called
            by the ORM. It instead directly fetches ir.rules and apply them. """
        if fields and 'ks_msg_edit' not in fields:
            fields.append('ks_msg_edit')

        return super(KsChatDelete, self).read(fields=fields, load=load)


class KsChatEnable(models.TransientModel):
    _inherit = "res.config.settings"
    ks_chat_enable = fields.Boolean(config_parameter='base_setup.ks_chat_enable')
    ks_admin_delete_access = fields.Boolean(config_parameter='base_setup.ks_admin_delete_access')

    @api.onchange('ks_chat_enable')
    def reset_admin_access(self):
        if not self.ks_chat_enable:
            self.ks_admin_delete_access = False


class KsHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        rec = super(KsHttp, self).session_info()
        rec['ks_chat_enable'] = self.env['ir.config_parameter'].sudo().get_param('base_setup.ks_chat_enable')
        rec['ks_admin_delete_access'] = self.env['ir.config_parameter'].sudo().get_param(
            'base_setup.ks_admin_delete_access')
        return rec
