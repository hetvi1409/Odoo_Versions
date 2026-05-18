from odoo import api , models, fields , _
import io
try:
   from odoo.tools.misc import xlsxwriter
except ImportError:
   import xlsxwriter
class AssetVerificationJob(models.Model):
    _name = 'asset.verification.job'
    _description = 'Asset Verification Job'

    name = fields.Char(string="Job Name", required=True)
    user_id = fields.Many2one('res.users', string="Connected User", default=lambda self: self.env.user)
    user_ids = fields.Many2many('res.users', string="Connected Users", default=lambda self: self.add_current_user())
    verification_period = fields.Selection([
        ('Q1', 'Quarter 1 (Jan - Mar)'),
        ('Q2', 'Quarter 2 (Apr - Jun)'),
        ('Q3', 'Quarter 3 (Jul - Sep)'),
        ('Q4', 'Quarter 4 (Oct - Dec)')
    ], string="Verification Period")
    verification_period_from = fields.Datetime(string="Verification Period From")
    verification_period_to = fields.Datetime(string="Verification Period To")
    asset_ids = fields.One2many('asset.verification.job.line', 'account_verification_job_id', string="Assets")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    ], default='draft', string="Status")
    total_assets = fields.Integer(string="Asset Count", compute="_compute_total_assets")
    verified_count = fields.Integer(string="Verified Assets", compute="_compute_verified_assets")
    not_verified_count = fields.Integer(string="Not Verified Assets", compute="_compute_not_verified_assets")
    completion_percentage = fields.Float(string="Completion %", compute="_compute_completion_percentage")
    location_id = fields.Many2one('stock.location',string="Location", help="Location of the asset")
    job_location_id = fields.Many2one('asset.verification.job.location','Job Location')


    def add_current_user(self):
        return [4,self.env.user.id]


    def action_download_report(self):
        # Redirect to the report download route
        return {
            'type': 'ir.actions.act_url',
            # 'url': '/asset_verification/report?job_id=%s' % self.id,
            'url': f'/asset_verification/report/{",".join(map(str, self.ids))}',
            'target': 'self',
        }

    # @api.onchange('job_location_id')
    # def _onchange_job_location_id(self):
    #     return {'warning': {
    #         'title': _("Please Refresh Asses"),
    #         'message': _(
    #             "To update asset values based on location , please click on update assets button")}
    #     }

    def update_assets(self):
        # Filter assets based on location if a location is specified
        domain = []
        if self.job_location_id:
            domain = [('job_location_id', '=', self.job_location_id.id)]

        # Fetch assets based on the location or all if no location is specified
        assets = self.env['account.asset'].search(domain)

        existing_lines = {line.asset_id.id: line for line in self.asset_ids}
        new_lines = []

        for asset in assets:
            if asset.id in existing_lines:
                line = existing_lines[asset.id]
                if line.asset_id.job_location_id != self.job_location_id:
                    print('NOT MATCH LOCATION')
                    continue
                if line.verified:
                    print('VERIFIED ASSET======>', asset)
                    continue
                new_lines.append((1, line.id, {'asset_id': asset.id, 'verified': False}))
            else:
                new_lines.append((0, 0, {'asset_id': asset.id,'verified': False}))

        # Remove lines for assets that no longer match the job location
        for line in self.asset_ids:
            if line.asset_id.job_location_id != self.job_location_id:
                new_lines.append((2, line.id, 0))

        self.asset_ids = new_lines


    # def write(self, vals):
    #     """
    #     Overwrite the create method to automatically add relevant assets to a new verification job.
    #     """
    #     print(vals,'saddasdsadsa')
    #     if 'job_location_id' in vals and vals.get('job_location_id'):
    #         confirm_wizard = self.env['asset.verification.confirm.wizard'].create({''})
    #
    #
    #     job = super(AssetVerificationJob, self).write(vals)
    #     return job


    @api.model_create_multi
    def create(self, vals_list):
        """
        Overwrite the create method to automatically add relevant assets to a new verification job.
        """
        for vals in vals_list:
            job = super(AssetVerificationJob, self).create(vals)
            print(vals,'vals...')

            # Fetch the location ID from the job (if provided)
            job_location_id = vals['job_location_id']

            # Filter assets based on location if a location is specified
            domain = []
            if job_location_id:
                domain = [('job_location_id', '=', job_location_id)]

            # Fetch assets based on the location or all if no location is specified
            assets = self.env['account.asset'].search(domain)

            # Create verification job lines
            lines = [(0, 0, {'asset_id': asset.id, 'verified': False}) for asset in assets]

            job.asset_ids = lines
            return job

    def _compute_total_assets(self):
        for record in self:
            record.total_assets = len(record.asset_ids)

    def _compute_verified_assets(self):
        for record in self:
            record.verified_count = len(record.asset_ids.filtered(lambda a: a.verified == True))

    def _compute_not_verified_assets(self):
        for record in self:
            record.not_verified_count = len(record.asset_ids.filtered(lambda a: a.verified == False))

    def _compute_completion_percentage(self):
        for record in self:
            if record.total_assets:
                record.completion_percentage = (record.verified_count / record.total_assets) * 100
            else:
                record.completion_percentage = 0.0

    def action_export_excel_report(self):
        data = self.generate_excel_report()
        return {
            'type': 'ir.actions.report',
            'report_type': 'xlsx',
            'data': {'model': 'asset.verification.job', 'report_name': 'asset_verification.job_excel_report'},
            'name': 'Asset Verification Excel Report',
            'file': 'asset_verification_job_report.xlsx',
            'report_file': data,
        }

    def generate_excel_report(self):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Verification Report')

        # Header: Job Summary
        worksheet.write('A1', 'Job Summary:')
        worksheet.write('A2', 'Job Name:')
        worksheet.write('B2', self.name or '')

        worksheet.write('A3', 'Verification Period From:')
        worksheet.write('B3', self.verification_period_from.strftime(
            '%Y-%m-%d %H:%M:%S') if self.verification_period_from else '')

        worksheet.write('A4', 'Verification Period To:')
        worksheet.write('B4', self.verification_period_to.strftime(
            '%Y-%m-%d %H:%M:%S') if self.verification_period_to else '')

        worksheet.write('A5', 'Status:')
        worksheet.write('B5', dict(self._fields['state'].selection).get(self.state, ''))

        worksheet.write('A6', 'Job Location:')
        worksheet.write('B6', self.job_location_id.name if self.job_location_id else '')

        # Asset Counts
        total_assets = len(self.asset_ids)
        verified_count = len(self.asset_ids.filtered(lambda line: line.verified))
        to_verify_count = total_assets - verified_count
        completion_percentage = (verified_count / total_assets * 100) if total_assets > 0 else 0

        worksheet.write('A8', 'Total Assets:')
        worksheet.write('B8', total_assets)

        worksheet.write('A9', 'Verified Assets:')
        worksheet.write('B9', verified_count)

        worksheet.write('A10', 'Assets to Verify:')
        worksheet.write('B10', to_verify_count)

        worksheet.write('A11', 'Completion Percentage:')
        worksheet.write('B11', f"{completion_percentage:.2f}%")

        # Adding space before the sections
        row = 13

        # Verified Assets Section
        worksheet.write(row, 0, 'Verified Assets')
        worksheet.write(row, 1, 'ID')
        worksheet.write(row, 2, 'Name')
        worksheet.write(row, 3, 'Barcode')
        worksheet.write(row, 4, 'Custodian')
        worksheet.write(row, 5, 'Status')
        row += 1

        # Write Verified Assets
        for line in self.asset_ids:
            if line.verified:
                worksheet.write(row, 1, line.asset_id.id or '')
                worksheet.write(row, 2, line.asset_id.name or '')
                worksheet.write(row, 3, line.asset_id.alternative_ref or '')
                worksheet.write(row, 4, line.asset_id.custodian_id.name if line.asset_id.custodian_id else '')  # Custodian
                worksheet.write(row, 5, 'Verified')
                row += 1

        # Adding space before new assets
        row += 2
        worksheet.write(row, 0, 'New Assets in Staging')
        worksheet.write(row, 1, 'ID')
        worksheet.write(row, 2, 'Name')
        worksheet.write(row, 3, 'Barcode')
        worksheet.write(row, 4, 'Custodian')
        worksheet.write(row, 5, 'Status')
        row += 1

        # Write New Assets
        staging_assets = self.env['asset.verification.staging'].search([
            ('verification_job_id', '=', self.id)
        ])

        for asset in staging_assets:
            worksheet.write(row, 1, '')
            worksheet.write(row, 2, asset.name or '')
            worksheet.write(row, 3, asset.barcode or '')
            worksheet.write(row, 4, asset.custodian_id.name if asset.custodian_id else '')  # Custodian
            worksheet.write(row, 5, 'New')
            row += 1

        # Adding space before missing assets
        row += 2
        worksheet.write(row, 0, 'Missing Assets')
        worksheet.write(row, 1, 'ID')
        worksheet.write(row, 2, 'Name')
        worksheet.write(row, 3, 'Barcode')
        worksheet.write(row, 4, 'Custodian')
        worksheet.write(row, 5, 'Status')
        row += 1

        # Write Missing Assets
        all_assets = self.asset_ids.mapped('asset_id')
        verified_assets = self.asset_ids.filtered(lambda l: l.verified).mapped('asset_id.id')
        missing_assets = all_assets.filtered(lambda asset: asset.id not in verified_assets)

        for asset in missing_assets:
            worksheet.write(row, 1, asset.id or '')
            worksheet.write(row, 2, asset.name or '')
            worksheet.write(row, 3, asset.alternative_ref or '')
            worksheet.write(row, 4, asset.custodian_id.name if asset.custodian_id else '')  # Custodian
            worksheet.write(row, 5, 'Missing')
            row += 1

        workbook.close()
        output.seek(0)
        return output.read()


    def action_generate_excel_report(self):
        # Return the action for generating the Excel report
        return {
            'type': 'ir.actions.report',
            'report_type': 'xlsx',
            'report_name': 'asset_verification.job_excel_report',
            'data': {'job_id': self.id}
        }

class AssetVerificationJobLines(models.Model):
    _name = 'asset.verification.job.line'
    _description = 'Asset Verification Job Lines'

    asset_id = fields.Many2one('account.asset', string="Assets")
    verified = fields.Boolean(readonly=True)
    account_verification_job_id = fields.Many2one('asset.verification.job', string="Assets")
    asset_verification_line_id = fields.Many2one('asset.verification', string="Asset Verification Line")

