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
    num_agrement_jury = fields.Many2one(related="session_ville_id.num_agrement_jury", copy=True)
    state = fields.Selection(related='session_ville_id.state', string="Région", store=True, readonly=False)
    coach_id = fields.Many2many(related="session_ville_id.coach_id", track_visibility='always')

    @api.onchange('session_ville_id')
    def onchange_session_ville_id(self):
        """ Cette fonction pour afficher la liste des adresses de centre d'examen 
        liée par une seul ville choisi par l'utilisateur dans l'interface de session"""
        for rec in self:
            return {'domain': {'session_adresse_examen': [('session_ville_id', '=', rec.session_ville_id.id)]}}

    # @api.onchange('session_ville_id')
    # def auto_set_value_of_argument_number(self):
    #     """ Affectation automatique du valeur d'agrement selon les villes """
    #     if self.session_ville_id.name_ville == "Lyon":
    #         self.num_agrement_jury = "2022-020"
    #     elif self.session_ville_id.name_ville == "Bordeaux":
    #         self.num_agrement_jury = "2022-01-B"
    #     elif self.session_ville_id.name_ville == "Nantes":
    #         self.num_agrement_jury = "DREAL/STRV/2022-014"
    #     elif self.session_ville_id.name_ville == "Paris":
    #         self.num_agrement_jury = "2019-0110"
    #     elif self.session_ville_id.name_ville == "Toulouse":
    #         self.num_agrement_jury = ""
    #     elif self.session_ville_id.name_ville == "Marseille" or self.session_ville_id.name_ville == "Nice":
    #         self.num_agrement_jury = ""
    #     else:
    #         self.num_agrement_jury = ""
