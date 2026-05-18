from werkzeug import urls
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class OwnershipVerification(models.TransientModel):
    """Class for to check the ownership"""
    _name = 'ownership.verification'

    enquiry_id = fields.Many2one('client.enquiry')
    comments = fields.Html(string="Comments", help="Add the Comments")
    jmc_number = fields.Char(string='JMC number', help='JMC number',tracking=True,readonly=True)
    type = fields.Selection([('verified', 'Verified'), ('not_verified', 'Not Verified')], required=True, string="Verification Result")
    attachment_image_ids = fields.Many2many('ir.attachment', relation="attachments_image_rel",
                                      string="Add Image", tracking=True)
    upload_document_name = fields.Char(string="Name")
    attachment_ids = fields.Many2many('ir.attachment', store=True,
                                      string="Assessment Report",tracking=True)


    def action_submit(self):
        if self.type == 'verified':
            self.enquiry_id.state = 'verification'
        else:
            self.enquiry_id.state = 'not_verified'





