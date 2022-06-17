# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from asyncio.log import logger
from distutils.command.build_scripts import first_line_re
import email
from pickle import APPEND
from posixpath import split
from tabnanny import check
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv import osv


from datetime import date, datetime
import requests
import logging
import json

_logger = logging.getLogger(__name__)
# allowedUrls
allowedUrls = ["https://www.digimoov.fr/"]


class mcmSession(models.Model):
    _inherit = "mcmacademy.session"
    id_group_edusign = fields.Char(string="ID Group Edusign", readonly=True)
    # Course API ID
    id_session_edusign = fields.Char(string="ID Session Edusign", readonly=True)

    # Create a new Course only if a course does not exist in edusign.
    # Patching a course will erase existing signatures.
    # We check if exam_date > today to allow patch request
    def addCourse(self, session, professorsId, headers):

        # Exit add course if professor ID is empty
        classroom = session.session_adresse_examen.adresse_centre_examen
        if classroom == False:
            classroom = ""

        if len(professorsId) == 0:
            return
        professor1 = ""
        professor2 = ""
        if len(professorsId) > 0:
            # Use checkExistance to get Professor ID by API ID
            checkProfessor = self.checkExistance(
                "https://ext.edusign.fr/v1/professor/get-id/", professorsId[0], headers
            )
            if checkProfessor["status"] == "success":
                professor1 = checkProfessor["result"]["ID"]
            if len(professorsId) == 2:
                checkProfessor = self.checkExistance(
                    "https://ext.edusign.fr/v1/professor/get-id/", professorsId[1], headers
                )
                if checkProfessor["status"] == "success":
                    professor2 = checkProfessor["result"]["ID"]

        nbAdd = 0
        nbEdit = 0
        heureExam = ""

        heureExam = (
            session.heure_examen_apres_midi
            if session.temps_convocation == "apres_midi"
            else session.heure_examen_matin
        )

        startDate = ("%sT%s:00.000Z" % (str(session.date_exam), str(heureExam))).replace("H", ":")
        h = int((str(heureExam).split("H", 1)[0])) + 3
        endDate = "%sT%s:00:00.000Z" % (str(session.date_exam), h)

        checkCrouse = self.checkExistance("https://ext.edusign.fr/v1/course/", session.id_session_edusign, headers)

        # -------------------------------------------------------------------------------

        if checkCrouse:
            print("A course with the same ID exists already.")
            _logger.info("A course with the same ID exists already.")
            # We check if exam_date >= today to allow patch request
            if date.today() <= session.date_exam:
                print(
                    "Today = %s < Exam date = %s, launching a patch request"
                    % (str(date.today()), str(session.date_exam))
                )
                _logger.info("A course with the same ID exists already.")
                patchUrl = "https://ext.edusign.fr/v1/course/?id=" + session.id_session_edusign

                data = {
                    "course": {
                        "ID": session.id_session_edusign,
                        "NAME": session.name,
                        "DESCRIPTION": "session de " + session.name,
                        "STUDENTS": [],
                        "CLASSROOM": classroom,
                        "START": startDate,
                        "END": endDate,
                        "PROFESSOR": professor1,
                        "PROFESSOR_2": professor2,
                        "SCHOOL_GROUP": [session.id_group_edusign],
                        "ZOOM": 0,
                        "API_ID": session.name,
                    }
                }
                print(data)

                # Edit by student ID
                result = requests.patch(patchUrl, data=json.dumps(data), headers=headers)

                print(
                    "addCourse() has launched a patch request for : %s %s %s "
                    % (str(result), str(result.status_code), str(json.loads(result.text)))
                )
                _logger.info(
                    "addCourse() has launched a patch request for :  %s %s %s"
                    % (str(result), str(result.status_code), str(json.loads(result.text)))
                )

                if result.status_code == 200:
                    nbEdit = nbEdit + 1

        else:
            if date.today() <= session.date_exam:

                postUrl = "https://ext.edusign.fr/v1/course"
                data = {
                    "course": {
                        "NAME": session.name,
                        "DESCRIPTION": "session de " + session.name,
                        "STUDENTS": [],
                        "CLASSROOM": classroom,
                        "START": startDate,
                        "END": endDate,
                        "PROFESSOR": professor1,
                        "PROFESSOR_2": professor2,
                        "SCHOOL_GROUP": [session.id_group_edusign],
                        "ZOOM": 0,
                        "API_ID": session.name,
                    }
                }

                print(data)
                _logger.info("Edusign addCourse start post request...")
                print("Edusign addCourse start post request...")
                result = requests.post(postUrl, data=json.dumps(data), headers=headers)
                status_code = result.status_code

                if status_code == 200:
                    resultContent = json.loads(result.text)
                    print(
                        "Edusign addCourse() response :%s with status code %s"
                        % (
                            str(resultContent),
                            str(status_code),
                        )
                    )
                    _logger.info(
                        "Edusign addCourse() response :%s with status code %s"
                        % (
                            str(resultContent),
                            str(status_code),
                        )
                    )
                    if resultContent["status"] == "success":
                        nbAdd = nbAdd + 1
                        print("Course created with ID: ", resultContent["result"]["ID"])
                        _logger.info("Groupe created with ID: %s" % resultContent["result"]["ID"])
                        # add group id to self
                        session.id_session_edusign = resultContent["result"]["ID"]

    # Add an empty group to Edusing
    # check group existance with session.id
    # assign id if true
    # create if false
    def addGroup(self, session, headers):

        result = ""
        checkGroup = self.checkExistance("https://ext.edusign.fr/v1/group/get-id/", session.id, headers)

        # -------------------------------------------------------------------------------
        edusignGroupID = ""

        if checkGroup:
            if "id" in checkGroup["result"]:
                edusignGroupID = checkGroup["result"]["id"]
            elif "ID" in checkGroup["result"]:
                edusignGroupID = checkGroup["result"]["ID"]
            else:
                print("Please check the id key in addGroup() checkExistance response.")

            print(
                "Edusign addGroup updated the session %s with edusignGroupID='%s'..."
                % (str(session.name), str(edusignGroupID))
            )
            _logger.info(
                "Edusign addGroup updated the session %s with edusignGroupID='%s'..."
                % (str(session.name), str(edusignGroupID))
            )

            session.id_group_edusign = edusignGroupID

        else:
            postUrl = "https://ext.edusign.fr/v1/group"
            data = {
                "group": {
                    "NAME": session.name,
                    "DESCRIPTION": "",
                    "STUDENTS": [],
                    "PARENT": "",
                    "API_ID": session.name,
                    "API_TYPE": "",
                }
            }
            _logger.info("Edusign addGroup start post request for %s..." % (str(session.name)))
            print("Edusign addGroup start post request for %s..." % (str(session.name)))
            result = requests.post(postUrl, data=json.dumps(data), headers=headers)
            status_code = result.status_code

            if status_code == 200:
                resultContent = json.loads(result.text)
                print(
                    "Edusign Add a group response  %s: | with status code %s" % (str(resultContent), str(status_code))
                )
                _logger.info(
                    "Edusign Add a group response  %s: | with status code %s" % (str(resultContent), str(status_code))
                )
                if resultContent["status"] == "success":

                    if "id" in resultContent["result"]:
                        edusignGroupID = resultContent["result"]["id"]
                    elif "ID" in resultContent["result"]:
                        edusignGroupID = resultContent["result"]["ID"]
                    else:
                        print("Please verify result id key in addStudent() response")
                    # add group id to self
                    session.id_group_edusign = edusignGroupID
                    print("Groupe created with ID: ", edusignGroupID)
                    _logger.info("Groupe created with ID: %s " % (str(edusignGroupID)))

    # Check existance of a value(group/student) and returns False or the content of the request.
    # return the content in case we want to search for the ID of a group/student.
    # WE can use it to return the ID
    def checkExistance(self, url, value, headers):
        if not value:
            print("checkExistance function has returned False due to empty value.")
            return False
        print("checkExistence() function url request: ", url + str(value))
        getResult = requests.get(url + str(value), headers=headers)
        getContent = json.loads(getResult.text)
        # check if group already exist

        check = True if getContent["status"] == "success" else False
        if check:
            print("Function checkexistance has returned : ", getContent)
            return getContent
        else:
            return False

    ##restore student by ID
    def restoreStudent(self, id, email, headers):
        result = requests.get("https://ext.edusign.fr/v1/student/restore/" + str(id), headers=headers)
        print(result.text, "https://ext.edusign.fr/v1/student/restore/" + str(id))

        if result.status_code == 200:

            _logger.info("Student with email %s has been restored. " % (str(email)))
            print("Student with email %s has been restored. " % (str(email)))

        else:
            print("error restore!")

    ## Check student existance
    # If False create new student and assign a group by self.id_group_edusign
    # if True Edit Groups and add another self.id_group_edusign to the existance
    # We can use it for adding a new student or update an existant student
    def addStudent(self, student, headers):
        # First thing is to check if a group is already created.
        # In case there is a session not created in edusign and this function has lunched a student creation or update
        # on empty group
        name = {
            "firstName": student.firstName if student.firstName else "No_firstName",
            "lastName": student.lastName if student.lastName else "No_lastName",
        }
        if not student.firstName or not student.lastName:
            splitName = self.splitName(student.name)
            print(splitName)
            name["firstName"] = splitName["firstName"]
            name["lastName"] = splitName["lastName"]

        firstName = name["firstName"]
        lastName = name["lastName"]
        print(
            "======================= firstName='%s' lastName='%s' name='%s' lastName='%s' "
            % (name["firstName"], name["lastName"], student.name, student.lastName)
        )

        nbAdd = 0
        nbEdit = 0
        url = "https://ext.edusign.fr/v1/student"
        result = ""
        checkStudent = self.checkExistance("https://ext.edusign.fr/v1/student/by-email/", student.email, headers)

        # -------------------------------------------------------------------------------
        edusignStudentID = ""
        print(checkStudent)
        if checkStudent:
            edusignStudentID = checkStudent["result"]["id"]
            # Student exists, we make a patch request.
            # We pass all info in data, in case there is an update.
            # We can optimise it later.
            url = "https://ext.edusign.fr/v1/student/?id=" + edusignStudentID

            # Check group id existance in the student groups.

            groups = checkStudent["result"]["GROUPS"]
            if self.id_group_edusign not in checkStudent["result"]["GROUPS"] or checkStudent["result"]["GROUPS"] == []:
                groups.append(self.id_group_edusign)

            if checkStudent["result"]["HIDDEN"] == 1:
                self.restoreStudent(edusignStudentID, student.email, headers)
            data = {
                "student": {
                    "ID": edusignStudentID,
                    "FIRSTNAME": firstName,
                    "LASTNAME": lastName,
                    "EMAIL": student.email,
                    "FILE_NUMBER": "",
                    "PHOTO": "",
                    "HIDDEN": 0,
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

            print(
                "addStudent() has launched a patch request for : %s %s %s"
                % (str(result), str(result.status_code), str(json.loads(result.text)))
            )
            _logger.info(
                "addStudent() has launched a patch request for : %s %s %s"
                % (str(result), str(result.status_code), str(json.loads(result.text)))
            )

            if result.status_code == 200:
                nbEdit = nbEdit + 1
        else:

            # students doesn't exist, we make a post request and create a new one.
            data = {
                "student": {
                    "FIRSTNAME": firstName,
                    "LASTNAME": lastName,
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
                }
            }

            # Add a new student
            result = requests.post(url, data=json.dumps(data), headers=headers)
            resultContent = json.loads(result.text)
            print("]]]]]]]]]]]]", firstName)

            print(
                "addStudent() has launched a post request for ",
                "FIRSTNAME",
                firstName,
                "LASTNAME",
                lastName,
                "EMAIL",
                student.email,
                "with results: ",
                result,
                result.status_code,
                result.text,
            )
            _logger.info(
                "addStudent() has launched a post request for FIRSTNAME '%s' LASTNAME '%s' EMAIL '%s' with results: {%s} {%s}"
                % (str(firstName), str(lastName), str(student.email), str(result), str(resultContent))
            )

            if result.status_code == 200 and "result" in resultContent:
                nbAdd = nbAdd + 1
                if "id" in resultContent["result"]:
                    edusignStudentID = resultContent["result"]["id"]
                elif "ID" in resultContent["result"]:
                    edusignStudentID = resultContent["result"]["ID"]
                else:
                    print("Please verify result id key in addStudent() response")
        return {"nbAdd": nbAdd, "nbEdit": nbEdit, "id": edusignStudentID}

    # This function takes a list of students IDs and update Groups
    def updateStudentLists(self, students, headers):

        # Check if a group exists with group ID
        checkGroup = self.checkExistance("https://ext.edusign.fr/v1/group/", self.id_group_edusign, headers)

        if checkGroup:
            url = "https://ext.edusign.fr/v1/group/?id=" + self.id_group_edusign

            data = {
                "group": {
                    "ID": self.id_group_edusign,
                    "NAME": self.name,
                    "DESCRIPTION": "",
                    "STUDENTS": students,
                    "API_ID": self.name,
                }
            }
            # Edit by student ID
            result = requests.patch(url, data=json.dumps(data), headers=headers)

            print(
                "updateStudentLists() has launched a patch request with a response : %s %s %s"
                % (str(result), str(result.status_code), str(result.text))
            )
            _logger.info(
                "updateStudentLists() has launched a patch request with a response : %s %s %s"
                % (str(result), str(result.status_code), str(result.text))
            )

        else:
            return False

    # Update Group exceot students Ids
    def updateGroup(self, headers):
        nbCount = {
            "nbAdd": 0,
            "nbEdit": 0,
        }
        # Call addgroup to check if group matches edusign with odoo

        nb = nbCount
        # Loop and add each student.
        # Create and update students
        studentsID = []
        for student in self.client_ids:

            nb = self.addStudent(student, headers)
            nbCount = {
                "nbAdd": nb["nbAdd"] + nbCount["nbAdd"],
                "nbEdit": nb["nbEdit"] + nbCount["nbEdit"],
            }
            # Fill students ID from edusign to update the group list
            studentsID.append(nb["id"])
        # Check if a group exists with group ID
        checkGroup = self.checkExistance("https://ext.edusign.fr/v1/group/", self.id_group_edusign, headers)

        if checkGroup:
            url = "https://ext.edusign.fr/v1/group/?id=" + self.id_group_edusign

            data = {
                "group": {
                    "ID": self.id_group_edusign,
                    "NAME": self.name,
                    "DESCRIPTION": "",
                    "STUDENTS": studentsID,
                    "API_ID": self.name,
                }
            }
            # Edit by student ID
            result = requests.patch(url, data=json.dumps(data), headers=headers)

            print(
                "updateGroup has launched() a patch request with a response : %s %s %s"
                % (str(result), str(result.status_code), str(result.text))
            )
            _logger.info(
                "updateGroup has launched() a patch request with a response : %s %s %s"
                % (str(result), str(result.status_code), str(result.text))
            )

        else:
            return False

    def addProfessor(self, professor, headers):
        firstName = ""
        lastName = ""
        # split name and surname
        name = {
            "firstName": professor.surveillant_id["name"] if professor.surveillant_id["name"] else "No_firstName",
            "lastName": professor.surveillant_id["name"] if professor.surveillant_id["name"] else "No_lastName",
        }

        if professor.surveillant_id["name"]:
            splitName = self.splitName(professor.surveillant_id["name"])
            print(splitName)
            name["firstName"] = splitName["firstName"]
            name["lastName"] = splitName["lastName"]

        firstName = name["firstName"]
        lastName = name["lastName"]
        # if not professor.surveillant_id.firstName or not professor.surveillant_id.lastName:
        #     splitName = self.splitName(professor)
        #     print(splitName)
        #     name["firstName"] = splitName["firstName"]
        #     name["lastName"] = splitName["lastName"]

        firstName = name["firstName"]
        lastName = name["lastName"]
        nbAdd = 0
        nbEdit = 0

        result = ""
        checkProfessor = self.checkExistance("https://ext.edusign.fr/v1/professor/by-email/", professor.email, headers)

        # -------------------------------------------------------------------------------
        url = ""
        if checkProfessor:

            # Professor exists, we make a patch request.
            # We pass all info in data, in case there is an update.
            # We can optimise it later to change only updated field.
            url = "https://ext.edusign.fr/v1/professor/?id=" + checkProfessor["result"]["id"]

            #

            data = {
                "professor": {
                    "ID": checkProfessor["result"]["id"],
                    "FIRSTNAME": firstName,
                    "LASTNAME": lastName,
                    "EMAIL": professor.email,
                    "PHONE": professor.phone,
                    "API_ID": professor.id,
                }
            }

            # Edit by professor ID
            result = requests.patch(url, data=json.dumps(data), headers=headers)

            print(
                "addProfessor() has launched a patch request for : %s %s %s"
                % (str(result), str(result.status_code), str(json.loads(result.text)))
            )
            _logger.info(
                "addProfessor() has launched a patch request for : %s %s %s"
                % (str(result), str(result.status_code), str(json.loads(result.text)))
            )

            if result.status_code == 200:
                nbEdit = nbEdit + 1

        # else:
        #     print(
        #         "Find a user with the same email %s but the ID=%s did not match with edusign external API ID=%s "
        #         % (str(professor.email), str(professor.id), str(checkProfessor["result"]["API_ID"]))
        #     )

        #     _logger.info(
        #         "Find a user with the same email %s but the ID=%s did not match with edusign external API ID=%s "
        #         % (str(professor.email), str(professor.id), str(checkProfessor["result"]["API_ID"]))
        #     )

        else:

            # professors doesn't exist, we make a post request and create a new one.
            url = "https://ext.edusign.fr/v1/professor"
            data = {
                "professor": {
                    "FIRSTNAME": firstName,
                    "LASTNAME": lastName,
                    "EMAIL": professor.email,
                    "FILE_NUMBER": "",
                    "PHOTO": "",
                    "PHONE": professor.phone,
                    "GROUPS": [self.id_group_edusign],
                    "TRAINING_NAME": self.diplome_vise,
                    "COMPANY": "",
                    "TAGS": ["DIGIMOOV"],
                    "SEND_EMAIL_CREDENTIALS": "",
                    "API_ID": professor.id,
                    "API_TYPE": "",
                    "BADGE_ID": "",
                }
            }

            # Add a new professor
            result = requests.post(url, data=json.dumps(data), headers=headers)
            print(
                "addProfessor() has launched a patch request for ",
                "FIRSTNAME",
                firstName,
                "LASTNAME",
                lastName,
                "EMAIL",
                professor.email,
                "with results: ",
                result,
                result.status_code,
                result.text,
            )
            _logger.info(
                "addProfessor() has launched a patch request for ",
                "FIRSTNAME",
                firstName,
                "LASTNAME",
                lastName,
                "EMAIL",
                professor.email,
                "with results: ",
                result,
                result.status_code,
                json.loads(result.text),
            )
            if result.status_code == 200:
                nbAdd = nbAdd + 1
        return {"nbAdd": nbAdd, "nbEdit": nbEdit}

    # Get a name and split it into firstname and lastname
    def splitName(self, name):
        firstName = "No_firstName"
        lastName = "No_lastName"
        if name == "":
            firstName = name
            lastName = name
        # Cas d'un nom composé
        else:
            if " " in name:
                nameCopy = name
                nameCopy = " ".join(name.split())
                nameCopy = name.split(" ", 1)
                if nameCopy:
                    firstName = nameCopy[0]
                    lastName = nameCopy[1]

            # Cas d'un seul nom
            else:
                firstName = name
                lastName = name

        return {"firstName": firstName, "lastName": lastName}

    def allowExecution(self):
        # if not in localhost
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        checkDate = True
        checkUrl = str(base_url) in allowedUrls
        if self.date_exam:
            checkDate = date.today() <= self.date_exam
        print(
            "Edusign allowExecution() has checked date.today() <= date.exam = %s and base url=%s is allowed to execute API calls = %s"
            % (str(checkDate), str(base_url), str(checkUrl))
        )
        _logger.info(
            "Edusign allowExecution() has checked date.today() <= date.exam = %s and base url=%s is allowed to execute API calls = %s"
            % (str(checkDate), str(base_url), str(checkUrl))
        )
        return checkUrl and checkDate

    # Add a new group to a Professor passed in parameters and add a new group using Edit a professor's variable

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
        if self.allowExecution():
            print(
                "################## ################## ################## ################## ################## ##################\n"
                "#################                                                                              ##################\n"
                "#################                    Edusign Main Function has executed.                        ##################\n"
                "#################                                                                              ##################\n"
                "################## ################## ################## ################## ################## ##################\n"
            )
            _logger.info(
                "\n"
                + "################## ################## ################## ################## ################## ##################\n"
                "#################                                                                              ##################\n"
                "#################                   Edusign Main Function has executed.                        ##################\n"
                "#################                                                                              ##################\n"
                "################## ################## ################## ################## ################## ##################\n"
            )

            # Get edusign api key
            company = self.env["res.company"].sudo().search([("id", "=", 2)], limit=1)
            if company:
                api_key = company.edusign_api_key
                if not api_key:
                    _logger.info("Please add edusign api_key")
                    return

                headers = {
                    "Authorization": "Bearer %s" % (str(api_key)),
                    "Content-Type": "application/json",
                    "cache-control": "no-cache",
                }
                for res in self:
                    check = self.checkExistance("https://ext.edusign.fr/v1/group/", res.id_group_edusign, headers)
                    if not check:
                        print("Trying to add the group %s on Edusign with API ID %s : " % (str(res.name), str(res.id)))
                        _logger.info(
                            "Trying to add the group %s on Edusign with API ID %s : " % (str(res.name), str(res.id))
                        )
                        # Addgroup
                        self.addGroup(res, headers)
                    else:
                        print(
                            "The group '%s' with the ID '%s' already exists"
                            % (str(res.name), str(res.id_group_edusign))
                        )
                        _logger.info(
                            "The group '%s' with the ID '%s' already exists"
                            % (str(res.name), str(res.id_group_edusign))
                        )

                    nbCount = {
                        "nbAdd": 0,
                        "nbEdit": 0,
                    }
                    nb = nbCount
                    # Loop and add each student.
                    # Create and update students
                    studentsID = []
                    for student in res.client_ids:

                        nb = self.addStudent(student, headers)
                        nbCount = {
                            "nbAdd": nb["nbAdd"] + nbCount["nbAdd"],
                            "nbEdit": nb["nbEdit"] + nbCount["nbEdit"],
                        }
                        # Fill students ID from edusign to update the group list
                        studentsID.append(nb["id"])

                    print("Edusign Students ID in this session", studentsID)
                    _logger.info("Edusign Students ID in this session %s" % str(studentsID))
                    # Make an update to students Lists
                    self.updateStudentLists(studentsID, headers)

                    # iterate self in case it returns more than one object.
                    # get professor ID to create a course
                    professorsId = []
                    nbCountProfessor = {
                        "nbAdd": 0,
                        "nbEdit": 0,
                    }

                    # create and update professor
                    for surveillant in res.surveillant_id:

                        # nb = self.addStudent(surveillant, headers)
                        if surveillant:

                            professorsId.append(surveillant.id)

                            nb = self.addProfessor(surveillant, headers)

                        nbCountProfessor = {
                            "nbAdd": nb["nbAdd"] + nbCountProfessor["nbAdd"],
                            "nbEdit": nb["nbEdit"] + nbCountProfessor["nbEdit"],
                        }

                    # If  ProfessorsId[] is empty we can not create a course.
                    if professorsId:
                        self.addCourse(res, professorsId, headers)
                    else:
                        print(
                            "\n\nImpossible to create a Course, Please assign Professor to the session "
                            + res.name
                            + "\n\n"
                        )
                        _logger.info(
                            "\n\nImpossible to create a Course, Please assign Professor to the session "
                            + res.name
                            + "\n\n"
                        )

                    print(str(nbCount["nbAdd"]) + " client(s) gagné(s) sont ajoutes a la session " + res.name)
                    _logger.info(str(nbCount["nbAdd"]) + " client(s) gagné(s) sont ajoutes a la session " + res.name)
                    print(str(nbCount["nbEdit"]) + " client(s) gagné(s) sont modifies dans la session " + res.name)
                    _logger.info(
                        str(nbCount["nbEdit"]) + " client(s) gagné(s) sont modifies dans la session " + res.name
                    )

                    print(
                        "################## ################## ################## ################## ################## ##################\n"
                        "#################                                                                              ##################\n"
                        "#################                   Edusign Main Function has finished.                        ##################\n"
                        "#################                                                                              ##################\n"
                        "################## ################## ################## ################## ################## ##################\n"
                    )
                    _logger.info(
                        "\n"
                        + "################## ################## ################## ################## ################## ##################\n"
                        "#################                                                                              ##################\n"
                        "#################                   Edusign Main Function has finished.                        ##################\n"
                        "#################                                                                              ##################\n"
                        "################## ################## ################## ################## ################## ##################\n"
                    )
                else:
                    print("Exit Main edusign because Allow function has returned False. ")
                    _logger.info("Exit Main edusign because Allow function has returned False. ")

    # @api.model
    # def create(self, vals):
    #     print(
    #         "################## ################## ################## ################## ################## ##################\n"
    #         "#################                                                                              ##################\n"
    #         "#################                   Edusign Create Function has executed.                        ##################\n"
    #         "#################                                                                              ##################\n"
    #         "################## ################## ################## ################## ################## ##################\n"
    #     )
    #     _logger.info(
    #         "\n"
    #         + "################## ################## ################## ################## ################## ##################\n"
    #         "#################                                                                              ##################\n"
    #         "#################                   Edusign Create Function has executed.                        ##################\n"
    #         "#################                                                                              ##################\n"
    #         "################## ################## ################## ################## ################## ##################\n"
    #     )
    #     res = super(mcmSession, self).create(vals)
    #     _logger.info("create session %s : " % (str(res)))
    #     company = self.env["res.company"].sudo().search([("id", "=", 2)], limit=1)
    #     if self.allowExecution():
    #         if company:
    #             api_key = company.edusign_api_key
    #             if not api_key:
    #                 _logger.info("Please add edusign api_key")
    #                 return
    #             headers = {
    #                 "Authorization": "Bearer %s" % (str(api_key)),
    #                 "Content-Type": "application/json",
    #             }
    #             print("Run addGroup() from create function.")
    #             _logger.info("Run addGroup() from create function.")
    #             self.addGroup(res, headers)
    #         return res
    #     else:
    #         return res

    # def write(self, vals):

    #     print(
    #         "################## ################## ################## ################## ################## ##################\n"
    #         "#################                                                                              ##################\n"
    #         "#################                   Edusign Write Function has executed.                        ##################\n"
    #         "#################                                                                              ##################\n"
    #         "################## ################## ################## ################## ################## ##################\n"
    #     )
    #     _logger.info(
    #         "\n"
    #         + "################## ################## ################## ################## ################## ##################\n"
    #         "#################                                                                              ##################\n"
    #         "#################                   Edusign Write Function has executed.                        ##################\n"
    #         "#################                                                                              ##################\n"
    #         "################## ################## ################## ################## ################## ##################\n"
    #     )
    #     res = super(mcmSession, self).write(vals)
    #     if self.allowExecution():
    #         company = self.env["res.company"].sudo().search([("id", "=", 2)], limit=1)
    #         if company:
    #             api_key = company.edusign_api_key
    #             if not api_key:
    #                 _logger.info("Please add edusign api_key")
    #                 return
    #             headers = {
    #                 "Authorization": "Bearer %s" % (str(api_key)),
    #                 "Content-Type": "application/json",
    #             }

    #             nbCount = {
    #                 "nbAdd": 0,
    #                 "nbEdit": 0,
    #             }
    #             # Call addgroup to check if group matches edusign with odoo

    #             nb = nbCount
    #             # Loop and add each student.
    #             # Create and update students
    #             studentsID = []
    #             # check if Students list has been updated
    #             if "name" in vals:
    #                 self.addGroup(self, headers)
    #                 self.updateGroup(headers)
    #             if "client_ids" in vals:
    #                 self.addGroup(self, headers)
    #                 print("Students list has been updated from session.")
    #                 _logger.info("Students list has been updated from session")

    #                 for student in self.client_ids:

    #                     nb = self.addStudent(student, headers)
    #                     nbCount = {
    #                         "nbAdd": nb["nbAdd"] + nbCount["nbAdd"],
    #                         "nbEdit": nb["nbEdit"] + nbCount["nbEdit"],
    #                     }
    #                     # Fill students ID from edusign to update the group list
    #                     studentsID.append(nb["id"])
    #                 print("Edusign Students ID in this session", studentsID)
    #                 _logger.info("Edusign Students ID in this session %s = %s" % (str(self.name), str(studentsID)))
    #                 # Make an update to students Lists
    #                 self.updateStudentLists(studentsID, headers)

    #             if "surveillant_id" in vals or "session_adresse_examen" in vals:
    #                 # Professor list has been updated
    #                 # Create professor if not exist and Launch create course
    #                 # get professor ID to create a course
    #                 self.addGroup(self, headers)
    #                 professorsId = []
    #                 nbCountProfessor = {
    #                     "nbAdd": 0,
    #                     "nbEdit": 0,
    #                 }

    #                 # create and update professor
    #                 for surveillant in self.surveillant_id:
    #                     print(surveillant.id)
    #                     # nb = self.addStudent(surveillant, headers)
    #                     if surveillant:

    #                         professorsId.append(surveillant.id)

    #                         nb = self.addProfessor(surveillant, headers)

    #                     nbCountProfessor = {
    #                         "nbAdd": nb["nbAdd"] + nbCountProfessor["nbAdd"],
    #                         "nbEdit": nb["nbEdit"] + nbCountProfessor["nbEdit"],
    #                     }

    #                 # If  ProfessorsId[] is empty we can not create a course.
    #                 if professorsId:
    #                     self.addCourse(self, professorsId, headers)
    #                 else:
    #                     print(
    #                         "\n\nImpossible to create a Course, Please assign Professor to the session "
    #                         + self.name
    #                         + "\n\n"
    #                     )
    #                     _logger.info(
    #                         "\n\nImpossible to create a Course, Please assign Professor to the session "
    #                         + self.name
    #                         + "\n\n"
    #                     )
    #         return res
    #     else:
    #         return res
