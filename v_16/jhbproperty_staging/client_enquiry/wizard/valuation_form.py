from werkzeug import urls

from odoo import fields, models, _


class ValuationForm(models.TransientModel):
    """Assessment Validation"""
    _name = 'assessment.valuation.wizard'
    _description = 'Assessment validation'

    property_id = fields.Many2one('building', string="Property Name")
    assessment_id = fields.Many2one('enquiry.assessment', string="Assessment",
                                    readonly=True)
    property_number = fields.Char(string="Property Number")
    property_description = fields.Char(string="Property Description")
    address = fields.Char(string="Address", required=True)
    contract_ids = fields.Many2many('rental.contract',
                                    string="Lease")
    only_portion = fields.Selection([('yes', 'Yes'), ('no', 'No')], required=True,
                                    string="Only Portion need to be valued",
                                    help="If only a portion need to be valued")
    size = fields.Char(string="Size to be valued")
    # gis_print = fields.Binary(string="Assessment Report")
    # circulation_comments = fields.Text(string="Circulation comments")
    property_category = fields.Selection([('commercial', 'Commercial'),
                                          ('industrial', 'Industrial'),
                                          ('residential', 'residential'),
                                          ('retail', 'Retail/Shop'),
                                          ('vacant', 'Vacant Land')],
                                         string="Property Category")
    purpose_valuation = fields.Selection([('development', 'Possible Development'),
                                          ('sale', 'Sale')],
                                         string="Purpose of valuation")
    jmc_number = fields.Char(string="JMC Number", help="JMC number")
    attachment_ids = fields.Many2many('ir.attachment', help="Attachment")

    def action_submit(self):
        """Submit the valuation form"""
        valuation = self.env['assessment.valuation'].create({
            'assessment_id': self.assessment_id.id,
            'address': self.address,
            'only_portion': self.only_portion,
            'property_id': self.property_id.id,
            'property_number': self.property_number,
            'property_description': self.property_description,
            'contract_ids': self.contract_ids,
            'size': self.size,
            # 'gis_print': self.gis_print,
            # 'circulation_comments': self.circulation_comments,
            'property_category': self.property_category,
            'purpose_valuation': self.purpose_valuation,
            'jmc_number': self.jmc_number,
            'attachment_ids': self.attachment_ids,
        })
        self.assessment_id.state = 'valuation'
        self.assessment_id.valuation_ids = [(4, valuation.id)]
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        Urls = urls.url_join(base_url,
                             'web#id=%s&model=assessment.valuation&view_type=form' % valuation.id)
        mail_content = _('Hi,<br>'
                         'Check these valuation %s.'
                         '<div style = "text-align: center; margin-top: 16px;"><a href = "%s"'
                         'style = "padding: 5px 10px; font-size: 12px; line-height: 18px; color: #FFFFFF; '
                         'border-color:#875A7B;text-decoration: none; display: inline-block; '
                         'margin-bottom: 0px; font-weight: 400;text-align: center; vertical-align: middle; '
                         'cursor: pointer; white-space: nowrap; background-image: none; '
                         'background-color: #875A7B; border: 1px solid #875A7B; border-radius:3px;">'
                         'View %s</a></div>'
                         ) % (valuation.name, Urls,
                              valuation.name)
        recipient_ids = self.env.ref(
            'client_enquiry.group_property_manager').users
        partner = recipient_ids.mapped('partner_id')
        main_content = {
            'subject': _(
                'Valuation: %s' % self.assessment_id.name),
            'author_id': self.env.user.partner_id.id,
            'body_html': mail_content,
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_id = self.env['mail.mail'].sudo().create(main_content)
        mail_id.mail_message_id.body = mail_content
        mail_id.sudo().send()

        mail_template = self.env.ref(
            'client_enquiry.email_template_enquiry_assessment_upload_valuation')
        recipient_ids = self.env.ref(
            'client_enquiry.group_asset_evaluator').users
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.assessment_id.id, force_send=True,
                                email_values=email_values)

