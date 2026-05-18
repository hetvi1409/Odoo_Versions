from werkzeug import urls

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AssessmentValuation(models.Model):
    """Assessment Valuation"""
    _name = 'assessment.valuation'
    _description = 'Assessment valuation'

    name = fields.Char()
    property_id = fields.Many2one('building', string="Property")
    assessment_id = fields.Many2one('enquiry.assessment', string="Assessment",
                                    domain="[('state', 'in', ['valuation', 'objection'])]",
                                    required=True)
    property_number = fields.Char(string="Property Number")
    property_description = fields.Char(string="Property Description")
    address = fields.Char(string="Address", required=True)
    contract_ids = fields.Many2many('rental.contract',
                                    string="Lease")
    only_portion = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                    required=True,
                                    string="Only Portion need to be valued",
                                    help="If only a portion need to be valued")
    size = fields.Char(string="Size to be valued")
    property_category = fields.Selection([('commercial', 'Commercial'),
                                          ('industrial', 'Industrial'),
                                          ('residential', 'residential'),
                                          ('retail', 'Retail/Shop'),
                                          ('vacant', 'Vacant Land')],
                                         string="Property Category")
    purpose_valuation = fields.Selection(
        [('development', 'Possible Development'),
         ('sale', 'Sale')],
        string="Purpose of valuation")
    attachment_ids = fields.Many2many('ir.attachment', string="Assessment Documents")
    jmc_number = fields.Char(string="JMC Number", help="JMC number")

    @api.model
    def create(self, values):
        """Method for generating sequence"""
        if values.get('name', _('New')) == _('New'):
            values['name'] = self.env['ir.sequence'].next_by_code(
                'assessment.valuation') or _('New')
        return super(AssessmentValuation, self).create(values)

    # def action_approve(self):
    #     """Method for approve the assessment valuation"""
    #     for rec in self:
    #         rec.state = 'approve'
    #         base_url = self.env['ir.config_parameter'].sudo().get_param(
    #             'web.base.url')
    #         Urls = urls.url_join(base_url,
    #                              'web#id=%s&model=assessment.valuation&view_type=form' % rec.id)
    #         mail_content = _('Hi,<br>'
    #                          'Valuation %s was approved.'
    #                          '<div style = "text-align: center; margin-top: 16px;"><a href = "%s"'
    #                          'style = "padding: 5px 10px; font-size: 12px; line-height: 18px; color: #FFFFFF; '
    #                          'border-color:#875A7B;text-decoration: none; display: inline-block; '
    #                          'margin-bottom: 0px; font-weight: 400;text-align: center; vertical-align: middle; '
    #                          'cursor: pointer; white-space: nowrap; background-image: none; '
    #                          'background-color: #875A7B; border: 1px solid #875A7B; border-radius:3px;">'
    #                          'View %s</a></div>'
    #                          ) % (rec.name, Urls,
    #                               rec.name)
    #         # recipient_ids = self.env.ref(
    #         #     'client_enquiry.group_property_manager').users
    #         partner = rec.assessment_id.partner_id
    #         main_content = {
    #             'subject': _(
    #                 'Assessment Valuation Approved: %s' % self.assessment_id.name),
    #             'author_id': self.env.user.partner_id.id,
    #             'body_html': mail_content,
    #             'recipient_ids': [(6, 0, partner.ids)]
    #         }
    #         mail_id = self.env['mail.mail'].sudo().create(main_content)
    #         mail_id.mail_message_id.body = mail_content
    #         mail_id.sudo().send()
    #         rec.assessment_id.state = 'valuation_completed'
    #
    # def action_refuse(self):
    #     """Method for refuse the assessment valuation"""
    #     for rec in self:
    #         rec.state = 'refuse'
    #         base_url = self.env['ir.config_parameter'].sudo().get_param(
    #             'web.base.url')
    #         Urls = urls.url_join(base_url,
    #                              'web#id=%s&model=assessment.valuation&view_type=form' % rec.id)
    #         mail_content = _('Hi,<br>'
    #                          'Valuation %s was Refused.'
    #                          '<div style = "text-align: center; margin-top: 16px;"><a href = "%s"'
    #                          'style = "padding: 5px 10px; font-size: 12px; line-height: 18px; color: #FFFFFF; '
    #                          'border-color:#875A7B;text-decoration: none; display: inline-block; '
    #                          'margin-bottom: 0px; font-weight: 400;text-align: center; vertical-align: middle; '
    #                          'cursor: pointer; white-space: nowrap; background-image: none; '
    #                          'background-color: #875A7B; border: 1px solid #875A7B; border-radius:3px;">'
    #                          'View %s</a></div>'
    #                          ) % (rec.name, Urls,
    #                               rec.name)
    #         # recipient_ids = self.env.ref(
    #         #     'client_enquiry.group_property_manager').users
    #         partner = rec.assessment_id.partner_id
    #         main_content = {
    #             'subject': _(
    #                 'Assessment Valuation Refused: %s' % self.assessment_id.name),
    #             'author_id': self.env.user.partner_id.id,
    #             'body_html': mail_content,
    #             'recipient_ids': [(6, 0, partner.ids)]
    #         }
    #         mail_id = self.env['mail.mail'].sudo().create(main_content)
    #         mail_id.mail_message_id.body = mail_content
    #         mail_id.sudo().send()

    # def unlink(self):
    #     """Super this method to add a condition in deleting the record"""
    #     for rec in self:
    #         if rec.state != 'draft':
    #             raise ValidationError(_('We can only delete the valuation'
    #                                     ' in draft state.'))
    #     return super().unlink()
