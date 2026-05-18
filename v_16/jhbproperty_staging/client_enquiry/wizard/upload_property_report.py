from odoo import fields, models, _
from odoo.exceptions import UserError

class UploadPropertyReport(models.TransientModel):
    _name = 'upload.property.report'
    _description = 'Upload Property Report'

    attachment_ids = fields.Many2many('ir.attachment',
                                      string="Attachment", tracking=True)
    upload_document_name = fields.Char(string="Name")
    upload_document_id = fields.Many2one(comodel_name='client.enquiry',help="Add the audit universe")

    document_id = fields.Many2one('enquiry.assessment', string="Audit Details")

    # def action_submit(self):
    #     if not self.upload_document_id.user_id:
    #         self.upload_document_id.user_id = self.env.user.id
    #
    #     self.upload_document_id.with_context(
    #         upload_report_document_ids=self.attachment_ids.ids
    #     ).action_upload_document()


