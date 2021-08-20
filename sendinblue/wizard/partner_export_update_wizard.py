# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ParterExportsendinblue(models.TransientModel):
    _name = 'partner.export.sendinblue'
    _description = "Partner Export Sendinblue"

    odoo_list_ids = fields.Many2many('sendinblue.lists', string='sendinblue Lists', domain=[('odoo_list_id', '!=', False)])

    # @api.multi
    def get_mailing_contact_id(self, partner_id, force_create=False):
        mailing_contact_obj = self.env['mailing.contact'] #v13
        if not partner_id.email:
            return False
        query = """
                SELECT id 
                  FROM mailing_contact
                WHERE LOWER(substring(email, '([^ ,;<@]+@[^> ,;]+)')) = LOWER(substring('{}', '([^ ,;<@]+@[^> ,;]+)'))""".format(
            partner_id.email)
        self._cr.execute(query)
        contact_id = self._cr.fetchone()
        contact_id = contact_id[0] if contact_id else False
        prepared_vals = {'name': partner_id.name, 'email': partner_id.email, 'country_id': partner_id.country_id.id}
        if contact_id:
            contact_id = mailing_contact_obj.browse(contact_id)
            contact_id.write(prepared_vals)
        if not contact_id and force_create:
            contact_id = mailing_contact_obj.create(prepared_vals)
        return contact_id.id

    # @api.multi
    def action_export_partner_sendinblue(self):
        mailing_contact_obj = self.env['mailing.contact'] #v13
        partner_ids = self.env['res.partner'].search([('id', 'in', self._context.get('active_ids', []))])
        vals_list = []
        contact_ids = mailing_contact_obj
        for partner_id in partner_ids:
            for odoo_list_id in self.odoo_list_ids:
                contact_id = self.get_mailing_contact_id(partner_id, force_create=True)
                if contact_id:
                    contact_id = mailing_contact_obj.browse(contact_id)
                    if odoo_list_id.id not in contact_id.subscription_list_ids.mapped('list_id').mapped('sendinblue_list_id').ids:
                        vals = {'list_id': odoo_list_id.odoo_list_id.id, 'contact_id': contact_id.id}
                        # vals_list.append((0,0, vals))
                        contact_id.write({'subscription_list_ids': [(0,0, vals)]})
                    if contact_id not in contact_ids:
                        contact_ids += contact_id
        if contact_ids:
            # contact_ids.write({'subscription_list_ids': vals_list})
            contact_ids.action_export_to_sendinblue()
        return True

    # @api.multi
    def action_update_partner_sendinblue(self):
        mailing_contact_obj = self.env['mailing.contact'] #v13
        partner_ids = self.env['res.partner'].search([('id', 'in', self._context.get('active_ids', []))])
        for partner_id in partner_ids:
            contact_id = self.get_mailing_contact_id(partner_id)
            if contact_id:
                contact_id = mailing_contact_obj.browse(contact_id)
                contact_id.action_update_to_sendinblue()
        return True
