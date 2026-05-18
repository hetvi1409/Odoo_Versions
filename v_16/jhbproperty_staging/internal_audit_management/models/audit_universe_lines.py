# -*- coding: utf-8 -*-
from odoo.exceptions import ValidationError
from odoo import fields, models, _,api



class AuditUniverseLines(models.Model):

    _name = "audit.universe.lines"
    _description = "Audit Universe Lines"

    audit_universe_id = fields.Many2one(comodel_name="audit.universe",help="Add the audit universe")
    sequence = fields.Integer(string="Number",help="Sequence will be automatically created",compute='_compute_sequence')
    activity = fields.Html(string="Process/Activity",help="Enter the process or activity")
    department_id = fields.Many2one("hr.department",string="Department",help="Enter the department")
    department_head_id = fields.Many2one("hr.employee",string="Head of the Department",help="Enter the Head of the department")
    unit = fields.Many2one("hr.employee",string="Unit",help="Select the Unit")
    unit_head = fields.Many2one("hr.employee",string="Unit Head",help="Select the Unit Head")
    audit_interest = fields.Html(string="Identifiable area of audit interest ",help="Add the audit interest")
    # control_objective = fields.Html(string="Objective",help="Add the Objective")
    # scope = fields.Html(string="ScOPE",help="Add the Scope")
    # key_assessed = fields.Html(string="Key Control that must be assessed",help="Ad the key control assessed")
    # existing_control = fields.Html(string="Assess the adequacy of the existing Controls",help="Add the existing controls")
    # agree_opinion = fields.Selection([('adequate', 'Adequate'), ('partially_adequate', 'Partially Adequate'),('not_adequate', 'Not Adequate'),('no_control','No controls to provide reasonable assurance')],string="Agree on an Opinion on the Adequacy of Controls",help="Add the agreement opinion")
    @api.depends('sequence')
    def _compute_sequence(self):
        var = 1
        for record in self:
            record.sequence = var
            var += 1