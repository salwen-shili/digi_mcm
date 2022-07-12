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
    state = fields.Selection([
        ('auvergne', 'Auvergne-Rhône-Alpes'),
        ('bourgogne', 'Bourgogne-Franche-Comté'),
        ('bretagne', 'Bretagne'),
        ('centre_val', 'Centre-Val de Loire'),
        ('grand_est', 'Grand Est'),
        ('hauts', 'Hauts-de-France'),
        ('martinique', 'Martinique'),
        ('normandie', 'Normandie'),
        ('aquitaine', 'Nouvelle-Aquitaine'),
        ('occitanie', 'Occitanie'),
        ('pays_loire', 'Pays de la Loire'),
        ('provence', "Provence-Alpes-Côte d'Azur"),
        ('ile_de_france', "Île-de-France"),
    ], default=False, tracking=True)
    num_agrement_jury = fields.Many2one('approval.number', string="Numéro d'agrément")


class SessionApprovalNumber(models.Model):
    _name = "approval.number"
    _description = "Approval number"

    name = fields.char()
    active = fields.Boolean('Active', default=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    description = fields.Char()

