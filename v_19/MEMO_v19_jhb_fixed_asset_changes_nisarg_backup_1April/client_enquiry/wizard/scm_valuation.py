from werkzeug import urls
from odoo import fields, models, _
from odoo.exceptions import UserError
# import subprocess
# from docx2pdf import convert
# import subprocess
# import io


class SCMValuation(models.TransientModel):
    """Model for SCM Valuation"""
    _name = 'scm.valuation.wizard'
    _description = "SCM Valuation"

    assessment_id = fields.Many2one('enquiry.assessment', string="Assessment",
                                    readonly=True)
    valuation_id = fields.Many2one('assessment.valuation', readonly=True)
    valuation_report = fields.Binary(string="Valuation report")
    valuation_report_name = fields.Char(string="Valuation report name")
    # proceed_request = fields.Selection([('yes', 'Yes'), ('no', 'No')])
    filename = fields.Char(string="Filename")

    def action_submit(self):
        """method to submit the assessment valuation"""
        if not self.valuation_report:
            raise UserError(_('Attach a Valuation report'))
        file = str(self.valuation_report_name).split('.')[-1]
        if file != 'pdf':
            raise UserError(_('Please attach the pdf report'))
        # if not self.proceed_request:
        #     raise UserError(_('Add proceed request'))
        self.assessment_id.valuation_report = self.valuation_report
        # self.assessment_id.proceed_request = self.proceed_request
        # Document creation
        assessment_folder = self.env.ref('client_enquiry.document_enquiry')
        if self.assessment_id.property_id.sudo().region_id:
            region = self.env['documents.document'].search([
                ('name', '=', self.assessment_id.property_id.sudo().region_id.name),
                ('folder_id', '=', assessment_folder.id)
            ])
            if not region:
                region = self.env['documents.document'].create({
                    'name': self.assessment_id.property_id.sudo().region_id.name,
                    'folder_id': assessment_folder.id
                })
        else:
            region = self.env['documents.document'].sudo().search([
                ('name', '=', "Undefined Region"),
                ('folder_id', '=', assessment_folder.id)
            ])
            if not region:
                region = self.env['documents.document'].sudo().create({
                    'name': 'Undefined Region',
                    'folder_id': assessment_folder.id
                })
        jmc = self.env['documents.document'].sudo().search([
            ('name', '=', self.assessment_id.jmc_number),
            ('folder_id', '=', region.id)
        ])
        if not jmc:
            jmc = self.env['documents.document'].sudo().create({
                'name': self.assessment_id.jmc_number,
                'folder_id': region.id,
            })
        enquiry_folder = self.env['documents.document'].sudo().search([
                ('name', '=', self.assessment_id.name),
                ('folder_id', '=', jmc.id)
            ])
        if not enquiry_folder:
            enquiry_folder = self.env['documents.document'].create({
                'name': self.assessment_id.name,
                'folder_id': jmc.id,
            })

        valuation = self.env['documents.document'].sudo().search([
            ('name', '=', 'Valuation'),
            ('folder_id', '=', enquiry_folder.id)
        ])
        if not valuation:
            valuation = self.env['documents.document'].sudo().create({
                'name': 'Valuation',
                'folder_id': enquiry_folder.id,
            })
        report = self.env['ir.attachment'].sudo().create({
            'name': self.valuation_report_name,
            'datas': self.valuation_report,
            'res_model': self.assessment_id._name,
            'res_id': self.assessment_id.id
        })
        document = self.env['documents.document'].sudo().create({
            'name': report.name,
            'attachment_id': report.id,
            'folder_id': valuation.id
        })
        self.assessment_id.valuation_document_id = document.id
        self.assessment_id.valuation_folder_id = valuation.id
        # if self.proceed_request == 'no':
        #     self.assessment_id.state = 'terminate'
        #     self.assessment_id.enquiry_id.state = 'cancelled'
        #     base_url = self.env['ir.config_parameter'].sudo().get_param(
        #         'web.base.url')
        #     Urls = urls.url_join(base_url,
        #                          'web#id=%s&model=enquiry.assessment&view_type=form' % self.assessment_id.id)
        #     mail_content = _('Hi,<br>'
        #                      'Your assessment %s was Terminated.'
        #                      '<div style = "text-align: center; margin-top: 16px;"><a href = "%s"'
        #                      'style = "padding: 5px 10px; font-size: 12px; line-height: 18px; color: #FFFFFF; '
        #                      'border-color:#875A7B;text-decoration: none; display: inline-block; '
        #                      'margin-bottom: 0px; font-weight: 400;text-align: center; vertical-align: middle; '
        #                      'cursor: pointer; white-space: nowrap; background-image: none; '
        #                      'background-color: #875A7B; border: 1px solid #875A7B; border-radius:3px;">'
        #                      'View %s</a></div>'
        #                      ) % (self.assessment_id.name, Urls,
        #                           self.assessment_id.name)
        #     # recipient_ids = self.env.ref(
        #     #     'client_enquiry.group_property_manager').users
        #     partner = self.assessment_id.partner_id
        #     main_content = {
        #         'subject': _(
        #             'Assessment Terminated: %s' % self.assessment_id.name),
        #         'author_id': self.env.user.partner_id.id,
        #         'body_html': mail_content,
        #         'recipient_ids': [(6, 0, partner.ids)]
        #     }
        #     mail_id = self.env['mail.mail'].sudo().create(main_content)
        #     mail_id.mail_message_id.body = mail_content
        #     mail_id.sudo().send()
        # else:
            # self.assessment_id.state = 'transition'

        self.assessment_id.state = 'valuation_completed'

        mail_template = self.env.ref(
            'client_enquiry.email_template_enquiry_assessment_upload_transaction')
        recipient_ids = self.env.ref(
            'client_enquiry.group_property_manager').users
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.assessment_id.id, force_send=True,
                                email_values=email_values)
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Uploaded the valuation report',
                'type': 'rainbow_man',
            }
        }

