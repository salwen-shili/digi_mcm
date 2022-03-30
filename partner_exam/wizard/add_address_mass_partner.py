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
            print("statut", statut)
            if statut and statut.etat_financement_cpf_cb != None and statut.mode_de_financement == "cpf":
                # set the selected field for each partner
                statut.etat_financement_cpf_cb = statut.statut_cpf
            # Remplir nombre de passage dans la fiche client
            # examen = self.env['info.examen'].sudo().search([('partner_id', "=", statut.id)], limit=1,
            #                                                order="id desc")
            # if examen:
            #     if examen.nombre_de_passage == "premier":
            #         statut.nombre_de_passage = "Premier" # affectation valeur "Premier" dans champ nombre de passage
            #     if examen.nombre_de_passage == "deuxieme":
            #         statut.nombre_de_passage = "Deuxième"
            #     if examen.nombre_de_passage == "troisieme":
            #         statut.nombre_de_passage = "Troisième"
            # Remplir les champ boolean pour recuperer les couleur (vert,rouge et orange)
            if statut.resultat == 'Admis(e)':
                statut.is_recu = True
                statut.is_ajourne = False
            if statut.resultat == 'Ajourné(e)':
                statut.is_ajourne = True
                statut.is_recu = False
            if statut.presence == 'Présent(e)':
                statut.is_present = True
                statut.is_Absent = False
                statut.is_absence_justifiee = False
            if statut.presence == 'Absent(e)':
                statut.is_Absent = True
                statut.is_present = False
                statut.is_absence_justifiee = False
            if statut.presence == 'Absence justifiée':
                statut.is_absence_justifiee = True
                statut.is_Absent = False
                statut.is_present = False



