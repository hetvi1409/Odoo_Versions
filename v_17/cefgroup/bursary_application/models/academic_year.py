from odoo import fields, models, api
from dateutil.relativedelta import relativedelta


class AcademicYear(models.Model):
    _name = "academic.year"
    _description = "Academic Year"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Academic Year", readonly=True)
    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)

    _sql_constraints = [
        ('unique_academic_year', 'UNIQUE(name)',
         'The Academic Year name must be unique.')
    ]

    @api.onchange('start_date')
    def _onchange_start_date(self):
        if self.start_date:
            self.end_date = self.start_date + relativedelta(years=1, days=-1)
            self.name = f"{self.start_date.year}-{self.end_date.year}"

    @api.model
    def create(self, vals):
        if vals.get('start_date') and not vals.get('end_date'):
            start_date = fields.Date.from_string(vals['start_date'])
            end_date = start_date + relativedelta(years=1, days=-1)
            vals['end_date'] = end_date
        if vals.get('start_date') and vals.get('end_date') and not vals.get(
                'name'):
            start_year = fields.Date.from_string(vals['start_date']).year
            end_year = fields.Date.from_string(vals['end_date']).year
            vals['name'] = f"{start_year}-{end_year}"
        return super().create(vals)



class CourseType(models.Model):
    _name = "course.type"
    _description = "Course Type"

    name = fields.Char(string="Name", required=True)

    _sql_constraints = [
        ('unique_name', 'UNIQUE(name)',
         'The Field of Study must be unique.')
    ]


class FieldStuday(models.Model):
    _name = "field.study"
    _description = "Field Of Study"

    name = fields.Char(string="Name", required=True)
    field_study_id = fields.Many2one('course.type')
    _sql_constraints = [
        ('unique_name', 'UNIQUE(name)',
         'The Field of Study must be unique.')
    ]
