from odoo import api, fields, models


class McmacademySessionVille(models.Model):
    _inherit = "mcmacademy.session"
     # "Inherit this mcmacademy.session to add list of villes"

    # lier chaque session par une ville et adresse d'examen
    session_ville_id = fields.Many2one('session.ville',string="Ville",required=True,track_visibility='always')#edit the field to be required and show field edit history
    session_adresse_examen =fields.Many2one('session.adresse.examen',"Adresse d'examen")
    phone = fields.Char(related="session_adresse_examen.phone")
    email = fields.Char(related="session_adresse_examen.email")
    #Add new field "lien" contains link of center adress exam
    lien = fields.Char(related="session_adresse_examen.lien", string="Lien d'accées au centre d'examen")

    @api.onchange('session_ville_id')
    def onchange_session_ville_id(self):
        """ Cette fonction pour afficher la liste des adresses de centre d'examen 
        liée par une seul ville choisi par l'utilisateur dans l'interface de session"""
        for rec in self:
            return {'domain': {'session_adresse_examen': [('session_ville_id', '=', rec.session_ville_id.id)]}}