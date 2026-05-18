import json
from odoo import http
from odoo.http import content_disposition, request
from odoo.tools import html_escape


class XLSXReport(http.Controller):
    @http.route('/budget_xlsx_reports', type='http', auth='user', methods=['POST'],
                csrf=False)
    def budget_report_xlsx(self, model, options, output_format, report_name):
        uid = request.session.uid
        report_obj = request.env[model].with_user(uid)
        options = json.loads(options)
        try:
            if output_format == 'budget_xlsx':
                response = request.make_response(
                    None, headers=[('Content-Type', 'application/vnd.ms-excel'),
                                   ('Content-Disposition',
                                    content_disposition(report_name + '.xlsx'))])
                report_obj.get_xlsx_report(options, response)
                return response
        except Exception as event:
            serialize = http.serialize_exception(event)
            error = {
                'code': 200,
                'message': 'Odoo Server Error',
                'data': serialize
            }
            return request.make_response(html_escape(json.dumps(error)))
