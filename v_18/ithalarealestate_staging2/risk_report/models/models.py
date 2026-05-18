# -*- coding: utf-8 -*-

from odoo import models, fields, api


class risk_report(models.Model):
    _name = 'risk_report.risk_report'
    _description = 'risk_report.risk_report'

    tenant = fields.Char()
    total_score = fields.Integer()
    alcohol = fields.Integer()
    fuel = fields.Integer()
    uber = fields.Integer()
    gambling = fields.Integer()
    credit = fields.Integer()
    age_score = fields.Integer()
    employeement = fields.Integer()
    address = fields.Integer()

