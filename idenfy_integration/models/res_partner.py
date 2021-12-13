import base64
import requests
from odoo import fields,models,_

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _get_idenfy_document_data_id(self):
        for rec in self:
            rec.idenfy_document_data_id = self.env['idenfy.data'].search([('id','in',rec.idenfy_data_ids.ids),('type','=','other_documents')],order='id desc',limit=1)
            rec.idenfy_dl_data_id = self.env['idenfy.data'].search([('id', 'in', rec.idenfy_data_ids.ids), ('type', '=', 'licence')], order='id desc',limit=1)

    def _get_is_idenfy_approved(self):
        for rec in self:
            rec.is_idenfy_approved = False
            # docExpiry = rec.idenfy_document_data_id.res_data and eval(rec.idenfy_document_data_id.res_data or '{}').get('docExpiry', '')
            # current_date = fields.Date.today()
            # if rec.idenfy_document_data_id.status == 'APPROVED' and docExpiry and fields.Date.from_string(docExpiry) < current_date:
            if rec.idenfy_document_data_id.status == 'APPROVED':
                rec.is_idenfy_approved = True

    idenfy_document_data_id = fields.Many2one('idenfy.data','Idenfy Document',compute='_get_idenfy_document_data_id')
    idenfy_dl_data_id = fields.Many2one('idenfy.data', 'Idenfy Driving Licence', compute='_get_idenfy_document_data_id')
    idenfy_data_ids = fields.One2many('idenfy.data','partner_id','Idenfy Data')
    is_idenfy_approved = fields.Boolean('Is Approved',compute='_get_is_idenfy_approved')

    def _create_documents_idenfy(self, website):
        if not website:
            return False
        for rec in self:
            for idenfy in [rec.idenfy_document_data_id]:
                doc_file_res = website._idenfy_send_request('files', request_data={"scanRef": idenfy.scanref})
                for document in ['FACE','BACK','FRONT']:
                    image_url = doc_file_res.get(document,'')
                    if website.id == 1:
                        folder_id = self.env['documents.folder'].sudo().search(
                            [('name', "=", _('Documents MCM ACADEMY')), ('company_id', "=", 1)],limit=1)
                        if not folder_id:
                            vals_list = []
                            vals = {
                                'name': "Documents MCM ACADEMY"
                            }
                            vals_list.append(vals)
                            folder_id = self.env['documents.folder'].sudo().create(vals_list)
                            vals_list = []
                            vals = {
                                'name': "Statut document",
                                'folder_id': folder_id.id,
                            }
                            vals_list.append(vals)
                            facet = self.env['documents.facet'].sudo().create(vals_list)
                    elif website.id == 2:
                        folder_id = self.env['documents.folder'].sudo().search(
                            [('name', "=", _('Documents Digimoov')), ('company_id', "=", 2)],limit=1)
                        if not folder_id:
                            vals_list = []
                            vals = {
                                'name': "Documents Digimoov",
                                'company_id': 2
                            }
                            vals_list.append(vals)
                            folder_id = self.env['documents.folder'].sudo().create(vals_list)
                            vals_list = []
                            vals = {
                                'name': "Statut document",
                                'folder_id': folder_id.id,
                            }
                            vals_list.append(vals)
                            facet = self.env['documents.facet'].sudo().create(vals_list)
                    else:
                        folder_id = self.env['documents.folder'].search([],limit=1)
                    if image_url:
                        if document=='FRONT':
                            document = "Carte d'identité Recto"
                        elif document=='BACK' :
                            document = "Carte d'identité Verso"
                        elif document=='FACE' :
                            document = "Visage"
                        image_binary = base64.b64encode(requests.get(image_url).content)
                        vals = {
                            'name':document,
                            'datas': image_binary,
                            'type':'binary',
                            'partner_id':rec.id,
                            'folder_id':folder_id.id,
                            'state':'validated',
                        }
                        #search if the client has already a document with same name
                        partner_document = self.env['documents.document'].sudo().search(
                            [('name', "=", document), ('partner_id', "=", rec.id)])
                        if not partner_document:
                            self.env['documents.document'].create(vals)
        return True

    def uploaded_doc_after_check_status(self,website):
        doc_check_status = website._idenfy_send_request('status', request_data={"scanRef": self.idenfy_document_data_id.scanref})
        self.idenfy_document_data_id.status = doc_check_status.get('status', '')
        return doc_check_status.get('status', '')

    def check_status(self,website):
        for rec in self:
            doc_check_status = rec.idenfy_document_data_id.status not in ['APPROVED'] and rec.idenfy_document_data_id.scanref and website._idenfy_send_request('status', request_data={"scanRef": rec.idenfy_document_data_id.scanref}).get('status','') or rec.idenfy_document_data_id.status
            # website._idenfy_send_request('status', request_data={"scanRef": rec.idenfy_document_data_id.scanref})
            rec.idenfy_document_data_id.status = doc_check_status
            if doc_check_status in ['ACTIVE','APPROVED']:
                return True
        return False


    def fetch_document_details_from_idenfy(self,website):
        if not website:
            return False
        for rec in self:
            rec._create_documents_idenfy(website)
            doc_response = website._idenfy_send_request('data', request_data={"scanRef":rec.idenfy_document_data_id.scanref})
            rec.idenfy_document_data_id.write({'res_data': doc_response})
            if rec.numero_carte_identite == doc_response.get('docNumber'):
                return True
            rec.write({
                'birth_name': doc_response.get('docLastName') + ' ' + doc_response.get('docFirstName'),
                'nationality': doc_response.get('orgNationality') or doc_response.get('docNationality') or doc_response.get('docIssuingCountry'),
                'birthday': doc_response.get('docDob'),
                'birth_city': doc_response.get('orgBirthPlace') or doc_response.get('birthPlace'),
                'numero_carte_identite': doc_response.get('docNumber'),
                'title': self.env['res.partner.title'].search([('name', '=', 'Monsieur'), ('shortcut', '=', False)], limit=1) if doc_response.get('docSex') == 'MALE' else self.env[
                    'res.partner.title'].search([('name', '=', 'Madame')], limit=1),
                # 'numero_permis': dl_response.get('docNumber', '') or rec.numero_permis or ''
            })
        return True

