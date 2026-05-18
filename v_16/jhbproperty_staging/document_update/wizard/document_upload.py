from odoo import fields, models


class JMCDocumentWizard(models.TransientModel):
    _name = "jmc.documents"
    _description = "Document Request"


    name = fields.Char()
    owner_id = fields.Many2one('res.users', required=True, string="Owner", default=lambda self: self.env.user.id)
    partner_id = fields.Many2one('res.partner', string="Contact")
    folder_id = fields.Many2one('documents.folder', string="Workspace", required=True)
    res_model = fields.Char('Resource Model')
    res_id = fields.Integer('Resource ID')
    # folder_ids = fields.Many2many('documents.folder', compute="_compute_folder_ids")
    # jmc_number = fields.Char(string="JMC Number", required=True)
    document = fields.Binary(string="Document", required=True)
    folder = fields.Selection([('Assessment', 'Assessment'),
                               ('Valuation', 'Valuation'),
                               ('Transaction Report', 'Transaction Report'),
                               ('Committees', 'Committees'),
                               ('Tender', 'Tender'),
                               ('Executive Adjudication Committee', 'Executive Adjudication Committee'),
                               ('Agreement', 'Agreement')
                               ], required=True)
    transaction_folder = fields.Selection([('Transaction Report Draft', 'Transaction Report Draft'),
                                           ('Transaction Report Final Signed', 'Transaction Report Final Signed')])
    committee_folder = fields.Selection([('Transaction Committee', 'Transaction Committee'),
                                         ('Board Committee', 'Board Committee'),
                                         ('Technical Growth Cluster', 'Technical Growth Cluster'),
                                         ('Executive Management Team', 'Executive Management Team'),
                                         ('Section 79 Committee', 'Section 79 Committee'),
                                         ('Sub-Mayoral Committee', 'Sub-Mayoral Committee'),
                                         ('Mayoral Committee', 'Mayoral Committee'),
                                         ('Council', 'Council'),
                                         ('Section 79 Notice', 'Section 79 Notice'),])
    tender_folder = fields.Selection([('Bid Composition Memo', 'Bid Composition Memo'),
                                      ('Bid Specification Committee', 'Bid Specification Committee'),
                                      ('RFP Document', 'RFP Document'),
                                      ('Bid Advert', 'Bid Advert'),
                                      ('Bid evaluation Committee', 'Bid evaluation Committee')])
    executive_folder = fields.Selection([('EAC Report draft', 'EAC Report draft'),
                                         ('EAC Report Final Signed', 'EAC Report Final Signed'),
                                         ('Approved EAC Minutes', 'Approved EAC Minutes')])
    agreement_folder = fields.Selection([('Instruction to Legal for Development Sale/Lease Agreement',
                                          'Instruction to Legal for Development Sale/Lease Agreement'),
                                         ('Development Sale/Lease Agreement', 'Development Sale/Lease Agreement')])
    property_id = fields.Many2one('building', string="JMC Number")

    def action_upload_document(self):
        """Upload document"""
        property_name = self.property_id
        self.folder_id = self.env.ref('document_update.portfolio_city_interventions')
        jmc_folder = self.env['documents.folder'].search([('name', '=', property_name.jmc_number),
                                                          ('parent_folder_id', '=', self.folder_id.id)])
        if not jmc_folder:
            jmc_folder = self.env['documents.folder'].create({
                'name': property_name.jmc_number,
                'parent_folder_id': self.folder_id.id
            })
        document_folder = self.env['documents.folder'].search([
            ('name', '=', self.folder),
            ('parent_folder_id', '=', jmc_folder.id)])
        if not document_folder:
            document_folder = self.env['documents.folder'].create({
                'name': self.folder,
                'parent_folder_id': jmc_folder.id
            })
        final_folder = document_folder
        if self.transaction_folder:
            transaction_folder = self.env['documents.folder'].search([
                ('name', '=', self.transaction_folder),
                ('parent_folder_id', '=', document_folder.id)])
            if not transaction_folder:
                transaction_folder = self.env['documents.folder'].create({
                    'name': self.transaction_folder,
                    'parent_folder_id': document_folder.id
                })
            final_folder = transaction_folder
        if self.committee_folder:
            committee_folder = self.env['documents.folder'].search([
                ('name', '=', self.committee_folder),
                ('parent_folder_id', '=', document_folder.id)])
            if not committee_folder:
                committee_folder = self.env['documents.folder'].create({
                    'name': self.committee_folder,
                    'parent_folder_id': document_folder.id
                })
            final_folder = committee_folder
        if self.tender_folder:
            tender_folder = self.env['documents.folder'].search([
                ('name', '=', self.tender_folder),
                ('parent_folder_id', '=', document_folder.id)])
            if not tender_folder:
                tender_folder = self.env['documents.folder'].create({
                    'name': self.tender_folder,
                    'parent_folder_id': document_folder.id
                })
            final_folder = tender_folder
        if self.executive_folder:
            executive_folder = self.env['documents.folder'].search([
                ('name', '=', self.executive_folder),
                ('parent_folder_id', '=', document_folder.id)])
            if not executive_folder:
                executive_folder = self.env['documents.folder'].create({
                    'name': self.executive_folder,
                    'parent_folder_id': document_folder.id
                })
            final_folder = executive_folder
        if self.agreement_folder:
            agreement_folder = self.env['documents.folder'].search([
                ('name', '=', self.agreement_folder),
                ('parent_folder_id', '=', document_folder.id)])
            if not agreement_folder:
                agreement_folder = self.env['documents.folder'].create({
                    'name': self.agreement_folder,
                    'parent_folder_id': document_folder.id
                })
            final_folder = agreement_folder
        attachment = self.env['ir.attachment'].sudo().create({
            'name': self.name,
            'datas': self.document,
        })
        document = self.env['documents.document'].create({
            'name': self.name,
            'type': 'empty',
            'folder_id': final_folder.id,
            'owner_id': self.owner_id.id,
            'partner_id': self.partner_id.id if self.partner_id else False,
            'attachment_id': attachment.id,
            'res_model': self.res_model,
            'res_id': self.res_id,
            'jmc_number': property_name.jmc_number,
            'erf_number': property_name.name,
            'address': property_name.address,
            'jmc_property_id': property_name.id,
        })
