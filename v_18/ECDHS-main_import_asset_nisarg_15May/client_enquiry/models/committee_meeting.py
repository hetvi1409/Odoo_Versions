from odoo import api, fields, models


class CommitteeMeeting(models.Model):
    _inherit = 'committee.meeting'

    assessment_id = fields.Many2one('enquiry.assessment',
                                    string="Assessment", help="Assessment",
                                    readonly=True)
    is_transaction = fields.Boolean(string="Transaction",
                                    help="Transaction Report")
    transaction_document_id = fields.Many2one('documents.document',
                                              string="Document",
                                              help="Documents")

    @api.model
    def create(self, values):
        """Method for adding some values to the assessment"""
        res = super(CommitteeMeeting, self).create(values)

        if self.env.context.get('assessment'):
            request = self.env[self.env.context.get('active_model')].browse(self.env.context.get('active_id'))

            res.assessment_id.sudo().committee_meeting_ids = [(4, res.id)]
            res.sudo().assessment_id.sudo().internal_meeting_ids = [(4, res.id)]
            request.meeting_id = res.id
            request.active = False
        return res

