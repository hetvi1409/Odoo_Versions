# -*- coding: utf-8 -*-
import math

from odoo import api, fields, models, _
from odoo.addons.oi_risk_management.models.risk import RISK_SCORES
from odoo.exceptions import UserError


class AsymmetricEvaluationCriteria(models.Model):
    _name = 'oi_risk.asymmetric_evaluation_criteria'

    p = fields.Integer(required=True, string='Likelihood/Probability')
    s = fields.Integer(required=True, string='Severity/Impact')
    name = fields.Char(compute='_compute_name', store=True)
    risk_type = fields.Selection(selection=[
        ('very_high', 'Very High'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ], compute='_compute_risk_type')

    @api.depends('p', 's')
    def _compute_name(self):
        for record in self:
            record.name = 'P%s S%s' % (record.p, record.s,)

    def _compute_risk_type(self):
        evaluation_system = self.env['ir.config_parameter'].sudo().get_param('oi_risk_management.evaluation_system')

        evaluation_type_names = {
            'very_high': self.env['oi_risk.asymmetric_evaluation_criteria'].search([]).filtered(
                lambda risk: risk.risk_type == 'very_high'),
            'high': self.env['oi_risk.asymmetric_evaluation_criteria'].search([]).filtered(
                lambda risk: risk.risk_type == 'high'),
            'medium': self.env['oi_risk.asymmetric_evaluation_criteria'].search([]).filtered(
                lambda risk: risk.risk_type == 'medium'),
            'low': self.env['oi_risk.asymmetric_evaluation_criteria'].search([]).filtered(
                lambda risk: risk.risk_type == 'low'),
        }

        for record in self:
            if evaluation_system == 'symmetric':
                index = math.ceil(record.p * record.s / 6.25) - 1
                record.risk_type = RISK_SCORES[index][0]
            elif evaluation_system == 'asymmetric':
                evaluation_type_names = {
                    'very_high': self.env['ir.config_parameter'].sudo().get_param(
                        'oi_risk.asymmetric_evaluation_very_high_ids').split(',') if self.env[
                        'ir.config_parameter'].sudo().get_param(
                        'oi_risk.asymmetric_evaluation_very_high_ids') else '',
                    'high': self.env['ir.config_parameter'].sudo().get_param(
                        'oi_risk.asymmetric_evaluation_high_ids').split(',') if self.env[
                        'ir.config_parameter'].sudo().get_param(
                        'oi_risk.asymmetric_evaluation_high_ids') else '',
                    'medium': self.env['ir.config_parameter'].sudo().get_param(
                        'oi_risk.asymmetric_evaluation_medium_ids').split(',') if self.env[
                        'ir.config_parameter'].sudo().get_param(
                        'oi_risk.asymmetric_evaluation_medium_ids') else '',
                    'low': self.env['ir.config_parameter'].sudo().get_param(
                        'oi_risk.asymmetric_evaluation_low_ids').split(',') if self.env[
                        'ir.config_parameter'].sudo().get_param(
                        'oi_risk.asymmetric_evaluation_low_ids') else ''
                }

            for risk_type, criteria_ids in evaluation_type_names.items():
                if record.name in criteria_ids:
                    record.risk_type = risk_type
                    break


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    do_risk_treatments_have_owner = fields.Boolean(string="Owner for treatments",
                                                   config_parameter="oi_risk_management.do_risk_treatments_have_owner")

    main_risk_type = fields.Selection(selection=[
        ('inherent_risk', 'Inherent Risk'),
        ('current_risk', 'Current Risk'),
        ('residual_risk', 'Residual Risk'),
    ], required=True, string="Main risk type",
        config_parameter="oi_risk_management.main_risk_type")

    evaluation_system = fields.Selection([
        ('symmetric', 'Symmetric'),
        ('asymmetric', 'Asymmetric'),
    ], config_parameter="oi_risk_management.evaluation_system", required=True)

    asymmetric_evaluation_very_high_ids = fields.Many2many('oi_risk.asymmetric_evaluation_criteria',
                                                           'setting_very_high_evaluation_rel',
                                                           compute='_compute_asymmetric_evaluation_very_high_ids',
                                                           inverse='_inverse_asymmetric_evaluation_very_high_str',
                                                           string='Very High Evaluation Criteria')
    asymmetric_evaluation_very_high_str = fields.Char(string='Very High Evaluation Criteria',
                                                      config_parameter='oi_risk.asymmetric_evaluation_very_high_ids')

    asymmetric_evaluation_high_ids = fields.Many2many('oi_risk.asymmetric_evaluation_criteria',
                                                      'setting_high_evaluation_rel',
                                                      compute='_compute_asymmetric_evaluation_high_ids',
                                                      inverse='_inverse_asymmetric_evaluation_high_str',
                                                      string='High Evaluation Criteria')
    asymmetric_evaluation_high_str = fields.Char(string='High Evaluation Criteria',
                                                 config_parameter='oi_risk.asymmetric_evaluation_high_ids')

    asymmetric_evaluation_medium_ids = fields.Many2many('oi_risk.asymmetric_evaluation_criteria',
                                                        'setting_medium_evaluation_rel',
                                                        compute='_compute_asymmetric_evaluation_medium_ids',
                                                        inverse='_inverse_asymmetric_evaluation_medium_str',
                                                        string='Medium Evaluation Criteria')
    asymmetric_evaluation_medium_str = fields.Char(string='Medium Evaluation Criteria',
                                                   config_parameter='oi_risk.asymmetric_evaluation_medium_ids')

    asymmetric_evaluation_low_ids = fields.Many2many('oi_risk.asymmetric_evaluation_criteria',
                                                     'setting_low_evaluation_rel',
                                                     compute='_compute_asymmetric_evaluation_low_ids',
                                                     inverse='_inverse_asymmetric_evaluation_low_str',
                                                     string='Low Evaluation Criteria')
    asymmetric_evaluation_low_str = fields.Char(string='Low Evaluation Criteria',
                                                config_parameter='oi_risk.asymmetric_evaluation_low_ids')

    def _compute_asymmetric_evaluation(self, risk_type):
        for setting in self:
            if setting['asymmetric_evaluation_%s_str' % (risk_type,)]:
                names = setting['asymmetric_evaluation_%s_str' % (risk_type,)].split(',')
                evaluation_criteria = self.env['oi_risk.asymmetric_evaluation_criteria'].search([('name', 'in', names)])
                setting['asymmetric_evaluation_%s_ids' % (risk_type,)] = evaluation_criteria
            else:
                setting['asymmetric_evaluation_%s_ids' % (risk_type,)] = None

    def _inverse_asymmetric_evaluation(self, risk_type):
        """ As config_parameters does not accept m2m field,
            we store the fields with a comma separated string into a Char config field """
        for setting in self:
            if setting['asymmetric_evaluation_%s_ids' % (risk_type,)]:
                setting['asymmetric_evaluation_%s_str' % (risk_type,)] = ','.join(
                    setting['asymmetric_evaluation_%s_ids' % (risk_type,)].mapped('name'))
            else:
                setting['asymmetric_evaluation_%s_str' % (risk_type,)] = ''

    @api.depends('asymmetric_evaluation_very_high_str')
    def _compute_asymmetric_evaluation_very_high_ids(self):
        """ As config_parameters does not accept m2m field,
            we store the fields with a comma separated string into a Char config field """
        self._compute_asymmetric_evaluation('very_high')

    def _inverse_asymmetric_evaluation_very_high_str(self):
        """ As config_parameters does not accept m2m field,
            we store the fields with a comma separated string into a Char config field """
        self._inverse_asymmetric_evaluation('very_high')

    @api.depends('asymmetric_evaluation_high_str')
    def _compute_asymmetric_evaluation_high_ids(self):
        """ As config_parameters does not accept m2m field,
            we store the fields with a comma separated string into a Char config field """
        self._compute_asymmetric_evaluation('high')

    def _inverse_asymmetric_evaluation_high_str(self):
        """ As config_parameters does not accept m2m field,
            we store the fields with a comma separated string into a Char config field """
        self._inverse_asymmetric_evaluation('high')

    @api.depends('asymmetric_evaluation_medium_str')
    def _compute_asymmetric_evaluation_medium_ids(self):
        """ As config_parameters does not accept m2m field,
            we store the fields with a comma separated string into a Char config field """
        self._compute_asymmetric_evaluation('medium')

    def _inverse_asymmetric_evaluation_medium_str(self):
        """ As config_parameters does not accept m2m field,
            we store the fields with a comma separated string into a Char config field """
        self._inverse_asymmetric_evaluation('medium')

    @api.depends('asymmetric_evaluation_low_str')
    def _compute_asymmetric_evaluation_low_ids(self):
        """ As config_parameters does not accept m2m field,
            we store the fields with a comma separated string into a Char config field """
        self._compute_asymmetric_evaluation('low')

    def _inverse_asymmetric_evaluation_low_str(self):
        """ As config_parameters does not accept m2m field,
            we store the fields with a comma separated string into a Char config field """
        self._inverse_asymmetric_evaluation('low')

    def _remove_from_other_evaluations(self, changed_field):
        fields = ['asymmetric_evaluation_very_high_ids', 'asymmetric_evaluation_high_ids',
                  'asymmetric_evaluation_medium_ids',
                  'asymmetric_evaluation_low_ids']
        fields.remove(changed_field)

        for other_field in fields:
            criteria_to_remove = self[other_field] & self[changed_field]
            self[other_field] -= criteria_to_remove

    @api.onchange('asymmetric_evaluation_very_high_ids')
    def _onchange_asymmetric_evaluation_very_high(self):
        self._remove_from_other_evaluations('asymmetric_evaluation_very_high_ids')

    @api.onchange('asymmetric_evaluation_high_ids')
    def _onchange_asymmetric_evaluation_very(self):
        self._remove_from_other_evaluations('asymmetric_evaluation_high_ids')

    @api.onchange('asymmetric_evaluation_medium_ids')
    def _onchange_asymmetric_evaluation_medium(self):
        self._remove_from_other_evaluations('asymmetric_evaluation_medium_ids')

    @api.onchange('asymmetric_evaluation_low_ids')
    def _onchange_asymmetric_evaluation_low(self):
        self._remove_from_other_evaluations('asymmetric_evaluation_low_ids')

    def set_values(self):
        if self.evaluation_system == 'asymmetric' and len(self.asymmetric_evaluation_very_high_ids) + len(
                self.asymmetric_evaluation_high_ids) + \
                len(self.asymmetric_evaluation_medium_ids) + len(self.asymmetric_evaluation_low_ids) < 25:
            raise UserError(_("you must setup all the criteria for the asymmetric evaluation system"))
        super(ResConfigSettings, self).set_values()

        for record in self.env['oi_risk_management.risk'].search([]):
            record._compute_main_risk_total_score()
