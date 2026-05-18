# -*- coding: utf-8 -*-
from odoo import fields, models, _, api
from datetime import date


class PestelAnalysis(models.Model):
    _name = "pestel.analysis"
    _description = "Pestel analysis"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", required=True)
    sequence_no = fields.Char(string='Sequence Number', readonly=True, copy=False)
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
    user_preparer_ids = fields.Many2many('res.users',
                                         'user_pestal_prep_rel',
                                         string="Preparer", tracking=True)
    user_reviewer_1_ids = fields.Many2many('res.users',
                                           'user_pestal_review_fir_rel',
                                           string="First Reviewer",
                                           tracking=True)
    user_reviewer_2_ids = fields.Many2many('res.users',
                                           'user_pestal_review_sec_rel',
                                           string="Second Reviewer ",
                                           tracking=True)
    user_approver_ids = fields.Many2many('res.users',
                                         'user_pestel_audit_rel',
                                         string="Approver", tracking=True)
    political_factor = fields.One2many('political.factor','political_factor_id', string='Political Factor')
    political = fields.Html(string='Political', compute="_compute_political_factor")
    economic_factor = fields.One2many('economic.factor','economic_factor_id', string='Economic Factor')
    economic = fields.Html(string='Economic',
                            compute="_compute_economic_factor")
    social_factor = fields.One2many('social.factor','social_factor_id', string='Social Factor')
    social = fields.Html(string='Social',
                           compute="_compute_social_factor")
    technological_factor = fields.One2many('technological.factor','technological_factor_id', string='Technological Factor')
    techno = fields.Html(string='Techno', compute="_compute_techno_factor")
    environmental_factor = fields.One2many('environmental.factor','environmental_factor_id', string='Environmental Factor')
    environment = fields.Html(string='Environment', compute="_compute_environment_factor")
    legislative_factor = fields.One2many('legislative.factor','legislative_factor_id', string='Legislative Factor')
    legislative = fields.Html(string='Legislative', compute="_compute_legislative_factor")
    tracking_ids = fields.One2many('pestel.tracking', 'tracking_id', string='Tracking')
    feedback = fields.Char(string="Audit Reverts/ Review Notes", tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['sequence_no'] = self.env['ir.sequence'].next_by_code('pestel.analysis')

        records = super(PestelAnalysis, self).create(vals_list)
        return records

    @api.depends('political_factor.critical_issues')
    def _compute_political_factor(self):
        for rec in self:
            political_description = [
                f"<li>{poltcl.critical_issues}</li>"
                for poltcl in rec.political_factor
                if poltcl.critical_issues
            ]
            rec.political = f"<ul>{''.join(political_description)}</ul>" if political_description else ""

    @api.depends('economic_factor.critical_issues')
    def _compute_economic_factor(self):
        for rec in self:
            economic_description = [
                f"<li>{eco.critical_issues}</li>"
                for eco in rec.economic_factor
                if eco.critical_issues
            ]
            rec.economic = f"<ul>{''.join(economic_description)}</ul>" if economic_description else ""

    @api.depends('social_factor.critical_issues')
    def _compute_social_factor(self):
        for rec in self:
            social_description = [
                f"<li>{socio.critical_issues}</li>"
                for socio in rec.social_factor
                if socio.critical_issues
            ]
            rec.social = f"<ul>{''.join(social_description)}</ul>" if social_description else ""

    @api.depends('technological_factor.critical_issues')
    def _compute_techno_factor(self):
        for rec in self:
            techno_description = [
                f"<li>{tech.critical_issues}</li>"
                for tech in rec.technological_factor
                if tech.critical_issues
            ]
            rec.techno = f"<ul>{''.join(techno_description)}</ul>" if techno_description else ""

    @api.depends('environmental_factor.critical_issues')
    def _compute_environment_factor(self):
        for rec in self:
            environment_description = [
                f"<li>{envi.critical_issues}</li>"
                for envi in rec.environmental_factor
                if envi.critical_issues
            ]
            rec.environment = f"<ul>{''.join(environment_description)}</ul>" if environment_description else ""

    @api.depends('legislative_factor.critical_issues')
    def _compute_legislative_factor(self):
        for rec in self:
            legislative_description = [
                f"<li>{legis.critical_issues}</li>"
                for legis in rec.legislative_factor
                if legis.critical_issues
            ]
            rec.legislative = f"<ul>{''.join(legislative_description)}</ul>" if legislative_description else ""

    def action_review(self):
        """First Review"""
        mail_template = self.env.ref(
            'internal_audit_management.email_template_pestel_analysis_to_review')
        recipient_ids = self.user_reviewer_1_ids
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)
        self.message_post(
            body=_('The Pestel Analysis %s - %s was reviewed by %s') % (
                self.start_date, self.end_date, self.env.user.name))
        self.stages = 'first_reviewer'

    def action_2nd_review(self):
        """Second Review"""
        mail_template = self.env.ref(
            'internal_audit_management.email_template_pestel_analysis_sec_review')
        recipient_ids = self.user_reviewer_2_ids
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)
        self.message_post(
            body=_('The Pestel Analysis %s - %s was reviewed by %s') % (
                self.start_date, self.end_date, self.env.user.name))
        self.stages = 'second_reviewer'

    def action_approve(self):
        """First Review"""
        mail_template = self.env.ref(
            'internal_audit_management.email_template_pestel_analysis_approve')
        recipient_ids = self.user_approver_ids
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)
        self.message_post(
            body=_('The Pestel Analysis %s - %s was approved by %s') % (
                self.start_date, self.end_date, self.env.user.name))
        self.stages = 'approved'

    def action_reject(self):
        """First Review"""
        mail_template = self.env.ref(
            'internal_audit_management.email_template_pestel_analysis_reject')
        recipient_ids = self.env.user
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)
        self.message_post(
            body=_('The Pestel Analysis %s - %s was rejected by %s') % (
                self.start_date, self.end_date, self.env.user.name))
        self.stages = 'rejected'

    def action_revert(self):
        mail_template = self.env.ref(
            'internal_audit_management.email_template_pestel_analysis_reverted')
        recipient_ids = self.user_preparer_ids
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)
        self.message_post(
            body=_('The Pestel Analysis %s - %s was reverted by %s') % (
                self.start_date, self.end_date, self.env.user.name))
        return {
            'name': 'Revert Procedure',
            'type': 'ir.actions.act_window',
            'res_model': 'pestel.analysis.revert.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_pestel_details': self.id,
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
            'internal_audit_management.email_template_pestel_analysis_update')
        recipient_ids = self.user_preparer_ids
        partner = recipient_ids.mapped('partner_id')
        email_values = {
            'recipient_ids': [(6, 0, partner.ids)]
        }
        mail_template.send_mail(self.id, force_send=True,
                                email_values=email_values)
        self.message_post(
            body=_('The Pestel Analysis %s - %s was updated by %s') % (
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


class PoliticalFactor(models.Model):
    _name = "political.factor"
    _description = "Political Factor"

    political_factor_id = fields.Many2one('pestel.analysis')
    critical_issues = fields.Html(string='Critical Issues', required=True)
    internal_audit_implication = fields.Html(string='Internal Audit Implications')
    sequence = fields.Integer(string="Number",help="Sequence will be automatically created",compute='_compute_sequence')

    @api.depends('sequence')
    def _compute_sequence(self):
        sequence = 1
        for record in self:
            record.sequence = sequence
            sequence += 1

class EconomicFactor(models.Model):
    _name = "economic.factor"
    _description = "Economic Factor"

    economic_factor_id = fields.Many2one('pestel.analysis')
    critical_issues = fields.Html(string='Critical Issues', required=True)
    internal_audit_implication = fields.Html(string='Internal Audit Implications')
    sequence = fields.Integer(string="Number", help="Sequence will be automatically created",
                              compute='_compute_sequence')

    @api.depends('sequence')
    def _compute_sequence(self):
        sequence = 1
        for record in self:
            record.sequence = sequence
            sequence += 1

class SocialFactor(models.Model):
    _name = "social.factor"
    _description = "Social Factor"

    social_factor_id = fields.Many2one('pestel.analysis')
    critical_issues = fields.Html(string='Critical Issues', required=True)
    internal_audit_implication = fields.Html(string='Internal Audit Implications')
    sequence = fields.Integer(string="Number", help="Sequence will be automatically created",
                              compute='_compute_sequence')

    @api.depends('sequence')
    def _compute_sequence(self):
        sequence = 1
        for record in self:
            record.sequence = sequence
            sequence += 1

class TechnologicalFactor(models.Model):
    _name = "technological.factor"
    _description = "Technological Factor"

    technological_factor_id = fields.Many2one('pestel.analysis')
    critical_issues = fields.Html(string='Critical Issues')
    internal_audit_implication = fields.Html(string='Internal Audit Implications')
    sequence = fields.Integer(string="Number", help="Sequence will be automatically created",
                              compute='_compute_sequence')

    @api.depends('sequence')
    def _compute_sequence(self):
        sequence = 1
        for record in self:
            record.sequence = sequence
            sequence += 1

class EnvironmentalFactor(models.Model):
    _name = "environmental.factor"
    _description = "Environmental Factor"

    environmental_factor_id = fields.Many2one('pestel.analysis')
    critical_issues = fields.Html(string='Critical Issues')
    internal_audit_implication = fields.Html(string='Internal Audit Implications')
    sequence = fields.Integer(string="Number",
                              help="Sequence will be automatically created",
                              compute='_compute_sequence')

    @api.depends('sequence')
    def _compute_sequence(self):
        sequence = 1
        for record in self:
            record.sequence = sequence
            sequence += 1


class LegislativeFactor(models.Model):
    _name = "legislative.factor"
    _description = "Legislative Factor"

    legislative_factor_id = fields.Many2one('pestel.analysis')
    critical_issues = fields.Html(string='Critical Issues')
    internal_audit_implication = fields.Html(string='Internal Audit Implications')
    sequence = fields.Integer(string="Number",
                              help="Sequence will be automatically created",
                              compute='_compute_sequence')

    @api.depends('sequence')
    def _compute_sequence(self):
        sequence = 1
        for record in self:
            record.sequence = sequence
            sequence += 1


class PestelTracking(models.Model):
    _name = "pestel.tracking"
    _description = "Pestel Tracking"

    tracking_id = fields.Many2one('pestel.analysis', string='Tracking')
    user_id = fields.Many2one('res.users',string='User')
    previous = fields.Char(string='Previous')
    new_state = fields.Char(string='New')
    comment = fields.Char(string='Comment')
    date_updated = fields.Date(string='Date')
