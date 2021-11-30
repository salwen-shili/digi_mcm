from odoo import _
from odoo import models, fields,api
from datetime import datetime,timedelta,date
from odoo.exceptions import ValidationError
import functools
import xmlrpc.client
import requests
from requests.structures import CaseInsensitiveDict
from unidecode import unidecode
import locale

class Session(models.Model):
    _inherit='mcmacademy.session'

    #Supprimer session  automatiquement  de plateforme 360
    # après 4jours de date d'examen
    def supprimer_session_automatque(self):
        # Remplacez les paramètres régionaux de l'heure par le paramètre de langue actuel
        # du compte dans odoo
        locale.setlocale(locale.LC_TIME, str(self.env.user.lang) + '.utf8')
        company_id = '56f5520e11d423f46884d593'
        api_key = 'cnkcbrhHKyfzKLx4zI7Ub2P5'
        headers = CaseInsensitiveDict()
        headers["Accept"] = "*/*"
        params = (
            ('company', '56f5520e11d423f46884d593'),
            ('apiKey', 'cnkcbrhHKyfzKLx4zI7Ub2P5'),
        )
        url_groups = 'https://app.360learning.com/api/v1/groups'
        response_grps = requests.get(url_groups, params=params)
        groupes = response_grps.json()
        print(response_grps.json())
        #Trouver la session de 360 sur odoo
        #Récuperer la date d'examen, calculer la date de suppression(+4jours)
        # puis supprimer le groupe
        for groupe in groupes:

            nomgroupe = str(groupe['name']).lower()
            nomgroupe = unidecode(nomgroupe)
            id_groupe = groupe['_id']
            find_sessions=self.env['mcmacademy.session'].sudo().search([])
            for find_session in find_sessions:
                if find_session and (find_session.date_exam) and (find_session.session_ville_id.name_ville):
                    new_format = '%d %B %Y'
                    date_exam = find_session.date_exam
                    # Changer format de date et la mettre en majuscule
                    datesession = str(date_exam.strftime(new_format).lower())
                    date_session = unidecode(datesession)
                    ville = str(find_session.session_ville_id.name_ville).lower()
                    ville =unidecode(ville)
                    print('date d\'examen', date_session)
                    # date de suppression est date d'examen + 4jours
                    date_suppression = find_session.date_exam + timedelta(days=4)
                    today = date.today()
                    print('date_sup avant if', date_session, date_suppression, today, nomgroupe, ville)
                    if ((date_suppression <= today) and (ville in nomgroupe) and (date_session in nomgroupe)):
                        print('date_sup', date_session , date_suppression, today,nomgroupe,ville )
                        url = 'https://app.360learning.com/api/v1/groups/'+id_groupe+'?company=' + company_id + '&apiKey=' + api_key
                        resp = requests.delete(url)
                        print('url', resp.status_code)
                    else:
                      print('date incompatible', find_session.name)

    # Supprimer session manuellement de plateforme 360
    def supprimer_session_manuelle (self):
        company_id = '56f5520e11d423f46884d593'
        api_key = 'cnkcbrhHKyfzKLx4zI7Ub2P5'
        headers = CaseInsensitiveDict()
        headers["Accept"] = "*/*"
        params = (
            ('company', '56f5520e11d423f46884d593'),
            ('apiKey', 'cnkcbrhHKyfzKLx4zI7Ub2P5'),
        )
        url_groups = 'https://app.360learning.com/api/v1/groups'
        response_grps = requests.get(url_groups, params=params)
        existe = False
        groupes = response_grps.json()
        print(response_grps.json())
        # Trouver la session de 360 sur odoo
        # puis supprimer le groupe
        for groupe in groupes:
            nomgroupe = str(groupe['name']).lower()
            nomgroupe = unidecode(nomgroupe)
            id_groupe = groupe['_id']
            ville =str(self.session_ville_id.name_ville).lower()
            new_format = '%d %B %Y'
            date_exam = self.date_exam
            # Changer format de date et la mettre en majuscule
            datesession = str(date_exam.strftime(new_format).lower())
            date_session = unidecode(datesession)
            if  (ville in nomgroupe) and (date_session in nomgroupe) :
                        print('date_sup' )
                        url = 'https://app.360learning.com/api/v1/groups/' + id_groupe + '?company=' + company_id + '&apiKey=' + api_key
                        resp = requests.delete(url)
                        print('url', 'resp.status_code')
