# -*- coding: utf-8 -*-
from odoo.exceptions import ValidationError
from odoo import fields, models, _,api


class ActivityDescription(models.Model):

    _name = "activity.description"
    _description = "Activity description"

    project_activity_description_id = fields.Many2one(comodel_name="project.task",help="Add the Activity Description")
    activity_no = fields.Integer(string="Activity no",help="Activity Number",compute='_compute_activity_no')
    system_activity = fields.Html(string="Activity",help="Add Activity")
    description_activity = fields.Html(string="Description Activity",help="Add Description of Activity")
    verification = fields.Html(string="Verification",help="Add the Verification")
    risk_identified = fields.Html(string="Risk Identified",help="Add the Risk Identified")

    @api.depends('activity_no')
    def _compute_activity_no(self):
        var = 1
        for record in self:
            record.activity_no = var
            var += 1
            # if record.display_type not in ["line_note", "line_section"]:


