# -*- coding: utf-8 -*-
from odoo.exceptions import ValidationError
from odoo import fields, models, _,api



class ControlAssessment(models.Model):

    _name = "control.assessment"
    _description = "Control Assessment"

    project_control_id = fields.Many2one(comodel_name="project.task",help="Add the control assessment")
    control_objective = fields.Html(string="Objective",help="Add the Objective")
    scope = fields.Html(string="ScOPE",help="Add the Scope")
    key_assessed = fields.Html(string="Key Control that must be assessed",help="Ad the key control assessed")
    existing_control = fields.Html(string="Assess the adequacy of the existing Controls",help="Add the existing controls")
    agree_opinion = fields.Selection([('adequate', 'Adequate'), ('partially_adequate', 'Partially Adequate'),('not_adequate', 'Not Adequate'),('no_control','No controls to provide reasonable assurance')],string="Agree on an Opinion on the Adequacy of Controls",help="Add the agreement opinion")
