from datetime import datetime, timedelta
from odoo import api, fields, models
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter

class AuditMeterReports(models.Model):
    """Model for getting dynamic report """
    _name = "audit.meter.only.report"
    _description = "Audit Meter Report"

    purchase_report = fields.Char(string="Purchase Report",
                                  help='Name of the report')
    date_from = fields.Datetime(string="Date From", help='Start date of report')
    date_to = fields.Datetime(string="Date to", help='End date of report')
    report_type = fields.Selection([
        ('All', 'All'),
        ('Today', 'Today'),
        ('Yesterday', 'Yesterday'),
        ('Last Week', 'Last Week'),
        ('This Week', 'This Week'),
        ('Last Month', "Last Month"),
        ('This Month', "This Month"),
        ('Custom', 'Custom')], default='All',
        help='The order of the report')
    exception = fields.Selection([('Duplicate Invoices', 'Duplicate Invoices'),
                                  ('Duplicate Payments', 'Duplicate Payments')])

    @api.model
    def get_audit_meter_only_details(self, option):
        """Function for getting datas for requests """
        report_values = self.env['audit.meter.only.report'].search(
            [('id', '=', option[0])])
        data = {
            'report_type': report_values.report_type,
            'model': self,
            'exception': report_values.exception,
            'date_from': report_values.date_from if report_values.date_from else fields.Date.today(),
        }
        if report_values.date_from:
            data.update({
                'date_from': report_values.date_from,
            })
        filters = self.get_filter(option)
        lines = self._get_report_values(data).get('data')
        return {
            'name': "Audit Report",
            'type': 'ir.actions.client',
            'tag': 's_r',
            'orders': data,
            'filters': filters,
            'report_lines': lines,
        }

    def get_filter(self, option):
        """Function for get data according to order_by filter """
        data = self.get_filter_data(option)
        filters = {}
        if data.get('report_type') == 'All':
            filters['report_type'] = 'All'
        if data.get('report_type') == 'Today':
            filters['report_type'] = 'Today'
        if data.get('report_type') == 'Yesterday':
            filters['report_type'] = 'Yesterday'
        if data.get('report_type') == 'Last Week':
            filters['report_type'] = 'Last Week'
        if data.get('report_type') == 'This Week':
            filters['report_type'] = 'This Week'
        if data.get('report_type') == 'Last Month':
            filters['report_type'] = 'Last Month'
        if data.get('report_type') == 'This Month':
            filters['report_type'] = 'This Month'
        else:
            filters['report_type'] = 'Custom'
        if data.get('exception') == 'Duplicate Invoices':
            filters['exception'] = 'Duplicate Invoices'
        return filters

    def get_filter_data(self, option):
        """ Function for get filter data in report """
        record = self.env['audit.meter.only.report'].search(
            [('id', '=', option[0])])
        default_filters = {}
        filter_dict = {
            'report_type': record.report_type,
            'exception': record.exception
        }
        filter_dict.update(default_filters)
        return filter_dict

    def get_account_details_lines(self, data):
        """ Function for get report value using sql query """
        report_sub_lines = []
        print(data)
        query = """ """
        # SELECT audit.name, audit.id, category.x_name ->> 'en_US' as category_name,
        #             manufacturer.x_name ->> 'en_US' as manufacturer_name, audit.x_studio_account_number as account_number,
        #             audit.x_studio_serial_number as serial_number, meter_condition.x_name ->> 'en_US' as meter_condition_name,
        #             audit.x_studio_condition_comments as condition_comments
        #             FROM res_partner as audit
        #             LEFT JOIN x_property_category as category on audit.x_studio_category = category.id
        #             LEFT JOIN x_meter_manufacturer as manufacturer on audit.x_studio_meter_manufacturer_1 = manufacturer.id
        #             LEFT JOIN x_meter_condition as meter_condition on audit.x_studio_meter_condition = meter_condition.id
        #             WHERE audit.x_studio_meter_audit = 'true'  and audit.user_id = """ + str(self.env.uid) + """
        #             AND audit.write_date::date = '""" + str(data['date_from']) + """';
        print(query)
        self._cr.execute(query)
        report_by_order_details = self._cr.dictfetchall()
        report_sub_lines.append(report_by_order_details)
        return report_sub_lines

    def _get_report_values(self, data):
        """ Get report values based on the provided data. """
        docs = data['model']
        report_res = self.get_account_details_lines(data)[0]
        return {
            'doc_ids': self.ids,
            'docs': docs,
            'data': report_res,
        }

class CustomPartnerReport(models.AbstractModel):
    _name = 'report.audit_meter_report.report_partner_custom_document'
    _description = 'Custom Partner Report'

    def _get_report_values(self, docids, data=None):
        docs = self.env['res.partner'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'res.partner',
            'docs': docs,
        }
