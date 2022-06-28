import json
import locale
import re

import requests

from odoo import api, fields, models, _
import logging

from odoo.odoo.tools import datetime

_logger = logging.getLogger(__name__)


class InheritMcmacademySession(models.Model):
    _inherit = "mcmacademy.session"

    def notif_rainbow_man(self, message):
        print("notif_rainbow_man")
        return {
            'effect': {
                'fadeout': 'slow',
                'message': message,
                'type': 'rainbow_man',
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
                        # print("Values all :", value)
                        name_classe_evalbox = str(value['name'])

                        date = (re.findall(r'\d+/\d+/\d+', name_classe_evalbox))
                        if date:
                            # date_exam_class_evalbox = name_classe_evalbox.split().pop(-1) #date examen Evalbox
                            newformat = "%Y-%m-%d"
                            date_eval = datetime.strptime(str(date[0]), "%d/%m/%Y")
                            date_exam_evalbox = date_eval.strftime(newformat)
                            print("date_exam_evalbox/////////////////", date_exam_evalbox)
                            ville_class_evalbox = name_classe_evalbox.split().pop(
                                -2).capitalize()  # Ville de classe evalbox
                            print("ville_class_evalbox", ville_class_evalbox)
                            print("self", self)
                            session = self.session_ville_id.name_ville  # search for the session using the date and city choosed by user
                            print("session", session)
                            if self.session_ville_id.name_ville == ville_class_evalbox and str(
                                    self.date_exam) == date_exam_evalbox:
                                print("ville_class_evalbox", ville_class_evalbox)
                                print("//////////////////////////SESSION 18 MAI//////////////////////////////", session)
                                id_class_evalbox = value['id_class']
                                print("test test", id_class_evalbox)
                                response = requests.get(
                                    'https://api.evalbox.com/api/v1/classes/timeline/id_class/' + id_class_evalbox,
                                    headers=headers)
                                exams = json.loads(response.text)
                                print("exams", exams)
                                examen = exams['rows']
                                id_qcm = False
                                id_qro = False
                                for exam in examen:
                                    if "QCM" in exam['title']:
                                        qcm = exam
                                id_qcm = qcm['id_exam']
                                print('qcm x:=', id_qcm)
                                for exam in examen:
                                    if "QRO" in exam['title']:
                                        qro = exam
                                id_qro = qro['id_exam']
                                print('qro x:=', id_qro)
                                for exam in examen:  # Parcourir la list des examens avec key "rows"
                                    exam_new = exam
                                    title_timeline = exam[
                                        'title']  # Title evalbox "Examen Capacité marchandise QRO - 26 Janvier 2022"
                                    print("title_timeline", exam)
                                    if "QCM" in title_timeline:
                                        response = requests.get(
                                            'https://api.evalbox.com/api/v1/exams/marks/id/' + str(id_qcm),
                                            headers=headers)
                                        marks = json.loads(response.text)
                                        # print("marks", marks)
                                        marks_rows = marks['rows']
                                        for m_rows in marks_rows:
                                            email_evalbox = m_rows['email']
                                            # print("email_evalbox", email_evalbox)
                                            mark_qcm = m_rows['mark']
                                            for client in self.client_ids.sudo().search(
                                                    [("email", "=", email_evalbox)]):
                                                if client:
                                                    exam = self.env['info.examen'].sudo().search(
                                                        [("partner_id.email", "=", email_evalbox)],
                                                        order="id desc", limit=1)
                                                    print("exam///", exam)


                                                    # test qro
                                                    response = requests.get(
                                                        'https://api.evalbox.com/api/v1/exams/marks/id/' + str(id_qro),
                                                        headers=headers)
                                                    marks = json.loads(response.text)
                                                    print("marks++++++++++++++++++++++++++==", marks)
                                                    marks_rows = marks['rows']
                                                    for m_rows in marks_rows:
                                                        email_evalbox = m_rows['email']
                                                        print("email_evalbox", email_evalbox)
                                                        mark_qro = m_rows['mark']

                                                    if exam:
                                                        for examen in exam:
                                                            if str(examen.date_exam) == str(date_exam_evalbox):
                                                                print("ooookk", examen)
                                                                examen.epreuve_a = mark_qcm
                                                                print("examen.epreuve_a", examen.epreuve_a)
                                                    else:
                                                        exam.sudo().create(
                                                            {
                                                                'partner_id': client.id,
                                                                'session_id': client.mcm_session_id.id,
                                                                'module_id': client.module_id.id,
                                                                'date_exam': client.mcm_session_id.date_exam,
                                                                'epreuve_a': mark_qcm,
                                                                # 'epreuve_b': 0,
                                                                #'presence': 'absence_justifiee',
                                                                'ville_id': client.mcm_session_id.session_ville_id.id, })
                                                        response = requests.get(
                                                            'https://api.evalbox.com/api/v1/exams/marks/id/' + str(
                                                                id_qro),
                                                            headers=headers)
                                                        marks = json.loads(response.text)
                                                        print("marks++++++++++++++++++++++++++==", marks)
                                                        marks_rows = marks['rows']
                                                        for m_rows in marks_rows:
                                                            email_evalbox = m_rows['email']
                                                            print("email_evalbox", email_evalbox)
                                                            mark_qro = m_rows['mark']
                                                            for client in self.client_ids.search(
                                                                    [("email", "=", email_evalbox)]):
                                                                if client:
                                                                    exam = self.env['info.examen'].sudo().search(
                                                                        [("partner_id.email", "=", email_evalbox)],
                                                                        order="id desc", limit=1)
                                                                    if exam:
                                                                        for examen in exam:
                                                                            if str(examen.date_exam) == str(
                                                                                    date_exam_evalbox):
                                                                                print("ooookk", examen)
                                                                                examen.epreuve_b = mark_qro
                                                                                print("examen.epreuve_a",
                                                                                      examen.epreuve_a)
                                                                                print("examen.epreuve_b",
                                                                                      examen.epreuve_b)
                                                                            else:
                                                                                exam.sudo().write(
                                                                                    {'epreuve_b': mark_qro})
                                    else:
                                        response = requests.get(
                                            'https://api.evalbox.com/api/v1/exams/marks/id/' + str(id_qro),
                                            headers=headers)
                                        marks = json.loads(response.text)
                                        print("marks++++++++++++++++++++++++++==", marks)
                                        marks_rows = marks['rows']
                                        for m_rows in marks_rows:
                                            email_evalbox = m_rows['email']
                                            print("email_evalbox", email_evalbox)
                                            mark_qro = m_rows['mark']
                                            for client in self.client_ids.search([("email", "=", email_evalbox)]):
                                                if client:
                                                    exam = self.env['info.examen'].sudo().search(
                                                        [("partner_id.email", "=", email_evalbox)],
                                                        order="id desc", limit=1)
                                                    if exam:
                                                        for examen in exam:
                                                            if str(examen.date_exam) == str(date_exam_evalbox):
                                                                print("ooookk", examen)
                                                                examen.epreuve_b = mark_qro
                                                                print("examen.epreuve_a", examen.epreuve_a)
                                                                print("examen.epreuve_b", examen.epreuve_b)
                                                            else:
                                                                exam.sudo().write({'epreuve_b': mark_qro})
        # #return self.notif_rainbow_man()
        # notification = {
        #     'type': 'ir.actions.client',
        #     'tag': 'display_notification',
        #     'params': {
        #         'title': ('Your Custom Title'),
        #         'message': 'Your Custom Message',
        #         'type': 'success',  # types: success,warning,danger,info
        #         'sticky': True,  # True/False will display for few seconds if false
        #     },
        # }
        return self.notif_rainbow_man(message='Opération Evalbox réussie!')

        # name_evalbox = exams['head']['name']
        # title_evalbox = exams['head']['title']
        # ville_evalbox = name_evalbox.split().pop(-2).capitalize()
        # #date_exam_evalbox = name_evalbox.split().pop(-1)
        # students = exams['rows']
        # for student in students:
        #     email_student = student['email']
        #     date_evalbox = exams['head']['start_at']
        #     newformat = "%Y-%m-%d"
        #     date_eval = datetime.strptime(date_evalbox, "%Y-%m-%d %H:%M:%S")
        #     date_exam_evalbox = date_eval.strftime(newformat)
        #     if email_student is None:
        #         for partner in self.env['res.partner'].sudo().search([('statut', "=", "won"),('email', "=", email_student)]):
        #             print("partner_email", partner)
        #     else:
        #         firstname_evalbox = student['firstname']
        #         email_evalbox = student['email']
        #         exist_list = []
        #         for partner in self.env['res.partner'].sudo().search([('statut', "=", "won"), ('email', "=", email_evalbox)]):
        #             print("date_exam_evalbox//////////////////////", date_exam_evalbox,
        #                   partner.mcm_session_id.date_exam)
        #             exam_exist = self.env['info.examen'].sudo().search([('partner_id', "=", partner.id)], limit=1)
        #             exist_list.append(exam_exist.id)
        #             print("exist_list", exist_list)
        #             if exam_exist: #Si client a eu une note existante dans la liste des examens
        #                 if date_exam_evalbox == partner.mcm_session_id.date_exam:
        #                     print("date_exam_evalbox//////////////////////", date_exam_evalbox,
        #                           partner.mcm_session_id.date_exam)
        #                     if student['mark'] is not False:
        #                         print()
        #                         examen = self.env['info.examen'].sudo().update({
        #                             'partner_id': partner.id,
        #                             'session_id': partner.session_id,
        #                             'module_id': partner.module_id,
        #                             'epreuve_a': student['mark'],
        #                             'epreuve_b': 15,
        #                         })
        #                     else:
        #                         examen = self.env['info.examen'].sudo().update({
        #                             'partner_id': partner.id,
        #                             'session_id': partner.session_id,
        #                             'module_id': partner.module_id,
        #                             'epreuve_a': student['mark'],
        #                             'epreuve_b': 0,
        #                             'presence': 'Absent',
        #                         })
        #
        #             else:
        #                 if date_exam_evalbox == partner.session_id.date_exam:
        #                     examen = self.env['info.examen'].sudo().create({
        #                         'partner_id': partner.id,
        #                         'session_id': partner.session_id,
        #                         'module_id': partner.module_id,
        #                         'epreuve_a': student['mark'],
        #                         'epreuve_b': 0,
        #                     })

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
        for client in self.client_ids:
            print("client.nom_evalbox", client.nom_evalbox, client.prenom_evalbox, client.email,
                  client.get_external_id())
            data = {
                "head": {
                    "name": session_name + " " + session_ville + " " + session_examen,
                    "year": year,
                    "year_end": next_year,
                },
                "rows": [
                    {
                        "firstname": client.nom_evalbox,
                        "lastname": client.prenom_evalbox,
                        "email": client.email,
                        "custom_fields": {
                            "prenom_officiel": client.firstName,
                            "prenom_officiel": client.lastName,
                        },
                        "externid": client.get_external_id()
                    },

                ],
            }
            print(json.dumps(data))
            # response = requests.post('https://examiner.evalbox.com/api/v1/classes/create',
            #                          data=json.dumps(data), headers=headers)
            # result = json.loads(response.text)
            # print("response", response)
            # print("classes_post", result)
