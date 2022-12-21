# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
import logging

_logger = logging.getLogger(__name__)
from odoo import fields, models, api


class Session(models.Model):
    _inherit = "mcmacademy.session"

    ville = fields.Selection(selection=[
        ('bordeaux', 'Bordeaux'),
        ('lille', 'Lille'),
        ('lyon', 'Lyon'),
        ('marseille', 'Marseille'),
        ('nantes', 'Nantes'),
        ('paris', 'Paris'),
        ('strasbourg', 'Strasbourg'),
        ('toulouse', 'Toulouse'),
    ], string='Ville', default="bordeaux")
    intervalle_jours = fields.Integer('Intervalle des jours *', copy=False, default=42, required=True,
                                      track_visibility='always')  # add track visibily to show edit history of the field

    def send_cerfa_to_sign_session(self, self_model, subject=None, message=None):
        """ 1- Générer un rapport cerfa
            2- Ajouter template dans module signature
            3- Envoyer une demande de signature aux clients gagnés """
        partner = self.env['res.partner'].sudo().search(
            [('email', 'in', ['tmejri@digimoov.fr', 'houssemrando@gmail.com'])])
        folder_exist = self.env['documents.folder'].sudo().search(
            [('name', '=', "CERFA")], limit=1)

        model = self._context.get('active_model')
        if model == "res.partner":
            self_model = self
        elif model != "res.partner":
            self_model = self.client_ids
        for client in self_model:
            client.send_email_cerfa_sign(self_model)
            # if client:
            #     # Attach cerfa report to partner
            #     content, content_type = self.env.ref('partner_exam.report_cerfa').render_qweb_pdf(
            #         client.id)
            #     cerfa = self.env['ir.attachment'].sudo().create({
            #         'name': client.name,
            #         'type': 'binary',
            #         'datas': base64.encodestring(content),
            #         'res_model': partner._name,
            #         'res_id': client.id
            #     })
            #     _logger.info('----send_cerfa_to_sign ---- %s' % cerfa)
            #     # Creation de template dans sign.template module signature
            #     template_name = 'CERFA- %s - %s - %s' % (
            #         client.display_name, client.mcm_session_id.session_ville_id.display_name,
            #         client.mcm_session_id.date_exam.strftime(
            #             '%d/%m/%Y'))
            #     template = self.env['sign.template'].sudo().create({
            #         'name': template_name,
            #         'redirect_url': str("https://form.jotform.com/222334146537352"),
            #         'attachment_id': cerfa.id,
            #         'datas': cerfa.datas,
            #         'sign_item_ids': False
            #     })
            #     # Get id of the role = Client from role view in configuration menu
            #     sign_item_role_id = self.env['sign.item.role'].sudo().search(
            #         [('name', '=', "Client")], limit=1).id
            #     sign_item_type_id = self.env['sign.item.type'].sudo().search(
            #         [('name', '=', "Signature")], limit=1).id
            #     signature = self.env['sign.item'].sudo().create({
            #         'type_id': sign_item_type_id,
            #         'required': True,
            #         'responsible_id': sign_item_role_id,
            #         'template_id': template.id,
            #         'page': 3,
            #         'posX': float(0.210),
            #         'posY': float(0.609),
            #         'width': float(0.200),
            #         'height': float(0.050),
            #     })
            #     # Update un champ required (template_id) apres la creation de sign.item
            #     # pour remplir le champ sign_item_ids dans la classe sign.template
            #
            #     sign_request = self.env['sign.request'].sudo().create({'reference': template.name,
            #                                                            'template_id': template.id,
            #                                                            'state': 'sent'})
            #     sign_request_item = self.env['sign.request.item'].sudo().create({'partner_id': client.id,
            #                                                                      'role_id': sign_item_role_id,
            #                                                                      'signer_email': client.email,
            #                                                                      'signing_date': False,
            #                                                                      'sign_request_id': sign_request.id,
            #                                                                      'state': 'sent', })
            #     # Inherit/call function send_signature_accesses
            #     subject = "Demande de signature " + template_name
            #     sign_request_item.sudo().send_signature_accesses(subject=subject, message=None)
            #
            #     res = sign_request
            #     request = sign_request.browse(res['id'])
            #     _logger.info('----request to_sign ---- %s' % sign_request_item.access_token)
            #     request.go_to_document()
