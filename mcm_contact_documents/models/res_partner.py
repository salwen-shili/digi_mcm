from odoo import fields, models, _


class Partner(models.Model):
    _inherit = "res.partner"

    def action_see_documents(self):
        self.ensure_one()
        return {
            'name': _('Documents'),
            'res_model': 'documents.document',
            'type': 'ir.actions.act_window',
            'views': [[False, "tree"], [False, "kanban"],[False, "form"]],
            'view_mode': 'tree,kanban,form',
            'context': {
                "search_default_partner_id": self.id,
                "default_partner_id": self.id,
                "searchpanel_default_folder_id": False
            },
        }