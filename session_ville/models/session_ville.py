from odoo import api, fields, models, _


class SessionVille(models.Model):
    _name = "session.ville"
    _rec_name = 'name_ville'
    _order = 'name_ville asc'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Ville"

    name_ville = fields.Char(string="Nom Ville")
    # Ce champ "active" pour permettre a l'utilisateur d'archiver un enregistrement(ville)
    active = fields.Boolean('Active', default=True)
    description = fields.Text()
    ville_formation = fields.Boolean('Habilitation electrique',default=False,track_visibility=True)
    session_adresse_examen_ids = fields.One2many('session.adresse.examen', 'session_ville_id')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

