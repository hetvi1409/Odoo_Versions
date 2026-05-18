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
    process_status = fields.Selection([
        ('assessment', 'Assessment'),
        ('sent_for_comments', 'Sent for Comments'),
        ('ptob', 'PTOB'),
        ('valuation', 'Valuation'),
        ('transaction', 'Transaction'),
        ('eac', 'EAC'),
        ('property_intelligence', 'Property Intelligence'),
        ('land_regularization', 'Land Regularization'),
        ('enquiry', 'Enquiry')
    ], string='Select Process', copy=False, required=True)
    enquiry_id = fields.Many2one('client.enquiry', string="Enquiry")
    assessment_id = fields.Many2one('enquiry.assessment', string="Assessment")
    comment_id = fields.Many2one('circulation.comments', string="Comments")
    valuation_id = fields.Many2one('assessment.valuation', string="Valuation")
    transaction_id = fields.Many2one('client.transaction', string="Transaction")
    eac_id = fields.Many2one('eac.process', string="EAC")
    land_id = fields.Many2one('land.regularization', string="Land Regularization")
    # property_intelligence_id = fields.Many2one('property.intelligence', string="Property Intelligent")


    team_id = fields.Many2one('helpdesk.team', string="Team",
                              related="enquiry_id.team_id", store=True)
    policy_id = fields.Many2one('client.enquiry.sla.policy', string="SLA Policy")
    deadline = fields.Datetime("Deadline",
                               compute='_compute_deadline',
                               compute_sudo=True, store=True)
    property_intelligence_id = fields.Many2one('property.intelligence',string ='Property Intelligence')
    reached_datetime = fields.Datetime("Reached Date",
                                       help="Datetime at which the SLA stage was reached for the first time")
    status = fields.Selection(
        [('failed', 'Failed'), ('reached', 'Reached'), ('ongoing', 'Ongoing')],
        string="Status",
        compute='_compute_status', compute_sudo=True)
    color = fields.Integer("Color Index", compute='_compute_color')
    exceeded_hours = fields.Float("Exceeded Working Hours",
                                  compute='_compute_exceeded_hours',
                                  compute_sudo=True, store=True,
                                  help="Working hours exceeded for reached SLAs compared with deadline. Positive number means the SLA was reached after the deadline.")

    @api.depends('assessment_id', 'process_status','comment_id','land_id','valuation_id')
    def _compute_deadline(self):
        """Compute deadline based on enquiry state"""
        if self.process_status:
            policies = self.env['client.enquiry.sla.policy'].search([('process_status','=', 'assessment')])
            comment = self.env['client.enquiry.sla.policy'].search([('process_status','=', 'sent_for_comments')])
            valuation = self.env['client.enquiry.sla.policy'].search([('process_status','=', 'valuation')])
            transaction = self.env['client.enquiry.sla.policy'].search([('process_status','=', 'transaction')])
            land = self.env['client.enquiry.sla.policy'].search([('process_status','=', 'land_regularization')])
            enquiry = self.env['client.enquiry.sla.policy'].search([('process_status','=', 'enquiry')])
            eac = self.env['client.enquiry.sla.policy'].search([('process_status','=', 'eac')])
            property_intelligence = self.env['client.enquiry.sla.policy'].search([('process_status','=', 'property_intelligence')])
            for rec in policies :
                if rec.deadline_type== 'days' and self.process_status == 'assessment' and rec.dead_line and self.assessment_id and  self.assessment_id.last_stage_updated:
                    self.deadline = self.assessment_id.last_stage_updated + relativedelta(days=int(self.policy_id.dead_line))
            for rec in comment :
                if rec.deadline_type== 'days' and self.process_status == 'sent_for_comments' and rec.dead_line and self.comment_id and self.comment_id.last_stage_updated:
                    self.deadline = self.comment_id.last_stage_updated + relativedelta(days=int(self.policy_id.dead_line))
            for rec in valuation:
                if rec.deadline_type == 'days' and self.process_status == 'valuation' and rec.dead_line and self.valuation_id and self.valuation_id.last_stage_updated:
                    self.deadline = self.valuation_id.last_stage_updated + relativedelta(days=int(self.policy_id.dead_line))

            for rec in transaction:
                if rec.deadline_type == 'days' and self.process_status == 'transaction' and rec.dead_line and self.transaction_id and self.transaction_id.last_stage_updated:
                    self.deadline = self.transaction_id.last_stage_updated + relativedelta(
                        days=int(self.policy_id.dead_line))
            for rec in land:
                if rec.deadline_type == 'days' and self.process_status == 'land_regularization' and rec.dead_line and self.land_id and self.land_id.last_stage_updated:
                    self.deadline = self.land_id.last_stage_updated + relativedelta(
                        days=int(self.policy_id.dead_line))

            for rec in enquiry:
                if rec.deadline_type == 'days' and self.process_status == 'enquiry' and rec.dead_line and self.enquiry_id and self.enquiry_id.last_stage_updated:
                    self.deadline = self.enquiry_id.last_stage_updated + relativedelta(
                        days=int(self.policy_id.dead_line))

            for rec in eac:
                if rec.deadline_type == 'days' and self.process_status == 'eac' and rec.dead_line and self.eac_id and self.eac_id.last_stage_updated:
                    self.deadline = self.eac_id.last_stage_updated + relativedelta(
                        days=int(self.policy_id.dead_line))

            for rec in property_intelligence:
                if rec.deadline_type == 'days' and self.process_status == 'property_intelligence' and rec.dead_line and self.property_intelligence_id and self.property_intelligence_id.last_stage_updated:
                    self.deadline = self.eac_id.last_stage_updated + relativedelta(
                        days=int(self.policy_id.dead_line))



            # if self.policy_id.deadline_type == 'days':
            #     self.deadline = self.policy_id.reached_state_comments + relativedelta(days=int(self.policy_id.dead_line))
            if self.policy_id.deadline_type == 'months' and self.process_status == 'assessment' and self.dead_line and self.assessment_id and self.assessment_id.last_stage_updated:
                self.deadline =self.assessment_id.last_stage_updated + relativedelta(months=int(self.policy_id.dead_line))
            if self.policy_id.deadline_type == 'months' and self.process_status == 'land_regularization' and self.dead_line and self.land_id and self.land_id.last_stage_updated:
                self.deadline = self.land_id.last_stage_updated + relativedelta(
                    months=int(self.policy_id.dead_line))

            if self.policy_id.deadline_type == 'months' and self.process_status == 'property_intelligence' and self.dead_line and self.property_intelligence_id and self.property_intelligence_id.last_stage_updated:
                self.deadline = self.property_intelligence_id.last_stage_updated + relativedelta(
                    months=int(self.policy_id.dead_line))

            if self.policy_id.deadline_type == 'months' and self.process_status == 'enquiry' and self.dead_line and self.enquiry_id and self.enquiry_id.last_stage_updated:
                self.deadline = self.enquiry_id.last_stage_updated + relativedelta(
                    months=int(self.policy_id.dead_line))


            # if self.policy_id.deadline_type == 'months' and self.process_status == 'property_intelligence' and self.dead_line and self.property_intelligence_id and self.property_intelligence_id.last_stage_updated:
            #     self.deadline = self.property_intelligence_id.last_stage_updated + relativedelta(
            #         months=int(self.policy_id.dead_line))
            if self.policy_id.deadline_type == 'months' and self.process_status == 'eac' and self.dead_line and self.eac_id and self.eac_id.last_stage_updated:
                self.deadline =self.eac_id.last_stage_updated + relativedelta(months=int(self.policy_id.dead_line))
            if self.policy_id.deadline_type == 'months' and self.process_status == 'transaction' and self.dead_line and self.transaction_id and self.transaction.last_stage_updated:
                self.deadline = self.transaction_id.last_stage_updated + relativedelta(
                    months=int(self.policy_id.dead_line))
            if self.policy_id.deadline_type == 'months' and self.process_status == 'valuation' and self.dead_line and self.valuation_id and self.valuation_id.last_stage_updated:
                self.deadline = self.valuation_id.last_stage_updated + relativedelta(months=int(self.policy_id.dead_line))
            if self.policy_id.deadline_type == 'months' and self.process_status == 'sent_for_comments' and self.dead_line and self.comment_id and self.comment_id.last_stage_updated:
                self.deadline = self.comment_id.last_stage_updated + relativedelta(months=int(self.policy_id.dead_line))
            if self.policy_id.deadline_type == 'weeks' and self.process_status == 'assessment' and rec.dead_line and self.assessment_id and self.assessment_id.last_stage_updated:
                self.deadline = self.assessment_id.last_stage_updated + relativedelta(days=7 * int(self.policy_id.dead_line))
            if self.policy_id.deadline_type == 'weeks' and self.process_status == 'sent_for_comments' and rec.dead_line and self.comment_id and self.comment_id.last_stage_updated:
                self.deadline = self.comment_id.last_stage_updated + relativedelta(days=7 * int(self.policy_id.dead_line))
            if self.policy_id.deadline_type == 'weeks' and self.process_status == 'valuation' and rec.dead_line and self.valuation_id and self.valuation_id.last_stage_updated:
                self.deadline = self.valuation_id.last_stage_updated + relativedelta(days=7 * int(self.policy_id.dead_line))
            if self.policy_id.deadline_type == 'weeks' and self.process_status == 'transaction' and rec.dead_line and self.transaction_id and self.transaction_id.last_stage_updated:
                self.deadline = self.transaction_id.last_stage_updated + relativedelta(days=7 * int(self.policy_id.dead_line))
            if self.policy_id.deadline_type == 'weeks' and self.process_status == 'eac' and rec.dead_line and self.eac_id and self.eac_id.last_stage_updated:
                self.deadline = self.eac_id.last_stage_updated + relativedelta(
                    days=7 * int(self.policy_id.dead_line))
            if self.policy_id.deadline_type == 'weeks' and self.process_status == 'land_regularization' and rec.dead_line and self.eac_id and self.eac_id.last_stage_updated:
                self.deadline = self.land_id.last_stage_updated + relativedelta(
                    days=7 * int(self.policy_id.dead_line))
            if self.policy_id.deadline_type == 'weeks' and self.process_status == 'property_intelligence' and rec.dead_line and self.property_intelligence_id and self.property_intelligence_id.last_stage_updated:
                self.deadline = self.property_intelligence_id.last_stage_updated + relativedelta(
                    days=7 * int(self.policy_id.dead_line))

            if self.policy_id.deadline_type == 'weeks' and self.process_status == 'enquiry' and rec.dead_line and self.enquiry_id and self.enquiry_id.last_stage_updated:
                self.deadline = self.enquiry_id.last_stage_updated + relativedelta(
                    days=7 * int(self.policy_id.dead_line))


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
            if reached_datetime and status.deadline:
                if reached_datetime <= status.deadline:
                    start_dt = reached_datetime
                    end_dt = status.deadline
                else:
                    start_dt = status.deadline
                    end_dt = reached_datetime
                time = start_dt - end_dt
                times = 24 * time.days + (time.seconds /(60 * 60))
                status.exceeded_hours = times
