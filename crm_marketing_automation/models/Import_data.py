import base64
import binascii
import codecs
import collections
import unicodedata

import chardet
import datetime
import io
import itertools
import logging
import psycopg2
import operator
import os
import re
import requests
from datetime import date,datetime
from PIL import Image

from odoo import api, fields, models
from odoo.exceptions import AccessError
from odoo.tools.translate import _
from odoo.tools.mimetypes import guess_mimetype
from odoo.tools import config, DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, pycompat
import logging
_logger = logging.getLogger(__name__)

class Import(models.TransientModel):
    _inherit  ='base_import.import'
    # date_import=fields.datetime('Dernière mis à jour')

    def do(self, fields, columns, options, dryrun=False):
        date_import=date.today()
        result= super(Import, self).do(fields, columns, options, dryrun)
        _logger.info('Imporrrttttttttt %s ' %str(self.res_model))
        if "crm.lead" == self.res_model:

            leads = self.env['crm.lead'].search([('stage_id.name','!=',"Formation sur 360")])
            statut_cpf=['']
            for lead in leads:
                # if lead.stage_id.name!="Formation sur 360":
                    num_dossier = str(lead.num_dossier)
                    partners = self.env['res.partner'].search([('numero_cpf',"=",num_dossier)])
                    _logger.info('lead %s' %lead.name)
                    for partner in partners:
                        # if (partner.numero_cpf) and (partner.numero_cpf == lead.num_dossier):
                        #     print('lead',lead.num_dossier,'partner',partner.numero_cpf)
                        """Changer statut_cpf des fiches client selon
                                                  statut de dossier nsur edof"""
                        if lead.stage_id.name == "En formation":
                            partner.statut_cpf = "in_training"
                        if lead.stage_id.name == "Accepté":
                            partner.statut_cpf = "accepted"
                        if "Annulé" in lead.stage_id.name:
                            partner.statut_cpf = "canceled"
                        if lead.stage_id.name == "Sortie de formation":
                            partner.statut_cpf = "out_training"
                        if lead.stage_id.name == "Facturé":
                            partner.statut_cpf = "bill"
                        if lead.stage_id.name == "Service fait déclaré":
                            partner.statut_cpf = "service_declared"
                        if "Service fait validé" in lead.stage_id.name:
                            partner.statut_cpf = "service_validated"
                        if lead.stage_id.name == "Annulation titulaire":
                            partner.statut_cpf = "canceled"

                        # lead.sudo().write({
                        #         'partner_id': partner,
                        #         'name': partner.name,
                        #         'mode_de_financement': 'cpf',
                        #         'module_id': partner.module_id ,
                        #         'mcm_session_id': partner.mcm_session_id,
                        #         'company_id':partner.company_id.id if partner.company_id else False
                        #
                        #     })


        return result