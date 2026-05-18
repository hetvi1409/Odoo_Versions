from werkzeug import urls

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import html2plaintext


class AuditMethodology(models.Model):
    """Audit Methodology"""
    _name = 'audit.methodology'
    _description = "Audit Methodology"
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", required=True)

    financial_year_id = fields.Many2one('arp.year', string="Financial Period/Year", required=True)
    state = fields.Selection([('new', 'New'), ('review', 'Review'),  ('refuse', 'Refuse'),
                              ('approve', 'Approve')],
                             default="new", string="State")
    approved_date = fields.Datetime(string="Approved Date", )
    attachment_ids = fields.Many2many('ir.attachment',
                                      string="Upload Internal Audit Methodology")
    # requirements = fields.Char(string="Requirements", required=True,
    #                            help="Requirements")
    # record_work_done = fields.Char(string="Work done", required=False,
    #                                help="Record of work done")
    # conclusion = fields.Char(string="Conclusion", required=False,
    #                          help="Conclusion")
    notes = fields.Html(string="Notes", related="note_id.notes")
    note_id = fields.Many2one('audit.methodology.note', string="Notes")
    audit_id = fields.Many2one('audit.request', string="Audit")
    team_id = fields.Many2one('hr.department', string="Team", required=True)
    # team_reviewer_id = fields.Many2one('audit.team', string="Reviewer", required=True)
    # team_approver_id = fields.Many2one('audit.team', string="Approver", required=True)
    # role_id = fields.Many2one('audit.role', string="Roles")
    user_id = fields.Many2one('res.users', tracking=True,
                              string="Responsible Person/Preparer")
    # user_reviewer_id = fields.Many2one('res.users', tracking=True,
    #                           string="Responsible Person/Reviewer")
    feedback = fields.Char(string="Feedback", tracking=True)
    # audit_methodology_tracking_ids = fields.One2many('audit.methodology.tracking', 'audit_methodology_tracking_id', string='Tracking')
    # comment_ids = fields.One2many('audit.comments', 'audit_methodology_id',
    #                               tracking=False, string="Comments")
    document_ids = fields.Many2many('ir.attachment', 'documents_attachment_methodology_rel',
                                    string="Upload Documents")
    user_ids = fields.Many2many('res.users', string="Preparer")
    user_reviewer_ids = fields.Many2many('res.users', 'user_reviewer_rel', string="Reviewer")
    user_approver_ids = fields.Many2many('res.users', 'user_approver_aud_rel', string="Approver",)


    @api.onchange('team_id')
    def _onchange_team_id(self):
        """Onchange Team"""
        for rec in self:
            user = []
            if rec.team_id:
                role = self.env['audit.role'].search([('team_ids', 'in', rec.team_id.id), ('type', '=', 'Preparer')])
                user = role.team_member_ids.mapped('user_id').ids
            rec.user_ids = user

            reviewer = []
            if rec.team_id:
                role = self.env['audit.role'].search([('team_ids', 'in', rec.team_id.id), ('type', '=', 'Reviewer')])
                reviewer = role.team_member_ids.mapped('user_id').ids
            rec.user_reviewer_ids = reviewer
            approver = []
            if rec.team_id:
                role = self.env['audit.role'].search([('team_ids', 'in', rec.team_id.id), ('type', '=', 'Approver')])
                approver = role.team_member_ids.mapped('user_id').ids
            rec.user_approver_ids = approver

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            record._create_document_records()
        return records

    def write(self, vals):
        # Update the record
        res = super(AuditMethodology, self).write(vals)
        # Automatically create a document record
        self._create_document_records()
        return res

    def _create_document_records(self):
        document = self.env['documents.document']
        for record in self:
            for attachment in record.document_ids:
                document.create({
                    'name': attachment.name,
                    'attachment_id': attachment.id,
                    'folder_id': 1,
                    # Specify the folder ID or logic to determine the correct folder
                    'owner_id': self.env.user.id,
                    # Optional: assign the current user as the owner
                })

    @api.onchange('user_id')
    def _onchange_user_id(self):
        """Onchange user id"""
        self.team_id = self.user_id.team_id.id
        # self.role_id = self.user_id.role_id.id

    def get_list_url(self):
        """Method for create the url."""
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        Urls = urls.url_join(base_url,
                             'web#id=%s&model=audit.methodology&view_type=list' % self.id)
        return Urls

    def action_review(self):
        """method for review"""
        # if not self.comment_ids:
        #     raise UserError(_("Please add the comments"))
        # self.state = 'review'
        mail_template = self.env.ref(
            'internal_audit_system.email_template_audit_methodology_review')
        mail_template.send_mail(self.id, force_send=True)
        previous_state = self.state
        self.state = 'review'
        # for record in self:
        #     # Add a new line in the tracking
        #     self.env['audit.methodology.tracking'].create({
        #         'audit_methodology_tracking_id': record.id,
        #         'user_id': self.env.user.id,
        #         'previous_stage_id': previous_state,
        #         'new_stage_id': record.state,
        #         'date': fields.Datetime.now(),
        #     })

    def action_approve(self):
        """Method for approve"""
        if not self.attachment_ids:
            raise UserError(_("Please Attach the documents"))
        mail_template = self.env.ref(
            'internal_audit_system.email_template_audit_methodology_approve')
        mail_template.send_mail(self.id, force_send=True)
        previous_state = self.state
        self.state = 'approve'
        self.approved_date = fields.Datetime.now()
        # Perform the approval action
        # for record in self:
        #     # Add a new line in the tracking
        #     self.env['audit.methodology.tracking'].create({
        #         'audit_methodology_tracking_id': record.id,
        #         'user_id': self.env.user.id,
        #         'previous_stage_id': previous_state,
        #         'new_stage_id': record.state,
        #         'date': fields.Datetime.now(),
        #     })
        # print("lklkl", self.audit_methodology_tracking_ids.previous_stage_id)

    def action_mark_discrepancy(self):
        """Action refuse the request"""
        # self.state = 'refuse'
        mail_template = self.env.ref(
            'internal_audit_system.email_template_audit_methodology_refuse')
        mail_template.send_mail(self.id, force_send=True)
        previous_state = self.state
        self.state = 'refuse'
        # Perform the approval action
        # for record in self:
        #     # Add a new line in the tracking
        #     self.env['audit.methodology.tracking'].create({
        #         'audit_methodology_tracking_id': record.id,
        #         'user_id': self.env.user.id,
        #         'previous_stage_id': previous_state,
        #         'new_stage_id': record.state,
        #         'date': fields.Datetime.now(),
        #     })

    def action_send_back_review(self):
        """Action SEND BACK TO REVIEW"""
        if not self.feedback:
            raise UserError(_('Please add the feedback'))
        # self.state = 'review'
        mail_template = self.env.ref(
            'internal_audit_system.email_template_audit_methodology_reviewed')
        mail_template.send_mail(self.id, force_send=True)
        previous_state = self.state
        self.state = 'review'
        # Perform the approval action
        # for record in self:
        #     # Add a new line in the tracking
        #     self.env['audit.methodology.tracking'].create({
        #         'audit_methodology_tracking_id': record.id,
        #         'user_id': self.env.user.id,
        #         'previous_stage_id': previous_state,
        #         'new_stage_id': record.state,
        #         'date': fields.Datetime.now(),
        #     })

    def action_send_back_new(self):
        """Action send back to newt"""
        # self.state = 'new'
        mail_template = self.env.ref(
            'internal_audit_system.email_template_audit_methodology_new')
        mail_template.send_mail(self.id, force_send=True)
        previous_state = self.state
        self.state = 'new'
        # Perform the approval action
        # for record in self:
        #     # Add a new line in the tracking
        #     self.env['audit.methodology.tracking'].create({
        #         'audit_methodology_tracking_id': record.id,
        #         'user_id': self.env.user.id,
        #         'previous_stage_id': previous_state,
        #         'new_stage_id': record.state,
        #         'date': fields.Datetime.now(),
        #     })

    def action_create_note(self):
        """Create a note for the audit methodology"""
        return {
            'name': _('Audit Notes'),
            'type': 'ir.actions.act_window',
            'res_model': 'audit.methodology.note',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_audit_methodology_id': self.id,
                'default_team_reviewer_id': self.team_id.id,
                'default_user_reviewer_ids': self.user_reviewer_ids.ids,
                'default_user_approver_ids': self.user_approver_ids.ids,
            }
        }

    def action_edit_note(self):
        """Create a note for the audit methodology"""
        return {
            'name': _('Audit Notes'),
            'type': 'ir.actions.act_window',
            'res_model': 'audit.methodology.note',
            'view_mode': 'form',
            'target': 'new',
            'res_id': self.note_id.id,
            'domain': [('audit_methodology_id', '=', self.id)],
            # 'context': {
            #     'default_audit_methodology_id': self.id
            # }
        }

    @api.model_create_multi
    def create(self, vals_list):
        """Create multiple records and update linked audit requests and documents."""
        records = super(AuditMethodology, self).create(vals_list)
        for record in records:
            # preserve document sync from previous implementation
            record._create_document_records()
            if record.audit_id:
                record.audit_id.audit_methodology_id = record.id
        return records


class AuditMethodologyNote(models.Model):
    """Audit Methodology Note"""
    _name = 'audit.methodology.note'
    _description = 'Audit Methodology Note'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name")
    notes = fields.Html(string="Notes")
    audit_methodology_id = fields.Many2one('audit.methodology', string="Audit Methodology", required=True)
    state = fields.Selection([('new', 'New'), ('review', 'Review'), ('refuse', 'Refuse'),
                              ('approve', 'Approve')], tracking=True,
                             default="new", string="State")
    approver_id = fields.Many2one('res.users', string="Approvered By", readonly=True)
    team_reviewer_id = fields.Many2one('audit.team', string="Team",
                                       required=False, related="audit_methodology_id.team_id")
    team_approver_id = fields.Many2one('audit.team', string="Approver",
                                       required=False,)
    user_reviewer_ids = fields.Many2many('res.users', 'user_reviewer_id_rel',
                                         string="Reviewer", related="audit_methodology_id.user_reviewer_ids")
    user_approver_ids = fields.Many2many('res.users', 'user_approver_id_rel',
                                         string="Approver", related="audit_methodology_id.user_approver_ids")

    @api.onchange('team_reviewer_id')
    def _onchange_team_id(self):
        """Onchange Team"""
        for rec in self:
            # user = []
            # if rec.team_id:
            #     role = self.env['audit.role'].search([('team_id', '=', rec.team_id.id), ('type', '=', 'Preparer')])
            #     user = role.team_member_ids.mapped('user_id').ids
            # rec.user_ids = user

            reviewer = []
            if rec.team_reviewer_id:
                role = self.env['audit.role'].search([('team_id', '=', rec.team_reviewer_id.id), ('type', '=', 'Reviewer')])
                reviewer = role.team_member_ids.mapped('user_id').ids
            rec.user_reviewer_ids = reviewer

            approver = []
            if rec.team_reviewer_id:
                role = self.env['audit.role'].search([('team_id', '=', rec.team_reviewer_id.id), ('type', '=', 'Approver')])
                approver = role.team_member_ids.mapped('user_id').ids
            rec.user_approver_ids = approver

    @api.depends( 'team_reviewer_id', 'team_approver_id')
    def _compute_user_ids(self):
        """Compute User IDs for adding domains"""
        for rec in self:
            reviewer = []
            if rec.team_reviewer_id:
                reviewer = rec.team_reviewer_id.team_member_ids.mapped(
                    'user_id').ids
            rec.user_reviewer_ids = reviewer
            approver = []
            if rec.team_approver_id:
                approver = rec.team_approver_id.team_member_ids.mapped(
                    'user_id').ids
            rec.user_approver_ids = approver


    @api.model
    def create(self, values):
        """Updating values to audit request"""
        if values.get('notes'):
            # Generating name from first line of the description
            text = html2plaintext(values['notes'])
            name = text.strip().replace('*', '').partition("\n")[0]
            values['name'] = (name[:97] + '...') if len(name) > 100 else name
        else:
            values['name'] = _('Untitled Note')
        res = super().create(values)
        if res.audit_methodology_id:
            res.audit_methodology_id.note_id = res.id
        return res

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
