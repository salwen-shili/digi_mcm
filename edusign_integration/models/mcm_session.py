# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import email
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

    # Add an empty group to Edusing
    def addOneGroup(self, session, headers):

        print("session name from AddOneGroupFunction: ", session.name)
        postUrl = "https://ext.edusign.fr/v1/group"
        data = {
            "group": {
                "NAME": session.name,
                "DESCRIPTION": "",
                "STUDENTS": "",
                "PARENT": "",
                "API_ID": "",
                "API_TYPE": "",
            }
        }
        _logger.info("Edusign addOneGroup start post request...")
        print("Edusign addOneGroup start post request...")
        result = requests.post(postUrl, data=json.dumps(data), headers=headers)
        status_code = result.status_code

        if status_code == 200:
            resultContent = json.loads(result.content)
            print(
                "Edusign Add a group response :",
                resultContent,
                "| status_code:",
                status_code,
            )
            _logger.info(
                "Edusign Add a group response :",
                resultContent,
                "| status_code:",
                status_code,
            )
            if resultContent["status"] == "success":

                print("Groupe created with ID: ", resultContent["result"]["ID"])
                _logger.info("Groupe created with ID: ", resultContent["result"]["ID"])
                # add group id to self
                session.id_group_edusign = resultContent["result"]["ID"]

    # Check existance of a value(group/student) and returns False or the content of the request.
    # return the content in case we want to search for the ID of a group/student.
    # WE can use it to return the ID
    def checkExistance(self, url, value, headers):
        if not value:
            print("checkExistance function has returned False due to empty value.")
            return False
        getResult = requests.get(url + value, headers=headers)
        getContent = json.loads(getResult.content)
        # check if group already exist
        check = True if getContent["status"] == "success" else False
        if check:
            print("Function checkexistance has returned : " + getContent)
            return getContent
        else:
            return False

    ## Check student existance
    # If False create new student and assign a group by self.id_group_edusign
    # if True Edit Groups and add another self.id_group_edusign to the existance
    # We can use it for adding a new student or update an existant student
    def addStudent(self, student, headers):
        url = "https://ext.edusign.fr/v1/student"
        result = ""

        checkStudent = self.checkExistance("https://ext.edusign.fr/v1/student/by-email/:", student.email, headers)
        # -------------------------------------------------------------------------------
        if not checkStudent and str(student.id) == str(checkStudent["result"].id):
            # Student exists, we make a patch request.
            # We pass all info in data, in case there is an update.
            url = "https://ext.edusign.fr/v1/student/:" + checkStudent["result"].id

            # Check group id existance in the student groups.
            groups = (
                checkStudent["result"]
                if self.id_group_edusign in checkStudent["result"].GROUPS
                else checkStudent["result"].GROUPS.append(self.id_group_edusign)
            )
            data = {
                "student": {
                    "ID": checkStudent["result"].id,
                    "FIRSTNAME": "student.firstname",
                    "LASTNAME": "student.lastName",
                    "EMAIL": student.email,
                    "FILE_NUMBER": "",
                    "PHOTO": "",
                    "PHONE": student.phone,
                    "GROUPS": groups,
                    "TRAINING_NAME": self.diplome_vise,
                    "COMPANY": "",
                    "TAGS": ["DIGIMOOV"],
                    "SEND_EMAIL_CREDENTIALS": "",
                    "API_ID": student.id,
                    "API_TYPE": "",
                    "BADGE_ID": "",
                    "STUDENT_FOLLOWER_ID": [],
                }
            }
            # Edit by student ID
            result = requests.patch(url, data=json.dumps(data), headers=headers)
        else:
            # students doesn't exist, we make a post request and create a new one.
            data = {
                "student": {
                    "FIRSTNAME": "student.firstname",
                    "LASTNAME": "student.lastName",
                    "EMAIL": student.email,
                    "FILE_NUMBER": "",
                    "PHOTO": "",
                    "PHONE": student.phone,
                    "GROUPS": [self.id_group_edusign],
                    "TRAINING_NAME": self.diplome_vise,
                    "COMPANY": "",
                    "TAGS": ["DIGIMOOV"],
                    "SEND_EMAIL_CREDENTIALS": "",
                    "API_ID": student.id,
                    "API_TYPE": "",
                    "BADGE_ID": "",
                    "STUDENT_FOLLOWER_ID": [],
                }
            }
            # Add a new student
            result = requests.post(url, data=json.dumps(data), headers=headers)

        status_code = result.status_code
        resultContent = json.loads(result.content)
        if status_code == 200:

            print(
                "addStudent function post/patch request result :",
                resultContent,
                "| status_code:",
                status_code,
            )
            _logger.info(
                "addStudent function post/patch request result :",
                resultContent,
                "| status_code:",
                status_code,
            )
            if resultContent["status"] == "success":
                print("Student created with ID: ", resultContent["result"]["ID"])
                _logger.info("Student created with ID: ", resultContent["result"]["ID"])
                return True
                # add group id to self
        # Because we use return so if code gets to here it means we have an error
        else:
            print(resultContent["message"])
            _logger.info(resultContent["message"])
            return False

    # Add a new group to a Student passed in parameters and add a new group using Edit a student's variable

    # A function to show a notification
    # types: success,warning,danger,info
    def showNotification(self, title, message, type):

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": (title),
                "message": message,
                "type": type,  # types: success,warning,danger,info
                "sticky": True,  # True/False will display for few seconds if false
            },
        }

    ################## ################## ################## ################## ################## ##################
    #################                                                                              ##################
    #################                        Main Function Statrs Here.                            ##################
    #################                                                                              ##################
    ################## ################## ################## ################## ################## ##################

    # All logics is here
    def main(self):
        # if not in localhost
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        # if "localhost" not in str(base_url) and "dev.odoo" not in str(base_url):

        # Get edusign api key
        company = self.env["res.company"].sudo().search([("id", "=", 2)], limit=1)
        if company:
            api_key = company.edusign_api_key
            headers = {
                "Authorization": "Bearer %s" % (str(api_key)),
                "Content-Type": "application/json",
            }

            # iterate self in case it returns more than one object.
            for res in self:
                # check if group exist already by id
                check = self.checkExistance("https://ext.edusign.fr/v1/group/", res.id_group_edusign, headers)
                if not check:
                    print("Trying to add a group on Edusign with name : ", res.name, res.id_group_edusign)
                    _logger.info("Trying to add a group on Edusign with name : ", res.name, res.id_group_edusign)
                    self.addOneGroup(res, headers)
                else:
                    print("A group with the same ID already exist -  ", res.name, res.id_group_edusign)
                    _logger.info("A group with the same ID already exist -  ", res.name, res.id_group_edusign)

                for students in self:
                    for student in students:
                        i = i + 1
                        self.addStudent(student, headers)
                print(i + " client(s) gagné(s) sont ajoutes a la session ." + res.name)
                _logger.info(i + " client(s) gagné(s) sont ajoutes a la session ." + res.name)
        return
