# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class FleetReportWizard(models.TransientModel):
    _name = 'fleet.report.wizard'
    _description = 'Fleet Report Wizard'

    report_type = fields.Selection([
        ('transport_requests', 'Transport Requests'),
        ('trip_authorities', 'Trip Authorities'),
        ('vehicle_checklists', 'Vehicle Checklists'),
        ('lost_theft', 'Lost & Theft Reports'),
    ], string='Report Type', required=True, default='transport_requests')

    date_from = fields.Date(string='Date From', required=True)
    date_to = fields.Date(string='Date To', required=True, default=fields.Date.context_today)

    vehicle_ids = fields.Many2many('fleet.vehicle', string='Vehicles')
    department_ids = fields.Many2many('hr.department', string='Departments')

    def action_generate_report(self):
        """Generate the selected report"""
        self.ensure_one()
        # Placeholder for report generation logic
        return {
            'type': 'ir.actions.act_window',
            'name': 'Report Results',
            'res_model': self.report_type.replace('_', '.'),
            'view_mode': 'list,form',
            'domain': [('create_date', '>=', self.date_from), ('create_date', '<=', self.date_to)],
        }
