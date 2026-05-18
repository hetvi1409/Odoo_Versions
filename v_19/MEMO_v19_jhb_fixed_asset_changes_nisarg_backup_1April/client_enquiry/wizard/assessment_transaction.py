from odoo import fields, models, _, Command


class AssessmentTransaction(models.TransientModel):
    """Class for assessment Transition"""
    _name = 'assessment.transaction'
    _description = 'Assessment Transaction'

    assessment_id = fields.Many2one('enquiry.assessment',
                                    string="Assessment", help="Assessment", readonly=True)
    jmc_number = fields.Char(related='assessment_id.jmc_number',
                             string='JMC number', help='JMC number')
    transition_report = fields.Binary(string="Transaction Report", help="Transaction Report", required=True)
    transition_report_name = fields.Char(string="Transition Report Name", help="Transition Report Name")

    def action_submit(self):
        """Method for submit transaction report"""
        assessment_folder = self.env.ref('client_enquiry.document_enquiry')
        if self.assessment_id.property_id.sudo().region_id:
            region = self.env['documents.document'].sudo().search([
                ('name', '=', self.assessment_id.property_id.sudo().region_id.name),
                ('folder_id', '=', assessment_folder.id),('type','=','folder')
            ])
            if not region:
                region = self.env['documents.document'].sudo().create({
                    'name': self.assessment_id.property_id.region_id.name,
                    'folder_id': assessment_folder.id,
                    'type':'folder'
                })
        else:
            region = self.env['documents.document'].sudo().search([
                ('name', '=', "Undefined Region"),
                ('folder_id', '=', assessment_folder.id),('type','=','folder')
            ])
            if not region:
                region = self.env['documents.document'].sudo().create({
                    'name': 'Undefined Region',
                    'folder_id': assessment_folder.id,
                    'type':'folder'
                })

        jmc = self.env['documents.document'].sudo().search([
            ('name', '=', self.assessment_id.jmc_number),
            ('folder_id', '=', region.id),('type','=','folder')
        ])
        if not jmc:
            jmc = self.env['documents.document'].sudo().create({
                'name': self.assessment_id.jmc_number,
                'folder_id': region.id,
                'type':'folder'
            })
        enquiry_folder = self.env['documents.document'].sudo().search([
            ('name', '=', self.assessment_id.name),
            ('folder_id', '=', jmc.id),('type','=','folder')
        ])
        if not enquiry_folder:
            enquiry_folder = self.env['documents.document'].sudo().create({
                'name': self.assessment_id.name,
                'folder_id': jmc.id,
                'type':'folder'
            })
        transaction = self.env['documents.document'].sudo().search([
            ('name', '=', 'Transaction Report'),
            ('folder_id', '=', enquiry_folder.id),('type','=','folder')
        ])
        if not transaction:
            transaction = self.env['documents.document'].sudo().create({
                'name': 'Transaction Report',
                'folder_id': enquiry_folder.id,
                'type':'folder'
            })
        sign_transaction = self.env['documents.document'].sudo().search([
            ('name', '=', 'Sign Transaction Report'),
            ('folder_id', '=', transaction.id),('type','=','folder')
        ])
        if not sign_transaction:
            sign_transaction = self.env['documents.document'].sudo().create({
                'name': 'Sign Transaction Report',
                'folder_id': transaction.id,
                'type':'folder'
            })
        action = self.env['documents.workflow.rule'].sudo().search([
            ('domain_folder_id', '=', transaction.id),
            ('create_model', '=', 'sign.template.direct')])
        if action:
            action.folder_id = sign_transaction.id
        if not action:
            action = self.env['documents.workflow.rule'].sudo().create({
                'domain_folder_id': transaction.id,
                'create_model': 'sign.template.direct',
                'name': 'Sign Transaction Report',
                'folder_id': sign_transaction.id
            })
        report = self.env['ir.attachment'].sudo().create({
            'name': self.transition_report_name,
            'datas': self.transition_report,
            'res_model': self.assessment_id._name,
            'res_id': self.assessment_id.id
        })
        # Commented this: Creating the sign document from the document module.
        document = self.env['documents.document'].sudo().create({
            'name': report.name,
            'attachment_id': report.id,
            'folder_id': transaction.id
        })
        self.assessment_id.transaction_folder_id = transaction.id
        # Crating sign documents.
        # template = self.env['sign.template'].create({
        #     'attachment_id': report.id,
        #     'folder_id': assessment.id,
        #
        # })
        # sign_request = self.env['sign.request'].create({
        #     'template_id': template.id,
        #     'reference': 'Sign Request Subject',
        #     'request_item_ids': [(0, 0, {
        #         'partner_id': self.env.user.partner_id.id,
        #         'role_id': self.env.ref('sign.sign_item_role_default').id
        #     })]
        # })
        self.assessment_id.transaction_report_ids = report
        self.assessment_id.transaction_document_id = document.id
        # self.assessment_id.transaction_sign_document_id = sign_request.id

        self.assessment_id.state = 'transition'
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Uploaded the Transaction report',
                'type': 'rainbow_man',
            }
        }

