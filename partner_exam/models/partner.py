# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.tools import datetime, base64


class noteExamen(models.Model):
    _name = "info.examen"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Les Notes d'examens"

    partner_id = fields.Many2one('res.partner', string="Client")
    epreuve_a = fields.Float(string="Epreuve A(QCM):")
    epreuve_b = fields.Float(string="Epreuve B(QRO)")
    moyenne_generale = fields.Float(string="Moyenne Générale")
    mention = fields.Selection(selection=[
        ('recu', 'reçu'),
        ('ajourne', 'ajourné')],
        string="Mention", default=False)
    resultat = fields.Selection(selection=[
        ('recu', 'Reçu'),
        ('ajourne', 'Ajourné')], string="Résultat")
    date_exam = fields.Date(related="partner_id.mcm_session_id.date_exam", string="Date Examen")
    active = fields.Boolean('Active', default=True)
    module_ids = fields.One2many('mcmacademy.module', 'info_examen_id')
    date_today = fields.Date(string="Date d'envoi de relevée de note: ", default=datetime.today())
    company_id = fields.Many2one(
        'res.company', string='Company', change_default=True,
        default=lambda self: self.env.company,
        required=False, readonly=False)
    nombre_de_passage = fields.Selection(selection=[
        ('premier', 'premier'),
        ('deuxieme', 'deuxième'),
        ('troisieme', 'troisième')],
        string="Nombre De Passage", default="premier")

    presence = fields.Selection(selection=[
        ('present', 'Présent'),
        ('Absent', 'Absent')],
        string="Présence", default="present")

    # def _compute_historic_sessions(self):
    #     # here compute & fill related_ids with ids of related object
    #     a = []
    #     a = self.partner_id.historic_sessions_ids
    #     res = a
    #     self.historic_sessions_ids = res


    def action_get_attachment(self):
        """ this method called from button action in view xml """
        pdf = self.env.ref('partner_exam.report_id').render_qweb_pdf(self.ids)
        b64_pdf = base64.b64encode(pdf[0])
        # save pdf as attachment
        name = self.partner_id.name
        return self.env['ir.attachment'].create({
            'name': name,
            'type': 'binary',
            'datas': b64_pdf,
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/x-pdf'
        })

    def action_send_email(self):
        '''
        This function opens a window to compose an email, with the emai template message loaded by default
        '''

        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = \
                ir_model_data.get_object_reference('partner_exam', 'email_template_edi_invoice_id')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model': 'info.examen',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
        }

        lang = self.env.context.get('lang')
        if {'default_template_id', 'default_model', 'default_res_id'} <= ctx.keys():
            template = self.env['mail.template'].browse(ctx['default_template_id'])
            if template and template.lang:
                lang = template._render_template(template.lang, ctx['default_model'], ctx['default_res_id'])

        self = self.with_context(lang=lang)

        # for record in records:
        #     attachment = self.env['ir.attachment'].create( \
        #         {'name': 'Tax Exemption',
        #          'type': 'binary',
        #          'datas': record.x_tax_exemption,
        #          'res_model': 'crm.lead',
        #          'res_id': record.id, })

        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }


class resComapny(models.Model):
    _inherit = "res.partner"
    _description = ""

    note_exam = fields.Char("Note d'examen blanc")
    note_exam_id = fields.One2many('info.examen', 'partner_id')
    note_exam_count = fields.Integer(compute="compute_notes_exams_count")
    this_is_technical_field = fields.Boolean(readonly=True, default=True)

    @api.depends('note_exam_id')
    def get_prev_period(self, note_exam_id):
        if note_exam_id:
            result = self.cr("""SELECT id FROM info_examen WHERE id < %s ORDER BY id DESC LIMIT 1""", [note_exam_id])
            result = self.cr.dictfetchall()
            print
            print(result)
            result  # holds the one row data
            current_id = result[0]['id']
        return 0

    # @api.onchange('epreuve_a', 'epreuve_b', 'moyenne_generale', 'mention', 'resultat', 'nombre_de_passage',
    #               'partner_id')
    # def _def_onchange_epreuve(self):
    #     self.epreuve_a = 0.0
    #     self.epreuve_b = 0.0
    #     self.moyenne_generale = 0.0
    #     self.mention = False
    #     self.resultat = False
    #     self.nombre_de_passage = False
    #     for rec in self:
    #         if rec.note_exam_id or rec.note_exam_id.epreuve_a or rec.note_exam_id.epreuve_b:
    #             for recc in self.env['info.examen'].search([], limit=1, order='create_date desc'):
    #                 if rec.name == recc.partner_id.name:
    #                     print(rec.name)
    #                     rec.epreuve_a = recc.epreuve_a
    #                     rec.epreuve_b = recc.epreuve_b
    #                     rec.moyenne_generale = recc.moyenne_generale
    #                     rec.mention = recc.mention
    #                     rec.resultat = recc.resultat
    #                     rec.nombre_de_passage = recc.nombre_de_passage


    def compute_notes_exams_count(self):
        for record in self:
            record.note_exam_count = self.env['info.examen'].search_count(
                [('partner_id', 'child_of', self.id)])

    def get_notes_history(self):
        self.ensure_one()
        return {
            "name": self.name,
            "view_type": "form",
            "view_mode": "tree,form",
            "res_model": "info.examen",
            "type": "ir.actions.act_window",
            "domain": [("partner_id", "child_of", self.id)],
            'context': {'default_note_exam_id': self.note_exam_id.ids},
        }
