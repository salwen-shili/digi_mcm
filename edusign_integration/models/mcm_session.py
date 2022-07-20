# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from asyncio.log import logger
from distutils.command.build_scripts import first_line_re
import email
from http import client
from pickle import APPEND
from posixpath import split
from tabnanny import check
from unittest import result
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv import osv
from urllib import parse


from datetime import date, datetime
import requests
import logging
import json

_logger = logging.getLogger(__name__)


class mcmSession(models.Model):
    _inherit = "mcmacademy.session"
    id_group_edusign = fields.Char(string="ID Group Edusign", readonly=True)
    # Course API ID
    id_session_edusign = fields.Char(string="ID Session Edusign", readonly=True)
    # session_verouille = fields.Char(string="ID Session Edusign", readonly=True)

    # Create a new Course only if a course does not exist in edusign.
    # Patching a course will erase existing signatures.
    # We check if exam_date > today to allow patch request
    def addCourse(self, session, professorsEmails, headers):

        # Exit add course if professor ID is empty
        classroom = session.session_adresse_examen.adresse_centre_examen
        if classroom == False:
            classroom = ""

        if len(professorsEmails) == 0:
            return
        professor1 = ""
        professor2 = ""
        if len(professorsEmails) > 0:
            # Use checkExistance to get Professor ID by API ID
            checkProfessor = self.checkExistance(
                "https://ext.edusign.fr/v1/professor/by-email/", professorsEmails[0], headers
            )
            if "status" in checkProfessor:
                if checkProfessor["status"] == "success":
                    professor1 = checkProfessor["result"]["ID"]
                if len(professorsEmails) == 2:
                    checkProfessor = self.checkExistance(
                        "https://ext.edusign.fr/v1/professor/by-email/", professorsEmails[1], headers
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

        if checkCrouse:
            print("A course with the same ID exists already.")
            _logger.info("A course with the same ID exists already.")
            # We check if exam_date >= today to allow patch request
            editCourse = (
                checkCrouse["result"]["NAME"] != session.name
                or checkCrouse["result"]["CLASSROOM"] != classroom
                or checkCrouse["result"]["START"] != startDate
                or checkCrouse["result"]["END"] != endDate
                or checkCrouse["result"]["PROFESSOR"] != professor1
                or checkCrouse["result"]["PROFESSOR_2"] != professor2
                or checkCrouse["result"]["SCHOOL_GROUP"] != [session.id_group_edusign]
                or checkCrouse["result"]["API_ID"] != session.name
            )
            print(
                checkCrouse["result"]["NAME"] != session.name,
                checkCrouse["result"]["CLASSROOM"] != classroom,
                checkCrouse["result"]["START"] != startDate,
                checkCrouse["result"]["END"] != endDate,
                checkCrouse["result"]["PROFESSOR"] != professor1,
                checkCrouse["result"]["PROFESSOR_2"] != professor2,
                checkCrouse["result"]["SCHOOL_GROUP"] != [session.id_group_edusign],
                checkCrouse["result"]["API_ID"] != session.name,
            )

            if editCourse:
                # -------------------------------------------------------------------------------
                if date.today() <= session.date_exam:
                    print(
                        "Today = %s <= Exam date = %s, launching a patch request"
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
                return

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
                    print("Edusign addCourse() response :%s " % (str(resultContent),))
                    _logger.info("Edusign addCourse() response :%s " % (str(resultContent),))
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
        if self.allowExecution("from addGroup()") == False:
            _logger.info("Edusign addGroup exit by the function allowExecution")
            return
        result = ""
        checkGroup = self.checkExistance("https://ext.edusign.fr/v1/group/get-id/", session.name, headers)

        # -------------------------------------------------------------------------------
        edusignGroupID = ""

        if checkGroup:
            if "id" in checkGroup["result"]:
                if checkGroup["result"]["id"] != edusignGroupID:
                    edusignGroupID = checkGroup["result"]["id"]
                    print(
                        "Edusign addGroup updated the session %s with edusignGroupID='%s'..."
                        % (str(session.name), str(edusignGroupID))
                    )
                    _logger.info(
                        "Edusign addGroup updated the session %s with edusignGroupID='%s'..."
                        % (str(session.name), str(edusignGroupID))
                    )
            elif "ID" in checkGroup["result"]:
                if checkGroup["result"]["ID"] != edusignGroupID:
                    edusignGroupID = checkGroup["result"]["ID"]
                    print(
                        "Edusign addGroup updated the session %s with edusignGroupID='%s'..."
                        % (str(session.name), str(edusignGroupID))
                    )
                    _logger.info(
                        "Edusign addGroup updated the session %s with edusignGroupID='%s'..."
                        % (str(session.name), str(edusignGroupID))
                    )
            else:
                print("Please check the id key in addGroup() from checkExistance response.")

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
                print("Edusign Add a group response  %s: " % (str(resultContent)))
                _logger.info("Edusign Add a group response  %s: " % (str(resultContent)))
                if resultContent["status"] == "success":

                    if "id" in resultContent["result"]:
                        edusignGroupID = resultContent["result"]["id"]
                    elif "ID" in resultContent["result"]:
                        edusignGroupID = resultContent["result"]["ID"]
                    else:
                        print("Please verify result id key in addGroup() response")
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

        getResult = requests.get(url + str(value), headers=headers)
        getContent = json.loads(getResult.text)
        # check if group already exist

        check = True if getContent["status"] == "success" else False
        print("checkExistence() function url request: %s with response: %s" % (url + str(value), str(check)))
        _logger.info("checkExistence() function url request: %s with response: %s" % (url + str(value), str(check)))

        if check:
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

        if self.allowExecution("from addStudent()") == False:
            _logger.info("Edusign addStudent exit by the function allowExecution")
            return
        # First thing is to check if a group is already created.
        # In case there is a session not created in edusign and this function has lunched a student creation or update
        # on empty group
        if self.id_group_edusign == False:
            self.addGroup(self, headers)
        # Slipt name
        name = {
            "firstName": student.firstName if student.firstName else "No_firstName",
            "lastName": student.lastName if student.lastName else "No_lastName",
        }
        if not student.firstName or not student.lastName:

            splitName = self.splitName(student.name)
            name["firstName"] = splitName["firstName"]
            name["lastName"] = splitName["lastName"]

        firstName = (
            name["firstName"] + " (" + str(student.code_evalbox) + ")" if student.code_evalbox else name["firstName"]
        )
        lastName = name["lastName"]

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
            editStudent = (
                checkStudent["result"]["GROUPS"] != groups
                or checkStudent["result"]["FIRSTNAME"] != firstName
                or checkStudent["result"]["LASTNAME"] != lastName
                or checkStudent["result"]["PHONE"] != student.phone
                or checkStudent["result"]["TRAINING_NAME"] != self.diplome_vise
                or checkStudent["result"]["API_ID"] != str(student.id)
            )
            print(
                checkStudent["result"]["GROUPS"] != groups,
                checkStudent["result"]["FIRSTNAME"] != firstName,
                checkStudent["result"]["LASTNAME"] != lastName,
                checkStudent["result"]["PHONE"] != student.phone,
                checkStudent["result"]["TRAINING_NAME"] != self.diplome_vise,
                checkStudent["result"]["API_ID"] != str(student.id),
            )
            _logger.info(
                "%s %s %s %s %s %s"
                % (
                    str(checkStudent["result"]["GROUPS"] != groups),
                    str(checkStudent["result"]["FIRSTNAME"] != firstName),
                    str(checkStudent["result"]["LASTNAME"] != lastName),
                    str(checkStudent["result"]["PHONE"] != student.phone),
                    str(checkStudent["result"]["TRAINING_NAME"] != self.diplome_vise),
                    str(checkStudent["result"]["API_ID"] != student.id),
                )
            )

            # Edit by student ID
            if editStudent:
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

                result = requests.patch(url, data=json.dumps(data), headers=headers)

                print(
                    "addStudent() has launched a patch request with a response : %s %s %s"
                    % (str(result), str(result.status_code), str(json.loads(result.text)))
                )
                _logger.info(
                    "addStudent() has launched a patch request with a response : %s %s %s"
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

            print(
                "addStudent() has launched a post request for FIRSTNAME '%s' LASTNAME '%s' EMAIL '%s' with results: {%s} {%s}"
                % (str(firstName), str(lastName), str(student.email), str(result), str(resultContent))
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
        if self.allowExecution("from updateStudentLists()") == False:
            _logger.info("Edusign addStudent exit by the function allowExecution")
            return
        # Check if a group exists with group ID
        _logger.info("updateStudentLists()...")
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
            if checkGroup["result"]["STUDENTS"] != students:
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
        if self.allowExecution("from addProfessor()") == False:
            _logger.info("Edusign addStudent exit by the function allowExecution")
            return
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
                "addProfessor() has launched a post request for",
                professor.id,
                " FIRSTNAME",
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
                "addProfessor() has launched a post request for",
                professor.id,
                " FIRSTNAME",
                firstName,
                "LASTNAME",
                lastName,
                "EMAIL",
                professor.email,
                "with results: ",
                result,
                result.status_code,
                str(result.text),
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
                nameCopy = nameCopy.split(" ", 1)
                if nameCopy:
                    firstName = nameCopy[0]
                    lastName = nameCopy[1]

            # Cas d'un seul nom
            else:
                firstName = name
                lastName = name

        return {"firstName": firstName, "lastName": lastName}

    def allowExecution(self, func):
        # if not in localhost
        if self.date_exam == False:
            print("Session %s has a date_exam= %s" % (str(self.name), str(self.date_exam)))
            _logger.info("Session %s has a date_exam= %s" % (str(self.name), str(self.date_exam)))
            return False

        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        checkDate = True
        # checkUrl = True
        checkUrl = "localhost" not in str(base_url) and "dev.odoo" not in str(base_url)
        if self.date_exam:
            checkDate = date.today() <= self.date_exam
        print(
            "Edusign allowExecution() %s has checked %s date.today() <= %s = %s and base url=%s is allowed to execute API calls = %s"
            % (str(func), str(self.name), str(self.date_exam), str(checkDate), str(base_url), str(checkUrl))
        )
        _logger.info(
            "Edusign allowExecution() %s has checked %s date.today() <= %s = %s and base url=%s is allowed to execute API calls = %s"
            % (str(func), str(self.name), str(self.date_exam), str(checkDate), str(base_url), str(checkUrl))
        )
        return checkUrl and checkDate

    def allowGetPresence(self, func):
        # if not in localhost
        if self.date_exam == False:
            print("Session %s has a date_exam= %s" % (str(self.name), str(self.date_exam)))
            _logger.info("Session %s has a date_exam= %s" % (str(self.name), str(self.date_exam)))
            return False

        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        checkDate = True
        checkUrl = True
        # checkUrl = "localhost" not in str(base_url) and "dev.odoo" not in str(base_url)
        if self.date_exam:
            checkDate = date.today() >= self.date_exam
        print(
            "Edusign allowGetPresence() %s has checked %s date.today() >= %s = %s and base url=%s is allowed to execute API calls = %s"
            % (str(func), str(self.name), str(self.date_exam), str(checkDate), str(base_url), str(checkUrl))
        )
        _logger.info(
            "Edusign allowGetPresence() %s has checked %s date.today() >= %s = %s and base url=%s is allowed to execute API calls = %s"
            % (str(func), str(self.name), str(self.date_exam), str(checkDate), str(base_url), str(checkUrl))
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

    # All logics are here for the button "Envoyer a edusign"
    def sendToEdusign(self):
        if self.allowExecution("from sendToEdusign") == True:
            print(
                "################## ################## ################## ################## ################## ##################\n"
                "#################                                                                              ##################\n"
                "#################                    Edusign sendToEdusign() Function has executed.                        ##################\n"
                "#################                                                                              ##################\n"
                "################## ################## ################## ################## ################## ##################\n"
            )
            _logger.info(
                "\n"
                + "################## ################## ################## ################## ################## ##################\n"
                "#################                                                                              ##################\n"
                "#################                   Edusign sendToEdusign() Function has executed.                        ##################\n"
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
                        print(
                            "Trying to add the group %s on Edusign with API ID %s : " % (str(res.name), str(res.name))
                        )
                        _logger.info(
                            "Trying to add the group %s on Edusign with API ID %s : " % (str(res.name), str(res.name))
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
                    professorsEmails = []
                    nbCountProfessor = {
                        "nbAdd": 0,
                        "nbEdit": 0,
                    }

                    # create and update professor
                    for surveillant in res.surveillant_id:

                        # nb = self.addStudent(surveillant, headers)
                        if surveillant:

                            professorsEmails.append(surveillant.email)

                            nb = self.addProfessor(surveillant, headers)

                        nbCountProfessor = {
                            "nbAdd": nb["nbAdd"] + nbCountProfessor["nbAdd"],
                            "nbEdit": nb["nbEdit"] + nbCountProfessor["nbEdit"],
                        }

                    # If  ProfessorsId[] is empty we can not create a course.
                    if professorsEmails:
                        self.addCourse(res, professorsEmails, headers)
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
                    print(str(nbCount["nbEdit"]) + " client(s) gagné(s) sont modifiés dans la session " + res.name)
                    _logger.info(
                        str(nbCount["nbEdit"]) + " client(s) gagné(s) sont modifiés dans la session " + res.name
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
                    _logger.info("Exit Main edusign because Allow function ha returned False. ")
        else:
            _logger.info("Edusign main function has exit by the allowExecution()")

    # Make get/post/patch request
    def sendRequest(self, type, url, headers, payload=False):
        getResult = ""
        if type == "get":
            getResult = requests.get(url, headers=headers)
        elif type == "post":
            getResult = requests.post(url, payload, headers=headers)
        elif type == "patch":
            getResult = requests.get(url, payload, headers=headers)
        else:
            return False

        getContent = json.loads(getResult.text)
        # check if the request state is sucess

        check = (
            True
            if getContent["status"] == "success"
            or getContent["status"] == "error"
            and getContent["message"] == "Course already locked"
            else False
        )

        print("%s request url : %s with response: \n%s" % (str(type), str(url), str(getContent)))
        _logger.info("%s request url: %s with response: \n%s" % (str(type), str(url), str(getContent)))

        if check:
            return getContent
        else:
            return False

    # Write Exam Line
    # Get student ID from API
    # Search student id in odoo
    # if found will search if we have already a line exam
    # if line exam found will update it if presence is different else will create a new one
    def writeExamLine(self, session, student, headers):

        resultContent = self.sendRequest(
            "get",
            "https://ext.edusign.fr/v1/student/{}".format(student["studentId"]),
            headers,
        )
        if resultContent:
            id = resultContent["result"]["API_ID"]
            partner = self.env["res.partner"].sudo().search([("id", "=", int(id))])
            if partner:

                exam = partner.note_exam_id
                presence = "present" if student["state"] else "Absent"
                print(
                    "partner_id",
                    partner.id,
                    "session_id",
                    partner.mcm_session_id.id,
                    "module_id",
                    partner.module_id.id,
                    "date_exam",
                    partner.mcm_session_id.date_exam,
                    "ville_id",
                    "presence",
                    presence,
                    session.session_ville_id.id,
                )
                _logger.info(
                    "partner_id",
                    partner.id,
                    "session_id",
                    partner.mcm_session_id.id,
                    "module_id",
                    partner.module_id.id,
                    "date_exam",
                    partner.mcm_session_id.date_exam,
                    "ville_id",
                    "presence",
                    presence,
                    session.session_ville_id.id,
                )
                # search for existance
                examLines = (
                    self.env["info.examen"]
                    .sudo()
                    .search(
                        [
                            ("partner_id", "=", partner.id),
                            ("session_id", "=", partner.mcm_session_id.id),
                        ],
                        order="id desc",
                    )
                )
                print("print (examLines)", examLines)
                _logger.info("print (examLines)", examLines)

                if not examLines:

                    exam.sudo().create(
                        {
                            "partner_id": partner.id,
                            "session_id": partner.mcm_session_id.id,
                            "module_id": partner.module_id.id,
                            "date_exam": partner.mcm_session_id.date_exam,
                            "presence": presence,
                            "ville_id": session.session_ville_id.id,
                        }
                    )
                    print("print (after if not examLines)", examLines)
                    _logger.info("No lines => Exam line created ")
                    
                else:
                    for line in examLines:
                        _logger.info("if line.presence != presence %s and line.date_exam == partner.mcm_session_id.date_exam %s" %(str(line.presence != presence),str(line.date_exam == partner.mcm_session_id.date_exam)))
                        if line.presence != presence and line.date_exam == partner.mcm_session_id.date_exam:
                            line.presence = presence
                            print("Update presence in the same line. ")
                            _logger.info("Update presence in the same line. ")
                        else:
                            
                            exam.sudo().create(
                                {
                                    "partner_id": partner.id,
                                    "session_id": partner.mcm_session_id.id,
                                    "module_id": partner.module_id.id,
                                    "date_exam": partner.mcm_session_id.date_exam,
                                    "presence": presence,
                                    "ville_id": session.session_ville_id.id,
                                }
                            )
                            
                            print("else line.presence != presence and line.date_exam == partner.mcm_session_id.date_exam:")
                            _logger.info("else line.presence != presence and line.date_exam == partner.mcm_session_id.date_exam:")
                            
        else:
            print("Student with id %s does not exist" % (str(student["studentId"])))
            _logger.info("Student with id %s does not exist" % (str(student["studentId"])))
            return

    def lockCourse(self, session, headers):
        locked = self.sendRequest(
            "get", "https://ext.edusign.fr/v1/course/lock/{}".format(session.id_session_edusign), headers
        )

        if locked and "status" in locked:
            if locked["status"] == "success":
                # get url
                url = locked["result"]["link"]
                self.urlToirAttachement(session, url)

            return True
        else:
            print(
                "Error while locking the course %s with edusign course id %s"
                % (session.name, str(session.id_session_edusign))
            )
            return False

    def urlToirAttachement(self, session, url):
        _logger.info("Trying to Add url=%s to ir attachement.", url)
        attachment_obj = self.env["ir.attachment"]
        fileUrl = parse.urlparse(url)

        if not fileUrl.scheme:
            fileUrl = parse.urlparse("{}{}".format("http://", fileUrl))
        attachment = {
            "name": "Feuille_d'émargement_{}".format(session.name),
            "type": "url",
            "url": fileUrl.geturl(),
            "res_id": session.id,
            "res_model": "mcmacademy.session",
        }
        attachment_obj.create(attachment)

    # All logics are here for the button "Recuperer feuille de presence"
    def getPresenceList(self):
        if self.allowGetPresence("getPresenceList()") == True:
            print(
                "################## ################## ################## ################## ################## ##################\n"
                "#################                                                                               #################\n"
                "#################                    Edusign getPresenceList() Function has executed.           #################\n"
                "#################                                                                               #################\n"
                "################## ################## ################## ################## ################## ##################\n"
            )
            _logger.info(
                "\n"
                + "################## ################## ################## ################## ################## ##################\n"
                "#################                                                                               #################\n"
                "#################                   Edusign getPresenceList() Function has executed.            #################\n"
                "#################                                                                               #################\n"
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
                    course = self.sendRequest(
                        "get", "https://ext.edusign.fr/v1/course/{}".format(res.id_session_edusign), headers
                    )
                    # lock course and get presence file url
                    # Download and add presence sheet to ir attachement
                    lockCourse = self.lockCourse(res, headers)
                    print("=========", lockCourse)
                    if lockCourse:
                        if course and "STUDENTS" in course["result"]:
                            # get presence and write exam lines
                            studentsList = course["result"]["STUDENTS"]
                            for student in studentsList:
                                # Write an exam line
                                self.writeExamLine(res, student, headers)

                        else:
                            print("Edusign getPresence function exit! Course ID is null!")
                            _logger.info("Edusign getPresence function exit! Course ID is null!")
                            return

        else:
            _logger.info("Edusign main function has exit by the allowExecution()")

        # # Create function
        # @api.model
        # def create(self, vals):
        #     allow = self.allowExecution("from create()")
        #     if allow == False:
        #         _logger.info("Edusign create function exit by the function allowExecution")
        #         return super(mcmSession, self).create(vals)
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
        #     if allow:
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

        # res = super(mcmSession, self).write(vals)

        # if self.allowExecution("from write()") == True:
        #     print(
        #         "################## ################## ################## ################## ################## ##################\n"
        #         "#################                                                                              ##################\n"
        #         "#################                   Edusign Write Function has executed.                       ##################\n"
        #         "#################                                                                              ##################\n"
        #         "################## ################## ################## ################## ################## ##################\n"
        #     )
        #     _logger.info(
        #         "\n"
        #         + "################## ################## ################## ################## ################## ##################\n"
        #         "#################                                                                              ##################\n"
        #         "#################                   Edusign Write Function has executed.                       ##################\n"
        #         "#################                                                                              ##################\n"
        #         "################## ################## ################## ################## ################## ##################\n"
        #     )

        #     company = self.env["res.company"].sudo().search([("id", "=", 2)], limit=1)
        #     if company:
        #         api_key = company.edusign_api_key
        #         if not api_key:
        #             _logger.info("Please add edusign api_key")
        #             return
        #         headers = {
        #             "Authorization": "Bearer %s" % (str(api_key)),
        #             "Content-Type": "application/json",
        #         }

        #         if not self.id_group_edusign:
        #             self.addGroup(self, headers)

        #         nbCount = {
        #             "nbAdd": 0,
        #             "nbEdit": 0,
        #         }
        #         # Call addgroup to check if group matches edusign with odoo

        #         nb = nbCount
        #         # Loop and add each student.
        #         # Create and update students
        #         studentsID = []
        #         # check if Students list has been updated
        #         if "name" in vals:

        #             self.updateGroup(headers)
        #         if "client_ids" in vals:

        #             for student in self.client_ids:

        #                 nb = self.addStudent(student, headers)
        #                 nbCount = {
        #                     "nbAdd": nb["nbAdd"] + nbCount["nbAdd"],
        #                     "nbEdit": nb["nbEdit"] + nbCount["nbEdit"],
        #                 }
        #                 # Fill students ID from edusign to update the group list
        #                 studentsID.append(nb["id"])
        #             print("Edusign Students ID in this session", studentsID)
        #             _logger.info("Edusign Students ID in this session %s = %s" % (str(self.name), str(studentsID)))
        #             # Make an update to students Lists
        #             print(self.surveillant_id)
        #             if self.updateStudentLists(studentsID, headers):
        #                 print("Students list has been updated from session.")
        #                 _logger.info("Students list has been updated from session")
        #                 professorsEmails = []
        #                 nbCountProfessor = {
        #                     "nbAdd": 0,
        #                     "nbEdit": 0,
        #                 }

        #                 # create and update professor
        #                 for surveillant in self.surveillant_id:
        #                     print(surveillant.id)
        #                     # nb = self.addStudent(surveillant, headers)
        #                     if surveillant:

        #                         professorsEmails.append(surveillant.email)

        #                         nb = self.addProfessor(surveillant, headers)

        #                     nbCountProfessor = {
        #                         "nbAdd": nb["nbAdd"] + nbCountProfessor["nbAdd"],
        #                         "nbEdit": nb["nbEdit"] + nbCountProfessor["nbEdit"],
        #                     }

        #                 # If  ProfessorsId[] is empty we can not create a course.
        #                 if professorsEmails:
        #                     self.addCourse(self, professorsEmails, headers)
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

        #         if "surveillant_id" in vals or "session_adresse_examen" in vals:
        #             # Professor list has been updated
        #             # Create professor if not exist and Launch create course
        #             # get professor ID to create a course

        #             professorsEmails = []
        #             nbCountProfessor = {
        #                 "nbAdd": 0,
        #                 "nbEdit": 0,
        #             }

        #             # create and update professor
        #             for surveillant in self.surveillant_id:
        #                 print(surveillant.id)
        #                 # nb = self.addStudent(surveillant, headers)
        #                 if surveillant:

        #                     professorsEmails.append(surveillant.email)

        #                     nb = self.addProfessor(surveillant, headers)

        #                 nbCountProfessor = {
        #                     "nbAdd": nb["nbAdd"] + nbCountProfessor["nbAdd"],
        #                     "nbEdit": nb["nbEdit"] + nbCountProfessor["nbEdit"],
        #                 }

        #             # If  ProfessorsId[] is empty we can not create a course.
        #             if professorsEmails:
        #                 self.addCourse(self, professorsEmails, headers)
        #             else:
        #                 print(
        #                     "\n\nImpossible to create a Course, Please assign Professor to the session "
        #                     + self.name
        #                     + "\n\n"
        #                 )
        #                 _logger.info(
        #                     "\n\nImpossible to create a Course, Please assign Professor to the session "
        #                     + self.name
        #                     + "\n\n"
        #                 )
        #     return res
        # else:
        #     return res
