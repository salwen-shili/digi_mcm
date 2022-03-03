import datetime as datetime
from datetime import date, datetime, tzinfo, timedelta
from odoo.exceptions import UserError
import mimetypes
from odoo.tools.mimetypes import guess_mimetype

from odoo import api, fields, models, _


# ce programme est crée Par Mabrouk Seifeddinne le 28/06/2021
# cette application fait la gestions des intervenants dans une session
# on a herité des fields de res.partner par le champs intervenant_id pour la reecuperation automatique des fields
# chargement des documents curriculum_viatae,contrat_travail,rapport_entretient_embauche avec visualisation des attachements


class Intervenant(models.Model):
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _name = "info.listeintervenants"
    _description = "Add fields in session view"

    intervenant_id = fields.Many2one('res.partner', string="Nom & Prenom d'intervenant", required=True)
    session_id = fields.Many2one('mcmacademy.session', string="session")
    state = fields.Many2one('res.country.state', string="Département")
    partner_ids = fields.One2many('res.partner', 'session_id', 'Partners')
    country_id = fields.Many2one('res.country', string="Pays_id")
    adresse = fields.Char(string="Adresse", related="intervenant_id.street", required=True)
    email = fields.Char(related="intervenant_id.email", string="Email", required=True)
    code_interne = fields.Char(string="Code interne", required=True)
    mcm_session_id = fields.Many2one(string="session name", related="intervenant_id.mcm_session_id", required=True)
    ville = fields.Char(string="Ville", related="intervenant_id.city")
    telephone = fields.Char(string="Téléphone", related="intervenant_id.phone", required=True)
    nationalite = fields.Char(string="Nationalité", related="intervenant_id.nationality")
    date_naissance = fields.Date(string="Date de naissance", related="intervenant_id.birthday", required=True)
    ville_naissance = fields.Char(string="Ville de naissance", related="intervenant_id.birth_city", required=True)
    departement_naissance = fields.Char(string="Département de Naissance", related="intervenant_id.birth_state",
                                        required=True)
    country_id = fields.Many2one(string="Pays", related="intervenant_id.country_id")
    code_postale = fields.Char(string="Code_postale", related="intervenant_id.zip")
    civilite = fields.Char(string="Civilité")
    langue = fields.Char(string="Langue")
    social_security_number = fields.Char(string="Numéro de sécurité social")
    num_declaration_activité = fields.Char(string="Numéro de déclaration d'activité")
    entreprise = fields.Char(string="Entreprise")
    active = fields.Boolean('Active', default=True)
    num_siret = fields.Integer(string="Num_Siret")
    num_assurance = fields.Integer(string="Numéro d'assurance")
    default_status = fields.Char(string="status par défault")
    default_tarif = fields.Char(string="Tarif par défault")
    tva = fields.Float(string="Float")
    num_compte_comptabilite = fields.Char(string="Numéro compte comptabilité")
    bio = fields.Char(string="Bio")
    diplome = fields.Char(string="Diplôme")
    note_libre = fields.Char(string="Notes Libres")
    note_competance = fields.Char(string="Notes sur les Compétances")
    curriculum_viatae = fields.Binary("Curriculum_viatae", help="Charger votre document")
    filename_curiculum_vitae = fields.Char()
    contrat_travail = fields.Binary("Contrat de travail", help="Charger votre document")
    filename_contrat_travail = fields.Char()
    rapport_entretient_embauche = fields.Binary("Rapport d'entretient d'embauche", help="Charger votre document")
    formation_faite = fields.Char(string=" Formations Faites")
    formation_programme = fields.Char(string=" Formations Programmés")
    fonction_id = fields.Many2one('intervenant.fonction', string="Fonction", help="Choisir une fonction ")

    @api.constrains('curriculum_viatae')
    def _check_attachments(self):
        if self.filename_curiculum_vitae:
            if not self.filename_curiculum_vitae:
                raise exceptions.ValidationError(_("Veuillez charger un document!"))
            else:
                # Check the file's extension
                tmp = self.filename_curiculum_vitae.split('.')
                ext = tmp[len(tmp) - 1]
                if (ext not in ['pdf', 'png', 'jpg']):
                    raise UserError('Format fichier non valide ! \n Format accepté : jpg , png , pdf ')

    @api.constrains('contrat_travail')
    def _check_attachments1(self):
        if self.filename_contrat_travail:
            if not self.filename_contrat_travail:
                raise exceptions.ValidationError(_("Veuillez charger un document!"))
            else:
                # Check the file's extension
                tmp1 = self.filename_contrat_travail.split('.')
                ext1 = tmp1[len(tmp1) - 1]
                if (ext1 not in ['pdf', 'png', 'jpg']):
                    raise UserError('Format fichier non valide ! \n Format accepté : jpg , png , pdf ')
