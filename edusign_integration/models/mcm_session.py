# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime
import requests
import logging
import json

_logger = logging.getLogger(__name__)


class mcmSession(models.Model):
    _inherit = "mcmacademy.self"
    id_group_edusign = fields.Char(string="ID Group Edusign", readonly=True)

    # post request to create a group using https://ext.edusign.fr/v1/group
    # with a body :
    # {
    #     "group": {
    #         "NAME": "testing",
    #         "DESCRIPTION": "testing",
    #         "STUDENTS": [""],
    #         "PARENT": "",
    #         "API_ID": "",
    #         "API_TYPE": ""
    #     }
    # }

    def createGroup(self):
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        # if "localhost" not in str(base_url) and "dev.odoo" not in str(base_url):
        company = self.env["res.company"].sudo().search([("id", "=", 2)], limit=1)
        api_key = ""

        if company:
            api_key = company.edusign_api_key

            # get session name
            # session = self.env["mcmacademy.session"].sudo().search([("name", "=", "Lyon 20 Juillet 2022")], limit=1)

            print("Edusign add group post request to create : ", self.name)
            _logger.info("Edusign add group post request to create : ", self.name)
            headers = {
                "Authorization": "Bearer %s" % (str(api_key)),
                "Content-Type": "application/json",
            }

            url = "https://ext.edusign.fr/v1/group"

            data = {
                "group": {
                    "NAME": "testing",
                    "DESCRIPTION": "testing",
                    "STUDENTS": [""],
                    "PARENT": "",
                    "API_ID": "",
                    "API_TYPE": "",
                }
            }

            result = requests.post(url, data=json.dumps(data), headers=headers)
            status_code = result.status_code

            if status_code == 200:
                resultContent = json.loads(result.content)
                print(
                    "Edusign add group response :",
                    resultContent,
                    "| status_code:",
                    status_code,
                )
                _logger.info(
                    "Edusign add group response :",
                    resultContent,
                    "| status_code:",
                    status_code,
                )
                if resultContent["status"] == "success":
                    print(resultContent["result"]["ID"])
                    # add group id to self
