from odoo import models,fields,Command

class DocumentsDocument(models.Model):
    _inherit = 'documents.document'

    def write(self, vals):
        if vals.get('active') is False:
            for record in self:
                if record.res_model_name == 'Client Enquiry':

                    client_enquiry = self.env['client.enquiry'].browse(record.res_id)
                    val = client_enquiry.attachment_ids.ids
                    if record.attachment_id and record.attachment_id.id in val:
                        val.remove(record.attachment_id.id)

                        record.attachment_id = False
                        client_enquiry.write({
                            'attachment_ids': [(6, 0, val)] if val else [(5, 0, 0)]
                        })

                elif record.res_model_name == 'Enquiry assessment':

                    enquiry_assessment = self.env['enquiry.assessment'].browse(record.res_id)
                    val = enquiry_assessment.attachment_ids.ids
                    val_doc = enquiry_assessment.upload_report_document_ids.ids

                    if record.attachment_id and record.attachment_id.id in val:
                        val.remove(record.attachment_id.id)

                        record.attachment_id = False
                        enquiry_assessment.write({
                            'attachment_ids': [(6, 0, val)] if val else [(5, 0, 0)]
                        })

                    elif record.attachment_id and record.attachment_id.id in val_doc:
                        val_doc.remove(record.attachment_id.id)

                        record.attachment_id = False
                        enquiry_assessment.write({
                            'upload_report_document_ids': [(6, 0, val_doc)] if val_doc else [(5, 0, 0)]
                        })
                elif record.res_model_name == 'Circulation Comments':

                    enquiry_assessment = self.env['circulation.comments'].browse(record.res_id)
                    val = enquiry_assessment.attachment_ids.ids

                    if record.attachment_id and record.attachment_id.id in val:
                        val.remove(record.attachment_id.id)

                        record.attachment_id = False
                        enquiry_assessment.write({
                            'attachment_ids': [(6, 0, val)] if val else [(5, 0, 0)]
                        })


        return super(DocumentsDocument, self).write(vals)





