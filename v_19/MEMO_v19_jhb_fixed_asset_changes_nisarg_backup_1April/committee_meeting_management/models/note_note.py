from odoo import api, models, fields, _


class NoteNote(models.Model):
    """Class for notes"""
    _inherit = 'project.task'

    @api.model
    def create(self, vals):
        """generate purchase requisition sequence"""
        result = super(NoteNote, self).create(vals)
        if self.env.context.get('active_model') == 'committee.meeting':
            if self.env.context.get('active_id'):
                if self.env.context.get('notes'):
                    committee = self.env['committee.meeting'].browse(int(self.env.context.get('active_id')))
                    committee.note_id = result.id
                if self.env.context.get('agenda'):
                    committee = self.env['committee.meeting'].browse(int(self.env.context.get('active_id')))
                    committee.note_ids = [(4, result.id)]
                    committee.is_agenda = True
                if self.env.context.get('review'):
                    committee = self.env['committee.meeting'].browse(int(self.env.context.get('active_id')))
                    committee.note_review_ids = [(4, result.id)]
                    committee.review = True
        return result

    def action_edit(self):
        """For edit the note from the meeting"""
        return {
            'name': _('Notes'),
            'view_mode': 'form',
            'res_model': 'note.note',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': self.id
        }