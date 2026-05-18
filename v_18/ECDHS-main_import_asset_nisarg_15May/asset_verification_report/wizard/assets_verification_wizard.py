from odoo.tools.json import json_default
import io
import json
try:
   from odoo.tools.misc import xlsxwriter
except ImportError:
   import xlsxwriter
from odoo import fields, models, _,api
from odoo.exceptions import UserError

class AssetVerificationReport(models.TransientModel):
    _name = 'assets.verification.reports'
    _description = "Assets verification Reports"

    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    custodian_department_id = fields.Many2one('hr.department', string="Custodian Department" )
    job_location_id = fields.Many2one('asset.verification.job.location', string='Location')
    custodian_id = fields.Many2one('hr.employee', string='Custodian')
    # history_id = fields.Many2one('account.asset', string='Asset')
    history_id = fields.Many2one('asset.verification.history', string='Asset')
    asset_id = fields.Many2one('account.asset', string='Asset')
    verification_job_location_id = fields.Many2one('asset.verification.job', string='Job Location', required=True)
    asset_ids = fields.Many2many('account.asset', string='Assets')
    latest_verification_history_ids = fields.Many2many('asset.verification.history', string='Latest Verification History')

    period_start_date = fields.Date(string="Period Start Date")
    period_end_date = fields.Date(string="Period End Date")
    verification_status = fields.Selection([
        ('verified', 'Verified'),
        ('not_verified', 'Not Verified'),
        ('all', 'All')], string="Verification Status", default='all',required=True)

    @api.onchange('verification_job_location_id')
    def _onchange_job_location_id(self):

        print("ONCHANGE JOB LOCATION ID CALLED>>", self.verification_job_location_id)

        if self.verification_job_location_id:
            asset = self.env['asset.verification.job.line'].search([
                ('account_verification_job_id', '=', self.verification_job_location_id.id)
            ]).mapped('asset_id').filtered(lambda a: a.exists())
            assets = self.env['account.asset'].search([('id', 'in', asset.ids)])
            self.asset_ids = [(6, 0, assets.ids)]

        else:
            self.asset_ids = [(5, 0, 0)]




    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_ids = self.env.context.get('active_ids')
        active_model = self.env.context.get('active_model')

        if active_model == 'account.asset' and active_ids:
            res['asset_ids'] = [(6, 0, active_ids)]

        return res

    def action_generate_report(self):
        print("GENERATE REPORT CALLED>>",self)
        """Generate asset report in PDF or Excel"""
        # if no asset_ids and no asset_id, pass context to get all assets latest verification only
        if not self.asset_ids and not self.asset_id:
            self = self.with_context(latest_verification_history=True)
        data = {
            # 'date_from': self.date_from,
            # 'date_to': self.date_to,
            # 'custodian_department_id': self.custodian_department_id.id,
            'verification_job_location_id': self.verification_job_location_id.id,
            # 'custodian_id': self.custodian_id.id,
            # 'history_id': self.history_id.id,
            'asset_id': self.asset_id.id,
            'asset_ids': self.asset_ids.ids,
            'period_start_date': self.period_start_date,
            'period_end_date': self.period_end_date,
            'verification_status': self.verification_status,
        }
        print("\n\n\n\n DATA SENT TO REPORT >>>>", data)
        return self.env.ref('asset_verification_report.action_report_asset_verification_report').report_action(self, data=data)

    def action_get_xlsx_report_value(self, data):
        """"""
        return {
            'type': 'ir.actions.report',
            'data': {'model': self._name,
                     'options': json.dumps(data,
                                           default=json_default),
                     'output_format': 'xlsx_reports',
                     'report_name': 'Assets Verification Report',
                     },
            'report_type': 'xlsx_reports',
        }

    def action_export_excel(self):
        data = {
            # 'date_from': self.date_from,
            # 'date_to': self.date_to,
            # 'custodian_department_id': self.custodian_department_id.id,
            'verification_job_location_id': self.verification_job_location_id.id,
            # 'custodian_id': self.custodian_id.id,
            # 'history_id': self.history_id.id,
            'asset_id': self.asset_id.id,
            'asset_ids': self.asset_ids.ids,
            'latest_verification_history': self.env.context.get('latest_verification_history', False),
            'period_start_date': self.period_start_date,
            'period_end_date': self.period_end_date,
            'verification_status': self.verification_status,
        }
        return {
            'type': 'ir.actions.report',
            'data': {'model': self._name,
                     'options': json.dumps(data,
                                           default=json_default),
                     'output_format': 'xlsx_reports',
                     'report_name': 'Assets Verification Register',
                     },
            'report_type': 'xlsx_reports',
        }

    def _get_verified_job_lines(self, job_id):
        domain = [
            ('account_verification_job_id', '=', job_id),
            ('verified', '=', True)
        ]
        return self.env['asset.verification.job.line'].search(domain)

    def _get_not_verified_job_lines(self, job_id):
        domain = [
            ('account_verification_job_id', '=', job_id),
            ('verified', '=', False)
        ]
        return self.env['asset.verification.job.line'].search(domain)

    def _get_all_job_lines(self, job_id):
        domain = [
            ('account_verification_job_id', '=', job_id)
        ]
        return self.env['asset.verification.job.line'].search(domain)

    def get_xlsx_report(self, data, response):
        print("GET XLSX REPORT CALLED WITH DATA>>", data)
        Asset = self.env['account.asset']
        History = self.env['asset.verification.history']
        job_lines = self.env['asset.verification.job.line']

        if data.get('asset_ids') and not data.get('latest_verification_history'):
            asset_ids = data.get('asset_ids')
            assets = Asset.browse(asset_ids).exists()
        if asset_id := data.get('asset_id'):
            assets = History.search([('history_id', '=', asset_id)])
        if history_id := data.get('history_id'):
            assets = History.search([('history_id', '=', history_id)])
        if not data.get('asset_id') and not data.get('history_id') and not data.get('asset_ids'):
            assets = History.search([])

        # For latest verification history
        if data.get('asset_ids') and data.get('latest_verification_history'):
            asset_ids = data.get('asset_ids')
            assets = Asset.browse(asset_ids).exists()

        # When no asset selected, print only latest verification history per asset
        if not data.get('asset_id') and not data.get('asset_ids'):
            print("GETTING LATEST VERIFICATION HISTORY FOR ALL ASSETS")
            if not data.get('latest_verification_history'):
                # if not data.get('latest_verification_history') and not data.get('history_id'):
                all_assets = self.env['account.asset'].search([])
                latest_history_ids = []
                seen_assets = set()
                history = self.env['asset.verification.history'].search(
                    [('history_id', 'in', all_assets.ids)],
                    order='history_id, create_date desc'
                )
                for h in history:
                    asset_id = h.history_id.id
                    if asset_id not in seen_assets:
                        latest_history_ids.append(h.id)
                        seen_assets.add(asset_id)
                assets = self.env['account.asset'].browse(list(seen_assets)).exists()
                latesest_histories = self.env['asset.verification.history'].browse(latest_history_ids)

        if data.get('asset_ids') and data.get('verification_status'):

            if data.get('verification_job_location_id'):

                job_id = data.get('verification_job_location_id')
                status = data.get('verification_status')

                if status == 'verified':
                    job_lines = self._get_verified_job_lines(job_id)

                elif status == 'not_verified':
                    job_lines = self._get_not_verified_job_lines(job_id)

                elif status == 'all':
                    job_lines = self._get_all_job_lines(job_id)

                assets = job_lines.mapped('asset_id')

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('Assets Report')
        head = workbook.add_format({'font_size': 18, 'align': 'center', 'color': '#00008B', 'bold': True})
        asset_title_format = workbook.add_format({'bold': True, 'font_size': 14})

        # worksheet.merge_range('B1:E1', _('Asset Verification Register Report'), head)
        worksheet.merge_range('D1:G1', _('Asset Verification Register Report'), head)
        # Header
        header_format = workbook.add_format(
            {'bold': True, 'bg_color': '#DCE6F1'})
        headers = ['Asset', 'Barcode', 'Category', 'Serial Number', 'Verification Status', 'Verified By',
                   'Condition',
                   'Past Year', 'This Year', 'Comments', 'Custodian', 'Custodian Department', 'Job Location']
        for col, header in enumerate(headers):
            worksheet.write(2, col, header, header_format)
        worksheet.set_row(0, 30)
        worksheet.set_row(2, 25)

        worksheet.set_column(0, 0, 20)
        worksheet.set_column(1, 1, 25)
        worksheet.set_column(2, 2, 18)
        worksheet.set_column(3, 3, 20)
        worksheet.set_column(4, 4, 15)
        worksheet.set_column(5, 5, 15)
        worksheet.set_column(6, 6, 20)
        worksheet.set_column(7, 7, 20)
        worksheet.set_column(8, 8, 15)
        worksheet.set_column(9, 9, 20)

        row = 3
        for line in job_lines:
            worksheet.write(row, 0, line.asset_id.name or '')
            worksheet.write(row, 1, line.asset_id.alternative_ref or '')
            worksheet.write(row, 2, line.asset_id.afs_classification.name or '')
            worksheet.write(row, 3, line.asset_id.serial_number or '')
            worksheet.write(row, 4, "Verified" if line.verified else "Not Verified")
            worksheet.write(row, 5, line.write_uid.name if line.write_uid else '')
            worksheet.write(row, 6, line.asset_id.condition if line.asset_id.history_ids else '')
            worksheet.write(row, 6, 'Condition')
            worksheet.write(row, 7, fields.Date.today().year - 1)
            worksheet.write(row, 8, fields.Date.today().year)
            worksheet.write(row, 9, line.asset_id.condition if line.asset_id.history_ids else '')
            worksheet.write(row, 10, line.asset_id.custodian_id.name or '')
            worksheet.write(row, 11, line.asset_id.custodian_department_id.name or '')
            worksheet.write(row, 12, line.asset_id.job_location_id.name if line.asset_id.job_location_id else '')
            row += 1

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()