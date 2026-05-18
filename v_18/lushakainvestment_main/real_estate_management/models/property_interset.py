from odoo import fields, models, api
from odoo.exceptions import ValidationError


class PropertyInterset(models.Model):
    _name = 'property.interset'
    _description = "Property Interset"
    _order = 'start_date'

    start_date = fields.Date(
        string="Start Date",
        required=True
    )
    end_date = fields.Date(
        string="End Date",
        help="Leave blank for open-ended period (e.g., --> etc...)"
    )
    interest_rate = fields.Float(
        string="Interest Rate (%)",
        required=True,
    )

    name = fields.Char(
        string="Name",
        compute="_compute_name",
        store=True
    )

    @api.depends('start_date', 'end_date')
    def _compute_name(self):
        for rec in self:
            start = rec.start_date.strftime(
                '%d-%b-%Y') if rec.start_date else ''
            if rec.end_date:
                end = rec.end_date.strftime('%d-%b-%Y')
            else:
                end = '---> etc...'
            rec.name = f"{start} to {end}"

    @api.constrains('start_date', 'end_date')
    def _check_date_order(self):
        """ Ensure start_date <= end_date (when end_date exists) """
        for rec in self:
            if rec.end_date and rec.start_date > rec.end_date:
                raise ValidationError(
                    "End Date must be greater than or equal to Start Date."
                )

    @api.constrains('start_date', 'end_date')
    def _check_overlapping_periods(self):
        """ Prevent overlapping date ranges """
        for rec in self:
            domain = [
                ('id', '!=', rec.id),
                ('start_date', '<=', rec.end_date or fields.Date.max),
                ('end_date', '>=', rec.start_date),
            ]
            overlaps = self.search(domain, limit=1)

            if overlaps:
                raise ValidationError(
                    f"Date range {rec.name} overlaps with existing record "
                    f"{overlaps.name}."
                )