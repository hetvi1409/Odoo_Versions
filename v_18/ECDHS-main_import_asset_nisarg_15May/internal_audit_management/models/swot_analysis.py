# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import date



class SwotAnalysis(models.Model):
    _name = "swot.analysis"
    _description = "Swot analysis"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", required=True)
    sequence_no = fields.Char(string='Sequence Number', readonly=True,
                              copy=False)
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    stages = fields.Selection([
        ('preparer', 'Preparer'),
        ('first_reviewer', 'First Reviewer'),
        ('second_reviewer', 'Reviewer'),
        ('approved', 'Approved'),
        ('reverted', 'Reverted'),
        ('rejected', 'Rejected'),
    ], 'State', copy=False, default='preparer', tracking=True)
    user_preparer_ids = fields.Many2one('res.users',
                                         string="Preparer", tracking=True)
    user_reviewer_1_ids = fields.Many2one('res.users',string="First Reviewer",
                                           tracking=True)
    user_reviewer_2_ids = fields.Many2one('res.users',string="Second Reviewer ",tracking=True)
    user_approver_ids = fields.Many2one('res.users',string="Approver", tracking=True)
    strengths_ids = fields.One2many('strength.analysis','strength_id',string='Strengths')
    strengths = fields.Html(string='Strength',compute="_compute_strengths")
    weaknesses_ids = fields.One2many('weakness.analysis','weakness_id',string='Weaknesses')
    weakness = fields.Html(string='Weakness', compute="_compute_weakness")
    opportunities_ids = fields.One2many('opportunities.analysis','opportunities_id',string='Opportunities')
    opportunities = fields.Html(string='Opportunities', compute="_compute_opportunities")
    threats_ids = fields.One2many('threats.analysis','threats_id',string='Threats')
    threats = fields.Html(string='Threats',
                                compute="_compute_threats")
    tracking_ids = fields.One2many('revert.tracking','tracking_id',string='Tracking')
    feedback = fields.Char(string="Audit Reverts/ Review Notes", tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['sequence_no'] = self.env['ir.sequence'].next_by_code('swot.analysis')

        records = super(SwotAnalysis, self).create(vals_list)
        return records

    @api.depends('strengths_ids.critical_issue')
    def _compute_strengths(self):
        for rec in self:
            strength_description = [
                f"<li>{strgth.critical_issue}</li>"
                for strgth in rec.strengths_ids
                if strgth.critical_issue
            ]
            rec.strengths = f"<ul>{''.join(strength_description)}</ul>" if strength_description else ""

    @api.depends('weaknesses_ids.critical_issue')
    def _compute_weakness(self):
        for rec in self:
            weakness_description = [
                f"<li>{weak.critical_issue}</li>"
                for weak in rec.weaknesses_ids
                if weak.critical_issue
            ]
            rec.weakness = f"<ul>{''.join(weakness_description)}</ul>" if weakness_description else ""

    @api.depends('opportunities_ids.critical_issue')
    def _compute_opportunities(self):
        for rec in self:
            opportunities_description = [
                f"<li>{opprt.critical_issue}</li>"
                for opprt in rec.opportunities_ids
                if opprt.critical_issue
            ]
            rec.opportunities = f"<ul>{''.join(opportunities_description)}</ul>" if opportunities_description else ""

    @api.depends('threats_ids.critical_issue')
    def _compute_threats(self):
        for rec in self:
            threats_description = [
                f"<li>{threat.critical_issue}</li>"
                for threat in rec.threats_ids
                if threat.critical_issue
            ]
            rec.threats = f"<ul>{''.join(threats_description)}</ul>" if threats_description else ""

    def action_review(self):
        """First Review"""
        mail_template = self.env.ref(
            'internal_audit_management.email_template_swot_analysis_to_review')
        recipient_ids = self.user_reviewer_1_ids
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)
        self.message_post(
            body=_('The SWOT Analysis %s - %s was reviewed by %s') % (
                self.start_date,self.end_date, self.env.user.name))
        self.stages = 'first_reviewer'

    def action_2nd_review(self):
        """Second Review"""
        mail_template = self.env.ref(
            'internal_audit_management.email_template_swot_analysis_sec_review')
        recipient_ids = self.user_reviewer_2_ids
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)
        self.message_post(
            body=_('The SWOT Analysis %s - %s was reviewed by %s') % (
                self.start_date, self.end_date, self.env.user.name))
        self.stages = 'second_reviewer'

    def action_approve(self):
        """Approve"""
        mail_template = self.env.ref(
            'internal_audit_management.email_template_swot_analysis_approve')
        recipient_ids = self.user_approver_ids
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)
        self.message_post(
            body=_('The SWOT Analysis %s - %s was approved by %s') % (
                self.start_date, self.end_date, self.env.user.name))
        self.stages = 'approved'

    def action_reject(self):
        """Reject"""
        mail_template = self.env.ref(
            'internal_audit_management.email_template_swot_analysis_reject')
        recipient_ids = self.env.user
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)
        self.message_post(
            body=_('The SWOT Analysis %s - %s was rejected by %s') % (
                self.start_date, self.end_date, self.env.user.name))
        self.stages = 'rejected'

    def action_revert(self):
        mail_template = self.env.ref(
            'internal_audit_management.email_template_swot_analysis_reverted')
        recipient_ids = self.user_preparer_ids
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)
        self.message_post(
            body=_('The SWOT Analysis %s - %s was reverted by %s') % (
                self.start_date, self.end_date, self.env.user.name))
        return {
            'name': 'Revert Procedure',
            'type': 'ir.actions.act_window',
            'res_model': 'swot.analysis.revert.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_swot_details': self.id,
            },
        }

    def action_update(self):
        self.tracking_ids.create({
            'tracking_id': self.id,
            'comment': "The revert has been updated",
            'new_state': "Updated",
            'previous': self.stages,
            'user_id': self.env.user.id,
            'date_updated': date.today(),
        })
        mail_template = self.env.ref(
            'internal_audit_management.email_template_swot_analysis_update')
        recipient_ids = self.user_preparer_ids
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)
        self.message_post(
            body=_('The SWOT Analysis %s - %s was updated by %s') % (
                self.start_date, self.end_date, self.env.user.name))
        if self.stages == 'reverted':
            self.stages = 'first_reviewer'
        else:
            self.stages = 'second_reviewer'

    def action_view_records(self):
        """Method for view records"""
        return {
            'name': 'Audit Reverts/ Review Notes',
            'type': 'ir.actions.act_window',
            'res_model': 'audit.revert',
            'domain': [('res_id', '=', self.id), ('res_model', '=', self._name)],
            'view_mode': 'list,form',
            'target': 'current',
        }


class StrengthsAnalysis(models.Model):
    _name = "strength.analysis"
    _description = "Strength Analysis"

    strength_id = fields.Many2one('swot.analysis',string='Strength')
    critical_issue = fields.Html(string='Critical Issues', required=True)
    internal_audit = fields.Html(string='Internal Audit Implications')
    strategic_objectives = fields.Char(string='Strategic Objectives')
    target_date = fields.Date(string='Target Date')
    responsible_auditor = fields.Many2one('res.users',string='Responsible Auditor')
    upload_doc = fields.Many2many('ir.attachment',string="Attachment")
    sequence = fields.Integer(string="Number",
                              help="Sequence will be automatically created",
                              compute='_compute_sequence')

    @api.depends('sequence')
    def _compute_sequence(self):
        sequence = 1
        for record in self:
            record.sequence = sequence
            sequence += 1


class WeaknessAnalysis(models.Model):
    _name = "weakness.analysis"
    _description = "Weakness Analysis"

    weakness_id = fields.Many2one('swot.analysis',string='Weakness')
    critical_issue = fields.Html(string='Critical Issues', required=True)
    internal_audit = fields.Html(string='Internal Audit Implications')
    strategic_objectives = fields.Char(string='Strategic Objectives')
    target_date = fields.Date(string='Target Date')
    responsible_auditor = fields.Many2one('res.users',string='Responsible Auditor')
    upload_doc = fields.Many2many('ir.attachment',string="Attachment")
    sequence = fields.Integer(string="Number",
                              help="Sequence will be automatically created",
                              compute='_compute_sequence')

    @api.depends('sequence')
    def _compute_sequence(self):
        sequence = 1
        for record in self:
            record.sequence = sequence
            sequence += 1


class OpportunitiesAnalysis(models.Model):
    _name = "opportunities.analysis"
    _description = "Opportunities Analysis"

    opportunities_id = fields.Many2one('swot.analysis',string='Opportunity')
    critical_issue = fields.Html(string='Critical Issues', required=True)
    internal_audit = fields.Html(string='Internal Audit Implications')
    strategic_objectives = fields.Char(string='Strategic Objectives')
    target_date = fields.Date(string='Target Date')
    responsible_auditor = fields.Many2one('res.users',string='Responsible Auditor')
    upload_doc = fields.Many2many('ir.attachment',string="Attachment")
    sequence = fields.Integer(string="Number",
                              help="Sequence will be automatically created",
                              compute='_compute_sequence')

    @api.depends('sequence')
    def _compute_sequence(self):
        sequence = 1
        for record in self:
            record.sequence = sequence
            sequence += 1


class ThreatsAnalysis(models.Model):
    _name = "threats.analysis"
    _description = "Threats Analysis"

    threats_id = fields.Many2one('swot.analysis',string='Treats')
    critical_issue = fields.Html(string='Critical Issues', required=True)
    internal_audit = fields.Html(string='Internal Audit Implications')
    strategic_objectives = fields.Char(string='Strategic Objectives')
    target_date = fields.Date(string='Target Date')
    responsible_auditor = fields.Many2one('res.users',string='Responsible Auditor')
    upload_doc = fields.Many2many('ir.attachment',string="Attachment")
    sequence = fields.Integer(string="Number",
                              help="Sequence will be automatically created",
                              compute='_compute_sequence')

    @api.depends('sequence')
    def _compute_sequence(self):
        sequence = 1
        for record in self:
            record.sequence = sequence
            sequence += 1


class TrackingTracking(models.Model):
    _name = "revert.tracking"
    _description = "Revert Tracking"

    tracking_id = fields.Many2one('swot.analysis', string='Tracking')
    user_id = fields.Many2one('res.users',string='User')
    previous = fields.Char(string='Previous')
    new_state = fields.Char(string='New')
    comment = fields.Char(string='Comment')
    date_updated = fields.Date(string='Date')
