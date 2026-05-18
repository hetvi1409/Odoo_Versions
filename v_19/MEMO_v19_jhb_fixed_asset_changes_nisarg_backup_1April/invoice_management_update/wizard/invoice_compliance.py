from odoo import fields, models, _
from odoo.exceptions import UserError


class InvoiceCompliance(models.TransientModel):
    """The Model for invoice Compliance"""
    _name = 'invoice.compliance.wizard'
    _description = "Invoice Compliance"

    name = fields.Char(string='Name')
    invoice_id = fields.Many2one('account.move', string='Invoice')
    partner_id = fields.Many2one('res.partner', string='Customer')
    competition_certificate = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                               string='WIP/Competition '
                                                      'certificate')
    before_and_after_picture = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                                string='Before and after '
                                                       'pictures (if '
                                                       'applicable)',
                                                help='this is for to verify '
                                                     'before and after picture')
    scm_process_followed = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                            string='SCM process followed',
                                            help='For verify the scm process')
    followed_method = fields.Selection(
        [('rfq', 'RFQ'), ('rfp', 'RFP'), ('other', 'Other')], string='Method')
    compliance_report = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                         string='CSD compliance report',
                                         help="TO check the compliance report")
    letter_appointment = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                          string='Letter of appointment',
                                          help='For check the letter of '
                                               'appointment')
    date_timeframe = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                      string='Date or timeframe of appointment',
                                      help='Check the Date or timeframe')
    scope_of_work = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                     string='Scope of work',
                                     help='Check the scope of work')
    value_appointment = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                         string='Value of appointment',
                                         help='Check the value of appointment')
    creditors_recon = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                       string='Creditors recon',
                                       help='Check the value Creditors recon')
    bank_account_confirmation = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                                 string='Bank account '
                                                        'confirmation',
                                                 help='Check the bank account '
                                                      'confirmation')
    proof_of_payment = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                        string='Proof of payment',
                                        help='Verify the Proof of payment')
    authorization_signature = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                               string='Authorisation signatures',
                                               help='Verify the authorization '
                                                    'signature')
    invoice_date = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                    string='Invoice date (within 30 days)',
                                    help='Verify the invoice date is with in '
                                         'the 30 days')
    date_stamp = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                  string='Date stamp',
                                  help='Verify the Date of stamp')
    cross_cast_bill = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                       string="Cast and cross cast bill of goods and services",
                                       help="- Cast and cross cast bill of goods and services")
    tax = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                           string='Tax Invoice, VAT Invoice or Invoice')
    correct_name = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                    string='Correct Name')
    address = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                               string='Address of JPC and supplier')
    vat = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                           string='VAT Number of JPC and supplier')

    def action_submit(self):
        """Method for submit the compliance form"""
        if not self.competition_certificate:
            raise UserError(_('Please enter a compliance certificate'))
        if not self.before_and_after_picture:
            raise UserError(_('Please enter before and after picture details'))
        if not self.scm_process_followed:
            raise UserError(_('Please enter Scm process followed details'))
        if not self.compliance_report:
            raise UserError(_('Please enter the compliance report details'))
        if not self.letter_appointment:
            raise UserError(_('Please enter the letter appointment details'))
        if not self.date_timeframe:
            raise UserError(_('Please enter the date frame details'))
        if not self.scope_of_work:
            raise UserError(_('Please enter scope of work details'))
        if not self.value_appointment:
            raise UserError(_('Please Update the Value appointment'))
        if not self.creditors_recon:
            raise UserError(_('Please enter the creditors reco details'))
        if not self.bank_account_confirmation:
            raise UserError(
                _('Please Enter the Bank account confirmation details'))
        if not self.proof_of_payment:
            raise UserError(_('Please Enter the Proof of payment'))
        if not self.authorization_signature:
            raise UserError(_('Please Enter the authorization signature'))
        if not self.invoice_date:
            raise UserError(_('Please Enter the Invoice date details'))
        if not self.date_stamp:
            raise UserError(_('Please Enter the date stamp details'))
        if not self.cross_cast_bill:
            raise UserError(_('Please Enter the cross cast bill details'))
        if not self.tax:
            raise UserError(_('please enter the tax details'))
        if not self.correct_name:
            raise UserError(_('Please enter the name'))
        if not self.address:
            raise UserError(_('Please enter the address details'))
        if not self.vat:
            raise UserError(_('Please enter the vat details'))
        if self.competition_certificate == 'yes' and self.scm_process_followed == 'yes' and self.compliance_report == 'yes' and self.letter_appointment == 'yes' and self.date_timeframe == 'yes' and self.scope_of_work == 'yes' and self.value_appointment == 'yes' and self.creditors_recon == 'yes' and self.bank_account_confirmation == 'yes' and self.proof_of_payment == 'yes' and self.authorization_signature == 'yes' and self.invoice_date == 'yes' and self.date_stamp == 'yes' and self.cross_cast_bill == 'yes' and self.tax == 'yes' and self.correct_name == 'yes' and self.address == 'yes' and self.vat == 'yes':
            self.invoice_id.compliance = True
            self.invoice_id.state = 'approved'
        else:

            mail_content = _('Hi %s,<br>'
                             'Your compliance for the invoice %s has been '
                             'cancelled. Please attach the invoice documents '
                             'and contact the finance team.'
                             ) % \
                           (self.partner_id.name, self.invoice_id.name)
            main_content = {
                'subject': _('Checklist for invoice is failed.'),
                'author_id': self.env.user.partner_id.id,
                'body_html': mail_content,
                'email_to': self.partner_id.email
            }
            mail_id = self.env['mail.mail'].sudo().create(main_content)
            mail_id.mail_message_id.body = mail_content
            mail_id.sudo().send()
            self.invoice_id.button_cancel()
