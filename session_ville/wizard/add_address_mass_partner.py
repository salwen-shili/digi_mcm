# -*- coding: utf-8 -*-
from odoo import fields, models, _


class AddressSalleExamenWizard(models.TransientModel):
    _name = 'address.class.examen.wizard'
    _description = 'Create class exam entry.'

    # define the salle_id field which you will use to change the partner adress class for the selected partners, for example if the salle_id field is a char
    salle_id = fields.Many2one('session.adresse.examen', help="Choisir une adresse pour la salle d'examen!")

    # method update_partner_salle_examen which will be called from wizard once click on Planification des salles d'examens action in tree view of partners
    def update_partner_salle_examen(self):
        # return all selected records using active_ids and you can filter them and use any validation you want
        partners = self.env['res.partner'].browse(self._context.get('active_ids'))
        # loop the partners
        for salle in partners:
            # set the selected classe_id for each partner
            salle.salle_id = self.salle_id



