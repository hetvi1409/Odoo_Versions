# -*- coding: utf-8 -*-
from odoo import api,fields, models
from datetime import timedelta
from dateutil.relativedelta import relativedelta


class DocumentsDocument(models.Model):
    _inherit = 'documents.document'

    # Folder retention
    enabled = fields.Boolean(string="Enabled")
    is_permanent = fields.Boolean(string="Permanent", default=False,
                                  help="If checked, the folder and its contents will not be subject to automatic deletion based on retention policies.")
    retention_periods = fields.Float(string="Retention Frame")
    retention_duration_unit = fields.Selection(
        [('days', 'Days'), ('months', 'Months'), ('years', 'Years')],
        string='Duration Unit', default='months',
        help='Select the unit for the retention duration.')
    retention_duration_in_days = fields.Float(
        string='Retention Duration in Days',
        compute='_compute_retention_duration_in_days')
    # Documents retention
    retention_frame = fields.Float(string="Retention Frame", compute='_compute_retention_frame')
    retention_unit = fields.Char(compute='_compute_retention_frame')
    retention_end_date = fields.Datetime(string="Retention End Date",
                                         compute='_compute_retention_end_date')
    time_remaining = fields.Char(string="Time Remaining",
                                 compute='_compute_time_remaining')
    retention_type = fields.Selection([
        ('retain', 'Retain'),
        ('permanent', 'Permanent')
    ], string='Retention Type', compute='_compute_retention_type')

    def _compute_retention_frame(self):
        print("_compute_retention_frame")
        for rec in self:
            rec.retention_frame = False
            rec.retention_unit = False
            folder_retention = rec.folder_id.retention_periods
            if folder_retention:
                rec.retention_frame = folder_retention
            if rec.folder_id.retention_duration_unit:
                rec.retention_unit = rec.folder_id.retention_duration_unit

    def _compute_retention_end_date(self):
        print('_compute_retention_end_date')
        for record in self:
            record.retention_end_date = False
            if record.create_date and record.retention_frame and record.retention_unit:
                create_date = fields.Datetime.from_string(record.create_date)

                # Calculate retention end date based on retention unit
                if record.retention_unit == 'days':
                    retention_end_date = create_date + timedelta(
                        days=record.retention_frame)
                elif record.retention_unit == 'months':
                    retention_end_date = create_date + relativedelta(
                        months=record.retention_frame)
                elif record.retention_unit == 'years':
                    retention_end_date = create_date + relativedelta(
                        years=record.retention_frame)
                else:
                    # Default to days if retention unit is not recognized
                    retention_end_date = create_date + timedelta(
                        days=record.retention_frame)

                record.retention_end_date = retention_end_date

    @api.depends('retention_duration_unit')
    def _compute_time_remaining(self):
        print('_compute_time_remaining')
        for record in self:
            record.time_remaining = False
            if record.retention_end_date:
                current_date = fields.Datetime.now()
                remaining_time = relativedelta(record.retention_end_date,
                                               current_date)

                # Format the remaining time
                time_remaining_str = f"{remaining_time.years} yy, {remaining_time.months} mm, {remaining_time.days} dd, {remaining_time.hours} hh, {remaining_time.minutes} min"
                # Update the time_remaining field
                record.time_remaining = time_remaining_str

    @api.depends('retention_frame')
    def _compute_retention_type(self):
        print('_compute_retention_type')
        for doc in self:
            # Compute retention type based on retention frame
            doc.retention_type = 'permanent' if doc.retention_frame == 0 else 'retain'

    @api.depends('retention_periods', 'retention_duration_unit')
    def _compute_retention_duration_in_days(self):
        print('_compute_retention_duration_in_days')
        for record in self:
            record.retention_duration_in_days = False
            if not record.is_permanent:
                if record.retention_duration_unit == 'years':
                    record.retention_duration_in_days = record.retention_periods * 365
                elif record.retention_duration_unit == 'months':
                    record.retention_duration_in_days = record.retention_periods * 30
                else:
                    record.retention_duration_in_days = record.retention_periods