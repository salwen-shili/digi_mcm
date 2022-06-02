# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv import osv


from datetime import date, datetime
import requests
import logging
import json

_logger = logging.getLogger(__name__)


class mcmSession(models.Model):
    _inherit = "mcmacademy.session"
    id_group_edusign = fields.Char(string="ID Group Edusign", readonly=True)

    def createGroup(self):
        # iterate self in case it returns more than one object.
        for res in self:

            print("Edusign | call Create group on session : ", res.name, res.id_group_edusign)
            _logger.info("Edusign | call Create group on session : ", res.name)

            base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
            # if "localhost" not in str(base_url) and "dev.odoo" not in str(base_url):
            company = self.env["res.company"].sudo().search([("id", "=", 2)], limit=1)
            api_key = ""

            if company:
                api_key = company.edusign_api_key
                # check if group exist already by id

                headers = {
                    "Authorization": "Bearer %s" % (str(api_key)),
                    "Content-Type": "application/json",
                }

                getResult = requests.get("https://ext.edusign.fr/v1/group/" + res.id_group_edusign, headers=headers)
                getContent = json.loads(getResult.content)

                groupIsCreated = True if getContent["status"] == "success" else False
                print("Edusign group is created? : ", groupIsCreated)
                print(getContent)

                if not groupIsCreated:
                    # Session does not exist, post request to
                    postUrl = "https://ext.edusign.fr/v1/group/:id"

                    data = {
                        "group": {
                            "NAME": res.name,
                            "DESCRIPTION": "",
                            "STUDENTS": [""],
                            "PARENT": "",
                            "API_ID": "",
                            "API_TYPE": "",
                        }
                    }
                    _logger.info("Edusign createGroup start post request...")
                    print("Edusign createGroup start post request...")
                    result = requests.post(postUrl, data=json.dumps(data), headers=headers)
                    status_code = result.status_code

                    if status_code == 200:
                        resultContent = json.loads(result.content)
                        print(
                            "Edusign Create response :",
                            resultContent,
                            "| status_code:",
                            status_code,
                        )
                        _logger.info(
                            "Edusign Create response :",
                            resultContent,
                            "| status_code:",
                            status_code,
                        )
                        if resultContent["status"] == "success":

                            print("Groupe created with ID: ", resultContent["result"]["ID"])
                            _logger.info("Groupe created with ID: ", resultContent["result"]["ID"])
                            # add group id to self
                            res.id_group_edusign = resultContent["result"]["ID"]

                            # return {
                            #     "type": "ir.actions.client",
                            #     "tag": "display_notification",
                            #     "params": {
                            #         "title": _("i"),
                            #         "message": _("Groupe ajouté avec succès!"),
                            #         "sticky": True,
                            #         "className": "bg-success",
                            #     },
                            # }

                    else:
                        # group can't be created.
                        print("Exit Edusign CreateGroup post request with status code ", status_code)
                        _logger.info("Exit Edusign CreateGroup post request with status code ", status_code)

                        return {
                            "type": "ir.actions.client",
                            "tag": "display_notification",
                            "params": {
                                "title": _("Erreur"),
                                "message": _(
                                    "Impossible de créer le groupe dans edusign. API Edusign a enovye un erreur"
                                ),
                                "sticky": True,
                                "className": "bg-success",
                            },
                        }
                else:
                    # group exists
                    print("Exit Edusign CreateGroup get request with status code ", getContent)
                    _logger.info("Exit Edusign CreateGroup get request with status code ", getContent)

                    return {
                        "type": "ir.actions.client",
                        "tag": "display_notification",
                        "params": {
                            "title": _("i"),
                            "message": _("Un groupe avec ce nom existe déjà!"),
                            "sticky": True,
                            "className": "bg-success",
                        },
                    }
