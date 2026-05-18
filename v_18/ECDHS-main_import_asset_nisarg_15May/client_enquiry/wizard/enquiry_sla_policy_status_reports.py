import io
import json
from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo.tools import date_utils
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter
from odoo import fields, models, _


class EnquirySLAPolicyStatusReports(models.TransientModel):
    """SLA policy reporting"""
    _name = 'enquiry.sla.policy.status'
    _description = "SLA policy status report"

    type = fields.Selection([('annually', 'Annually'),
                             ('quarterly', 'Quarterly'),
                             ('monthly', 'Monthly'), ], default='quarterly')
    quarterly_type = fields.Selection([('q1', 'Q1'), ('q2', 'Q2'),
                                       ('q3', 'Q3'), ('q4', 'Q4')], default='q1')
    sla_type = fields.Selection([('success', 'Success'),
                                 ('failed', 'Failed'),],
                                string="SLA Status Type")
    monthly_type = fields.Selection([('january', 'January'),
                                     ('february', 'February'),
                                     ('march', 'March'), ('april', 'April'),
                                     ('may', 'May'),
                                     ('june', 'June'),
                                     ('july', 'July'),
                                     ('august', 'August'),
                                     ('september', 'September'),
                                     ('october', 'October'),
                                     ('november', 'November'),
                                     ('december', 'December')], string="Month")

    def action_print(self):
        data = {
                'type': self.type,
                'quarterly_type': self.quarterly_type,
                'sla_type': self.sla_type,
                'monthly_type': self.monthly_type
                }
        return self.env.ref('client_enquiry.action_report_client_enquiry_sla_policy_status_report').report_action(
            None, data=data)

    def action_print_xlsx(self):
        data = {
            'type': self.type,
            'quarterly_type': self.quarterly_type,
            'sla_type': self.sla_type,
            'monthly_type': self.monthly_type
        }
        return {
            'type': 'ir.actions.report',
            'data': {'model': 'enquiry.sla.policy.status',
                     'options': json.dumps(data,
                                           default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'report_name': 'SLS Report',
                     },
            'report_type': 'xlsx',
        }

    def get_xlsx_report(self, data, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet()
        cell_format = workbook.add_format({'font_size': 12, 'align': 'center'})
        head = workbook.add_format({'font_size': 18, 'align': 'center', 'color': '#00008B', 'bold': True})
        year = fields.Date.today().year
        month = fields.Date.today().month
        print(year, data)
        txt = workbook.add_format({'font_size': '9px', })
        start_date = datetime.strptime('0101' + str(year), '%d%m%Y')
        if data['type'] == 'annually':
            sheet.merge_range('A1:H2',  _("Service Standards"), head)
            sheet.write('A4', 'SLS', cell_format)
            sheet.write('B4', 'Core Service', cell_format)
            sheet.write('C4', 'Service Level Standard Target', cell_format)
            sheet.write('D4', 'Quarter 1', cell_format)
            sheet.write('E4', 'Quarter 2', cell_format)
            sheet.write('F4', 'Quarter 3', cell_format)
            sheet.write('G4', 'Quarter 4', cell_format)
            sheet.write('H4', 'YTD Total', cell_format)
            start_date = start_date
            end_date = start_date + relativedelta(years=+1, seconds=-1)
            print(start_date, end_date, 'start_date')
            quarter_start_one = start_date
            quarter_end_one = start_date + relativedelta(months=+3, seconds=-1)
            quarter_start_two = start_date + relativedelta(months=+3)
            quarter_end_two = quarter_start_two + relativedelta(months=+3,
                                                                seconds=-1)
            quarter_start_three = quarter_start_two + relativedelta(months=+3)
            quarter_end_three = quarter_start_three + relativedelta(months=+3,
                                                                    seconds=-1)
            quarter_start_four = quarter_start_three + relativedelta(months=+3)
            quarter_end_four = quarter_start_four + relativedelta(months=+3,
                                                                  seconds=-1)
            if data['sla_type'] == 'success':
                sql_query = """SELECT policy.sla_number, policy.name, policy.description,
                                        COUNT(CASE WHEN sla.reached_datetime >= '""" + str(
                    quarter_start_one) + """' AND sla.reached_datetime <= '""" + str(
                    quarter_end_one) + """' THEN sla.id END) AS count_within_date_range_q1,
                                        COUNT(CASE WHEN sla.reached_datetime >= '""" + str(
                    quarter_start_two) + """' AND sla.reached_datetime <= '""" + str(
                    quarter_end_two) + """' THEN sla.id END) AS count_within_date_range_q2,
                                        COUNT(CASE WHEN sla.reached_datetime >= '""" + str(
                    quarter_start_three) + """' AND sla.reached_datetime <= '""" + str(
                    quarter_end_three) + """' THEN sla.id END) AS count_within_date_range_q3,
                                        COUNT(CASE WHEN sla.reached_datetime >= '""" + str(
                    quarter_start_four) + """' AND sla.reached_datetime <= '""" + str(
                    quarter_end_four) + """' THEN sla.id END) AS count_within_date_range_q4,
                                        COUNT(sla.id) AS total_count
                                        FROM client_enquiry_sla_policy_status AS sla
                                        JOIN client_enquiry_sla_policy AS policy ON sla.policy_id = policy.id
                                        WHERE sla.reached_datetime >= '""" + str(
                    start_date) + """' AND sla.reached_datetime <= '""" + str(
                    end_date) + """' AND sla.deadline >= sla.reached_datetime
                                        GROUP BY sla.policy_id, policy.name, policy.description, policy.sla_number
                                        ORDER BY sla.policy_id ASC;"""
            elif data['sla_type'] == 'failed':
                sql_query = """SELECT policy.sla_number, policy.name, policy.description,
                                        COUNT(CASE WHEN sla.reached_datetime >= '""" + str(
                    quarter_start_one) + """' AND sla.reached_datetime <= '""" + str(
                    quarter_end_one) + """' THEN sla.id END) AS count_within_date_range_q1,
                                        COUNT(CASE WHEN sla.reached_datetime >= '""" + str(
                    quarter_start_two) + """' AND sla.reached_datetime <= '""" + str(
                    quarter_end_two) + """' THEN sla.id END) AS count_within_date_range_q2,
                                        COUNT(CASE WHEN sla.reached_datetime >= '""" + str(
                    quarter_start_three) + """' AND sla.reached_datetime <= '""" + str(
                    quarter_end_three) + """' THEN sla.id END) AS count_within_date_range_q3,
                                        COUNT(CASE WHEN sla.reached_datetime >= '""" + str(
                    quarter_start_four) + """' AND sla.reached_datetime <= '""" + str(
                    quarter_end_four) + """' THEN sla.id END) AS count_within_date_range_q4,
                                        COUNT(sla.id) AS total_count
                                        FROM client_enquiry_sla_policy_status AS sla
                                        JOIN client_enquiry_sla_policy AS policy ON sla.policy_id = policy.id
                                        WHERE sla.reached_datetime >= '""" + str(
                    start_date) + """' AND sla.reached_datetime <= '""" + str(
                    end_date) + """' AND sla.deadline <= sla.reached_datetime
                                        GROUP BY sla.policy_id, policy.name, policy.description, policy.sla_number
                                        ORDER BY sla.policy_id ASC;"""
            else:
                sql_query = """SELECT policy.sla_number, policy.name, policy.description,
                                        COUNT(CASE WHEN sla.create_date >= '""" + str(
                    quarter_start_one) + """' AND sla.create_date <= '""" + str(
                    quarter_end_one) + """' THEN sla.id END) AS count_within_date_range_q1,
                                        COUNT(CASE WHEN sla.create_date >= '""" + str(
                    quarter_start_two) + """' AND sla.create_date <= '""" + str(
                    quarter_end_two) + """' THEN sla.id END) AS count_within_date_range_q2,
                                        COUNT(CASE WHEN sla.create_date >= '""" + str(
                    quarter_start_three) + """' AND sla.create_date <= '""" + str(
                    quarter_end_three) + """' THEN sla.id END) AS count_within_date_range_q3,
                                        COUNT(CASE WHEN sla.create_date >= '""" + str(
                    quarter_start_four) + """' AND sla.create_date <= '""" + str(
                    quarter_end_four) + """' THEN sla.id END) AS count_within_date_range_q4,
                                        COUNT(sla.id) AS total_count
                                        FROM client_enquiry_sla_policy_status AS sla
                                        JOIN client_enquiry_sla_policy AS policy ON sla.policy_id = policy.id
                                        WHERE sla.create_date >= '""" + str(
                    start_date) + """' AND sla.create_date <= '""" + str(
                    end_date) + """'
                                        GROUP BY sla.policy_id, policy.name, policy.description, policy.sla_number
                                        ORDER BY sla.policy_id ASC;"""
            print(sql_query)
            self.env.cr.execute(sql_query)
            result = self.env.cr.fetchall()
            row = 4
            col = 0
            for res in result:
                sheet.write(row, col, res[0], txt)
                sheet.write(row, col + 1, res[1], txt)
                sheet.write(row, col + 2, res[2], txt)
                sheet.write(row, col + 3, res[3], txt)
                sheet.write(row, col + 4, res[4], txt)
                sheet.write(row, col + 5, res[5], txt)
                sheet.write(row, col + 6, res[6], txt)
                sheet.write(row, col + 7, res[7], txt)
                # sheet.write(row, col + 10, res[7], txt)
                row += 1
        if data['type'] == 'quarterly':
            sheet.merge_range('A1:G2', _("Service Standards"), head)
            sheet.write('A4', 'SLS', cell_format)
            sheet.write('B4', 'Core Service', cell_format)
            sheet.write('C4', 'Service Level Standard Target', cell_format)
            if data['quarterly_type'] == 'q1':
                sheet.write('D4', 'Jan', cell_format)
                sheet.write('E4', 'Feb', cell_format)
                sheet.write('F4', 'Mar', cell_format)
                sheet.write('G4', 'Q1 Actual', cell_format)
                start_date = start_date
                end_date = start_date + relativedelta(months=+3, seconds=-1)
                print(end_date)
                quarter_start_one = start_date
                quarter_end_one = start_date + relativedelta(months=+1,
                                                             seconds=-1)
                quarter_start_two = start_date + relativedelta(months=+1)
                quarter_end_two = quarter_start_two + relativedelta(months=+1,
                                                                    seconds=-1)
                quarter_start_three = quarter_start_two + relativedelta(
                    months=+1)
                quarter_end_three = quarter_start_three + relativedelta(
                    months=+1, seconds=-1)
            if data['quarterly_type'] == 'q2':
                sheet.write('D4', 'Apr', cell_format)
                sheet.write('E4', 'May', cell_format)
                sheet.write('F4', 'Jun', cell_format)
                sheet.write('G4', 'Q2 Actual', cell_format)
                start_date = start_date + relativedelta(months=+3)
                end_date = start_date + relativedelta(months=+3, seconds=-1)
                print(end_date)
                quarter_start_one = start_date
                quarter_end_one = start_date + relativedelta(months=+1,
                                                             seconds=-1)
                quarter_start_two = start_date + relativedelta(months=+1)
                quarter_end_two = quarter_start_two + relativedelta(months=+1,
                                                                    seconds=-1)
                quarter_start_three = quarter_start_two + relativedelta(
                    months=+1)
                quarter_end_three = quarter_start_three + relativedelta(
                    months=+1, seconds=-1)
            if data['quarterly_type'] == 'q3':
                sheet.write('D4', 'Jul', cell_format)
                sheet.write('E4', 'Aug', cell_format)
                sheet.write('F4', 'Sep', cell_format)
                sheet.write('G4', 'Q3 Actual', cell_format)
                start_date = start_date + relativedelta(months=+6)
                end_date = start_date + relativedelta(months=+3, seconds=-1)
                print(end_date)
                quarter_start_one = start_date
                quarter_end_one = start_date + relativedelta(months=+1,
                                                             seconds=-1)
                quarter_start_two = start_date + relativedelta(months=+1)
                quarter_end_two = quarter_start_two + relativedelta(months=+1,
                                                                    seconds=-1)
                quarter_start_three = quarter_start_two + relativedelta(
                    months=+1)
                quarter_end_three = quarter_start_three + relativedelta(
                    months=+1, seconds=-1)
            if data['quarterly_type'] == 'q4':
                sheet.write('D4', 'Oct', cell_format)
                sheet.write('E4', 'Nov', cell_format)
                sheet.write('F4', 'Dec', cell_format)
                sheet.write('G4', 'Q4 Actual', cell_format)
                start_date = start_date + relativedelta(months=+9)
                end_date = start_date + relativedelta(months=+3, seconds=-1)
                print(end_date)
                quarter_start_one = start_date
                quarter_end_one = start_date + relativedelta(months=+1,
                                                             seconds=-1)
                quarter_start_two = start_date + relativedelta(months=+1)
                quarter_end_two = quarter_start_two + relativedelta(months=+1,
                                                                    seconds=-1)
                quarter_start_three = quarter_start_two + relativedelta(
                    months=+1)
                quarter_end_three = quarter_start_three + relativedelta(
                    months=+1, seconds=-1)
            if data['sla_type'] == 'success':
                sql_query = """
                        SELECT
                            policy.sla_number, policy.name, policy.description,
                            COUNT(CASE WHEN sla.reached_datetime >= '""" + str(
                    quarter_start_one) + """' AND sla.reached_datetime <= '""" + str(
                    quarter_end_one) + """' THEN sla.id END) AS count_within_date_range_q1,
                            COUNT(CASE WHEN sla.reached_datetime >= '""" + str(
                    quarter_start_two) + """' AND sla.reached_datetime <= '""" + str(
                    quarter_end_two) + """' THEN sla.id END) AS count_within_date_range_q2,
                            COUNT(CASE WHEN sla.reached_datetime >= '""" + str(
                    quarter_start_three) + """"' AND sla.reached_datetime <= '""" + str(
                    quarter_end_three) + """' THEN sla.id END) AS count_within_date_range_q3,
                            COUNT(sla.id) AS total_count
                        FROM
                            client_enquiry_sla_policy_status AS sla
                        JOIN
                            client_enquiry_sla_policy AS policy ON sla.policy_id = policy.id
                        WHERE
                            sla.reached_datetime >= '""" + str(
                    start_date) + """' AND sla.reached_datetime <= '""" + str(
                    end_date) + """' AND sla.deadline >= sla.reached_datetime 
                        GROUP BY
                            sla.policy_id, policy.name, policy.description, policy.sla_number
                        ORDER BY sla.policy_id ASC;"""
            elif data['sla_type'] == 'failed':
                sql_query = """
                    SELECT
                        policy.sla_number, policy.name, policy.description,
                        COUNT(CASE WHEN sla.reached_datetime >= '""" + str(
                    quarter_start_one) + """' AND sla.reached_datetime <= '""" + str(
                    quarter_end_one) + """' THEN sla.id END) AS count_within_date_range_q1,
                        COUNT(CASE WHEN sla.reached_datetime >= '""" + str(
                    quarter_start_two) + """' AND sla.reached_datetime <= '""" + str(
                    quarter_end_two) + """' THEN sla.id END) AS count_within_date_range_q2,
                        COUNT(CASE WHEN sla.reached_datetime >= '""" + str(
                    quarter_start_three) + """"' AND sla.reached_datetime <= '""" + str(
                    quarter_end_three) + """' THEN sla.id END) AS count_within_date_range_q3,
                        COUNT(sla.id) AS total_count
                    FROM
                        client_enquiry_sla_policy_status AS sla
                    JOIN
                        client_enquiry_sla_policy AS policy ON sla.policy_id = policy.id
                    WHERE
                        sla.reached_datetime >= '""" + str(
                    start_date) + """' AND sla.reached_datetime <= '""" + str(
                    end_date) + """' AND sla.deadline <= sla.reached_datetime 
                    GROUP BY
                        sla.policy_id, policy.name, policy.description, policy.sla_number
                    ORDER BY sla.policy_id ASC;"""
            else:
                sql_query = """
                SELECT
                    policy.sla_number, policy.name, policy.description,
                    COUNT(CASE WHEN sla.create_date >= '""" + str(
                    quarter_start_one) + """' AND sla.create_date <= '""" + str(
                    quarter_end_one) + """' THEN sla.id END) AS count_within_date_range_q1,
                    COUNT(CASE WHEN sla.create_date >= '""" + str(
                    quarter_start_two) + """' AND sla.create_date <= '""" + str(
                    quarter_end_two) + """' THEN sla.id END) AS count_within_date_range_q2,
                    COUNT(CASE WHEN sla.create_date >= '""" + str(
                    quarter_start_three) + """"' AND sla.create_date <= '""" + str(
                    quarter_end_three) + """' THEN sla.id END) AS count_within_date_range_q3,
                    COUNT(sla.id) AS total_count
                FROM
                    client_enquiry_sla_policy_status AS sla
                JOIN
                    client_enquiry_sla_policy AS policy ON sla.policy_id = policy.id
                WHERE
                    sla.create_date >= '""" + str(
                    start_date) + """' AND sla.create_date <= '""" + str(
                    end_date) + """'
                GROUP BY
                    sla.policy_id, policy.name, policy.description, policy.sla_number
                ORDER BY sla.policy_id ASC;"""
            print(sql_query)
            self.env.cr.execute(sql_query)
            result = self.env.cr.fetchall()
            row = 4
            col = 0
            for res in result:
                sheet.write(row, col, res[0], txt)
                sheet.write(row, col + 1, res[1], txt)
                sheet.write(row, col + 2, res[2], txt)
                sheet.write(row, col + 3, res[3], txt)
                sheet.write(row, col + 4, res[4], txt)
                sheet.write(row, col + 5, res[5], txt)
                sheet.write(row, col + 6, res[6], txt)
                row += 1
        if data['type'] == 'monthly':
            start_date = start_date
            end_date = start_date + relativedelta(years=+1, seconds=-1)
            sheet.merge_range('A1:D2', _("Service Standards"), head)
            sheet.write('A4', 'SLS', cell_format)
            sheet.write('B4', 'Core Service', cell_format)
            sheet.write('C4', 'Service Level Standard Target', cell_format)
            sheet.write('D4', 'Monthly', cell_format)
            if data['monthly_type'] == 'january':
                start_date = datetime.strptime('0101' + str(year), '%d%m%Y')
                end_date = start_date + relativedelta(months=+1, seconds=-1)
            if data['monthly_type'] == 'february':
                start_date = datetime.strptime('0102' + str(year), '%d%m%Y')
                end_date = start_date + relativedelta(months=+1, seconds=-1)
            elif data['monthly_type'] == 'march':
                start_date = datetime.strptime('0103' + str(year), '%d%m%Y')
                end_date = start_date + relativedelta(months=+1, seconds=-1)
            elif data['monthly_type'] == 'april':
                start_date = datetime.strptime('0104' + str(year), '%d%m%Y')
                end_date = start_date + relativedelta(months=+1, seconds=-1)
            elif data['monthly_type'] == 'may':
                start_date = datetime.strptime('0105' + str(year), '%d%m%Y')
                end_date = start_date + relativedelta(months=+1, seconds=-1)
            elif data['monthly_type'] == 'june':
                start_date = datetime.strptime('0106' + str(year), '%d%m%Y')
                end_date = start_date + relativedelta(months=+1, seconds=-1)
            elif data['monthly_type'] == 'july':
                start_date = datetime.strptime('0107' + str(year), '%d%m%Y')
                end_date = start_date + relativedelta(months=+1, seconds=-1)
            elif data['monthly_type'] == 'august':
                start_date = datetime.strptime('0108' + str(year), '%d%m%Y')
                end_date = start_date + relativedelta(months=+1, seconds=-1)
            elif data['monthly_type'] == 'september':
                start_date = datetime.strptime('0109' + str(year), '%d%m%Y')
                end_date = start_date + relativedelta(months=+1, seconds=-1)
            elif data['monthly_type'] == 'october':
                start_date = datetime.strptime('0110' + str(year), '%d%m%Y')
                end_date = start_date + relativedelta(months=+1, seconds=-1)
            elif data['monthly_type'] == 'november':
                start_date = datetime.strptime('0111' + str(year), '%d%m%Y')
                end_date = start_date + relativedelta(months=+1, seconds=-1)
            elif data['monthly_type'] == 'december':
                start_date = datetime.strptime('0112' + str(year), '%d%m%Y')
                end_date = start_date + relativedelta(months=+1, seconds=-1)
            else:
                start_date = datetime.strptime('01' + str(month) + str(year),
                                               '%d%m%Y')
                end_date = start_date + relativedelta(months=+1, seconds=-1)
            if data['sla_type'] == 'success':
                sql_query = """SELECT policy.sla_number, policy.name, policy.description,
                                        COUNT(sla.id) AS total_count
                                    FROM
                                        client_enquiry_sla_policy_status AS sla
                                    JOIN
                                        client_enquiry_sla_policy AS policy ON sla.policy_id = policy.id
                                    WHERE
                                        sla.reached_datetime >= '""" + str(
                    start_date) + """' AND sla.reached_datetime <= '""" + str(
                    end_date) + """' AND sla.deadline >= sla.reached_datetime
                                    GROUP BY
                                        sla.policy_id, policy.name, policy.description, policy.sla_number
                                    ORDER BY sla.policy_id ASC;
                        """
            if data['sla_type'] == 'failed':
                sql_query = """SELECT
                                        policy.sla_number, policy.name, policy.description,
                                        COUNT(sla.id) AS total_count
                                    FROM
                                        client_enquiry_sla_policy_status AS sla
                                    JOIN
                                        client_enquiry_sla_policy AS policy ON sla.policy_id = policy.id
                                    WHERE
                                        sla.reached_datetime >= '""" + str(
                    start_date) + """' AND sla.reached_datetime <= '""" + str(
                    end_date) + """' AND sla.deadline <= sla.reached_datetime
                                    GROUP BY
                                        sla.policy_id, policy.name, policy.description, policy.sla_number
                                    ORDER BY sla.policy_id ASC;
                        """
            else:
                sql_query = """SELECT
                                policy.sla_number, policy.name, policy.description,
                                COUNT(sla.id) AS total_count
                            FROM
                                client_enquiry_sla_policy_status AS sla
                            JOIN
                                client_enquiry_sla_policy AS policy ON sla.policy_id = policy.id
                            WHERE
                                sla.create_date >= '""" + str(
                    start_date) + """' AND sla.create_date <= '""" + str(
                    end_date) + """'
                            GROUP BY
                                sla.policy_id, policy.name, policy.description, policy.sla_number
                            ORDER BY sla.policy_id ASC;
                """
            self.env.cr.execute(sql_query)
            result = self.env.cr.fetchall()
            row = 4
            col = 0
            for res in result:
                sheet.write(row, col, res[0], txt)
                sheet.write(row, col + 1, res[1], txt)
                sheet.write(row, col + 2, res[2], txt)
                sheet.write(row, col + 3, res[3], txt)
                row += 1
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()

