from odoo import fields,models

class IdenfyData(models.Model):
    _name = 'idenfy.data'

    name = fields.Char('Name')
    type = fields.Selection([('other_documents','Other Documents'),('licence','Driving Licence')])
    partner_id = fields.Many2one('res.partner','Contact')
    website_id = fields.Many2one('website', 'Website')
    req_data = fields.Text('Request Data')
    res_data = fields.Text('Response Data')
    token = fields.Char('Idenfy Token')
    scanref = fields.Char('Idenfy Scan Ref')
    idenfy_id = fields.Char('Idenfy Id')
    status = fields.Char('Status')

