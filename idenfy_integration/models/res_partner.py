import base64
import requests
from odoo import fields,models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _get_idenfy_document_data_id(self):
        for rec in self:
            rec.idenfy_document_data_id = self.env['idenfy.data'].search([('id','in',rec.idenfy_data_ids.ids),('type','=','other_documents')],order='id desc',limit=1)
            rec.idenfy_dl_data_id = self.env['idenfy.data'].search([('id', 'in', rec.idenfy_data_ids.ids), ('type', '=', 'licence')], order='id desc',limit=1)

    # idenfy_token = fields.Char('Idenfy Token')
    # idenfy_scanref = fields.Char('Idenfy Scan Ref')
    # idenfy_id = fields.Char('Idenfy Id')
    idenfy_document_data_id = fields.Many2one('idenfy.data','Idenfy Document',compute='_get_idenfy_document_data_id')
    idenfy_dl_data_id = fields.Many2one('idenfy.data', 'Idenfy Driving Licence', compute='_get_idenfy_document_data_id')
    idenfy_data_ids = fields.One2many('idenfy.data','partner_id','Idenfy Data')

    def _create_documents_idenfy(self, website):
        if not website:
            return False
        for rec in self:
            for idenfy in [rec.idenfy_document_data_id,rec.idenfy_dl_data_id]:
                doc_file_res = website._idenfy_send_request('files', request_data={"scanRef": idenfy.scanref})
                for document in ['FACE','BACK','FRONT']:
                    image_url = doc_file_res.get(document,'')
                    if image_url:
                        image_binary = base64.b64encode(requests.get(image_url).content)
                        vals = {
                            'name':document,
                            'datas': image_binary,
                            'type':'binary',
                            'partner_id':rec.id,
                            'folder_id':self.env['documents.folder'].search([],limit=1).id
                        }
                        self.env['documents.document'].create(vals)
        return True


    def fetch_document_details_from_idenfy(self,website):
        if not website:
            return False
        for rec in self:
            #other documents
            rec._create_documents_idenfy(website)
            doc_response = website._idenfy_send_request('data', request_data={"scanRef":rec.idenfy_document_data_id.scanref})
            rec.idenfy_document_data_id.write({'res_data':doc_response})
            rec.write({
                'birth_name' : doc_response.get('docLastName')+' '+doc_response.get('docFirstName'),
                'nationality' : doc_response.get('docNationality'),
                'birthday' : doc_response.get('docDob'),
                'birth_city':doc_response.get('birthPlace')
            })
            # Driving Licence documents
            dl_response = website._idenfy_send_request('data', request_data={"scanRef": rec.idenfy_dl_data_id.scanref})
            rec.idenfy_document_data_id.write({'res_data': doc_response})
            self._cr.commit()


