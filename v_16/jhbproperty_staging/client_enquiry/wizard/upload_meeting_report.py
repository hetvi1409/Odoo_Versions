from odoo import fields, models, _
from odoo.exceptions import UserError


class UploadMeetingReport(models.TransientModel):
    _name = 'upload.meeting.report'
    _description = 'Upload Meeting Report'

    assessment_id = fields.Many2one('enquiry.assessment',
                                    string='Assessment', help="Assessment")
    internal_meeting_document_ids = fields.Many2many('ir.attachment',
                                                     string='Reports', required=True)
    is_no_document_available = fields.Boolean(string="No document available")

    def action_submit(self):
        """Methode for submit the form"""
        if not self.is_no_document_available:
            if not self.internal_meeting_document_ids:
                raise UserError(_('Please add a documents'))
        if self.env.context.get('internal_meeting'):
            documents = []
            if self.internal_meeting_document_ids:
                for rec in self.internal_meeting_document_ids:
                    rec.res_model = self.assessment_id._name
                    rec.res_id = self.assessment_id.id
                    document = self.env.ref(
                        'client_enquiry.document_enquiry')
                    if self.assessment_id.property_id.sudo().region_id:
                        region = self.env['documents.folder'].sudo().search([
                            ('name', '=', self.assessment_id.property_id.sudo().region_id.name),
                            ('parent_folder_id', '=', document.id)
                        ])
                        if not region:
                            region = self.env['documents.folder'].sudo().create({
                                'name': self.assessment_id.property_id.sudo().region_id.name,
                                'parent_folder_id': document.id
                            })
                    else:
                        region = self.env['documents.folder'].sudo().search([
                            ('name', '=', "Undefined Region"),
                            ('parent_folder_id', '=', document.id)
                        ])
                        if not region:
                            region = self.env['documents.folder'].sudo().create({
                                'name': 'Undefined Region',
                                'parent_folder_id': document.id
                            })
                    jmc = self.env['documents.folder'].sudo().search([
                        ('name', '=', self.assessment_id.jmc_number),
                        ('parent_folder_id', '=', region.id)
                    ])
                    if not jmc:
                        jmc = self.env['documents.folder'].sudo().create({
                            'name': self.assessment_id.jmc_number,
                            'parent_folder_iddefault_res_id': region.id,
                        })
                    enquiry_folder = self.env['documents.folder'].sudo().search(
                        [
                            ('name', '=', self.assessment_id.name),
                            ('parent_folder_id', '=', jmc.id)
                        ])
                    if not enquiry_folder:
                        enquiry_folder = self.env['documents.folder'].create({
                            'name': self.assessment_id.name,
                            'parent_folder_id': jmc.id,
                        })
                    assessment = self.env['documents.folder'].sudo().search([
                        ('name', '=', 'Committees'),
                        ('parent_folder_id', '=', enquiry_folder.id)
                    ])
                    if not assessment:
                        assessment = self.env['documents.folder'].sudo().create({
                            'name': 'Committees',
                            'parent_folder_id': enquiry_folder.id,
                        })
                    board = self.env['documents.folder'].sudo().search([
                        ('name', '=', 'Board committee'),
                        ('parent_folder_id', '=', assessment.id)
                    ])
                    if not board:
                        board = self.env['documents.folder'].sudo().create({
                            'name': 'Board committee',
                            'parent_folder_id': assessment.id,
                        })
                    document = self.env['documents.document'].sudo().create({
                        'name': rec.name,
                        'attachment_id': rec.id,
                        'folder_id': board.id
                    })
                    documents.append(document.id)
                self.assessment_id.internal_meeting_document_ids = self.internal_meeting_document_ids
                self.assessment_id.state = 'internal_meeting_approved'
                self.assessment_id.board_meeting_folder_id = assessment.id
                self.assessment_id.board_document_ids = self.env['documents.document'].browse(documents)
                return {
                    'effect': {
                        'fadeout': 'slow',
                        'message': 'Uploaded the Internal Meeting report',
                        'type': 'rainbow_man',
                    }
                }
            else:
                self.assessment_id.state = 'internal_meeting_approved'
                return {
                    'effect': {
                        'fadeout': 'slow',
                        'message': 'No document is uploaded',
                        'type': 'rainbow_man',
                    }
                }
        if self.env.context.get('executive_management_team'):
            documents = []
            if self.internal_meeting_document_ids:
                for rec in self.internal_meeting_document_ids:
                    rec.res_model = self.assessment_id._name
                    rec.res_id = self.assessment_id.id
                    document = self.env.ref('client_enquiry.document_enquiry')
                    if self.assessment_id.property_id.sudo().region_id:
                        region = self.env['documents.folder'].sudo().search([
                            ('name', '=', self.assessment_id.property_id.sudo().region_id.name),
                            ('parent_folder_id', '=', document.id)
                        ])
                        if not region:
                            region = self.env['documents.folder'].sudo().create({
                                'name': self.assessment_id.property_id.sudo().region_id.name,
                                'parent_folder_id': document.id
                            })
                    else:
                        region = self.env['documents.folder'].sudo().search([
                            ('name', '=', "Undefined Region"),
                            ('parent_folder_id', '=', document.id)
                        ])
                        if not region:
                            region = self.env['documents.folder'].sudo().create({
                                'name': 'Undefined Region',
                                'parent_folder_id': document.id
                            })
                    jmc = self.env['documents.folder'].sudo().search([
                        ('name', '=', self.assessment_id.jmc_number),
                        ('parent_folder_id', '=', region.id)
                    ])
                    if not jmc:
                        jmc = self.env['documents.folder'].sudo().create({
                            'name': self.assessment_id.jmc_number,
                            'parent_folder_id': region.id,
                        })
                    enquiry_folder = self.env['documents.folder'].sudo().search(
                        [
                            ('name', '=', self.assessment_id.name),
                            ('parent_folder_id', '=', jmc.id)
                        ])
                    if not enquiry_folder:
                        enquiry_folder = self.env['documents.folder'].create({
                            'name': self.assessment_id.name,
                            'parent_folder_id': jmc.id,
                        })
                    assessment = self.env['documents.folder'].sudo().search([
                        ('name', '=', 'Committees'),
                        ('parent_folder_id', '=', enquiry_folder.id)
                    ])
                    if not assessment:
                        assessment = self.env['documents.folder'].sudo().create({
                            'name': 'Committees',
                            'parent_folder_id': enquiry_folder.id,
                        })
                    executive = self.env['documents.folder'].sudo().search([
                        ('name', '=', 'Executive Management Team'),
                        ('parent_folder_id', '=', assessment.id)
                    ])
                    if not executive:
                        executive = self.env['documents.folder'].sudo().create({
                            'name': 'Executive Management Team',
                            'parent_folder_id': assessment.id,
                        })
                    document = self.env['documents.document'].sudo().create({
                        'name': rec.name,
                        'attachment_id': rec.id,
                        'folder_id': executive.id
                    })
                    documents.append(document.id)
                self.assessment_id.executive_management_ids = self.internal_meeting_document_ids
                self.assessment_id.state = 'executive'
                self.assessment_id.executive_management_folder_id = executive.id
                self.assessment_id.executive_management_document_ids = self.env['documents.document'].browse(documents)
                return {
                    'effect': {
                        'fadeout': 'slow',
                        'message': 'Uploaded the Executive management team report',
                        'type': 'rainbow_man',
                    }
                }
            else:
                self.assessment_id.state = 'executive'
                return {
                    'effect': {
                        'fadeout': 'slow',
                        'message': 'No Document is uploaded',
                        'type': 'rainbow_man',
                    }
                }
        if self.env.context.get('mayoral'):
            documents = []
            if self.internal_meeting_document_ids:
                for rec in self.internal_meeting_document_ids:
                    rec.res_model = self.assessment_id._name
                    rec.res_id = self.assessment_id.id
                    document = self.env.ref('client_enquiry.document_enquiry')
                    if self.assessment_id.property_id.sudo().region_id:
                        region = self.env['documents.folder'].search([
                            ('name', '=', self.assessment_id.property_id.sudo().region_id.name),
                            ('parent_folder_id', '=', document.id)
                        ])
                        if not region:
                            region = self.env['documents.folder'].create({
                                'name': self.assessment_id.property_id.sudo().region_id.name,
                                'parent_folder_id': document.id
                            })
                    else:
                        region = self.env['documents.folder'].sudo().search([
                            ('name', '=', "Undefined Region"),
                            ('parent_folder_id', '=', document.id)
                        ])
                        if not region:
                            region = self.env['documents.folder'].sudo().create({
                                'name': 'Undefined Region',
                                'parent_folder_id': document.id
                            })
                    jmc = self.env['documents.folder'].sudo().search([
                        ('name', '=', self.assessment_id.jmc_number),
                        ('parent_folder_id', '=', region.id)
                    ])
                    if not jmc:
                        jmc = self.env['documents.folder'].sudo().create({
                            'name': self.assessment_id.jmc_number,
                            'parent_folder_id': region.id,
                        })
                    enquiry_folder = self.env['documents.folder'].sudo().search(
                        [
                            ('name', '=', self.assessment_id.name),
                            ('parent_folder_id', '=', jmc.id)
                        ])
                    if not enquiry_folder:
                        enquiry_folder = self.env['documents.folder'].create({
                            'name': self.assessment_id.name,
                            'parent_folder_id': jmc.id,
                        })
                    assessment = self.env['documents.folder'].sudo().search([
                        ('name', '=', 'Committees'),
                        ('parent_folder_id', '=', enquiry_folder.id)
                    ])
                    if not assessment:
                        assessment = self.env['documents.folder'].sudo().create({
                            'name': 'Committees',
                            'parent_folder_id': enquiry_folder.id,
                        })
                    mayoral = self.env['documents.folder'].sudo().search([
                        ('name', '=', 'Mayoral Committee'),
                        ('parent_folder_id', '=', assessment.id)
                    ])
                    if not mayoral:
                        mayoral = self.env['documents.folder'].sudo().create({
                            'name': 'Mayoral Committee',
                            'parent_folder_id': assessment.id,
                        })
                    document = self.env['documents.document'].sudo().create({
                        'name': rec.name,
                        'attachment_id': rec.id,
                        'folder_id': mayoral.id
                    })
                    documents.append(document.id)
                self.assessment_id.mayoral_attachment_ids = self.internal_meeting_document_ids
                self.assessment_id.state = 'mayoral_approved'
                self.assessment_id.mayoral_meeting_folder_id = mayoral.id
                self.assessment_id.mayoral_document_ids = self.env['documents.document'].browse(documents)
                return {
                    'effect': {
                        'fadeout': 'slow',
                        'message': 'Uploaded the Mayoral report',
                        'type': 'rainbow_man',
                    }
                }
            else:
                self.assessment_id.state = 'mayoral_approved'
                return {
                    'effect': {
                        'fadeout': 'slow',
                        'message': 'No document Uploaded',
                        'type': 'rainbow_man',
                    }
                }
        if self.env.context.get('sub_mayoral'):
            documents = []
            if self.internal_meeting_document_ids:
                for rec in self.internal_meeting_document_ids:
                    rec.res_model = self.assessment_id._name
                    rec.res_id = self.assessment_id.id
                    document = self.env.ref('client_enquiry.document_enquiry')
                    if self.assessment_id.property_id.sudo().region_id:
                        region = self.env['documents.folder'].sudo().search([
                            ('name', '=', self.assessment_id.property_id.sudo().region_id.name),
                            ('parent_folder_id', '=', document.id)
                        ])
                        if not region:
                            region = self.env['documents.folder'].sudo().create({
                                'name': self.assessment_id.property_id.sudo().region_id.name,
                                'parent_folder_id': document.id
                            })
                    else:
                        region = self.env['documents.folder'].sudo().search([
                            ('name', '=', "Undefined Region"),
                            ('parent_folder_id', '=', document.id)
                        ])
                        if not region:
                            region = self.env['documents.folder'].sudo().create({
                                'name': 'Undefined Region',
                                'parent_folder_id': document.id
                            })
                    jmc = self.env['documents.folder'].sudo().search([
                        ('name', '=', self.assessment_id.jmc_number),
                        ('parent_folder_id', '=', region.id)
                    ])
                    if not jmc:
                        jmc = self.env['documents.folder'].sudo().create({
                            'name': self.assessment_id.jmc_number,
                            'parent_folder_id': region.id,
                        })
                    enquiry_folder = self.env['documents.folder'].sudo().search(
                        [
                            ('name', '=', self.assessment_id.name),
                            ('parent_folder_id', '=', jmc.id)
                        ])
                    if not enquiry_folder:
                        enquiry_folder = self.env['documents.folder'].create({
                            'name': self.assessment_id.name,
                            'parent_folder_id': jmc.id,
                        })
                    assessment = self.env['documents.folder'].sudo().search([
                        ('name', '=', 'Committees'),
                        ('parent_folder_id', '=', enquiry_folder.id)
                    ])
                    if not assessment:
                        assessment = self.env['documents.folder'].sudo().create({
                            'name': 'Committees',
                            'parent_folder_id': enquiry_folder.id,
                        })
                    mayoral = self.env['documents.folder'].sudo().search([
                        ('name', '=', 'Sub-Mayoral Committee'),
                        ('parent_folder_id', '=', assessment.id)
                    ])
                    if not mayoral:
                        mayoral = self.env['documents.folder'].sudo().create({
                            'name': 'Sub-Mayoral Committee',
                            'parent_folder_id': assessment.id,
                        })
                    document = self.env['documents.document'].sudo().create({
                        'name': rec.name,
                        'attachment_id': rec.id,
                        'folder_id': mayoral.id
                    })
                    documents.append(document.id)
                self.assessment_id.sub_mayoral_attachment_ids = self.internal_meeting_document_ids
                self.assessment_id.state = 'sub_mayoral'
                self.assessment_id.sub_mayoral_folder_id = mayoral.id
                self.assessment_id.sub_mayoral_document_ids = self.env['documents.document'].browse(documents)
                return {
                    'effect': {
                        'fadeout': 'slow',
                        'message': 'Uploaded the Sub mayoral report',
                        'type': 'rainbow_man',
                    }
                }
            else:
                self.assessment_id.state = 'sub_mayoral'
                return {
                    'effect': {
                        'fadeout': 'slow',
                        'message': 'No document Uploaded',
                        'type': 'rainbow_man',
                    }
                }
        if self.env.context.get('council'):
            documents = []
            if self.internal_meeting_document_ids:
                for rec in self.internal_meeting_document_ids:
                    rec.res_model = self.assessment_id._name
                    rec.res_id = self.assessment_id.id
                    document = self.env.ref('client_enquiry.document_enquiry')
                    if self.assessment_id.property_id.sudo().region_id:
                        region = self.env['documents.folder'].sudo().search([
                            ('name', '=', self.assessment_id.sudo().property_id.region_id.name),
                            ('parent_folder_id', '=', document.id)
                        ])
                        if not region:
                            region = self.env['documents.folder'].sudo().create({
                                'name': self.assessment_id.property_id.sudo().region_id.name,
                                'parent_folder_id': document.id
                            })
                    else:
                        region = self.env['documents.folder'].sudo().search([
                            ('name', '=', "Undefined Region"),
                            ('parent_folder_id', '=', document.id)
                        ])
                        if not region:
                            region = self.env['documents.folder'].sudo().create({
                                'name': 'Undefined Region',
                                'parent_folder_id': document.id
                            })
                    jmc = self.env['documents.folder'].sudo().search([
                        ('name', '=', self.assessment_id.jmc_number),
                        ('parent_folder_id', '=', region.id)
                    ])
                    if not jmc:
                        jmc = self.env['documents.folder'].sudo().create({
                            'name': self.assessment_id.jmc_number,
                            'parent_folder_id': region.id,
                        })
                    enquiry_folder = self.env['documents.folder'].sudo().search(
                        [
                            ('name', '=', self.assessment_id.name),
                            ('parent_folder_id', '=', jmc.id)
                        ])
                    if not enquiry_folder:
                        enquiry_folder = self.env['documents.folder'].create({
                            'name': self.assessment_id.name,
                            'parent_folder_id': jmc.id,
                        })
                    assessment = self.env['documents.folder'].sudo().search([
                        ('name', '=', 'Committees'),
                        ('parent_folder_id', '=', enquiry_folder.id)
                    ])
                    if not assessment:
                        assessment = self.env['documents.folder'].sudo().create({
                            'name': 'Committees',
                            'parent_folder_id': enquiry_folder.id,
                        })
                    council = self.env['documents.folder'].sudo().search([
                        ('name', '=', 'Council Committee'),
                        ('parent_folder_id', '=', assessment.id)
                    ])
                    if not council:
                        council = self.env['documents.folder'].sudo().create({
                            'name': 'Council Committee',
                            'parent_folder_id': assessment.id,
                        })
                    document = self.env['documents.document'].sudo().create({
                        'name': rec.name,
                        'attachment_id': rec.id,
                        'folder_id': council.id
                    })
                    documents.append(document.id)
                self.assessment_id.council_attachment_ids = self.internal_meeting_document_ids
                self.assessment_id.council_meeting_folder_id = council.id
                self.assessment_id.council_document_ids = documents
                self.assessment_id.state = 'council_approved'
                return {
                    'effect': {
                        'fadeout': 'slow',
                        'message': 'Uploaded the council report',
                        'type': 'rainbow_man',
                    }
                }
            else:
                self.assessment_id.state = 'council_approved'
                return {
                    'effect': {
                        'fadeout': 'slow',
                        'message': 'No document Uploaded',
                        'type': 'rainbow_man',
                    }
                }
        if self.env.context.get('technical'):
            documents = []
            if self.internal_meeting_document_ids:
                for rec in self.internal_meeting_document_ids:
                    rec.res_model = self.assessment_id._name
                    rec.res_id = self.assessment_id.id
                    document = self.env.ref('client_enquiry.document_enquiry')
                    if self.assessment_id.property_id.sudo().region_id:
                        region = self.env['documents.folder'].sudo().search([
                            (
                            'name', '=', self.assessment_id.property_id.sudo().region_id.name),
                            ('parent_folder_id', '=', document.id)
                        ])
                        if not region:
                            region = self.env['documents.folder'].sudo().create({
                                'name': self.assessment_id.property_id.sudo().region_id.name,
                                'parent_folder_id': document.id
                            })
                    else:
                        region = self.env['documents.folder'].sudo().search([
                            ('name', '=', "Undefined Region"),
                            ('parent_folder_id', '=', document.id)
                        ])
                        if not region:
                            region = self.env['documents.folder'].sudo().create({
                                'name': 'Undefined Region',
                                'parent_folder_id': document.id
                            })
                    jmc = self.env['documents.folder'].sudo().search([
                        ('name', '=', self.assessment_id.jmc_number),
                        ('parent_folder_id', '=', region.id)
                    ])
                    if not jmc:
                        jmc = self.env['documents.folder'].sudo().create({
                            'name': self.assessment_id.jmc_number,
                            'parent_folder_id': region.id,
                        })
                    enquiry_folder = self.env['documents.folder'].sudo().search(
                        [
                            ('name', '=', self.assessment_id.name),
                            ('parent_folder_id', '=', jmc.id)
                        ])
                    if not enquiry_folder:
                        enquiry_folder = self.env['documents.folder'].create({
                            'name': self.assessment_id.name,
                            'parent_folder_id': jmc.id,
                        })
                    assessment = self.env['documents.folder'].sudo().search([
                        ('name', '=', 'Committees'),
                        ('parent_folder_id', '=', enquiry_folder.id)
                    ])
                    if not assessment:
                        assessment = self.env['documents.folder'].sudo().create({
                            'name': 'Committees',
                            'parent_folder_id': enquiry_folder.id,
                        })
                    technical = self.env['documents.folder'].sudo().search([
                        ('name', '=', 'Technical Growth Cluster'),
                        ('parent_folder_id', '=', assessment.id)
                    ])
                    if not technical:
                        technical = self.env['documents.folder'].sudo().create({
                            'name': 'Technical Growth Cluster',
                            'parent_folder_id': assessment.id,
                        })
                    document = self.env['documents.document'].sudo().create({
                        'name': rec.name,
                        'attachment_id': rec.id,
                        'folder_id': technical.id
                    })
                    documents.append(document.id)
                self.assessment_id.technical_growth_ids = self.internal_meeting_document_ids
                self.assessment_id.technical_growth_folder_id = technical.id
                self.assessment_id.technical_growth_document_ids = documents
                self.assessment_id.state = 'technical_growth'
                return {
                    'effect': {
                        'fadeout': 'slow',
                        'message': 'Uploaded the Technical growth report',
                        'type': 'rainbow_man',
                    }
                }
            else:
                self.assessment_id.state = 'technical_growth'
                return {
                    'effect': {
                        'fadeout': 'slow',
                        'message': 'Nod document uploaded',
                        'type': 'rainbow_man',
                    }
                }
        if self.env.context.get('council_section_79'):
            if self.internal_meeting_document_ids:
                documents = []
                for rec in self.internal_meeting_document_ids:
                    rec.res_model = self.assessment_id._name
                    rec.res_id = self.assessment_id.id
                    document = self.env.ref(
                        'client_enquiry.document_enquiry')
                    if self.assessment_id.property_id.sudo().region_id:
                        region = self.env['documents.folder'].sudo().search([
                            ('name', '=',
                             self.assessment_id.property_id.sudo().region_id.name),
                            ('parent_folder_id', '=', document.id)
                        ])
                        if not region:
                            region = self.env['documents.folder'].sudo().create({
                                'name': self.assessment_id.property_id.sudo().region_id.name,
                                'parent_folder_id': document.id
                            })
                    else:
                        region = self.env['documents.folder'].sudo().search([
                            ('name', '=', "Undefined Region"),
                            ('parent_folder_id', '=', document.id)
                        ])
                        if not region:
                            region = self.env['documents.folder'].sudo().create({
                                'name': 'Undefined Region',
                                'parent_folder_id': document.id
                            })
                    jmc = self.env['documents.folder'].sudo().search([
                        ('name', '=', self.assessment_id.jmc_number),
                        ('parent_folder_id', '=', region.id)
                    ])
                    if not jmc:
                        jmc = self.env['documents.folder'].sudo().create({
                            'name': self.assessment_id.jmc_number,
                            'parent_folder_id': region.id,
                        })
                    assessment = self.env['documents.folder'].sudo().search([
                        ('name', '=', 'Committees'),
                        ('parent_folder_id', '=', jmc.id)
                    ])
                    if not assessment:
                        assessment = self.env['documents.folder'].sudo().create({
                            'name': 'Committees',
                            'parent_folder_id': jmc.id,
                        })
                    section = self.env['documents.folder'].sudo().search([
                        ('name', '=', 'Section 79 Committee'),
                        ('parent_folder_id', '=', assessment.id)
                    ])
                    if not section:
                        section = self.env['documents.folder'].sudo().create({
                            'name': 'Section 79 Committee',
                            'parent_folder_id': assessment.id,
                        })
                    document = self.env['documents.document'].sudo().create({
                        'name': rec.name,
                        'attachment_id': rec.id,
                        'folder_id': section.id
                    })
                    documents.append(document.id)
                self.assessment_id.council_79_attachment_ids = self.internal_meeting_document_ids
                self.assessment_id.council_79_folder_id = section.id
                self.assessment_id.council_79_document_ids = documents
                self.assessment_id.state = 'council_79_approved'
                return {
                    'effect': {
                        'fadeout': 'slow',
                        'message': 'Uploaded the Council Section 79 report',
                        'type': 'rainbow_man',
                    }
                }
            else:
                self.assessment_id.state = 'council_79_approved'
                return {
                    'effect': {
                        'fadeout': 'slow',
                        'message': 'No document uploaded',
                        'type': 'rainbow_man',
                    }
                }
        if self.env.context.get('section_179'):
            documents = []
            polices = self.env['client.enquiry.sla.policy.status'].search([
                ('enquiry_id', '=', self.assessment_id.enquiry_id.id),
                ('status', '=', 'ongoing')
            ])
            for pol in polices:
                pol.reached_datetime = fields.Datetime.now()
            if self.internal_meeting_document_ids:
                for rec in self.internal_meeting_document_ids:
                    rec.res_model = self.assessment_id._name
                    rec.res_id = self.assessment_id.id
                    rec.public = True
                    document = self.env.ref(
                        'client_enquiry.document_enquiry')
                    if self.assessment_id.property_id.sudo().region_id:
                        region = self.env['documents.folder'].sudo().search([
                            ('name', '=',
                             self.assessment_id.property_id.sudo().region_id.name),
                            ('parent_folder_id', '=', document.id)
                        ])
                        if not region:
                            region = self.env['documents.folder'].sudo().create({
                                'name': self.assessment_id.property_id.sudo().region_id.name,
                                'parent_folder_id': document.id
                            })
                    else:
                        region = self.env['documents.folder'].sudo().search([
                            ('name', '=', "Undefined Region"),
                            ('parent_folder_id', '=', document.id)
                        ])
                        if not region:
                            region = self.env['documents.folder'].sudo().create({
                                'name': 'Undefined Region',
                                'parent_folder_id': document.id
                            })
                    jmc = self.env['documents.folder'].sudo().search([
                        ('name', '=', self.assessment_id.jmc_number),
                        ('parent_folder_id', '=', region.id)
                    ])
                    if not jmc:
                        jmc = self.env['documents.folder'].sudo().create({
                            'name': self.assessment_id.jmc_number,
                            'parent_folder_id': region.id,
                        })
                    enquiry_folder = self.env['documents.folder'].sudo().search(
                        [
                            ('name', '=', self.assessment_id.name),
                            ('parent_folder_id', '=', jmc.id)
                        ])
                    if not enquiry_folder:
                        enquiry_folder = self.env['documents.folder'].create({
                            'name': self.assessment_id.name,
                            'parent_folder_id': jmc.id,
                        })
                    section_79 = self.env['documents.folder'].sudo().search([
                        ('name', '=', 'Section 79 Notice'),
                        ('parent_folder_id', '=', enquiry_folder.id)
                    ])
                    if not section_79:
                        section_79 = self.env['documents.folder'].sudo().create({
                            'name': 'Section 79 Notice',
                            'parent_folder_id': enquiry_folder.id,
                        })
                    document = self.env['documents.document'].sudo().create({
                        'name': rec.name,
                        'attachment_id': rec.id,
                        'folder_id': section_79.id
                    })
                    documents.append(document.id)
                self.assessment_id.section_79_folder_id = section_79.id
                self.assessment_id.section_79_section_ids = documents
                self.assessment_id.state = 'approved'
                self.assessment_id.enquiry_id.state = 'completed'
                return {
                    'effect': {
                        'fadeout': 'slow',
                        'message': 'Uploaded the Section 79 Notice Report',
                        'type': 'rainbow_man',
                    }
                }
            else:
                self.assessment_id.state = 'approved'
                self.assessment_id.enquiry_id.state = 'completed'
                return {
                    'effect': {
                        'fadeout': 'slow',
                        'message': 'No document uploaded',
                        'type': 'rainbow_man',
                    }
                }

    def action_submit_upload(self):
        """Method for re-upload the documents"""
        if not self.internal_meeting_document_ids:
            raise UserError(_('Please add a documents'))
        if self.env.context.get('technical'):
            documents = []
            for rec in self.internal_meeting_document_ids:
                rec.res_model = self.assessment_id._name
                rec.res_id = self.assessment_id.id
                document = self.env.ref('client_enquiry.document_enquiry')
                if self.assessment_id.property_id.sudo().region_id:
                    region = self.env['documents.folder'].sudo().search([
                        (
                        'name', '=', self.assessment_id.property_id.sudo().region_id.name),
                        ('parent_folder_id', '=', document.id)
                    ])
                    if not region:
                        region = self.env['documents.folder'].sudo().create({
                            'name': self.assessment_id.property_id.sudo().region_id.name,
                            'parent_folder_id': document.id
                        })
                else:
                    region = self.env['documents.folder'].sudo().search([
                        ('name', '=', "Undefined Region"),
                        ('parent_folder_id', '=', document.id)
                    ])
                    if not region:
                        region = self.env['documents.folder'].sudo().create({
                            'name': 'Undefined Region',
                            'parent_folder_id': document.id
                        })
                jmc = self.env['documents.folder'].sudo().search([
                    ('name', '=', self.assessment_id.jmc_number),
                    ('parent_folder_id', '=', region.id)
                ])
                if not jmc:
                    jmc = self.env['documents.folder'].sudo().create({
                        'name': self.assessment_id.jmc_number,
                        'parent_folder_id': region.id,
                    })
                enquiry_folder = self.env['documents.folder'].sudo().search([
                    ('name', '=', self.assessment_id.name),
                    ('parent_folder_id', '=', jmc.id)
                ])
                if not enquiry_folder:
                    enquiry_folder = self.env['documents.folder'].create({
                        'name': self.assessment_id.name,
                        'parent_folder_id': jmc.id,
                    })
                assessment = self.env['documents.folder'].sudo().search([
                    ('name', '=', 'Committees'),
                    ('parent_folder_id', '=', enquiry_folder.id)
                ])
                if not assessment:
                    assessment = self.env['documents.folder'].sudo().create({
                        'name': 'Committees',
                        'parent_folder_id': enquiry_folder.id,
                    })
                technical = self.env['documents.folder'].sudo().search([
                    ('name', '=', 'Technical Growth Cluster'),
                    ('parent_folder_id', '=', assessment.id)
                ])
                if not technical:
                    technical = self.env['documents.folder'].sudo().create({
                        'name': 'Technical Growth Cluster',
                        'parent_folder_id': assessment.id,
                    })
                document = self.env['documents.document'].sudo().create({
                    'name': rec.name,
                    'attachment_id': rec.id,
                    'folder_id': technical.id
                })
                documents.append(document.id)
            self.assessment_id.technical_growth_ids = self.internal_meeting_document_ids
            self.assessment_id.technical_growth_folder_id = technical.id
            self.assessment_id.technical_growth_document_ids = documents
            return {
                'effect': {
                    'fadeout': 'slow',
                    'message': 'Uploaded the Technical growth report',
                    'type': 'rainbow_man',
                }
            }
        if self.env.context.get('internal_meeting'):
            documents = []
            for rec in self.internal_meeting_document_ids:
                rec.res_model = self.assessment_id._name
                rec.res_id = self.assessment_id.id
                document = self.env.ref(
                    'client_enquiry.document_enquiry')
                if self.assessment_id.property_id.sudo().region_id:
                    region = self.env['documents.folder'].sudo().search([
                        ('name', '=', self.assessment_id.property_id.sudo().region_id.name),
                        ('parent_folder_id', '=', document.id)
                    ])
                    if not region:
                        region = self.env['documents.folder'].sudo().create({
                            'name': self.assessment_id.property_id.sudo().region_id.name,
                            'parent_folder_id': document.id
                        })
                else:
                    region = self.env['documents.folder'].sudo().search([
                        ('name', '=', "Undefined Region"),
                        ('parent_folder_id', '=', document.id)
                    ])
                    if not region:
                        region = self.env['documents.folder'].sudo().create({
                            'name': 'Undefined Region',
                            'parent_folder_id': document.id
                        })
                jmc = self.env['documents.folder'].sudo().search([
                    ('name', '=', self.assessment_id.jmc_number),
                    ('parent_folder_id', '=', region.id)
                ])
                if not jmc:
                    jmc = self.env['documents.folder'].sudo().create({
                        'name': self.assessment_id.jmc_number,
                        'parent_folder_iddefault_res_id': region.id,
                    })
                enquiry_folder = self.env['documents.folder'].sudo().search([
                    ('name', '=', self.assessment_id.name),
                    ('parent_folder_id', '=', jmc.id)
                ])
                if not enquiry_folder:
                    enquiry_folder = self.env['documents.folder'].create({
                        'name': self.assessment_id.name,
                        'parent_folder_id': jmc.id,
                    })
                assessment = self.env['documents.folder'].sudo().search([
                    ('name', '=', 'Committees'),
                    ('parent_folder_id', '=', enquiry_folder.id)
                ])
                if not assessment:
                    assessment = self.env['documents.folder'].sudo().create({
                        'name': 'Committees',
                        'parent_folder_id': enquiry_folder.id,
                    })
                board = self.env['documents.folder'].sudo().search([
                    ('name', '=', 'Board committee'),
                    ('parent_folder_id', '=', assessment.id)
                ])
                if not board:
                    board = self.env['documents.folder'].sudo().create({
                        'name': 'Board committee',
                        'parent_folder_id': assessment.id,
                    })
                document = self.env['documents.document'].sudo().create({
                    'name': rec.name,
                    'attachment_id': rec.id,
                    'folder_id': board.id
                })
                documents.append(document.id)
            self.assessment_id.internal_meeting_document_ids = self.internal_meeting_document_ids
            self.assessment_id.state = 'internal_meeting_approved'
            self.assessment_id.board_meeting_folder_id = assessment.id
            self.assessment_id.board_document_ids = self.env['documents.document'].browse(documents)
            return {
                'effect': {
                    'fadeout': 'slow',
                    'message': 'Uploaded the Internal Meeting report',
                    'type': 'rainbow_man',
                }
            }
        if self.env.context.get('executive_management_team'):
            documents = []
            for rec in self.internal_meeting_document_ids:
                rec.res_model = self.assessment_id._name
                rec.res_id = self.assessment_id.id
                document = self.env.ref('client_enquiry.document_enquiry')
                if self.assessment_id.property_id.sudo().region_id:
                    region = self.env['documents.folder'].sudo().search([
                        ('name', '=', self.assessment_id.property_id.sudo().region_id.name),
                        ('parent_folder_id', '=', document.id)
                    ])
                    if not region:
                        region = self.env['documents.folder'].sudo().create({
                            'name': self.assessment_id.property_id.sudo().region_id.name,
                            'parent_folder_id': document.id
                        })
                else:
                    region = self.env['documents.folder'].sudo().search([
                        ('name', '=', "Undefined Region"),
                        ('parent_folder_id', '=', document.id)
                    ])
                    if not region:
                        region = self.env['documents.folder'].sudo().create({
                            'name': 'Undefined Region',
                            'parent_folder_id': document.id
                        })
                jmc = self.env['documents.folder'].sudo().search([
                    ('name', '=', self.assessment_id.jmc_number),
                    ('parent_folder_id', '=', region.id)
                ])
                if not jmc:
                    jmc = self.env['documents.folder'].sudo().create({
                        'name': self.assessment_id.jmc_number,
                        'parent_folder_id': region.id,
                    })
                enquiry_folder = self.env['documents.folder'].sudo().search([
                    ('name', '=', self.assessment_id.name),
                    ('parent_folder_id', '=', jmc.id)
                ])
                if not enquiry_folder:
                    enquiry_folder = self.env['documents.folder'].create({
                        'name': self.assessment_id.name,
                        'parent_folder_id': jmc.id,
                    })
                assessment = self.env['documents.folder'].sudo().search([
                    ('name', '=', 'Committees'),
                    ('parent_folder_id', '=', enquiry_folder.id)
                ])
                if not assessment:
                    assessment = self.env['documents.folder'].sudo().create({
                        'name': 'Committees',
                        'parent_folder_id': enquiry_folder.id,
                    })
                executive = self.env['documents.folder'].sudo().search([
                    ('name', '=', 'Executive Management Team'),
                    ('parent_folder_id', '=', assessment.id)
                ])
                if not executive:
                    executive = self.env['documents.folder'].sudo().create({
                        'name': 'Executive Management Team',
                        'parent_folder_id': assessment.id,
                    })
                document = self.env['documents.document'].sudo().create({
                    'name': rec.name,
                    'attachment_id': rec.id,
                    'folder_id': executive.id
                })
                documents.append(document.id)
            self.assessment_id.executive_management_ids = self.internal_meeting_document_ids
            self.assessment_id.executive_management_folder_id = executive.id
            self.assessment_id.executive_management_document_ids = self.env['documents.document'].browse(documents)
            return {
                'effect': {
                    'fadeout': 'slow',
                    'message': 'Uploaded the Executive management team report',
                    'type': 'rainbow_man',
                }
            }
        if self.env.context.get('council_section_79'):
            documents = []
            for rec in self.internal_meeting_document_ids:
                rec.res_model = self.assessment_id._name
                rec.res_id = self.assessment_id.id
                document = self.env.ref(
                    'client_enquiry.document_enquiry')
                if self.assessment_id.property_id.sudo().region_id:
                    region = self.env['documents.folder'].sudo().search([
                        ('name', '=',
                         self.assessment_id.property_id.sudo().region_id.name),
                        ('parent_folder_id', '=', document.id)
                    ])
                    if not region:
                        region = self.env['documents.folder'].sudo().create({
                            'name': self.assessment_id.property_id.sudo().region_id.name,
                            'parent_folder_id': document.id
                        })
                else:
                    region = self.env['documents.folder'].sudo().search([
                        ('name', '=', "Undefined Region"),
                        ('parent_folder_id', '=', document.id)
                    ])
                    if not region:
                        region = self.env['documents.folder'].sudo().create({
                            'name': 'Undefined Region',
                            'parent_folder_id': document.id
                        })
                jmc = self.env['documents.folder'].sudo().search([
                    ('name', '=', self.assessment_id.jmc_number),
                    ('parent_folder_id', '=', region.id)
                ])
                if not jmc:
                    jmc = self.env['documents.folder'].sudo().create({
                        'name': self.assessment_id.jmc_number,
                        'parent_folder_id': region.id,
                    })
                enquiry_folder = self.env['documents.folder'].sudo().search([
                    ('name', '=', self.assessment_id.name),
                    ('parent_folder_id', '=', jmc.id)
                ])
                if not enquiry_folder:
                    enquiry_folder = self.env['documents.folder'].create({
                        'name': self.assessment_id.name,
                        'parent_folder_id': jmc.id,
                    })
                assessment = self.env['documents.folder'].sudo().search([
                    ('name', '=', 'Committees'),
                    ('parent_folder_id', '=', enquiry_folder.id)
                ])
                if not assessment:
                    assessment = self.env['documents.folder'].sudo().create({
                        'name': 'Committees',
                        'parent_folder_id': enquiry_folder.id,
                    })
                section = self.env['documents.folder'].sudo().search([
                    ('name', '=', 'Section 79 Committee'),
                    ('parent_folder_id', '=', assessment.id)
                ])
                if not section:
                    section = self.env['documents.folder'].sudo().create({
                        'name': 'Section 79 Committee',
                        'parent_folder_id': assessment.id,
                    })
                document = self.env['documents.document'].sudo().create({
                    'name': rec.name,
                    'attachment_id': rec.id,
                    'folder_id': section.id
                })
                documents.append(document.id)
            self.assessment_id.council_79_attachment_ids = self.internal_meeting_document_ids
            self.assessment_id.council_79_folder_id = section.id
            self.assessment_id.council_79_document_ids = documents
            return {
                'effect': {
                    'fadeout': 'slow',
                    'message': 'Uploaded the Council Section 79 report',
                    'type': 'rainbow_man',
                }
            }
        if self.env.context.get('sub_mayoral'):
            documents = []
            for rec in self.internal_meeting_document_ids:
                rec.res_model = self.assessment_id._name
                rec.res_id = self.assessment_id.id
                document = self.env.ref('client_enquiry.document_enquiry')
                if self.assessment_id.property_id.sudo().region_id:
                    region = self.env['documents.folder'].sudo().search([
                        ('name', '=', self.assessment_id.property_id.sudo().region_id.name),
                        ('parent_folder_id', '=', document.id)
                    ])
                    if not region:
                        region = self.env['documents.folder'].sudo().create({
                            'name': self.assessment_id.property_id.sudo().region_id.name,
                            'parent_folder_id': document.id
                        })
                else:
                    region = self.env['documents.folder'].sudo().search([
                        ('name', '=', "Undefined Region"),
                        ('parent_folder_id', '=', document.id)
                    ])
                    if not region:
                        region = self.env['documents.folder'].sudo().create({
                            'name': 'Undefined Region',
                            'parent_folder_id': document.id
                        })
                jmc = self.env['documents.folder'].sudo().search([
                    ('name', '=', self.assessment_id.jmc_number),
                    ('parent_folder_id', '=', region.id)
                ])
                if not jmc:
                    jmc = self.env['documents.folder'].sudo().create({
                        'name': self.assessment_id.jmc_number,
                        'parent_folder_id': region.id,
                    })
                enquiry_folder = self.env['documents.folder'].sudo().search([
                    ('name', '=', self.assessment_id.name),
                    ('parent_folder_id', '=', jmc.id)
                ])
                if not enquiry_folder:
                    enquiry_folder = self.env['documents.folder'].create({
                        'name': self.assessment_id.name,
                        'parent_folder_id': jmc.id,
                    })
                assessment = self.env['documents.folder'].sudo().search([
                    ('name', '=', 'Committees'),
                    ('parent_folder_id', '=', enquiry_folder.id)
                ])
                if not assessment:
                    assessment = self.env['documents.folder'].sudo().create({
                        'name': 'Committees',
                        'parent_folder_id': enquiry_folder.id,
                    })
                mayoral = self.env['documents.folder'].sudo().search([
                    ('name', '=', 'Sub-Mayoral Committee'),
                    ('parent_folder_id', '=', assessment.id)
                ])
                if not mayoral:
                    mayoral = self.env['documents.folder'].sudo().create({
                        'name': 'Sub-Mayoral Committee',
                        'parent_folder_id': assessment.id,
                    })
                document = self.env['documents.document'].sudo().create({
                    'name': rec.name,
                    'attachment_id': rec.id,
                    'folder_id': mayoral.id
                })
                documents.append(document.id)
            self.assessment_id.sub_mayoral_attachment_ids = self.internal_meeting_document_ids
            self.assessment_id.sub_mayoral_folder_id = mayoral.id
            self.assessment_id.sub_mayoral_document_ids = self.env['documents.document'].browse(documents)
            return {
                'effect': {
                    'fadeout': 'slow',
                    'message': 'Uploaded the Sub mayoral report',
                    'type': 'rainbow_man',
                }
            }
        if self.env.context.get('mayoral'):
            documents = []
            for rec in self.internal_meeting_document_ids:
                rec.res_model = self.assessment_id._name
                rec.res_id = self.assessment_id.id
                document = self.env.ref('client_enquiry.document_enquiry')
                if self.assessment_id.property_id.sudo().region_id:
                    region = self.env['documents.folder'].search([
                        ('name', '=', self.assessment_id.property_id.sudo().region_id.name),
                        ('parent_folder_id', '=', document.id)
                    ])
                    if not region:
                        region = self.env['documents.folder'].create({
                            'name': self.assessment_id.property_id.sudo().region_id.name,
                            'parent_folder_id': document.id
                        })
                else:
                    region = self.env['documents.folder'].sudo().search([
                        ('name', '=', "Undefined Region"),
                        ('parent_folder_id', '=', document.id)
                    ])
                    if not region:
                        region = self.env['documents.folder'].sudo().create({
                            'name': 'Undefined Region',
                            'parent_folder_id': document.id
                        })
                jmc = self.env['documents.folder'].sudo().search([
                    ('name', '=', self.assessment_id.jmc_number),
                    ('parent_folder_id', '=', region.id)
                ])
                if not jmc:
                    jmc = self.env['documents.folder'].sudo().create({
                        'name': self.assessment_id.jmc_number,
                        'parent_folder_id': region.id,
                    })
                enquiry_folder = self.env['documents.folder'].sudo().search([
                    ('name', '=', self.assessment_id.name),
                    ('parent_folder_id', '=', jmc.id)
                ])
                if not enquiry_folder:
                    enquiry_folder = self.env['documents.folder'].create({
                        'name': self.assessment_id.name,
                        'parent_folder_id': jmc.id,
                    })
                assessment = self.env['documents.folder'].sudo().search([
                    ('name', '=', 'Committees'),
                    ('parent_folder_id', '=', enquiry_folder.id)
                ])
                if not assessment:
                    assessment = self.env['documents.folder'].sudo().create({
                        'name': 'Committees',
                        'parent_folder_id': enquiry_folder.id,
                    })
                mayoral = self.env['documents.folder'].sudo().search([
                    ('name', '=', 'Mayoral Committee'),
                    ('parent_folder_id', '=', assessment.id)
                ])
                if not mayoral:
                    mayoral = self.env['documents.folder'].sudo().create({
                        'name': 'Mayoral Committee',
                        'parent_folder_id': assessment.id,
                    })
                document = self.env['documents.document'].sudo().create({
                    'name': rec.name,
                    'attachment_id': rec.id,
                    'folder_id': mayoral.id
                })
                documents.append(document.id)
            self.assessment_id.mayoral_attachment_ids = self.internal_meeting_document_ids
            self.assessment_id.mayoral_meeting_folder_id = mayoral.id
            self.assessment_id.mayoral_document_ids = self.env['documents.document'].browse(documents)
            return {
                'effect': {
                    'fadeout': 'slow',
                    'message': 'Uploaded the Mayoral report',
                    'type': 'rainbow_man',
                }
            }
        if self.env.context.get('council'):
            documents = []
            for rec in self.internal_meeting_document_ids:
                rec.res_model = self.assessment_id._name
                rec.res_id = self.assessment_id.id
                document = self.env.ref('client_enquiry.document_enquiry')
                if self.assessment_id.property_id.sudo().region_id:
                    region = self.env['documents.folder'].sudo().search([
                        ('name', '=', self.assessment_id.sudo().property_id.region_id.name),
                        ('parent_folder_id', '=', document.id)
                    ])
                    if not region:
                        region = self.env['documents.folder'].sudo().create({
                            'name': self.assessment_id.property_id.sudo().region_id.name,
                            'parent_folder_id': document.id
                        })
                else:
                    region = self.env['documents.folder'].sudo().search([
                        ('name', '=', "Undefined Region"),
                        ('parent_folder_id', '=', document.id)
                    ])
                    if not region:
                        region = self.env['documents.folder'].sudo().create({
                            'name': 'Undefined Region',
                            'parent_folder_id': document.id
                        })
                jmc = self.env['documents.folder'].sudo().search([
                    ('name', '=', self.assessment_id.jmc_number),
                    ('parent_folder_id', '=', region.id)
                ])
                if not jmc:
                    jmc = self.env['documents.folder'].sudo().create({
                        'name': self.assessment_id.jmc_number,
                        'parent_folder_id': region.id,
                    })
                enquiry_folder = self.env['documents.folder'].sudo().search([
                    ('name', '=', self.assessment_id.name),
                    ('parent_folder_id', '=', jmc.id)
                ])
                if not enquiry_folder:
                    enquiry_folder = self.env['documents.folder'].create({
                        'name': self.assessment_id.name,
                        'parent_folder_id': jmc.id,
                    })
                assessment = self.env['documents.folder'].sudo().search([
                    ('name', '=', 'Committees'),
                    ('parent_folder_id', '=', enquiry_folder.id)
                ])
                if not assessment:
                    assessment = self.env['documents.folder'].sudo().create({
                        'name': 'Committees',
                        'parent_folder_id': enquiry_folder.id,
                    })
                council = self.env['documents.folder'].sudo().search([
                    ('name', '=', 'Council Committee'),
                    ('parent_folder_id', '=', assessment.id)
                ])
                if not council:
                    council = self.env['documents.folder'].sudo().create({
                        'name': 'Council Committee',
                        'parent_folder_id': assessment.id,
                    })
                document = self.env['documents.document'].sudo().create({
                    'name': rec.name,
                    'attachment_id': rec.id,
                    'folder_id': council.id
                })
                documents.append(document.id)
            self.assessment_id.council_attachment_ids = self.internal_meeting_document_ids
            self.assessment_id.council_meeting_folder_id = council.id
            self.assessment_id.council_document_ids = documents
            return {
                'effect': {
                    'fadeout': 'slow',
                    'message': 'Uploaded the council report',
                    'type': 'rainbow_man',
                }
            }

