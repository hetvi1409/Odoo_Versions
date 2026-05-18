from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class TruckFormReport(models.AbstractModel):
    _name = 'report.client_enquiry.client_enquiry_sla_policy_status_report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['client.enquiry.sla.policy.status'].browse([])
        year = fields.Date.today().year
        month = fields.Date.today().month
        start_date = datetime.strptime('0101' + str(year), '%d%m%Y')
        if data['type'] == 'quarterly':
            if data['quarterly_type'] == 'q1':
                start_date = start_date
                end_date = start_date + relativedelta(months=+3, seconds=-1)
                quarter_start_one = start_date
                quarter_end_one = start_date + relativedelta(months=+1, seconds=-1)
                quarter_start_two = start_date + relativedelta(months=+1)
                quarter_end_two = quarter_start_two + relativedelta(months=+1, seconds=-1)
                quarter_start_three = quarter_start_two + relativedelta(months=+1)
                quarter_end_three = quarter_start_three + relativedelta(months=+1, seconds=-1)
            if data['quarterly_type'] == 'q2':
                start_date = start_date + relativedelta(months=+3)
                end_date = start_date + relativedelta(months=+3, seconds=-1)
                quarter_start_one = start_date
                quarter_end_one = start_date + relativedelta(months=+1, seconds=-1)
                quarter_start_two = start_date + relativedelta(months=+1)
                quarter_end_two = quarter_start_two + relativedelta(months=+1, seconds=-1)
                quarter_start_three = quarter_start_two + relativedelta(months=+1)
                quarter_end_three = quarter_start_three + relativedelta(months=+1, seconds=-1)
            if data['quarterly_type'] == 'q3':
                start_date = start_date + relativedelta(months=+6)
                end_date = start_date + relativedelta(months=+3, seconds=-1)
                quarter_start_one = start_date
                quarter_end_one = start_date + relativedelta(months=+1, seconds=-1)
                quarter_start_two = start_date + relativedelta(months=+1)
                quarter_end_two = quarter_start_two + relativedelta(months=+1, seconds=-1)
                quarter_start_three = quarter_start_two + relativedelta(months=+1)
                quarter_end_three = quarter_start_three + relativedelta(months=+1, seconds=-1)
            if data['quarterly_type'] == 'q4':
                start_date = start_date + relativedelta(months=+9)
                end_date = start_date + relativedelta(months=+3, seconds=-1)
                quarter_start_one = start_date
                quarter_end_one = start_date + relativedelta(months=+1, seconds=-1)
                quarter_start_two = start_date + relativedelta(months=+1)
                quarter_end_two = quarter_start_two + relativedelta(months=+1, seconds=-1)
                quarter_start_three = quarter_start_two + relativedelta(months=+1)
                quarter_end_three = quarter_start_three + relativedelta(months=+1, seconds=-1)
            if data['sla_type'] == 'success':
                sql_query = """
                        SELECT
                            policy.sla_number, policy.name, policy.description,
                            COUNT(CASE WHEN sla.reached_datetime >= '""" + str(quarter_start_one) + """' AND sla.reached_datetime <= '""" + str(quarter_end_one) + """' THEN sla.id END) AS count_within_date_range_q1,
                            COUNT(CASE WHEN sla.reached_datetime >= '""" + str(quarter_start_two) + """' AND sla.reached_datetime <= '""" + str(quarter_end_two) + """' THEN sla.id END) AS count_within_date_range_q2,
                            COUNT(CASE WHEN sla.reached_datetime >= '""" + str(quarter_start_three) + """"' AND sla.reached_datetime <= '""" + str(quarter_end_three) + """' THEN sla.id END) AS count_within_date_range_q3,
                            COUNT(sla.id) AS total_count
                        FROM
                            client_enquiry_sla_policy_status AS sla
                        JOIN
                            client_enquiry_sla_policy AS policy ON sla.policy_id = policy.id
                        WHERE
                            sla.reached_datetime >= '""" + str(start_date) + """' AND sla.reached_datetime <= '""" + str(end_date) + """' AND sla.deadline >= sla.reached_datetime 
                        GROUP BY
                            sla.policy_id, policy.name, policy.description, policy.sla_number
                        ORDER BY sla.policy_id ASC;"""
            elif data['sla_type'] == 'failed':
                sql_query = """
                    SELECT
                        policy.sla_number, policy.name, policy.description,
                        COUNT(CASE WHEN sla.reached_datetime >= '""" + str(quarter_start_one) + """' AND sla.reached_datetime <= '""" + str(quarter_end_one) + """' THEN sla.id END) AS count_within_date_range_q1,
                        COUNT(CASE WHEN sla.reached_datetime >= '""" + str(quarter_start_two) + """' AND sla.reached_datetime <= '""" + str(quarter_end_two) + """' THEN sla.id END) AS count_within_date_range_q2,
                        COUNT(CASE WHEN sla.reached_datetime >= '""" + str(quarter_start_three) + """"' AND sla.reached_datetime <= '""" + str(quarter_end_three) + """' THEN sla.id END) AS count_within_date_range_q3,
                        COUNT(sla.id) AS total_count
                    FROM
                        client_enquiry_sla_policy_status AS sla
                    JOIN
                        client_enquiry_sla_policy AS policy ON sla.policy_id = policy.id
                    WHERE
                        sla.reached_datetime >= '""" + str(start_date) + """' AND sla.reached_datetime <= '""" + str(end_date) + """' AND sla.deadline <= sla.reached_datetime 
                    GROUP BY
                        sla.policy_id, policy.name, policy.description, policy.sla_number
                    ORDER BY sla.policy_id ASC;"""
            else:
                sql_query = """
                SELECT
                    policy.sla_number, policy.name, policy.description,
                    COUNT(CASE WHEN sla.create_date >= '""" + str(quarter_start_one) + """' AND sla.create_date <= '""" + str(quarter_end_one) + """' THEN sla.id END) AS count_within_date_range_q1,
                    COUNT(CASE WHEN sla.create_date >= '""" + str(quarter_start_two) + """' AND sla.create_date <= '""" + str(quarter_end_two) + """' THEN sla.id END) AS count_within_date_range_q2,
                    COUNT(CASE WHEN sla.create_date >= '""" + str(quarter_start_three) + """"' AND sla.create_date <= '""" + str(quarter_end_three) + """' THEN sla.id END) AS count_within_date_range_q3,
                    COUNT(sla.id) AS total_count
                FROM
                    client_enquiry_sla_policy_status AS sla
                JOIN
                    client_enquiry_sla_policy AS policy ON sla.policy_id = policy.id
                WHERE
                    sla.create_date >= '""" + str(start_date) + """' AND sla.create_date <= '""" +  str(end_date) + """'
                GROUP BY
                    sla.policy_id, policy.name, policy.description, policy.sla_number
                ORDER BY sla.policy_id ASC;"""
            self.env.cr.execute(sql_query)
            result = self.env.cr.fetchall()
        if data['type'] == 'annually':
            start_date = start_date
            end_date = start_date + relativedelta(years=+1, seconds=-1)
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
                            COUNT(CASE WHEN sla.reached_datetime >= '""" + str(quarter_start_one) + """' AND sla.reached_datetime <= '""" + str(quarter_end_one) + """' THEN sla.id END) AS count_within_date_range_q1,
                            COUNT(CASE WHEN sla.reached_datetime >= '""" + str(quarter_start_two) + """' AND sla.reached_datetime <= '""" + str(quarter_end_two) + """' THEN sla.id END) AS count_within_date_range_q2,
                            COUNT(CASE WHEN sla.reached_datetime >= '""" + str(quarter_start_three) + """' AND sla.reached_datetime <= '""" + str(quarter_end_three) + """' THEN sla.id END) AS count_within_date_range_q3,
                            COUNT(CASE WHEN sla.reached_datetime >= '""" + str(quarter_start_four) + """' AND sla.reached_datetime <= '""" + str(quarter_end_four) + """' THEN sla.id END) AS count_within_date_range_q4,
                            COUNT(sla.id) AS total_count
                            FROM client_enquiry_sla_policy_status AS sla
                            JOIN client_enquiry_sla_policy AS policy ON sla.policy_id = policy.id
                            WHERE sla.reached_datetime >= '""" + str(start_date) + """' AND sla.reached_datetime <= '""" + str(end_date) + """' AND sla.deadline >= sla.reached_datetime
                            GROUP BY sla.policy_id, policy.name, policy.description, policy.sla_number
                            ORDER BY sla.policy_id ASC;"""
            elif data['sla_type'] == 'failed':
                sql_query = """SELECT policy.sla_number, policy.name, policy.description,
                            COUNT(CASE WHEN sla.reached_datetime >= '""" + str(quarter_start_one) + """' AND sla.reached_datetime <= '""" + str(quarter_end_one) + """' THEN sla.id END) AS count_within_date_range_q1,
                            COUNT(CASE WHEN sla.reached_datetime >= '""" + str(quarter_start_two) + """' AND sla.reached_datetime <= '""" + str(quarter_end_two) + """' THEN sla.id END) AS count_within_date_range_q2,
                            COUNT(CASE WHEN sla.reached_datetime >= '""" + str(quarter_start_three) + """' AND sla.reached_datetime <= '""" + str(quarter_end_three) + """' THEN sla.id END) AS count_within_date_range_q3,
                            COUNT(CASE WHEN sla.reached_datetime >= '""" + str(quarter_start_four) + """' AND sla.reached_datetime <= '""" + str(quarter_end_four) + """' THEN sla.id END) AS count_within_date_range_q4,
                            COUNT(sla.id) AS total_count
                            FROM client_enquiry_sla_policy_status AS sla
                            JOIN client_enquiry_sla_policy AS policy ON sla.policy_id = policy.id
                            WHERE sla.reached_datetime >= '""" + str(start_date) + """' AND sla.reached_datetime <= '""" + str(end_date) + """' AND sla.deadline <= sla.reached_datetime
                            GROUP BY sla.policy_id, policy.name, policy.description, policy.sla_number
                            ORDER BY sla.policy_id ASC;"""
            else:
                sql_query = """SELECT policy.sla_number, policy.name, policy.description,
                            COUNT(CASE WHEN sla.create_date >= '""" + str(quarter_start_one) + """' AND sla.create_date <= '""" + str(quarter_end_one) + """' THEN sla.id END) AS count_within_date_range_q1,
                            COUNT(CASE WHEN sla.create_date >= '""" + str(quarter_start_two) + """' AND sla.create_date <= '""" + str(quarter_end_two) + """' THEN sla.id END) AS count_within_date_range_q2,
                            COUNT(CASE WHEN sla.create_date >= '""" + str(quarter_start_three) + """' AND sla.create_date <= '""" + str(quarter_end_three) + """' THEN sla.id END) AS count_within_date_range_q3,
                            COUNT(CASE WHEN sla.create_date >= '""" + str(quarter_start_four) + """' AND sla.create_date <= '""" + str(quarter_end_four) + """' THEN sla.id END) AS count_within_date_range_q4,
                            COUNT(sla.id) AS total_count
                            FROM client_enquiry_sla_policy_status AS sla
                            JOIN client_enquiry_sla_policy AS policy ON sla.policy_id = policy.id
                            WHERE sla.create_date >= '""" + str(start_date) + """' AND sla.create_date <= '""" + str(end_date) + """'
                            GROUP BY sla.policy_id, policy.name, policy.description, policy.sla_number
                            ORDER BY sla.policy_id ASC;"""
            self.env.cr.execute(sql_query)
            result = self.env.cr.fetchall()
        if data['type'] == 'monthly':
            if data['monthly_type'] == 'january':
                start_date = datetime.strptime('0101' + str(year),'%d%m%Y')
                end_date = start_date + relativedelta(months=+1, seconds=-1)
            if data['monthly_type'] == 'february':
                start_date = datetime.strptime('0102' + str(year),'%d%m%Y')
                end_date = start_date + relativedelta(months=+1, seconds=-1)
            elif data['monthly_type'] == 'march':
                start_date = datetime.strptime('0103' + str(year),'%d%m%Y')
                end_date = start_date + relativedelta(months=+1, seconds=-1)
            elif data['monthly_type'] == 'april':
                start_date = datetime.strptime('0104' + str(year),'%d%m%Y')
                end_date = start_date + relativedelta(months=+1, seconds=-1)
            elif data['monthly_type'] == 'may':
                start_date = datetime.strptime('0105' + str(year),'%d%m%Y')
                end_date = start_date + relativedelta(months=+1, seconds=-1)
            elif data['monthly_type'] == 'june':
                start_date = datetime.strptime('0106' + str(year),'%d%m%Y')
                end_date = start_date + relativedelta(months=+1, seconds=-1)
            elif data['monthly_type'] == 'july':
                start_date = datetime.strptime('0107' + str(year),'%d%m%Y')
                end_date = start_date + relativedelta(months=+1, seconds=-1)
            elif data['monthly_type'] == 'august':
                start_date = datetime.strptime('0108' + str(year),'%d%m%Y')
                end_date = start_date + relativedelta(months=+1, seconds=-1)
            elif data['monthly_type'] == 'september':
                start_date = datetime.strptime('0109' + str(year),'%d%m%Y')
                end_date = start_date + relativedelta(months=+1, seconds=-1)
            elif data['monthly_type'] == 'october':
                start_date = datetime.strptime('0110' + str(year),'%d%m%Y')
                end_date = start_date + relativedelta(months=+1, seconds=-1)
            elif data['monthly_type'] == 'november':
                start_date = datetime.strptime('0111' + str(year),'%d%m%Y')
                end_date = start_date + relativedelta(months=+1, seconds=-1)
            elif data['monthly_type'] == 'december':
                start_date = datetime.strptime('0112' + str(year),'%d%m%Y')
                end_date = start_date + relativedelta(months=+1, seconds=-1)
            else:
                start_date = datetime.strptime('01' + str(month) + str(year), '%d%m%Y')
                end_date = start_date + relativedelta(months=+1, seconds=-1)
            if data['sla_type'] == 'success':
                sql_query = """SELECT policy.sla_number, policy.name, policy.description,
                                        COUNT(sla.id) AS total_count
                                    FROM
                                        client_enquiry_sla_policy_status AS sla
                                    JOIN
                                        client_enquiry_sla_policy AS policy ON sla.policy_id = policy.id
                                    WHERE
                                        sla.reached_datetime >= '""" + str(start_date) + """' AND sla.reached_datetime <= '""" + str(end_date) + """' AND sla.deadline >= sla.reached_datetime
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
                                sla.create_date >= '""" + str(start_date) + """' AND sla.create_date <= '""" + str(end_date) + """'
                            GROUP BY
                                sla.policy_id, policy.name, policy.description, policy.sla_number
                            ORDER BY sla.policy_id ASC;
                """
            self.env.cr.execute(sql_query)
            result = self.env.cr.fetchall()
        return {
            'doc_ids': docids,
            'doc_model': 'client.enquiry.sla.policy.status',
            'docs': docs,
            'data': data,
            'result': result,
            'type': data['type'],
            'quarterly_type': data['quarterly_type']
        }
