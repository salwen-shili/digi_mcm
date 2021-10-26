import base64
import requests
from odoo import fields,models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _get_idenfy_document_data_id(self):
        for rec in self:
            rec.idenfy_document_data_id = self.env['idenfy.data'].search([('id','in',rec.idenfy_data_ids.ids),('type','=','other_documents')],order='id desc',limit=1)
            rec.idenfy_dl_data_id = self.env['idenfy.data'].search([('id', 'in', rec.idenfy_data_ids.ids), ('type', '=', 'licence')], order='id desc',limit=1)

    def _get_is_idenfy_approved(self):
        for rec in self:
            rec.is_idenfy_approved = False
            if rec.idenfy_dl_data_id.status == 'APPROVED':
                rec.is_idenfy_approved = True

    idenfy_document_data_id = fields.Many2one('idenfy.data','Idenfy Document',compute='_get_idenfy_document_data_id')
    idenfy_dl_data_id = fields.Many2one('idenfy.data', 'Idenfy Driving Licence', compute='_get_idenfy_document_data_id')
    idenfy_data_ids = fields.One2many('idenfy.data','partner_id','Idenfy Data')
    is_idenfy_approved = fields.Boolean('Is Approved',compute='_get_is_idenfy_approved')

    def _create_documents_idenfy(self, website):
        if not website:
            return False
        for rec in self:
            for idenfy in [rec.idenfy_dl_data_id]:
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

    def check_status(self,website):
        for rec in self:
            # doc_check_status = website._idenfy_send_request('status', request_data={"scanRef": rec.idenfy_document_data_id.scanref})
            # rec.idenfy_document_data_id.status = doc_check_status.get('status','')
            check_status = website._idenfy_send_request('status', request_data={"scanRef": rec.idenfy_dl_data_id.scanref})
            rec.idenfy_dl_data_id.status = check_status.get('status', '')
            if check_status and check_status.get('status') in ['ACTIVE']:
                return True
        return False


    def fetch_document_details_from_idenfy(self,website):
        if not website:
            return False
        for rec in self:
            #other documents
            if rec.check_status(website):
                return True
            rec._create_documents_idenfy(website)
            # doc_response = website._idenfy_send_request('data', request_data={"scanRef":rec.idenfy_document_data_id.scanref})
            # rec.idenfy_document_data_id.write({'res_data':doc_response})
            # Driving Licence documents
            dl_response = website._idenfy_send_request('data', request_data={"scanRef": rec.idenfy_dl_data_id.scanref})
            if rec.numero_carte_identite == dl_response.get('docNumber'):
                return True
            rec.idenfy_dl_data_id.write({'res_data': dl_response})
            rec.write({
                'birth_name': dl_response.get('docFirstName') + ' ' + dl_response.get('docLastName'),
                # 'nationality': doc_response.get('docNationality'),
                'birthday': dl_response.get('docDob'),
                # 'birth_city': doc_response.get('birthPlace'),
                'numero_carte_identite': dl_response.get('docNumber'),
                # 'title': self.env['res.partner.title'].search([('name', '=', 'Monsieur'), ('shortcut', '=', False)], limit=1) if doc_response.get('docSex') == 'MALE' else self.env[
                #     'res.partner.title'].search([('name', '=', 'Madame')], limit=1),
                'numero_permis': dl_response.get('docNumber','') or rec.numero_permis or ''
            })

