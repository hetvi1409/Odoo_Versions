# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class TenderBriefingSession(models.Model):
    """Tender Briefing Session - Step 5 of Tender Process"""
    _name = 'sagovtender.briefing.session'
    _description = 'Tender Briefing Session'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'session_date desc, id desc'

    name = fields.Char(
        string='Session Reference',
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: _('New')
    )
    tender_id = fields.Many2one(
        'sagovtender.tender',
        string='Tender',
        required=True,
        ondelete='cascade',
        tracking=True
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    tender_number = fields.Char(
        string='Tender Number',
        related='tender_id.name',
        store=True,
        readonly=True
    )
    tender_title = fields.Char(
        string='Tender Title',
        related='tender_id.title',
        store=True,
        readonly=True
    )

    session_type = fields.Selection([
        ('compulsory', 'Compulsory Briefing'),
        ('optional', 'Optional Briefing'),
        ('site_visit', 'Site Visit'),
        ('combined', 'Briefing + Site Visit'),
    ], string='Session Type', required=True, default='optional', tracking=True)

    is_compulsory = fields.Boolean(
        string='Compulsory Attendance',
        default=False,
        tracking=True,
        help='If checked, non-attendance will disqualify bidders'
    )

    session_date = fields.Datetime(
        string='Session Date & Time',
        required=True,
        tracking=True
    )
    session_end_date = fields.Datetime(
        string='Session End Time',
        tracking=True
    )
    venue = fields.Char(
        string='Venue',
        required=True,
        tracking=True
    )
    venue_address = fields.Text(
        string='Venue Address',
        tracking=True
    )
    meeting_link = fields.Char(
        string='Virtual Meeting Link',
        help='Link for online/hybrid briefing sessions'
    )
    is_virtual = fields.Boolean(
        string='Virtual Session',
        default=False
    )

    site_visit_required = fields.Boolean(
        string='Site Visit Required',
        default=False,
        tracking=True
    )
    site_visit_location = fields.Char(
        string='Site Visit Location'
    )
    site_visit_date = fields.Datetime(
        string='Site Visit Date & Time'
    )
    site_visit_instructions = fields.Text(
        string='Site Visit Instructions'
    )

    registration_deadline = fields.Datetime(
        string='Registration Deadline',
        tracking=True,
        help='Deadline for bidders to register for the briefing'
    )
    max_attendees = fields.Integer(
        string='Maximum Attendees',
        help='Maximum number of attendees allowed (0 = unlimited)'
    )

    attendee_ids = fields.One2many(
        'sagovtender.briefing.attendee',
        'briefing_id',
        string='Attendees'
    )
    attendee_count = fields.Integer(
        string='Total Attendees',
        compute='_compute_attendee_count',
        store=True
    )
    registered_count = fields.Integer(
        string='Registered',
        compute='_compute_attendee_count',
        store=True
    )
    attended_count = fields.Integer(
        string='Attended',
        compute='_compute_attendee_count',
        store=True
    )

    question_ids = fields.One2many(
        'sagovtender.briefing.question',
        'briefing_id',
        string='Questions & Answers'
    )
    question_count = fields.Integer(
        string='Questions',
        compute='_compute_question_count',
        store=True
    )

    minutes = fields.Html(
        string='Minutes of Meeting',
        tracking=False,
    )
    key_points = fields.Text(
        string='Key Discussion Points'
    )
    clarifications_issued = fields.Html(
        string='Clarifications Issued',
        help='Official clarifications issued after the briefing'
    )

    addendum_required = fields.Boolean(
        string='Addendum Required',
        default=False,
        tracking=True,
        help='Check if tender documents need to be updated based on briefing'
    )
    addendum_description = fields.Text(
        string='Addendum Description'
    )

    responsible_user_id = fields.Many2one(
        'res.users',
        string='Responsible Officer',
        default=lambda self: self.env.user,
        tracking=True
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})

    state = fields.Selection([
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', required=True, tracking=True)

    notes = fields.Text(string='Notes')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('sagovtender.briefing.session') or _('New')
        return super(TenderBriefingSession, self).create(vals)

    @api.depends('attendee_ids', 'attendee_ids.state')
    def _compute_attendee_count(self):
        for record in self:
            record.attendee_count = len(record.attendee_ids)
            record.registered_count = len(record.attendee_ids.filtered(lambda a: a.state in ['registered', 'attended']))
            record.attended_count = len(record.attendee_ids.filtered(lambda a: a.state == 'attended'))

    @api.depends('question_ids')
    def _compute_question_count(self):
        for record in self:
            record.question_count = len(record.question_ids)

    @api.onchange('session_type')
    def _onchange_session_type(self):
        """Automatically set is_compulsory when session_type is 'compulsory'"""
        if self.session_type == 'compulsory':
            self.is_compulsory = True
        else:
            self.is_compulsory = False

    @api.constrains('session_date', 'session_end_date')
    def _check_session_dates(self):
        for record in self:
            if record.session_end_date and record.session_date:
                if record.session_end_date <= record.session_date:
                    raise ValidationError(_('Session end time must be after start time.'))

    @api.constrains('max_attendees', 'attendee_count')
    def _check_max_attendees(self):
        for record in self:
            if record.max_attendees > 0 and record.registered_count > record.max_attendees:
                raise ValidationError(_('Maximum number of attendees (%s) exceeded.') % record.max_attendees)

    def action_schedule(self):
        self.ensure_one()
        if not self.session_date:
            raise UserError(_('Please set the session date and time before scheduling.'))
        self.state = 'scheduled'
        self.message_post(body=_('Briefing session scheduled for %s') % self.session_date)

    def action_start_session(self):
        self.ensure_one()
        self.state = 'in_progress'
        self.message_post(body=_('Briefing session started.'))

    def action_complete(self):
        self.ensure_one()
        if not self.minutes:
            raise UserError(_('Please record the minutes of the meeting before completing.'))
        self.state = 'completed'
        self.message_post(body=_('Briefing session completed.'))

        if self.is_compulsory:
            non_attendees = self.attendee_ids.filtered(lambda a: a.state != 'attended')
            if non_attendees:
                self.message_post(
                    body=_('Warning: %s registered bidders did not attend the compulsory briefing.') % len(non_attendees)
                )

        # Trigger the tender's complete_briefing action
        if self.tender_id:
            self.tender_id.action_complete_briefing()

    def action_cancel(self):
        self.ensure_one()
        self.state = 'cancelled'
        self.message_post(body=_('Briefing session cancelled.'))

    def action_view_attendees(self):
        self.ensure_one()
        return {
            'name': _('Briefing Attendees'),
            'type': 'ir.actions.act_window',
            'res_model': 'sagovtender.briefing.attendee',
            'view_mode': 'list,form',
            'domain': [('briefing_id', '=', self.id)],
            'context': {'default_briefing_id': self.id}
        }

    def action_view_questions(self):
        self.ensure_one()
        return {
            'name': _('Questions & Answers'),
            'type': 'ir.actions.act_window',
            'res_model': 'sagovtender.briefing.question',
            'view_mode': 'list,form',
            'domain': [('briefing_id', '=', self.id)],
            'context': {'default_briefing_id': self.id}
        }


class TenderBriefingAttendee(models.Model):
    """Briefing Session Attendees"""
    _name = 'sagovtender.briefing.attendee'
    _description = 'Briefing Session Attendee'
    _order = 'registration_date desc'

    briefing_id = fields.Many2one(
        'sagovtender.briefing.session',
        string='Briefing Session',
        required=True,
        ondelete='cascade'
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    partner_id = fields.Many2one(
        'res.partner',
        string='Company/Bidder',
        required=True
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    attendee_name = fields.Char(
        string='Attendee Name',
        required=True
    )
    attendee_position = fields.Char(
        string='Position/Title'
    )
    attendee_email = fields.Char(
        string='Email',
        required=True
    )
    attendee_phone = fields.Char(
        string='Phone'
    )
    id_number = fields.Char(
        string='ID Number'
    )

    registration_date = fields.Datetime(
        string='Registration Date',
        default=fields.Datetime.now,
        readonly=True
    )
    attendance_confirmed = fields.Boolean(
        string='Attendance Confirmed',
        default=False
    )
    attendance_time = fields.Datetime(
        string='Attendance Time'
    )
    signature = fields.Binary(
        string='Signature'
    )

    state = fields.Selection([
        ('registered', 'Registered'),
        ('attended', 'Attended'),
        ('absent', 'Absent'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='registered', required=True)

    notes = fields.Text(string='Notes')

    _sql_constraints = [
        ('unique_attendee_briefing', 'unique(briefing_id, attendee_email)',
         'This email is already registered for this briefing session!')
    ]

    def action_mark_attended(self):
        for record in self:
            record.write({
                'state': 'attended',
                'attendance_confirmed': True,
                'attendance_time': fields.Datetime.now()
            })

    def action_mark_absent(self):
        for record in self:
            record.state = 'absent'


class TenderBriefingQuestion(models.Model):
    """Questions and Answers from Briefing Session"""
    _name = 'sagovtender.briefing.question'
    _description = 'Briefing Session Question'
    _order = 'sequence, create_date'

    sequence = fields.Integer(string='Sequence', default=10)
    briefing_id = fields.Many2one(
        'sagovtender.briefing.session',
        string='Briefing Session',
        required=True,
        ondelete='cascade'
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Asked By (Company)'
    )
    question_date = fields.Datetime(
        string='Question Date',
        default=fields.Datetime.now
    )
    question = fields.Text(
        string='Question',
        required=True
    )
    answer = fields.Text(
        string='Answer'
    )
    answered_by = fields.Many2one(
        'res.users',
        string='Answered By'
    , options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True})
    answer_date = fields.Datetime(
        string='Answer Date'
    )
    is_published = fields.Boolean(
        string='Published to All Bidders',
        default=False,
        help='If checked, this Q&A will be shared with all bidders'
    )
    requires_addendum = fields.Boolean(
        string='Requires Addendum',
        default=False,
        help='Check if this requires a formal addendum to tender documents'
    )
    category = fields.Selection([
        ('technical', 'Technical'),
        ('commercial', 'Commercial'),
        ('legal', 'Legal'),
        ('procedural', 'Procedural'),
        ('site', 'Site Related'),
        ('other', 'Other'),
    ], string='Category', default='technical')

    state = fields.Selection([
        ('pending', 'Pending Answer'),
        ('answered', 'Answered'),
        ('published', 'Published'),
    ], string='Status', default='pending', compute='_compute_state', store=True)

    @api.depends('answer', 'is_published')
    def _compute_state(self):
        for record in self:
            if record.is_published:
                record.state = 'published'
            elif record.answer:
                record.state = 'answered'
            else:
                record.state = 'pending'

    def action_answer_question(self):
        self.ensure_one()
        return {
            'name': _('Answer Question'),
            'type': 'ir.actions.act_window',
            'res_model': 'sagovtender.briefing.question',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new'
        }

    def action_publish(self):
        for record in self:
            if not record.answer:
                raise UserError(_('Please provide an answer before publishing.'))
            record.write({
                'is_published': True,
                'answered_by': self.env.user.id,
                'answer_date': fields.Datetime.now()
            })
