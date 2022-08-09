# -*- coding: utf-8 -*-
import requests
from datetime import datetime, timedelta, date
from odoo import models, fields, api, SUPERUSER_ID
from odoo.tools import datetime

import logging

_logger = logging.getLogger(__name__)


class enattente(models.Model):
    _name = 'mcm_openedx.enattente'
    _description = "les apprennat en attente sur l'api "

    name = fields.Char(string="Apprenat en attente")
    date_edof = fields.Date(string="Date d'ajout")
    billingState = fields.Char(string="Statut de payement")
    state = fields.Char(string="Statut de cpf")
    externalId = fields.Char(string="Numero de cpf")
    firstName = fields.Char(string="Nom")
    lastName = fields.Char(string="Prenom")
    existant = fields.Boolean(string="Exist sur ODOO", default=False)
    existantsurmooc = fields.Boolean(string="Exist sur Moocit", default=False)

    def wedof_api_integration_moocit(self):
        companies = self.env['res.company'].sudo().search([('id', "=", 2)])
        print(companies)
        api_key = ""
        if companies:
            api_key = companies.wedof_api_key
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
            'X-API-KEY': api_key,
        }
        params_we = (
            ('order', 'desc'),
            ('type', 'all'),
            ('state', 'accepted'),
            ('billingState', 'all'),
            ('certificationState', 'all'),
            ('sort', 'lastUpdate'),
        )

        data = '{}'
        response = requests.get('https://www.wedof.fr/api/registrationFolders/', headers=headers,
                                params=params_we)
        registrations = response.json()
        print(response.status_code)
        for dossier in registrations:
            externalId = dossier['externalId']
            diplome = dossier['trainingActionInfo']['title']
            email = dossier['attendee']['email']
            certificat = dossier['_links']['certification']['name']
            certificat_info = dossier['_links']['certification']['certifInfo']
            date_formation = dossier['trainingActionInfo']['sessionStartDate']
            """convertir date de formation """
            date_split = date_formation[0:10]
            date_ = datetime.strptime(date_split, "%Y-%m-%d")
            dateFormation = date_.date()
            idform = dossier['trainingActionInfo']['externalId']
            attendee = dossier['attendee']

            today = date.today()
            lastupdatestr = str(dossier['lastUpdate'])
            lastupdate = datetime.strptime(lastupdatestr, '%Y-%m-%dT%H:%M:%S.%fz')
            newformat = "%d/%m/%Y %H:%M:%S"
            lastupdateform = lastupdate.strftime(newformat)
            lastName = dossier['attendee']['lastName']
            firstName = dossier['attendee']['firstName']
            state = dossier['state']
            billingState = dossier['billingState']
            externalId = dossier['externalId']
            lastupd = datetime.strptime(lastupdateform, "%d/%m/%Y %H:%M:%S")
            # print('dateeeeeeeeee', today, dateFormation, certificat, idform)
            # print('diplome',diplome)
            if (certificat == "Habilitation pour l’accès à la profession de conducteur de taxi"):
                _logger.info("Habilitation pour l’accès à la profession de conducteur de taxi")
                _logger.info(attendee['email'])
                existee = self.env['mcm_openedx.enattente'].search(
                    [('name', '=', email)])
                _logger.info(existee.name)
                _logger.info(existee.externalId)
                if existee:
                    _logger.info("existtttt")
                    for partner in self.env['res.partner'].search(
                            [('numero_cpf', '!=', False, ('statut_cpf', '!=', 'canceled'))
                             ]):
                        if (partner.numero_cpf == existee.externalId):
                            existee.existant = True
                            _logger.info(existee.existant)
                            _logger.info("res.partner db", partner.numero_cpf)
                            for existt in self.env['mcm_openedx.course_stat'].sudo().search(
                                    [('email', "=", existee.name)]):

                                existee.existantsurmooc = True
                                print(partner.name)
                                print(partner.email)
                                _logger.info("okokkookkokookokokko")
                                if (dateFormation <= today):
                                    """si l'apprenant est sur moocit on change le statut de son dossier sur wedof """

                                    response_post = requests.post(
                                        'https://www.wedof.fr/api/registrationFolders/' + externalId + '/inTraining',
                                        headers=headers, data=data)
                                    _logger.info('response post %s' % str(response_post.text))
                                    # print('response post', str(response_post.text))

                if not existee:
                    _logger.info("dont exist")

                    new = self.env['mcm_openedx.enattente'].sudo().create({
                        'name': email,
                        'date_edof': dateFormation,
                        'state': state,
                        'billingState': billingState,
                        'externalId': externalId,
                        'lastName': lastName,
                        'firstName': firstName,
                    })
                    _logger.info(new)


class Coach(models.Model):
    _name = 'mcm_openedx.coach'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    _description = "coaches module en va affecter pour chaque coach sa liste des apprennats"
    name = fields.Char(string="Coaches")
    nombre_apprenant = fields.Integer()
    coach_name = fields.Many2one('res.partner', string="Tuteur", domain=[('est_coach', '=', True)])
    apprenant_name = fields.Many2many('res.partner', domain=[('est_coach', '=', False)])
    seats = fields.Integer(string="nombre de places")
    taken_seats = fields.Float(string="nombre des places ocuppé ", compute='_taken_seats')
    commentaire = fields.Char(string="Commentaires")
    color = fields.Integer()
    apprenant_email = fields.Char()

    @api.depends('seats', 'apprenant_name')
    def _taken_seats(self):
        for r in self:
            if not r.seats:
                r.taken_seats = 0.0
            else:
                r.taken_seats = 100.0 * len(r.apprenant_name) / r.seats

    def aff_coach(self):
        for partner in self.env['res.partner'].sudo().search(
                [('statut', "=", "won"), ('company_id', '=', 1), ('state', 'ilike', 'en_formation')]):

            for coaches in self.env['res.partner'].sudo().search(
                    [('est_coach', '=', 'True')]):
                # tester avec les commentaire ecrite si on trouve le nom des coache on les affecte
                for message in self.env['mail.message'].search(
                        [('res_id', "=", self.id), ('author_id', 'ilike', coaches.name)]):
                    print("message.author_id", message.author_id.name)

                    if (coaches.name, 'ilike', message.author_id.name):
                        print(coaches.name)
                        partner.coach_peda = message.author_id


# tester le nombre des coach et le nombre d'apprenant pour chaque un  , pour controller l'affectation des apprenants pour chaque'un
@api.depends('nombre_apprenant', 'coach_name', 'apprenant_name', 'seats')
def test_coach(self):
    count_apprennat = 0
    # determiner le nombre total des apprenants
    for apprenant in self.env['res.partner'].sudo().search(
            [('statut', "=", "won"), ('company_id', '=', 1), ('state', "=", "en_formation")]):
        count_apprennat = count_apprennat + 1

    # definir si le partner et coach
    for coach in self.env['res.partner'].sudo().search(
            [('est_coach', '=', 'True')]):
        count = 0

        # extraire les client ganger ayant le meme nom de coach dans la liste des partner
        # crer une liste pour stocker les apprennats ayant les informations que en est en train de chercher
        listapprenant = []
        for rec in self.env['res.partner'].sudo().search(
                [('coach_peda', 'like', coach.name)]):

            if (rec.coach_peda.name == coach.name):
                count = count + 1
                # stoker dans la liste les apprennats
                listapprenant.append(rec.id)

        nombre_apprenant = count
        # si le partner est un coach alors en va verifier si il existe deja dans la liste des coach pour lui affecter les apprenants

        if (coach):

            coach_name = coach.name
            print("coachs names", coach_name)
            # verfier dans la class Coach si il existe un coach ayant le meme nom que le coach affecter pour les apprenants

            exist = self.env['mcm_openedx.coach'].sudo().search([('coach_name', '=', coach.id)])
            # si le coach existe alors en va lui affecter la liste des apprenats ayant le nom de ce caoch

            if (exist):
                exist.seats = count_apprennat
                exist.nombre_apprenant = nombre_apprenant
                exist.sudo().write({'apprenant_name': [(6, 0, listapprenant)],
                                    })

            # si non en va creé le coach
            if not exist:
                newcoach = self.env['mcm_openedx.coach'].sudo().create({
                    'coach_name': coach.id, })
                newcoach.seats = count_apprennat
                newcoach.nombre_apprenant = nombre_apprenant
                newcoach.sudo().write({'apprenant_name': [(6, 0, listapprenant)],
                                       })

            print("nombre d'apprenant par coach ", coach_name, nombre_apprenant)


# chercher les nombre des apprennats qui n'on pas des coach et
# chercher le nombre d'apprennats par  coach pour voir la differance et affecter les apprenat aux coach qui a le nombre inferieur aux autres
def egalité(self):
    # ctrlf8
    self.test_coach()

    listcoach = []
    nombre_coach = 0
    sanscoach = 0
    # calculer nb coach
    for coach1 in self.env['mcm_openedx.coach'].sudo().search(
            [('coach_name', '!=', '')]):
        nombre_coach = nombre_coach + 1
        listcoach.append(coach1.nombre_apprenant)
        listcoach.sort()
        print(listcoach)
        print(listcoach[0])
        # calculer nb apprenants sans coaches
    for apprenatsanscoach in self.env['res.partner'].sudo().search(
            [('statut', "=", "won"), ('coach_peda', '=', False), ('company_id', '=', 1)]):
        sanscoach = sanscoach + 1
        # listaffecter.append()
        print("nb sans coach", sanscoach)
        limit = divmod(sanscoach, nombre_coach)
        print("div", limit[0])
        print("Rest", limit[1])
        for coach in self.env['mcm_openedx.coach'].sudo().search(
                [('coach_name', '!=', ''), ('nombre_apprenant', '=', listcoach[0])], limit=1):
            i = 0
            for apprenat in self.env['res.partner'].sudo().search(
                    [('statut', "=", "won"), ('coach_peda', '=', False), ('company_id', '=', 1)],
                    limit=limit[0]):

                coach.apprenant_email = apprenat.name
                listexiste = []
                listexiste.append(coach.apprenant_name)
                coach.lang = 'fr_FR'
                if self.env.su:
                    # sending mail in sudo was meant for it being sent from superuser
                    selff = self.with_user(SUPERUSER_ID)
                    template_id = int(self.env['ir.config_parameter'].sudo().get_param(
                        'mcm_openedx.mail_coachh'))
                    template_id = self.env['mail.template'].search([('id', '=', template_id)]).id
                    if not template_id:
                        template_id = self.env['ir.model.data'].xmlid_to_res_id(
                            'mcm_openedx.mail_coachh',
                            raise_if_not_found=False)
                    if not template_id:
                        template_id = self.env['ir.model.data'].xmlid_to_res_id(
                            'mcm_openedx.email_coachh',
                            raise_if_not_found=False)
                    if template_id:
                        coach.with_context(force_send=True).message_post_with_template(template_id,
                                                                                       composition_mode='comment', )
                        # ajouter une fonction pour connaitre l'utilisateur connecter et lui notifier si il a un nouveau apprenant
                        context = self._context
                        current_uid = context.get('uid')
                        user = self.env['res.users'].browse(current_uid)
                        print("emaillllllllllll", user.email)
                        if (user.email == coach.coach_name.email):
                            return {
                                'type': 'ir.actions.client',
                                'tag': 'display_notification',
                                'params': {
                                    'title': (' You have a new Mail🤓 🤓  '),
                                    'message': ('consulter votre boite  maill'),
                                    'sticky': True,
                                    'className': 'bg-danger'
                                }
                            }

                if apprenat.id not in listexiste:
                    print("app", apprenat.id)
                    print(coach.coach_name)
                    apprenat.coach_peda = coach.coach_name

                # appeler la fonction pour affecter les apprenats aux coach
            self.test_coach()


"""recuperer les dossier avec état accepté apartir d'api wedof,
      puis faire le parcours pour chaque dossier,
      si tout les conditions sont vérifiés on Passe le dossier dans l'état 'en formation'"""
