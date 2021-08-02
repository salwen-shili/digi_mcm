import datetime as datetime
from datetime import date, datetime, tzinfo, timedelta

from odoo import api, fields, models, _
# ce programme est crée Par Mabrouk Seifeddinne le 28/06/2021
# cette application fait la gestions des intervents dans une session
# on a herité des fields de res.partner par le champs intervenant_id pour la reecuperation automatique des fields
#chargement des documents curriculum_viatae,contrat_travail,rapport_entretient_embauche avec visualisation des attachements

class Intervenant(models.Model):
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _name = "info.listeintervenants"
    _description = "Add fields in session view"
    intervenant_id = fields.Many2one('res.partner', string="Nom et Prenom de l'intervenant" , required = True )
    # session_id = fields.Many2one('mcmacademy.session', string="session")
    state = fields.Many2one('res.country.state', string="Département")
    partner_ids = fields.One2many('res.partner', 'session_id', 'Partners')
    country_id = fields.Many2one('res.country', string="Pays_id")
    adresse = fields.Char(string="Adresse" , related="intervenant_id.street",required = True)
    email = fields.Char(related="intervenant_id.email",string="Email" , required = True)
    code_interne= fields.Char(string="Code interne" , required = True)
    mcm_session_id = fields.Many2one(string="session name" ,related="intervenant_id.mcm_session_id" ,required = True)
    ville = fields.Char(string="Ville", related="intervenant_id.city" )
    telephone = fields.Char(string="Téléphone" , related="intervenant_id.phone" , required = True)
    nationalite = fields.Char(string="Nationalité", related="intervenant_id.nationality")
    date_naissance = fields.Date(string="Date de naissance" , related="intervenant_id.birthday" ,required = True )
    ville_naissance = fields.Char(string="Ville de naissance", related="intervenant_id.birth_city", required = True)
    departement_naissance = fields.Char(string="Département de Naissance" ,related="intervenant_id.birth_state" , required = True)
    country_id = fields.Many2one(string="Pays" , related="intervenant_id.country_id", required = True)
    code_postale = fields.Char(string="Code_postale" , related="intervenant_id.zip" ,required = True)
    civilite = fields.Char(string="Civilité")
    langue = fields.Char(string="Langue" )
    social_security_number = fields.Char(string="Numéro de sécurité social",required = True)
    num_declaration_activité = fields.Char(string="Numéro de déclaration d'activité" , required = True)
    entreprise = fields.Char(string="Entreprise" ,required = True)
    active = fields.Boolean('Active', default=True)
    num_siret = fields.Integer(string="Num_Siret" , required = True)
    num_assurance = fields.Integer(string="Numéro d'assurance" , required = True)
    default_status = fields.Char(string="status par défault" , required = True )
    default_tarif = fields.Char(string="Tarif par défault" , required = True)
    tva = fields.Float(string="Float")
    num_compte_comptabilite = fields.Char(string="Numéro compte comptabilité")
    bio = fields.Char(string="Bio")
    diplome = fields.Char(string="Diplôme")
    note_libre = fields.Char(string="Notes Libres")
    note_competance = fields.Char(string="Notes sur les Compétances")
    curriculum_viatae = fields.Binary("Curriculum_viatae", help="Charger votre document" , filters ="*.png, *.jpeg ,*.pdf,*.doc,*.docx" )
    contrat_travail = fields.Binary("Contrat de travail", help="Charger votre document" ,filters ="*.png, *.jpeg ,*.pdf,*.doc,*.docx")
    rapport_entretient_embauche = fields.Binary("Rapport d'entretient d'embauche", help="Charger votre document" , filters ="*.png, *.jpeg ,*.pdf,*.doc,*.docx")
    formation_faite = fields.Char(string=" Formations Faites")
    formation_programme = fields.Char(string=" Formations Programmés")





