from odoo import fields, models, _
from odoo.exceptions import UserError


class CommitteeMeeting(models.Model):
    """Inherit the class for add the agenda, notes, report and votes details."""
    _inherit = 'committee.meeting'

    meeting_link = fields.Char(string="Meeting Link", help="Meeting link")
    agenda = fields.Html(string="Agenda", help="Agenda")
    note_id = fields.Many2one('note.note', string="Notes", help="Notes for the meeting")
    note = fields.Html(string="Note", help="Note for the meeting", related='note_id.memo')
    note_ids = fields.Many2many('note.note', string="Notes",
                                help="Notes for the agenda")
    note_review_ids = fields.Many2many('note.note', 'note_review_rel', string="Notes",
                                help="Notes for the agenda")
    final = fields.Html(string="Final", help="Final")
    state = fields.Selection([('completed', 'Completed')])

    # state = fields.Selection(selection_add=[('completed', 'Completed'),
    #                                     ],
    #                          ondelete={'completed': 'cascade'})
    is_completed = fields.Boolean(string="Completed", help="Is Completed the meeting")
    survey_id = fields.Many2one('survey.survey', string="Vote", help='Vote')
    answer_done_count = fields.Integer(related="survey_id.answer_done_count")
    session_state = fields.Selection(related="survey_id.session_state")
    active_votes = fields.Boolean(related="survey_id.active")
    certification = fields.Boolean(related="survey_id.certification")
    question_ids = fields.One2many(related="survey_id.question_ids")
    is_agenda = fields.Boolean(string="Agenda", help="Agenda")
    review = fields.Boolean(string="Review", help="Review")

    def action_sign_document(self):
        """Method for open the document"""
        return {
            'name': _('Documents'),
            'res_model': 'documents.document',
            'type': 'ir.actions.act_window',
            'domain': [('res_model', '=', self.assessment_id._name),
                       ('res_id', 'in', self.assessment_id.ids)],
            'view_mode': 'kanban,tree,form',
            'context': {
                'default_res_model': self.assessment_id._name,
                'default_res_id': self.assessment_id.id,
                'searchpanel_default_folder_id': self.assessment_id.transaction_folder_id.id
            }
        }

    def action_create_note(self):
        """Create a new note"""
        note = self.agenda
        for rec in self.note_ids:
            note = note + rec.memo
        return {
            'name': _('Notes'),
            'view_mode': 'form',
            'res_model': 'note.note',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context':
                {
                    'notes': True,
                    'default_memo': note
                }
        }

    def action_edit_note(self):
        """Edit a note"""
        return {
            'name': _('Notes'),
            'view_mode': 'form',
            'res_model': 'note.note',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': self.note_id.id
        }

    def action_add_section(self):
        """Add a section"""
        return {
            'name': _('Notes'),
            'view_mode': 'form',
            'res_model': 'note.note',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context':
                {
                    'agenda': True,
                }
        }

    def action_add_section_review(self):
        """Add a section review"""
        return {
            'name': _('Notes'),
            'view_mode': 'form',
            'res_model': 'note.note',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context':
                {
                    'review': True,
                }
        }

    def action_convert_as_final(self):
        """"Covert the notes as final"""
        final = ""
        final += self.note
        for rec in self.note_review_ids:
            final += rec.memo
        self.final = final

    def action_completed(self):
        """Set the meeting is completed"""
        if not self.note_ids and not self.agenda:
            raise UserError(_('Please update the agenda'))
        if not self.note:
            raise UserError(_('Please add a note'))
        if not self.note_review_ids:
            raise UserError(_('Please Update the review'))
        if not self.survey_id:
            raise UserError(_('Please Create a voting survey'))
        self.is_completed = True

    def action_create_servery(self):
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
                    'default_meeting_id': self.id
                }
        }

    def action_edit_servery(self):
        """Edit a servey"""
        return {
            'name': _('Votes'),
            'view_mode': 'form',
            'res_model': 'survey.survey',
            'type': 'ir.actions.act_window',
            'res_id': self.survey_id.id,
        }

    def action_send_survey(self):
        """Send vote"""
        return self.survey_id.action_send_survey()

    def action_result_survey(self):
        """See the result"""
        return self.survey_id.action_result_survey()

    def action_start_session(self):
        """To start the session"""
        return self.survey_id.action_start_session()

    def action_open_session_manager(self):
        """To open the session manager"""
        return self.survey_id.action_open_session_manager()

    def action_end_session(self):
        """To end the session"""
        return self.survey_id.action_end_session()

    def action_test_survey(self):
        """To test the  servey"""
        return self.survey_id.action_test_survey()

    def action_unarchive_votes(self):
        """To unarchive the votes"""
        return self.survey_id.action_unarchive()

    def action_print_survey(self):
        """To print the survey"""
        return self.survey_id.action_print_survey()

    def action_archive_votes(self):
        return self.survey_id.action_archive()
