# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time
from odoo import api, fields, models,_
from odoo.http import content_disposition

import logging
_logger = logging.getLogger(__name__)

class SurveyQuestion(models.Model):
    _inherit = 'survey.question'

    answer_score = fields.Float('Score')
    
class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"

    quizz_corrected = fields.Boolean(default=False,string="Examen corrigé")
    def update_partner_exam_result(self):
        for record in self:
            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'survey.user_input.wizard',
                'target': 'new',
                'context': {
                    'default_survey_user_input_id': self.ids[0],
                    'default_partner_id': record.partner_id.id,
                    'default_score': record.quizz_score,
                },
            }
    @api.model_create_multi
    def create(self, vals_list):
        for list in vals_list :

            if 'survey_id' in list and 'partner_id' in list :
                survey_id = list['survey_id']
                partner_id = list['partner_id']
                survey = self.env['survey.survey'].sudo().search([('id', "=", survey_id)],
                                                                    limit=1)
                partner = self.env['res.partner'].sudo().search([('id', "=", partner_id)],
                                                                    limit=1)
                if survey :
                    if survey.title == 'Examen blanc Français' :
                        print('title')
                        if partner :
                            print('partner')
                            if partner.phone:
                                phone = str(partner.phone.replace(' ', ''))[-9:]
                                phone = '+33' + ' ' + phone[0:1] + ' ' + phone[1:3] + ' ' + phone[3:5] + ' ' + phone[
                                                                                                               5:7] + ' ' + phone[
                                                                                                                            7:]
                                partner.phone = phone
                            url = 'https://tinyurl.com/mtw2tv8z'
                            body = "Cher %s, Pour profiter de la formation VTC à 20 euros vous devez passer un test d'entré de 30 min.Commencez ici : %s" % (
                                partner.name, url)
                            if body:
                                sms = self.env['mail.message'].sudo().search(
                                    [("body", "=", body), ("message_type", "=", 'sms'), ("res_id", "=", partner.id)])
                                if not sms:
                                    composer = self.env['sms.composer'].sudo().create({
                                        'res_model': 'res.partner',
                                        'res_ids': partner.id,
                                        'composition_mode': 'mass',
                                        'body': body,
                                        'mass_keep_log': True,
                                        'mass_force_send': True,
                                    })
                                    composer.action_send_sms()  # envoyer un sms d'inscription à l'examen blanc
                                if partner.phone:
                                    partner.phone = '0' + str(partner.phone.replace(' ', ''))[-9:]
        print('vals_list:', vals_list)
        return super(SurveyUserInput, self).create(vals_list)
    @api.depends('user_input_line_ids.answer_score', 'user_input_line_ids.question_id')
    def _compute_quizz_score(self):
        res = super(SurveyUserInput, self)._compute_quizz_score()
        for user_input in self:
            if user_input.question_ids :
                for question in user_input.question_ids :
                    if not question.labels_ids :
                        print('question :', question.title)

        return res

    @api.depends('user_input_line_ids.answer_score', 'user_input_line_ids.question_id')
    def _compute_quizz_score(self):
        for user_input in self:
            total_possible_score = sum([
                answer_score if answer_score > 0 else 0
                for answer_score in user_input.question_ids.mapped('labels_ids.answer_score')
            ])
            if user_input.question_ids :
                for question in user_input.question_ids :
                    if not question.labels_ids :
                        total_possible_score += question.answer_score
            if total_possible_score == 0:
                user_input.quizz_score = 0
            else:
                score = (sum(user_input.user_input_line_ids.mapped('answer_score')) / total_possible_score) * 100
                user_input.quizz_score = round(score, 2) if score > 0 else 0


class SurveyUserInputWizard(models.TransientModel):
    _name = 'survey.user_input.wizard'
    _description = 'confirm corrected exam'

    survey_user_input_id = fields.Many2one('survey.user_input', string="Examen")
    partner_id=fields.Many2one('res.partner',string="Client")
    score = fields.Float('Score (%)')

    def action_validate_correction_exam(self):
        self.env['survey.user_input'].sudo().search([('state', "=", 'new'),
                     ('partner_id', '=', self.partner_id.id)]).sudo().unlink()
        for rec in self:
            rec.survey_user_input_id.quizz_corrected = True
            rec.partner_id.note_exam = str(rec.score)
            other_user_input = self.env['survey.user_input'].sudo().search([
                ('partner_id', '=', rec.partner_id.id),
                ('survey_id', '=', rec.survey_user_input_id.survey_id.id),
                ('id', "!=", rec.survey_user_input_id.id)
            ])
            # if other_user_input:
            #     for user_input in other_user_input:
            #         user_input.sudo().unlink()
            mail_compose_message = self.env['mail.compose.message']
            mail_compose_message.fetch_sendinblue_template()
            if rec.score < 40:
                template_id = self.env['mail.template'].sudo().search(
                    [('subject', "=", "Résultat examen blanc : Ajourné MCM ACADEMY X BOLT"),
                     ('model_id', "=", 'res.partner')], limit=1)
                if template_id:
                    message = self.env['mail.message'].sudo().search(
                        [('subject', "=", "Résultat examen blanc : Ajourné MCM ACADEMY X BOLT"),
                         ('model', "=", 'res.partner'), ('res_id', "=", self.env.user.partner_id.id)],
                        limit=1)
                    if not message:
                        rec.partner_id.with_context(force_send=True).message_post_with_template(template_id.id,
                                                                                         composition_mode='comment',
                                                                                         )

                if rec.partner_id.phone:
                    phone = str(rec.partner_id.phone.replace(' ', ''))[-9:]
                    phone = '+33' + ' ' + phone[0:1] + ' ' + phone[1:3] + ' ' + phone[3:5] + ' ' + phone[
                                                                                                   5:7] + ' ' + phone[
                                                                                                                7:]
                    rec.partner_id.phone = phone
                body = "Bonjour %s, Vous avez malheureusement échoué à votre test d'entré pour la formation VTC. Merci de vérifier vos spams pour avoir plus d'information." % (
                    rec.partner_id.name)
                if body:
                    sms = self.env['mail.message'].sudo().search(
                        [("body", "=", body), ("message_type", "=", 'sms'), ("res_id", "=", rec.partner_id.id)])
                    if not sms:
                        composer = self.env['sms.composer'].with_context(
                            default_res_model='res.partner',
                            default_res_ids=rec.partner_id.id,
                            default_composition_mode='mass',
                        ).sudo().create({
                            'body': body,
                            'mass_keep_log': True,
                            'mass_force_send': True,
                        })

                        composer.action_send_sms()  # envoyer un sms d'echec d'examen
                    if rec.partner_id.phone:
                        rec.partner_id.phone = '0' + str(rec.partner_id.phone.replace(' ', ''))[-9:]

            else:
                succeeded_attempt = self.env['survey.user_input'].sudo().search([
                    ('partner_id', '=', rec.partner_id.id),
                    ('survey_id', '=', rec.survey_user_input_id.survey_id.id),
                ], limit=1)

                if succeeded_attempt:
                    report_sudo = self.env.ref('survey.certification_report').sudo()

                    report = report_sudo.render_qweb_pdf([succeeded_attempt.id], data={'report_type': 'pdf'})[0]
                    reporthttpheaders = [
                        ('Content-Type', 'application/pdf'),
                        ('Content-Length', len(report)),
                    ]
                    reporthttpheaders.append(('Content-Disposition', content_disposition('Certification.pdf')))
                mail_compose_message = self.env['mail.compose.message']
                mail_compose_message.fetch_sendinblue_template()
                template_id = False
                template_id = self.env['mail.template'].sudo().search(
                    [('name', "=", "BOLT - EXAMEN REUSSI MCM ACADEMY"),
                     ('model_id', "=", 'res.partner')], limit=1)
                if not template_id:
                    template_id = self.env['mail.template'].sudo().search(
                        [('subject', "=", "Inscription Examen VTC - MCM ACADEMY X BOLT"),
                         ('model_id', "=", 'res.partner')], limit=1)
                user = self.env['res.users'].sudo().search(
                    [('partner_id', "=", rec.partner_id.id)], limit=1)
                if template_id:
                    template_id.attachment_ids = False
                    template_id.attachment_ids = False
                    attachment = self.env['ir.attachment'].search(
                        [("name", "=", "certification.pdf"),('res_id',"=",rec.partner_id.id),('res_model',"=",'res.partner')], order='create_date desc',
                        limit=1)
                    if not attachment :
                        if succeeded_attempt:
                            attachment = self.env['ir.attachment'].search(
                                [("name", "=", "certification.pdf"), ('res_id', "=", succeeded_attempt.id),
                                 ('res_model', "=", 'survey.user_input')], order='create_date desc',
                                limit=1)
                    if attachment:
                        template_id.sudo().write({'attachment_ids': [(6, 0, attachment.ids)]})

                    rec.partner_id.with_context(force_send=True).message_post_with_template(template_id.id,
                                                                                     composition_mode='comment',
                                                                                     )
                    template_id.attachment_ids = False

                    if rec.partner_id.phone:
                        phone = str(rec.partner_id.phone.replace(' ', ''))[-9:]
                        phone = '+33' + ' ' + phone[0:1] + ' ' + phone[1:3] + ' ' + phone[3:5] + ' ' + phone[
                                                                                                       5:7] + ' ' + phone[
                                                                                                                    7:]
                        rec.partner_id.phone = phone
                    url = 'https://tinyurl.com/4hkrece9'
                    body = "Bonjour %s, Félicitation ! Vous avez réussi votre test. Vous pouvez finaliser votre inscription à la formation VTC : %s" % (
                        rec.partner_id.name,url)
                    if body:
                        sms = self.env['mail.message'].sudo().search(
                            [("body", "=", body), ("message_type", "=", 'sms'), ("res_id", "=", rec.partner_id.id)])
                        if not sms:
                            composer = self.env['sms.composer'].with_context(
                                default_res_model='res.partner',
                                default_res_ids=rec.partner_id.id,
                                default_composition_mode='mass',
                            ).sudo().create({
                                'body': body,
                                'mass_keep_log': True,
                                'mass_force_send': True,
                            })

                            composer.action_send_sms()  # envoyer un sms de reussite à l'examen
                        if rec.partner_id.phone:
                            rec.partner_id.phone = '0' + str(rec.partner_id.phone.replace(' ', ''))[-9:]