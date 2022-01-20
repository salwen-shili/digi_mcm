# -*- coding: utf-8 -*-
from odoo import fields, models, _


class UpdateFieldFinancementWizard(models.TransientModel):
    _name = 'financement.partner.state.wizard'

    # define fields which you will use to change the partner fields for the selected partners
    # method update_partner_salle_examen which will be called from wizard once click on Planification des salles d'examens action in tree view of partners
    def update_financement_field_in_partner(self):
        # return all selected records using active_ids and you can filter them and use any validation you want
        partners = self.env['res.partner'].browse(self._context.get('active_ids'))
        # loop the partners
        for statut in partners:
            if statut and statut.etat_financement_cpf_cb != None and statut.mode_de_financement == "cpf":
                # set the selected field for each partner
                statut.etat_financement_cpf_cb = statut.statut_cpf



