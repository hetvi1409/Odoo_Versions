
from odoo import api, fields, models


class CemeteryBurialReport(models.Model):
    _name = "cemetery.burial.report"
    _description = "Total Burial Per Cemetery"
    _auto = False

    cemetery_id = fields.Many2one('cemetery.cemetery', string="Cemetery", readonly=True)
    application_id = fields.Many2one('cemetery.application', string="Application", readonly=True)
    burial_total_count = fields.Integer(string="Total Burial Count")
    submitted_burial_total_count = fields.Integer(string="Total Submitted Burial Count")
    verified_burial_total_count = fields.Integer(string="Total Verified Burial Count")
    approved_burial_total_count = fields.Integer(string="Total Approved Burial Count")
    rejected_burial_total_count = fields.Integer(string="Total Rejected Burial Count")
    date_of_birth = fields.Date(string="Date of Birth")
    age = fields.Float(string="Age")

    @property
    def _table_query(self):
        query = """SELECT cemetery.name AS cemetery_name, cemetery.id as cemetery_id, cemetery.id as id,
                COUNT(application.id) AS burial_total_count, 
                SUM(CASE WHEN application.state = 'submitted' THEN 1 ELSE 0 END) 
                AS submitted_burial_total_count, 
                SUM(CASE WHEN application.state = 'verified' THEN 1 ELSE 0 END) 
                AS verified_burial_total_count, 
                SUM(CASE WHEN application.state = 'approved' THEN 1 ELSE 0 END) 
                AS approved_burial_total_count, 
                SUM(CASE WHEN application.state = 'rejected' THEN 1 ELSE 0 END) 
                AS rejected_burial_total_count, application.id as application_id,
                application.date_of_birth,
                AVG(EXTRACT(YEAR FROM AGE(application.date_of_birth))) AS age
                FROM cemetery_cemetery cemetery
                LEFT JOIN cemetery_application application ON
                 (cemetery.id = application.cemetery_id and interment_type = 'burial')
                GROUP BY cemetery.name,cemetery.id, application.id, application.date_of_birth"""
        return query