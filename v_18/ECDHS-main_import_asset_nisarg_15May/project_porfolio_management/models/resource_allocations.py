from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ResourceAllocations(models.Model):
    _name = 'resource.allocations'
    _rec_name= "project_id"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    resource = fields.Many2one('res.users',string='Resource')
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    remaining_days = fields.Integer(string='Days')
    days = fields.Integer(string='Days', compute="_compute_days")
    project_id = fields.Many2one('project.project', string="Project", required=True, domain=[('is_ppe', '=', True)])
    resource_ids = fields.One2many("resource.allocations.line", "resource_id")
    planned_hours = fields.Float(string="Planned Hours", compute="_compute_planned_hours")
    name = fields.Char(string="Reference", required=True, copy=False,
                       readonly=True, default=lambda self: _('New'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('project.resource') or _('New')
        return super().create(vals_list)

    @api.depends('start_date', 'end_date')
    def _compute_days(self):
        """Compute Days"""
        for rec in self:
            if rec.start_date and rec.end_date:
                rec.days = (rec.end_date - rec.start_date).days
            else:
                rec.days = 0

    @api.depends('resource_ids', 'start_date', 'end_date')
    def _compute_planned_hours(self):
        """"""
        for rec in self:
            rec.planned_hours = 0
            planned_hours = 0
            for line in rec.resource_ids:
                if line.hours != 0:
                    actual_hours = (8 * line.hours)* rec.days
                    planned_hours += actual_hours
            rec.planned_hours = planned_hours

class ResourceAllocationsLine(models.Model):
    _name = 'resource.allocations.line'

    user_id = fields.Many2one('hr.employee', string="Resource", required=True)
    hours = fields.Float(string="Hours in %")
    resource_id = fields.Many2one("resource.allocations")

    @api.constrains('hours', 'resource_id')
    def _check_hours_total(self):
        for rec in self:
            total_hours = rec.hours
            if total_hours > 100:
                raise ValidationError(
                    f"Total allocated hours ({total_hours}%) cannot exceed 100% for resource: {rec.resource_id.display_name}"
                )
