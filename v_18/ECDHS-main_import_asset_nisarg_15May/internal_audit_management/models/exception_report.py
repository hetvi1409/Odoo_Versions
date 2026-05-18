from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.tools import html2plaintext

class ExceptionReport(models.Model):
    _name = "exception.report"
    _rec_name = "requirements"

    requirements = fields.Char(string="Requirements", required=True,
                               help="Requirements")
    record_work_done = fields.Char(string="Work done", required=True,
                                   help="Record of work done")
    conclusion = fields.Char(string="Conclusion", required=True,
                             help="Conclusion")
    state = fields.Selection([('new', 'New'), ('review', 'Review'), ('refuse', 'Refuse'),
                              ('approve', 'Approve')],
                             default="new", string="State")
    attachment_ids = fields.Many2many('ir.attachment',
                                      string="Upload Risk Assessment "
                                             "And Response")


    notes = fields.Html(string="Notes", related="note_id.notes")
    note_id = fields.Many2one('exception.report.note', string="Notes")
    name = fields.Char()




    def action_review(self):
        """Review"""
        self.state = 'review'

    def action_approve(self):
        """Approve"""
        if not self.attachment_ids:
            raise UserError(_('Please attach the documents'))
        self.state = 'approve'

    def action_create_note(self):
        """Create a note for the audit methodology"""
        return {
            'name': _('Audit Notes'),
            'type': 'ir.actions.act_window',
            'res_model': 'exception.report.note',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_exception_report_id': self.id
            }
        }

    def action_edit_note(self):
        """Create a note for the audit methodology"""
        return {
            'name': _('Audit Notes'),
            'type': 'ir.actions.act_window',
            'res_model': 'exception.report.note',
            'view_mode': 'form',
            'target': 'new',
            'res_id': self.note_id.id,
            'domain': [('exception_report_id', '=', self.id)],
            # 'context': {
            #     'default_audit_methodology_id': self.id
            # }
        }

class FleetInternalAuditNote(models.Model):
    """Audit Methodology Note"""
    _name = 'exception.report.note'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name")
    notes = fields.Html(string="Notes")
    exception_report_id = fields.Many2one('exception.report', required=True)
    state = fields.Selection([('new', 'New'), ('review', 'Review'), ('refuse', 'Refuse'),
                              ('approve', 'Approve')], tracking=True,
                             default="new", string="State")
    approver_id = fields.Many2one('res.users', string="Approver", readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        records = super(FleetInternalAuditNote, self).create(vals_list)
        for record, vals in zip(records, vals_list):
            # Generate name based on notes
            notes = vals.get('notes')
            if notes:
                text = html2plaintext(notes)
                name = text.strip().replace('*', '').partition("\n")[0]
                record.name = (name[:97] + '...') if len(name) > 100 else name
            else:
                record.name = _('Untitled Note')

            # Link to exception report if provided
            if vals.get('exception_report_id'):
                record.exception_report_id.note_id = record.id
        return records

    def write(self, values):
        if values.get('notes'):
            # Generating name from first line of the description
            text = html2plaintext(values['notes'])
            name = text.strip().replace('*', '').partition("\n")[0]
            values['name'] = (name[:97] + '...') if len(name) > 100 else name
        else:
            values['name'] = _('Untitled Note')
        res = super().write(values)
        return res

    def action_review(self):
        """method for review"""
        self.state = 'review'

    def action_approve(self):
        """Method for approve"""
        self.state = 'approve'
        self.approver_id = self.env.uid

    def action_mark_discrepancy(self):
        """Action refuse the request"""
        self.state = 'refuse'

    def action_send_back_review(self):
        """Action SEND BACK TO REVIEW"""
        self.state = 'review'

    def action_send_back_new(self):
        """Action send back to newt"""
        self.state = 'new'
