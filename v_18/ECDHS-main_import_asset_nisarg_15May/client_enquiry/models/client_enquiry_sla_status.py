from dateutil.relativedelta import relativedelta
from odoo import api, fields, models


class ClientEnquirySLAPolicy(models.Model):
    """"Client Enquiry SLA Policy"""
    _name = 'client.enquiry.sla.policy'

    name = fields.Char(string="Name", required=True)
    sla_number = fields.Char(string="Number", readonly=True)
    description = fields.Char(string="Description", required=True)
    deadline_type = fields.Selection([('days', 'Days'), ('months', 'Months'),
                                      ('weeks', 'Weeks')], string="Deadline type")
    dead_line = fields.Integer(string="Deadline")
    state = fields.Selection([('draft', 'Draft'), ('submitted', 'Submitted to CBO'),
                              ('ownership', 'Documents submitted to property'
                                            ' department'),
                              ('compile', 'Compile Assessment review'),
                              ('valuation', 'Waiting for Valuation Result'),
                              ('transition', 'Transaction'),
                              ('internal_meeting', 'Internal Meeting'),
                              ('internal_meeting_approved', "Board Approved"),
                              ('technical_growth',
                               'Technical Growth Cluster Approved'),
                              ('executive', 'Executive Management Team'),
                              ('council_79_approved', "Council 79 Approved"),
                              ('sub_mayoral', 'Sub-Mayoral Approved'),
                              ('mayoral_approved', "Mayoral Approved"),
                              ])


class ClientEnquirySLAPolicyStatus(models.Model):
    """SLA Policy Status"""
    _name = 'client.enquiry.sla.policy.status'

    name = fields.Char(string="Name", required=True)
    enquiry_id = fields.Many2one('client.enquiry', string="Enquiry", required=True)
    team_id = fields.Many2one('helpdesk.team', string="Team",
                              related="enquiry_id.team_id", store=True)
    policy_id = fields.Many2one('client.enquiry.sla.policy', string="SLA Policy", required=True)
    deadline = fields.Datetime("Deadline",
                               compute='_compute_deadline',
                               compute_sudo=True, store=True)
    reached_datetime = fields.Datetime("Reached Date",
                                       help="Datetime at which the SLA stage was reached for the first time")
    status = fields.Selection(
        [('failed', 'Failed'), ('reached', 'Reached'), ('ongoing', 'Ongoing')],
        string="Status",
        compute='_compute_status', compute_sudo=True)
    color = fields.Integer("Color Index",
                           compute='_compute_color')
    exceeded_hours = fields.Float("Exceeded Working Hours",
                                  compute='_compute_exceeded_hours',
                                  compute_sudo=True, store=True,
                                  help="Working hours exceeded for reached SLAs compared with deadline. Positive number means the SLA was reached after the deadline.")

    @api.depends('enquiry_id', 'policy_id')
    def _compute_deadline(self):
        """Compute deadline based on enquiry state"""
        if self.policy_id:
            if self.policy_id.deadline_type == 'days':
                self.deadline = self.enquiry_id.last_stage_updated + relativedelta(days=int(self.policy_id.dead_line))
            if self.policy_id.deadline_type == 'months':
                self.deadline = self.enquiry_id.last_stage_updated + relativedelta(months=int(self.policy_id.dead_line))
            if self.policy_id.deadline_type == 'weeks':
                self.deadline = self.enquiry_id.last_stage_updated + relativedelta(days=7 * int(self.policy_id.dead_line))

    @api.depends('deadline', 'reached_datetime')
    def _compute_status(self):
        for status in self:
            if status.reached_datetime and status.deadline:  # if reached_datetime, SLA is finished: either failed or succeeded
                status.status = 'reached' if status.reached_datetime < status.deadline else 'failed'
            else:  # if not finished, deadline should be compared to now()
                status.status = 'ongoing' if not status.deadline or status.deadline > fields.Datetime.now() else 'failed'

    @api.depends('status')
    def _compute_color(self):
        for status in self:
            if status.status == 'failed':
                status.color = 1
            elif status.status == 'reached':
                status.color = 10
            else:
                status.color = 0

    @api.depends('deadline', 'reached_datetime')
    def _compute_exceeded_hours(self):
        for status in self:
            reached_datetime = status.reached_datetime or fields.Datetime.now()
            if status.deadline:
                if reached_datetime <= status.deadline:
                    start_dt = reached_datetime
                    end_dt = status.deadline
                else:
                    start_dt = status.deadline
                    end_dt = reached_datetime
                time = end_dt - start_dt
                status.exceeded_hours = (time.days * 24) + (time.seconds / 3600)
            else:
                # Handle case where deadline is missing
                status.exceeded_hours = 0.0
