from odoo import http
from odoo.http import request


class Risk(http.Controller):
    @http.route('/get/risk/data', auth='public', type='json')
    def get_risk_data(self, department_id=None, risk_ids=None):
        if risk_ids:
            if isinstance(risk_ids, list):
                risk_ids = tuple(risk_ids)

            risk_ids = str(risk_ids).rstrip(',)') + ')' if len(risk_ids) == 1 else str(risk_ids)
        query = '''
                SELECT
                    r.id AS risk_id,
                    r.name AS risk_name, c.score AS score,
                    CASE r.main_risk_total_score
                        WHEN 'very_high' THEN 5
                        WHEN 'high' THEN 4
                        WHEN 'medium' THEN 3
                        WHEN 'low' THEN 2
                        WHEN 'very_low' THEN 1
                        ELSE 0
                    END AS main_risk_score_num,
                    CASE r.inherent_risk_total_score
                        WHEN 'very_high' THEN 5
                        WHEN 'high' THEN 4
                        WHEN 'medium' THEN 3
                        WHEN 'low' THEN 2
                        WHEN 'very_low' THEN 1
                        ELSE 0
                    END AS inherent_risk_score_num,
                    CASE r.current_risk_total_score
                        WHEN 'very_high' THEN 5
                        WHEN 'high' THEN 4
                        WHEN 'medium' THEN 3
                        WHEN 'low' THEN 2
                        WHEN 'very_low' THEN 1
                        ELSE 0
                    END AS current_risk_score_num,
                    CASE r.residual_risk_total_score
                        WHEN 'very_high' THEN 5
                        WHEN 'high' THEN 4
                        WHEN 'medium' THEN 3
                        WHEN 'low' THEN 2
                        WHEN 'very_low' THEN 1
                        ELSE 0
                    END AS residual_risk_score_num,
                    d.name AS department_name,
                    t.name AS risk_type_name,
                    r.create_date,
                    r.write_date
                FROM oi_risk_management_risk AS r
                LEFT JOIN hr_department AS d ON r.department_id = d.id
                LEFT JOIN risk_type AS t ON r.risk_type_id = t.id
				LEFT JOIN oi_risk_management_risk_criteria as c ON r.control_effectiveness_id = c.id
            '''
        if department_id:
            query += f" WHERE r.department_id = {int(department_id)}"
            if risk_ids:
                query += f" AND r.id in {risk_ids}"
        else:
            if risk_ids:
                query += f" WHERE r.id in {risk_ids}"
        query += " ORDER BY main_risk_score_num DESC LIMIT 10;"
        request._cr.execute(query)
        data = request._cr.dictfetchall()
        return {'risk': data}

    @http.route('/risk/top', auth='public', type='json')
    def get_risk_top(self, department_id=None, risk_ids=None):
        """"""
        if risk_ids:
            if isinstance(risk_ids, list):
                risk_ids = tuple(risk_ids)

            risk_ids = str(risk_ids).rstrip(',)') + ')' if len(risk_ids) == 1 else str(risk_ids)
        query = '''SELECT
                r.id AS risk_id,
                r.name AS risk_name,

                CASE r.main_risk_total_score
                    WHEN 'very_high' THEN 5
                    WHEN 'high' THEN 4
                    WHEN 'medium' THEN 3
                    WHEN 'low' THEN 2
                    WHEN 'very_low' THEN 1
                    ELSE 0
                END AS main_risk_score_num

            FROM oi_risk_management_risk AS r
           
			 '''
        if department_id:
            query += f" WHERE r.department_id = {int(department_id)}"
            if risk_ids:
                query += f" AND r.id in {risk_ids}"
        else:
            if risk_ids:
                query += f" WHERE r.id in {risk_ids}"
        query += " ORDER BY main_risk_score_num DESC LIMIT 10;"

        request._cr.execute(query)
        top_risk = request._cr.dictfetchall()
        score = [record.get('main_risk_score_num') for record in top_risk]
        risk = [record.get('risk_name') for record in top_risk]
        return [score, risk]

    @http.route('/get/risk/departments', auth='public', type='json')
    def get_departments(self):
        request._cr.execute("SELECT id, name FROM hr_department ORDER BY name;")
        departments = request._cr.dictfetchall()
        return {'departments': departments}

    @http.route('/get/risk/options', type='json', auth='user')
    def get_risk_options(self):
        risks = request.env['oi_risk_management.risk'].search_read(
            [], ['id', 'name']
        )
        return {'risks': [{'risk_id': r['id'], 'risk_name': r['name']} for r in
                          risks]}

