# -*- coding: utf-8 -*-
from odoo import api, fields, models


class IndicatorDimension(models.Model):
    """ This model represents indicator.dimension"""
    _name = 'indicator.dimension'
    _description = 'Indicator Dimension'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Dimension", required=True)
    indicator_id = fields.Many2one('output.indicator', string="Indicator")
    type = fields.Selection([('number', 'Number'),
                             ('currency', 'Currency'),
                             ('text', 'Text'),
                             ('percentage', 'Percentage'),
                             ('rating', 'Rating'),
                             ('range', 'Range'),
                             ('cohort_groups', 'Cohorts / Groups')], string="Type")
    user_id = fields.Many2one('res.users', string='Responsible')
    date = fields.Date(string="Date", default=fields.Date.today())
    description = fields.Char(string="Description")
    option_ids = fields.Many2many('indicator.dimension.option', string="Options")
    line_ids = fields.One2many('indicator.dimension.line', 'dimension_id', string="Details")

class IndicatorDimensionLine(models.Model):
    """ This model represents performance.portfolio."""
    _name = 'indicator.dimension.line'
    _description = 'Indicator Dimension Line'

    name = fields.Char(string='Description', required=True)
    dimension_id = fields.Many2one('indicator.dimension', string='Indicator Dimension')


class IndicatorDimensionOption(models.Model):
    """ This model represents performance.portfolio."""
    _name = 'indicator.dimension.option'
    _description = 'Indicator Dimension Option'

    name = fields.Char(string='Description', required=True)
    dimension_id = fields.Many2one('indicator.dimension', string='Indicator Dimension')

