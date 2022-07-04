import json
import locale
import re

import requests

from datetime import datetime
from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


class InheritMcmacademySession(models.Model):
    _inherit = "mcmacademy.session"

    def notif_rainbow_man(self, message):
        print("notif_rainbow_man")
        """ Function of notification, it will be used many time just when u 
         call the function put message like value with your "texte" """
        return {
            'effect': {
                'fadeout': 'slow',  # Speed of animation of notification
                'message': message,  # message value will be called after
                'type': 'rainbow_man',  # Type of notification is rainbow_man
            }
        }

    def import_qcm_qro_evalbox_to_odoo(self):
        """ Evalbox intergration : Ici ou il y a la récupération des notes QCM et QRO d'Evalbox"""
        self.env.user.lang = 'fr_FR'
        locale.setlocale(locale.LC_TIME, str(self.env.user.lang) + '.utf8')
        headers = {
            'content_type': 'application/json',
            'User-Agent': 'MCM Academy',
            'X-API-Key': '060951a19c45fb4c2acd7f02ab59ba28',
            'X-APP-ID': 'info@mcm-academy.fr',
            'X-Evalbox': 'api',
        }
        # Récupérer la liste des classes
        response = requests.get('https://api.evalbox.com/api/v1/classes/all', headers=headers)
        classes = json.loads(response.text)
        # Synchronisations des notes d'examen depuis Evalbox vers Odoo
        for key, value in classes.items():  # Recherche par key value dans le retour json de la liste des classes
            if isinstance(value, dict):
                if 'name' in value:
                    year = value['year']
                    if int(year) > 2021:
                        name_classe_evalbox = str(value['name'])

                        date = (re.findall(r'\d+/\d+/\d+',
                                           name_classe_evalbox))  # I use re as Library python to extract date from a text (name)
                        if date:
                            newformat = "%Y-%m-%d"
                            date_eval = datetime.strptime(str(date[0]),
                                                          "%d/%m/%Y")  # date[0] because date value in a list to get the date i have call index [0]
                            date_exam_evalbox = date_eval.strftime(newformat)
                            ville_class_evalbox = name_classe_evalbox.split().pop(
                                -2).capitalize()  # Ville de classe evalbox
                            session = self.session_ville_id.name_ville  # search for the session using the date and city chosen by the user
                            if self.session_ville_id.name_ville == ville_class_evalbox and str(
                                    self.date_exam) == date_exam_evalbox:
                                id_class_evalbox = value['id_class']
                                response = requests.get(
                                    'https://api.evalbox.com/api/v1/classes/timeline/id_class/' + id_class_evalbox,
                                    headers=headers)  # URL to get the list of the timeline (examen dans evalbox par class)
                                exams = json.loads(response.text)
                                examen = exams['rows']
                                id_qcm = False
                                id_qro = False
                                for exam in examen:
                                    if "QCM" in exam['title']:
                                        qcm = exam
                                id_qcm = qcm['id_exam']  # Get the last value of collection list QRO line
                                for exam in examen:
                                    if "QRO" in exam['title']:
                                        qro = exam
                                id_qro = qro['id_exam']  # Get the last value of QRO line
                                for exam in examen:  # Parcourir la list des examens avec key "rows"
                                    title_timeline = exam[
                                        'title']  # Title evalbox "Examen Capacité marchandise QRO - 26 Janvier 2022"
                                    # if "QCM" in title_timeline:
                                    response = requests.get(
                                        'https://api.evalbox.com/api/v1/exams/marks/id/' + str(id_qcm),
                                        headers=headers)
                                    marks = json.loads(response.text)
                                    _logger.info(
                                        "********************** EVALBOX GET ROWS OF QCM EXAM (marks QCM)************************ %s" % str(
                                            marks))
                                    marks_rows = marks['rows']  # liste des examens avec note QCM de client
                                    for m_rows in marks_rows:
                                        email_evalbox = m_rows['email']
                                        mark_qcm = m_rows['mark']
                                        for client in self.client_ids.sudo().search([("email", "=",
                                                                                      email_evalbox)]):  # List of clients in session with state "won" & we compare with email if exist in evalbox
                                            if client:
                                                exam = self.env['info.examen'].sudo().search(
                                                    [("partner_id.email", "=", email_evalbox)],
                                                    order="id desc", limit=1)

                                                response = requests.get(
                                                    'https://api.evalbox.com/api/v1/exams/marks/id/' + str(id_qro),
                                                    headers=headers)  # Response to exam QRO
                                                marks = json.loads(response.text)
                                                marks_rows = marks['rows']
                                                for m_rows in marks_rows:
                                                    email_evalbox = m_rows['email']
                                                    mark_qro = m_rows['mark']

                                                if exam:
                                                    for examen in exam:
                                                        if str(examen.date_exam) == str(date_exam_evalbox):
                                                            examen.epreuve_a = mark_qcm
                                                            # New code qro
                                                            response = requests.get(
                                                                'https://api.evalbox.com/api/v1/exams/marks/id/' + str(
                                                                    id_qro),
                                                                headers=headers)
                                                            print("response", response)
                                                            marks = json.loads(response.text)
                                                            _logger.info(
                                                                "********************** EVALBOX GET ROWS OF QRO EXAM (marks QRO) FIRST IF EXAM ************************ %s" % str(
                                                                    marks))
                                                            marks_rows = marks['rows']
                                                            for m_rows in marks_rows:

                                                                print("m_rows", m_rows)
                                                                email_evalbox = m_rows['email']
                                                                mark_qro = m_rows['mark']
                                                                for client in self.client_ids.search(
                                                                        [("email", "=", email_evalbox)]):
                                                                    if client:
                                                                        exam = self.env['info.examen'].sudo().search(
                                                                            [("partner_id.email", "=", email_evalbox)],
                                                                            order="id desc", limit=1)
                                                                        if exam:
                                                                            print("compute_moyenne_generale")
                                                                            exam.compute_moyenne_generale()
                                                                            for examen in exam:
                                                                                if str(examen.date_exam) == str(
                                                                                        date_exam_evalbox):
                                                                                    examen.epreuve_b = mark_qro
                                                                                else:
                                                                                    exam.sudo().write(
                                                                                        {
                                                                                            'epreuve_b': mark_qro})

                                                else:  # if the exam does not exist with the same exam date
                                                    exam.sudo().create(
                                                        {
                                                            'partner_id': client.id,
                                                            'session_id': client.mcm_session_id.id,
                                                            'module_id': client.module_id.id,
                                                            'date_exam': client.mcm_session_id.date_exam,
                                                            'epreuve_a': mark_qcm,
                                                            # 'epreuve_b': 0,
                                                            'ville_id': client.mcm_session_id.session_ville_id.id, })
                                                    response = requests.get(
                                                        'https://api.evalbox.com/api/v1/exams/marks/id/' + str(
                                                            id_qro),
                                                        headers=headers)
                                                    print("response", response)
                                                    marks = json.loads(response.text)
                                                    _logger.info(
                                                        "********************** EVALBOX GET ROWS OF QRO EXAM (marks) SECOND ELSE QRO ************************ %s" % str(
                                                            marks))
                                                    marks_rows = marks['rows']
                                                    for m_rows in marks_rows:
                                                        print("m_rows", m_rows)
                                                        email_evalbox = m_rows['email']
                                                        mark_qro = m_rows['mark']
                                                        for client in self.client_ids.search(
                                                                [("email", "=", email_evalbox)]):
                                                            if client:
                                                                exam = self.env['info.examen'].sudo().search(
                                                                    [("partner_id.email", "=", email_evalbox)],
                                                                    order="id desc", limit=1)
                                                                if exam:
                                                                    exam.compute_moyenne_generale()
                                                                    for examen in exam:
                                                                        if str(examen.date_exam) == str(
                                                                                date_exam_evalbox):
                                                                            examen.epreuve_b = mark_qro
                                                                        else:
                                                                            exam.sudo().write(
                                                                                {
                                                                                    'epreuve_b': mark_qro})  # Update field in exam interface "epreuve_b" with Evalbox note
                                                                            exam.compute_moyenne_generale()

        return self.notif_rainbow_man(
            message='Opération QCM/QRO de Evalbox réussie! Bravo <b> %r </b>' % self.env.user.name)

    def create_class_odoo_to_evalbox(self):
        """ Evalbox intergration : Ici où il y a la création de classe à partir un button dans la session
        qui sera visible juste pour les utilisateurs avec le droit d'accès de session égale à manger"""
        self.env.user.lang = 'fr_FR'
        locale.setlocale(locale.LC_TIME, str(self.env.user.lang) + '.utf8')
        headers = {
            "user-agent": "MCM Academy",
            "x-api-key": "060951a19c45fb4c2acd7f02ab59ba28",
            "x-app-id": "info@mcm-academy.fr",
            "x-evalbox": "api",
            "content-type": "application/json",
            "cache-control": "no-cache",
        }
        session_name = "DIGIMOOV - EXAMEN CAPACITE DE MARCHANDISE -3T5 :"
        session_exam = self.date_exam
        session_ville = self.session_ville_id.name_ville
        newformat = "%d/%m/%Y"
        date_eval = datetime.strptime(str(session_exam), "%Y-%m-%d")
        session_examen = date_eval.strftime(newformat)

        print("session examen", session_examen)
        year = datetime.now().year
        print("session examen", year)
        next_year = year + 1

        # Récupérer la liste des classes
        response = requests.get('https://api.evalbox.com/api/v1/classes/all', headers=headers)
        classes = json.loads(response.text)
        print("ALL classes", classes)
        _logger.info(
            "********************** EVALBOX : GET ALL CLASSES ************************ %s" % str(
                classes))
        rows = []
        for client in self.client_ids:
            for rid, val in client.get_external_id().items():
                print("Val", val)
                row = {
                    "firstname": str(client.nom_evalbox),
                    "lastname": str(client.prenom_evalbox),
                    "email": str(client.email.lower()),
                    "custom_fields": {
                        "prenom_officiel": str(client.firstName),
                        "nom_officiel": str(client.lastName),
                    },
                    "externid": str(val),
                }
            if client.prenom_evalbox is False or client.prenom_evalbox is False or client.lastName is False or client.firstName is False:
                pass
            else:
                rows.append(row)
        data = {
            "head": {
                "name": session_name + " " + session_ville + " " + session_examen,
                "year": year,
                "year_end": next_year,
            },
            "rows": rows
        }
        response = requests.post('https://examiner.evalbox.com/api/v1/classes/create',
                                 data=json.dumps(data), headers=headers)
        result = json.loads(response.text)
        _logger.info(
            "********************** EVALBOX : CREATE CLASS TO EVALBOX POST ************************ %s" % str(
                result))
        return self.notif_rainbow_man(
            message='Opération creation de classe vers Evalbox réussie! Bravo <b> %r </b>' % self.env.user.name)
