from odoo.tools.json import json_default
from datetime import datetime, time
import io
import json
try:
   from odoo.tools.misc import xlsxwriter
except ImportError:
   import xlsxwriter
from odoo import fields, models, _,api
from odoo.exceptions import UserError
from ..report.asset_report_mixin import AssetVerificationReportMixin


class AssetVerificationReport(AssetVerificationReportMixin, models.TransientModel):
    _name = 'assets.verification.reports'
    _description = 'Assets Verification Reports'


    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')
    custodian_department_id = fields.Many2one('hr.department', string='Custodian Department')
    job_location_id = fields.Many2one('asset.verification.job.location', string='Location')
    custodian_id = fields.Many2one('hr.employee', string='Custodian')
    history_id = fields.Many2one('asset.verification.history', string='Asset')
    asset_id = fields.Many2one('account.asset', string='Asset')
    verification_job_location_id = fields.Many2one(
        'asset.verification.job', string='Job Location', required=True
    )
    asset_ids = fields.Many2many('account.asset', string='Assets')
    latest_verification_history_ids = fields.Many2many(
        'asset.verification.history', string='Latest Verification History'
    )
    period_start_date = fields.Date(string='Period Start Date')
    period_end_date = fields.Date(string='Period End Date')
    verification_status = fields.Selection(
        [('verified', 'Verified'), ('not_verified', 'Not-Verified'), ('all', 'All')],
        string='Verification Status',
        default='all',
    )


    @api.onchange('verification_job_location_id')
    def _onchange_job_location_id(self):
        if self.verification_job_location_id:
            asset_ids = self.env['asset.verification.job.line'].search([
                ('account_verification_job_id', '=', self.verification_job_location_id.id)
            ]).mapped('asset_id').filtered(lambda a: a.exists()).ids
            self.asset_ids = [(6, 0, asset_ids)]
        else:
            self.asset_ids = [(5, 0, 0)]

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_ids = self.env.context.get('active_ids')
        if self.env.context.get('active_model') == 'account.asset' and active_ids:
            res['asset_ids'] = [(6, 0, active_ids)]
        return res


    def _build_report_data(self, extra_context=None):
        data = {
            'asset_id': self.asset_id.id,
            'asset_ids': self.asset_ids.ids,
            'period_start_date': self.period_start_date,
            'period_end_date': self.period_end_date,
            'verification_job_location_id': self.verification_job_location_id.id,
            'verification_status': self.verification_status,
        }
        if extra_context:
            data['context'] = extra_context
        return data


    def action_generate_report(self):
        data = self._build_report_data()
        return self.env.ref(
            'asset_verification_report.action_report_asset_verification_report'
        ).report_action(self, data=data)

    def action_export_excel(self):
        data = self._build_report_data()
        return {
            'type': 'ir.actions.report',
            'data': {
                'model': self._name,
                'options': json.dumps(data, default=json_default),
                'output_format': 'xlsx_reports',
                'report_name': 'Assets Verification Register',
            },
            'report_type': 'xlsx_reports',
        }

    @api.model
    def action_get_xlsx_report_value(self, data):
        data = dict(data or {})
        data['context'] = dict(self.env.context)
        return {
            'type': 'ir.actions.report',
            'data': {
                'model': self._name,
                'options': json.dumps(data, default=json_default),
                'output_format': 'xlsx_reports',
                'report_name': 'Assets Verification Report',
            },
            'report_type': 'xlsx_reports',
        }

    # Column definitions: (header_label, width)
    _XLSX_COLUMNS = [('Asset', 20),('Barcode', 25),('Category', 18),('Serial Number', 20),('Verification Status', 15),
                    ('Verified By', 15),('Condition', 20),('Past Year', 20),('This Year', 15),('Comments', 20),
                    ('Custodian', 15),('Custodian Department', 22), ('Job Location', 18),
                ]

    # data from asset.verification.history
    def _xlsx_row_from_history(self, worksheet, row, line):
        asset = line.history_id
        today = fields.Date.today()
        worksheet.write(row, 0,  asset.name or '')
        worksheet.write(row, 1,  asset.alternative_ref or '')
        worksheet.write(row, 2,  asset.afs_classification.name if asset.afs_classification else '')
        worksheet.write(row, 3,  asset.serial_number or '')
        worksheet.write(row, 4,  'Verified')
        worksheet.write(row, 5,  line.asset_verification_user_id.name if line.asset_verification_user_id else '')
        worksheet.write(row, 6,  asset.condition if asset.history_ids else '')
        worksheet.write(row, 7,  today.year - 1)
        worksheet.write(row, 8,  today.year)
        worksheet.write(row, 9,  asset.condition if asset.history_ids else '')
        worksheet.write(row, 10, asset.custodian_id.name or '')
        worksheet.write(row, 11, asset.custodian_department_id.name if asset.custodian_department_id else '')
        worksheet.write(row, 12, asset.job_location_id.name if asset.job_location_id else '')

    # data from account.asset for not verified assets
    def _xlsx_row_from_asset(self, worksheet, row, asset):
        today = fields.Date.today()
        worksheet.write(row, 0,  asset.name or '')
        worksheet.write(row, 1,  asset.alternative_ref or '')
        worksheet.write(row, 2,  asset.afs_classification.name if asset.afs_classification else '')
        worksheet.write(row, 3,  asset.serial_number or '')
        worksheet.write(row, 4,  'Not Verified')
        worksheet.write(row, 5,  '')
        worksheet.write(row, 6,  asset.condition if asset.history_ids else '')
        worksheet.write(row, 7,  '-')
        worksheet.write(row, 8,  '-')
        worksheet.write(row, 9,  asset.condition if asset.history_ids else '')
        worksheet.write(row, 10, asset.custodian_id.name or '')
        worksheet.write(row, 11, asset.custodian_department_id.name if asset.custodian_department_id else '')
        worksheet.write(row, 12, asset.job_location_id.name if asset.job_location_id else '')

    def get_xlsx_report(self, data, response):
        """Main XLSX rendering method — called by the report framework."""
        resolved = self._resolve_report_data(data)
        job_lines = resolved['job_lines']       # verified histories
        final_assets = resolved['final_assets']  # not-verified assets
        status = data.get('verification_status') or 'all'

        #  Workbook setup
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('Assets Report')

        title_fmt = workbook.add_format({
            'font_size': 18, 'align': 'center',
            'color': '#00008B', 'bold': True,
        })
        header_fmt = workbook.add_format({'bold': True, 'bg_color': '#DCE6F1'})

        # Title
        last_col_letter = chr(ord('A') + len(self._XLSX_COLUMNS) - 1)
        worksheet.merge_range(f'D1:{last_col_letter}1', _('Asset Verification Register Report'), title_fmt)
        worksheet.set_row(0, 30)

        # Headers
        for col, (label, width) in enumerate(self._XLSX_COLUMNS):
            worksheet.write(2, col, label, header_fmt)
            worksheet.set_column(col, col, width)
        worksheet.set_row(2, 25)

        #  Data rows
        row = 3

        if status == 'not_verified':
            for asset in final_assets:
                self._xlsx_row_from_asset(worksheet, row, asset)
                row += 1

        elif status == 'verified':
            print("\n\n\n VERIFIED ASSET---->")
            for line in job_lines:
                self._xlsx_row_from_history(worksheet, row, line)
                row += 1

        else:  # 'all' – verified first, then not-verified
            for line in job_lines:
                self._xlsx_row_from_history(worksheet, row, line)
                row += 1
            for asset in final_assets:
                self._xlsx_row_from_asset(worksheet, row, asset)
                row += 1

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()