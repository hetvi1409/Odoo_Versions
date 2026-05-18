from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models


class DocumentsDocument(models.Model):
    _inherit = 'documents.document'

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
    jmc_number = fields.Char(string="JMC Number")
    erf_number = fields.Char(string="Erf Number")
    address = fields.Char(string="Address")
    jmc_property_id = fields.Many2one(comodel_name='building', string="JMC Number", tracking=True,
                                      context={'list_view_ref':'property_update.building_list'})
    general_type = fields.Selection([('general_file', 'General File'),
                                     ('property', 'Property')],default='general_file',
                                    string="Document Type", required=True)

    @api.depends('retention_frame')
    def _compute_retention_type(self):
        for doc in self:
            # Compute retention type based on retention frame
            doc.retention_type = 'permanent' if doc.retention_frame == 0 else 'retain'

    def _compute_retention_frame(self):
        for rec in self:
            rec.retention_frame = False
            rec.retention_unit = False
            folder_retention = rec.folder_id.retention_periods
            if folder_retention:
                rec.retention_frame = folder_retention
            if rec.folder_id.retention_duration_unit:
                rec.retention_unit = rec.folder_id.retention_duration_unit

    def _compute_retention_end_date(self):
        for record in self:
            record.retention_end_date = False
            if record.create_date and record.retention_frame and record.retention_unit:
                create_date = fields.Datetime.from_string(record.create_date)

                # Calculate retention end date based on retention unit
                if record.retention_unit == 'days':
                    retention_end_date = create_date + timedelta(days=record.retention_frame)
                elif record.retention_unit == 'months':
                    retention_end_date = create_date + relativedelta(months=record.retention_frame)
                elif record.retention_unit == 'years':
                    retention_end_date = create_date + relativedelta(years=record.retention_frame)
                else:
                    # Default to days if retention unit is not recognized
                    retention_end_date = create_date + timedelta(days=record.retention_frame)

                record.retention_end_date = retention_end_date

    @api.depends('folder_id.retention_duration_unit')
    def _compute_time_remaining(self):
        for record in self:
            record.time_remaining = False
            if record.retention_end_date:
                current_date = fields.Datetime.now()
                remaining_time = relativedelta(record.retention_end_date, current_date)

                # Format the remaining time
                time_remaining_str = f"{remaining_time.years} yy, {remaining_time.months} mm, {remaining_time.days} dd, {remaining_time.hours} hh, {remaining_time.minutes} min"
                # Update the time_remaining field
                record.time_remaining = time_remaining_str

    @api.onchange('jmc_property_id')
    def onchange_jmc_number(self):
        """Onchange JMC Number"""
        property_name = self.jmc_property_id
        self.jmc_number = property_name.jmc_number
        self.erf_number = property_name.name
        self.address = property_name.address

    def update_jmc_number(self):
        property_name = self.jmc_property_id
        self.jmc_number = property_name.jmc_number
        self.erf_number = property_name.name
        self.address = property_name.address
