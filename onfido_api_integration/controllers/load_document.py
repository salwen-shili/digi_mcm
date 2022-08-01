import dateutil
from odoo import http
from odoo.http import request
from datetime import datetime, date
from odoo.addons.portal.controllers.web import Home
import werkzeug
import base64
from odoo.addons.website.controllers.main import Website  # import website controller
import locale
import logging

_logger = logging.getLogger(__name__)


class LoadDocument(Website):

    @http.route('/charger_documents', type='http', auth='public', website=True)
    def load_document(self, **kw):
        partner=request.env['res.partner'].sudo().search([('id','=',request.env.user.partner_id.id)])
        values = {
            'sdk_token': '',
            'workflow_run_id': '',
            'api_token':'',
        }
        if partner:
            id_applicant=""
            sdk_token=""

            """Vérifier si on a deja créé un applicant lié à cet apprenant """
            # if partner.onfido_applicant_id:
            #     id_applicant= partner.onfido_applicant_id
            # else:
            id_applicant=partner.create_applicant(partner,
                                                      request.website.onfido_api_key_live)

            _logger.info('teeeeeeesttttt %s' %str(id_applicant)
                 )
            _logger.info('workfloow test  %s' %str(request.website.onfido_workflow_id))
            """Vérifier si on a généré un sdk token pour cet apprenant """
            # if partner.onfido_sdk_token and partner.exp_date_sdk_token and partner.exp_date_sdk_token >= datetime.now():
            #     sdk_token=partner.onfido_sdk_token
            # else:
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
            _logger.info("base urll %s" %str(base_url) )
            sdk_token=partner.generateSdktoken(id_applicant,
                                                       request.website.onfido_api_key_live,partner)

            workflow_run_id=partner.workflow_run(id_applicant,
                                                 request.website.onfido_api_key_live,request.website.onfido_workflow_id)
            values = {
                'workflow_run_id': workflow_run_id,
                'sdk_token': sdk_token,
                'api_token': request.website.onfido_api_key_live,
            }
            _logger.info("workflow %s" %str(workflow_run_id))
            """créer une ligne pour information Onfido """
            data_onfido = request.env['onfido.info'].sudo().create({
                'workflow_run_id' : workflow_run_id,
                'sdk_token' : sdk_token,
                

            })
            data_onfido.partner_id=partner
        return request.render("onfido_api_integration.load_document",
                              values)
        # else:
        #     raise werkzeug.exceptions.NotFound()


