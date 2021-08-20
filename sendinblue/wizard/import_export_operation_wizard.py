# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ImportExportOperation(models.TransientModel):
    _name = "sendinblue.import.export.operation"
    _description = "Import/Export Operation"

    account_ids = fields.Many2many('sendinblue.accounts', required=True,help="Accounts from which you want to perform import/export operation")

    get_lists = fields.Boolean("Lists/Audiences", help="Obtains available lists from sendinblue")
    get_folders = fields.Boolean("Folders", help="Obtains available Folders from sendinblue")
    get_templates = fields.Boolean("Templates", help="Get a list of an account's available templates.")
    get_campaigns = fields.Boolean("Campaigns", help="Get a list of campaigns.")
    get_senders = fields.Boolean('Senders',help="senders which is used for send email using senders email.")

    @api.model
    def default_get(self, fields):
        res = super(ImportExportOperation, self).default_get(fields)
        accounts = self.env['sendinblue.accounts'].search([])
        res.update({'account_ids': [(6, 0, accounts.ids)]})
        return res

    # @api.multi
    def process_operation(self):
        for account in self.account_ids:
            if self.get_folders:
                account.import_folders()
            if self.get_lists:
                account.import_lists()
            if self.get_templates:
                account.import_templates()
            if self.get_campaigns:
                account.import_campaigns()
            if self.get_senders:
                account.import_senders()
        return True
