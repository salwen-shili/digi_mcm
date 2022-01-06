from odoo import fields,models,api

class MailTemplate(models.Model):
    _inherit = 'mail.template'

    sb_template_id = fields.Char('Sendinblue Id')
    sb_sender_id = fields.Many2one('sendinblue.senders','Sender')

    def generate_email(self, res_ids, fields=None):
        res = super(MailTemplate, self).generate_email(res_ids=res_ids, fields=fields)
        if self._context.get('default_model') in ['res.partner','crm.lead']:
            for rec in res_ids:
                partner = self.env[self._context.get('default_model')].browse(rec)
                if not res[rec].get('email_from'):
                    res[rec].update({'email_from':'%s <%s>' % (partner.company_id.name, partner.company_id.email)})
        return res