import base64

from odoo import api, fields, models, _


class CalendarEvent(models.Model):
    """Adding agenda, meeting of minutes and vote"""
    _inherit = 'calendar.event'

    agenda = fields.Html(string="Agenda", help="Agenda")
    mom = fields.Html(string="Minutes Of Meeting", help="Minutes of meeting")
    survey_id = fields.Many2one('survey.survey', string="Vote", help='Vote')
    attachment_ids = fields.Many2many('ir.attachment', string="Documents")
    document_folder_id = fields.Many2one('documents.folder', string="Folder")

    need_section = fields.Boolean(string="Add More Agenda Section", compute="_compute_need_section")

    agenda_ids = fields.One2many('meeting.agenda', 'calendar_id', string="Agenda Details")
    mom_document_id = fields.Many2one('documents.document', string="MOM Document")
    mom_attachment_id = fields.Many2one('ir.attachment', string="MOM Attachment")
    agenda_document_id = fields.Many2one('documents.document', string="Agenda Document")
    agenda_attachment_id = fields.Many2one('ir.attachment', string="Agenda Attachment")

    def _compute_need_section(self):
        """Returns default value to the need_section field"""
        for rec in self:
            rec.need_section = self.env['ir.config_parameter'].sudo().get_param('board_management_system.need_section')

    def action_create_survey(self):
        """Create a new servey"""
        return {
            'name': _('Votes'),
            'view_mode': 'form',
            'res_model': 'survey.survey',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context':
                {
                    'meeting': True,
                    'default_meetings_id': self.id
                }
        }

    def action_edit_survey(self):
        """Edit a servey"""
        return {
            'name': _('Votes'),
            'view_mode': 'form',
            'res_model': 'survey.survey',
            'type': 'ir.actions.act_window',
            'res_id': self.survey_id.id,
        }

    def write(self, vals):
        """Adding documents to the records"""
        res = super().write(vals)
        if vals.get('attachment_ids'):
            main_folder = self.env.ref('board_management_system.documents_folder_meeting')
            for rec in vals.get('attachment_ids'):
                if rec[0] == 4:
                    attachment = self.env['ir.attachment'].browse(rec[-1])
                    meeting_folder = self.env['documents.folder'].search(
                        [('name', '=', self.name),
                         ('parent_folder_id', '=', main_folder.id)
                         ])
                    if not meeting_folder:
                        meeting_folder = self.env['documents.folder'].create({
                            'name': self.name,
                            'parent_folder_id': main_folder.id
                        })

                    document_folder = self.env['documents.folder'].search(
                        [('name', '=', "Document Library"),
                         ('parent_folder_id', '=', meeting_folder.id)
                         ])
                    if not document_folder:
                        document_folder = self.env['documents.folder'].create({
                            'name': "Document Library",
                            'parent_folder_id': meeting_folder.id
                        })
                    document = self.env['documents.document'].sudo().create({
                        'name': attachment.name,
                        'attachment_id': attachment.id,
                        'folder_id': document_folder.id
                    })
                    self.document_folder_id = meeting_folder.id
        return res

    def action_view_documents(self):
        """View tha attached documents"""
        return {
            'name': _('Documents'),
            'res_model': 'documents.document',
            'type': 'ir.actions.act_window',
            'view_mode': 'kanban,tree,form',
            'context': {
                'default_res_model': self._name,
                'default_res_id': self.id,
                'searchpanel_default_folder_id': self.document_folder_id.id
            }
        }

    def action_share_mom(self):
        """Share Meeting of minutes"""

        self.create_mom_document()
        data_id = self.mom_attachment_id.ids
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data._xmlid_lookup(
                'board_management_system.email_template_share_minutes_of_meeting')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data._xmlid_lookup(
                'mail.email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict(self.env.context or {})
        ctx.update({
            'default_model': self._name,
            'default_res_ids': self.ids,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'default_partner_ids': self.partner_ids.ids,
            'default_attachment_ids' : [(6, 0, data_id)]
        })
        action = {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }
        return action

    @api.onchange('appointment_type_id')
    def _onchange_appointment_type_id(self):
        """Adding the Attendees based on the appointment type"""
        for rec in self.appointment_type_id.staff_user_ids:
            self.update({
                'partner_ids': [(fields.Command.link(rec.partner_id.id))]
            })

    def action_send_mail(self):
        """Sending email notification"""
        self.sudo().create_mom_document()
        data_id = self.mom_attachment_id.ids
        self.sudo().create_agenda_document()

        agenda = self.agenda_attachment_id.ids
        data_id += agenda
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data._xmlid_lookup(
                'board_management_system.email_template_share_send_meeting_details')[
                1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data._xmlid_lookup(
                'mail.email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        if self.attachment_ids:
            data_id += self.attachment_ids.ids
        ctx = dict(self.env.context or {})
        ctx.update({
            'default_model': self._name,
            'default_res_ids': self.ids,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'default_partner_ids': self.partner_ids.ids,
            'default_attachment_ids': [(6, 0, data_id)]
        })
        action = {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            # 'views': [(compose_form_id, 'form')],
            # 'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }
        return action

    def create_mom_document(self):
        """Create a new MOM Document and save it in the document module."""
        report_template_id = self.env['ir.actions.report']._render_qweb_pdf(
            'board_management_system.minutes_of_meeting_report_action',
            res_ids=self.id)
        data_record = base64.b64encode(report_template_id[0])
        ir_values = {
            'name': "MOM",
            'type': 'binary',
            'datas': data_record,
            'store_fname': data_record,
            'mimetype': 'application/pdf',
            'res_id': self.id,
            'res_model': self._name
        }
        attachment = self.env['ir.attachment'].create(ir_values)
        main_folder = self.env.ref('board_management_system.documents_folder_meeting')
        meeting_folder = self.env['documents.folder'].search(
            [('name', '=', self.name),
             ('parent_folder_id', '=', main_folder.id)
             ])
        if not meeting_folder:
            meeting_folder = self.env['documents.folder'].create({
                'name': self.name,
                'parent_folder_id': main_folder.id
            })
        mom_document = self.env['documents.folder'].search(
            [('name', '=', "MOM"),
             ('parent_folder_id', '=', meeting_folder.id)
             ])
        if not mom_document:
            mom_document = self.env['documents.folder'].create({
                'name': "MOM",
                'parent_folder_id': meeting_folder.id
            })
        if self.mom_document_id:
            self.mom_document_id.attachment_id = attachment.id
        else:
            document = self.env['documents.document'].sudo().create({
                'name': attachment.name,
                'attachment_id': attachment.id,
                'folder_id': mom_document.id
            })
            self.mom_document_id = document.id
        self.mom_attachment_id = attachment.id

    def create_agenda_document(self):
        """Create a new agenda document"""

        report_template_id = self.env['ir.actions.report']._render_qweb_pdf(
            'board_management_system.agenda_report_action',
            res_ids=self.id)

        data_record = base64.b64encode(report_template_id[0])
        ir_values = {
            'name': "Agenda",
            'type': 'binary',
            'datas': data_record,
            'store_fname': data_record,
            'mimetype': 'application/pdf',
            'res_id': self.id,
            'res_model': self._name
        }
        attachment = self.env['ir.attachment'].create(ir_values)
        main_folder = self.env.ref(
            'board_management_system.documents_folder_meeting')
        meeting_folder = self.env['documents.folder'].search(
            [('name', '=', self.name),
             ('parent_folder_id', '=', main_folder.id)
             ])
        if not meeting_folder:
            meeting_folder = self.env['documents.folder'].create({
                'name': self.name,
                'parent_folder_id': main_folder.id
            })
        agenda_document = self.env['documents.folder'].search(
            [('name', '=', "Agenda"),
             ('parent_folder_id', '=', meeting_folder.id)
             ])
        if not agenda_document:
            agenda_document = self.env['documents.folder'].create({
                'name': "Agenda",
                'parent_folder_id': meeting_folder.id
            })
        if self.agenda_document_id:
            self.agenda_document_id.attachment_id = attachment.id
        else:
            document = self.env['documents.document'].sudo().create({
                'name': attachment.name,
                'attachment_id': attachment.id,
                'folder_id': agenda_document.id
            })
            self.agenda_document_id = document.id
        self.agenda_attachment_id = attachment.id


class MeetingAgenda(models.Model):
    """Create Sections for agenda"""
    _name = 'meeting.agenda'
    _description = "Agenda"

    name = fields.Html(string="Agenda")
    calendar_id = fields.Many2one('calendar.event', string="Calender Event")
