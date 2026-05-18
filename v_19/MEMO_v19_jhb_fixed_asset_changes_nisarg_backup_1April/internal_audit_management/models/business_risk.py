# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import base64
from werkzeug import urls
import io
import json
import xlsxwriter
from odoo.tools import date_utils




class BusinessRisk(models.Model):
    _name = "business.risk"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Business Risk"
    _rec_name = "name"

    name = fields.Char(string='Risk ID', default='New', tracking=True)
    summary = fields.Char(string='Title', tracking=True)
    description = fields.Text(string='Risk Description')
    owner = fields.Many2one('res.users', string='Owner', tracking=True)
    probability = fields.Selection([('low', 'Low'), ('low-medium', 'Low Medium'), ('medium', 'Medium'),
                                    ('medium-high', 'Medium High'), ('high', 'High')], string="Probability",
                                    tracking=True, default='low', required=True)
    impact = fields.Selection([('low', 'Low'), ('low-medium', 'Low Medium'), ('medium', 'Medium'),
                                    ('medium-high', 'Medium High'), ('high', 'High')], string="Impact",
                                    tracking=True, default='low', required=True)
    severity = fields.Char(string="Risk Severity", compute='_compute_severity')
    risk_score = fields.Float(string="Risk Score", compute='_compute_severity')

    action = fields.Text(string='Mitigation Actions', tracking=True)
    status = fields.Selection([ ('undetermined', 'Undetermined'),
                                ('mitigated', 'Mitigated'),
                                ('accepted', 'Accepted'),
                                ('transferred', 'Transferred')],
                                 string="Risk Status", default="undetermined", required=True, tracking=True)
    last_date = fields.Date(string='Previous Review')
    next_date = fields.Date(string='Next Review')
    solution = fields.Text(string='Solution', tracking=True)

    category = fields.Many2many('risk.category', string="Category Tag")
    # audit_universe_entity_ids = fields.Many2many('audit.universe.entity', string="Audit Universe")
    inherent_risk_score = fields.Float(string='Inherent Risk Score')
    control_effectiveness = fields.Selection([
        ('high_effectiveness', 'High Effectiveness'),
        ('moderate_effectiveness', 'Moderate Effectiveness'),
        ('low_effectiveness', 'Low Effectiveness'),
        ('ineffective', 'Ineffective')], string="Control Effectiveness")
    residual_risk_score = fields.Float(string='Residual Risk Score')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            sequence_code = 'business.risk'
            vals['name'] = self.env['ir.sequence'].next_by_code(
                sequence_code)
        res = super(BusinessRisk, self).create(vals_list)
        return res

    # @api.model
    # def create(self, vals):
    #     vals['name'] = self.env['ir.sequence'].next_by_code('business.risk')
    #     return super(BusinessRisk, self).create(vals)

    @api.depends('impact', 'probability')
    def _compute_severity(self):
        severity = {
            2: "Low",
            3: "Low",
            4: "Low",
            5: "Low-medium",
            6: "Medium",
            7: "Medium-high",
            8: "High",
            9: "High",
            10: "High",
        }
        vals = {
            "low": 1,
            "low-medium": 2,
            "medium": 3,
            "medium-high": 4,
            "high": 5,
        }
        for rec in self:
            # look up numeric values
            impact = vals[rec.impact]
            prob = vals[rec.probability]

            # calculate the severity
            sevval = impact + prob

            # increase severity under these conditions
            if impact == 3 and prob == 1:
                sevval += 1
            elif impact == 3 and prob == 5:
                sevval -= 1

            sev = severity[sevval]
            rec.severity = sev
            rec.risk_score = sevval
        return

    def action_excel_risk_report(self):
        plan = self.id
        data = {
            'model_id': self.id,
            'method': plan,
             'plan' :self.id

        }
        return {
            'type': 'ir.actions.report',
            'data': {'model': self._name,
                     'options': json.dumps(data,
                                           default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'report_name': 'Risk',
                     },
            'report_type': 'xlsx',
        }

    def get_xlsx_report(self, data, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet("Risk Report")

        # Formatting
        head_format = workbook.add_format({'align': 'center', 'bold': True, 'font_size': 20})
        sub_head_format = workbook.add_format({'align': 'center', 'bold': True, 'font_size': 11})
        text_format = workbook.add_format({'align': 'center', 'font_size': 10, 'text_wrap': True})
        date_format = workbook.add_format({'num_format': 'd-m-yyyy', 'align': 'center'})

        # Set Column Widths and Row Heights
        sheet.set_column('A:A', 5)  # Adjust for logo
        sheet.set_column('B:I', 15)
        sheet.set_column('J:K', 12)
        sheet.set_row(0, 40)  # Increase row height for logo

        # Insert Company Logo (Left Side, Bigger & Correctly Aligned)
        company_logo = self.env.company.logo
        if company_logo:
            try:
                image_data = io.BytesIO(base64.b64decode(company_logo))
                sheet.insert_image('A1', "image.png", {
                    'image_data': image_data,
                    'x_scale': 1.5,  # Increase size
                    'y_scale': 1.5,
                    'positioning': 1  # Move and resize with cells
                })
            except Exception as e:
                sheet.write('A1', "Logo Error", text_format)  # Error placeholder

        # Merge Title in Center
        sheet.merge_range('D1:J1', "Business Risk Report", head_format)

        # Insert Report Date (Top Right)
        sheet.write('K1', "Report Date:", text_format)
        sheet.write('L1', fields.Date.today(), date_format)

        # Table Headers
        headers = ["Owner", "Probability", "Impact", "Risk Severity", "Risk Status", "Last Date", "Next Review"]
        for col, header in enumerate(headers, start=1):
            sheet.write(6, col, header, sub_head_format)  # Shift down for proper spacing

        # Fetch Data
        plan = self.env[self._name].browse(int(data.get('plan', 0)))
        if plan.exists():
            row = 8
            sheet.write(row, 1, plan.owner.name if plan.owner else "N/A", text_format)
            sheet.write(row, 2, plan.probability if plan.probability else "Unknown", text_format)
            sheet.write(row, 3, plan.impact if plan.impact else "Unknown", text_format)
            sheet.write(row, 4, plan.severity if plan.severity else "Unknown", text_format)
            sheet.write(row, 5, plan.status if plan.status else "Not Defined", text_format)
            sheet.write(row, 6, plan.last_date if plan.last_date else "N/A", date_format)
            sheet.write(row, 7, plan.next_date if plan.next_date else "N/A", date_format)
        else:
            sheet.write(8, 1, "No Data Found", text_format)

        # Finalize Workbook
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
        # output = io.BytesIO()
        # workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        # sheet = workbook.add_worksheet()
        #
        # plan = self.env[self._name].browse(int(data['plan']))
        # cell_format = workbook.add_format(
        #     {'font_size': '12px', 'align': 'center'})
        # head = workbook.add_format(
        #     {'align': 'center', 'bold': True, 'font_size': '20px'})
        # small_head = workbook.add_format(
        #     {'align': 'center', 'font_size': '11px'})
        # txt = workbook.add_format({'font_size': '10px', 'align': 'center',
        #                            'valign': 'vcenter', 'text_wrap': True})
        # date = workbook.add_format({'num_format': 'd-m-yyyy'})
        # sheet.set_column(1, 11, 12, txt)
        #
        # image_data = io.BytesIO(base64.b64decode(self.env.company.logo))
        # sheet.insert_image('J2', "image.png", {
        #     'image_data': image_data,
        #     'x_scale': 0.5,  # Scale image if needed
        #     'y_scale': 0.5,
        #     'positioning': 1  # Move and resize with cells
        # })
        # sheet.write('J1', "Report Date", txt)
        # sheet.write('K1', fields.Date.today(), date)
        #
        # sheet.merge_range('B2:I3', plan.summary, head)
        # sheet.write('B5', "Owner", small_head)
        # sheet.write('C5', "Probability", small_head)
        # sheet.write('D5', "Impact", small_head)
        # sheet.write('E5', "Risk Severity", small_head)
        # sheet.write('F5', "Risk Status", small_head)
        # sheet.write('G5', "Last Date", date)
        # sheet.write('H5', "Next Review", date)
        #
        # # sheet.write('F5', "Period : ", small_head)
        # # sheet.write('G5', plan.period, txt)
        # # sheet.write('H5', "State : ", small_head)
        # # sheet.write('I5', plan.state, txt)
        # #
        # # sheet.write('B6', "Preparer: ", small_head)
        # # sheet.write('C6', plan.user_preparer_ids.name, date)
        # # sheet.write('D6', "First Reviewer: ", small_head)
        # # sheet.write('E6', plan.user_reviewer_1_ids.name, date)
        # # sheet.write('F6', "Second Reviewer:", small_head)
        # # sheet.write('G6', plan.user_reviewer_2_ids.name, txt)
        # # sheet.write('H6', "Approver: ", small_head)
        # # sheet.write('I6', plan.user_approver_ids.name, txt)
        # #
        # # sheet.write('B8', 'Process Name', small_head)
        # # sheet.write('C8', 'Category', small_head)
        # # sheet.write('D8', 'Departments', small_head)
        # # sheet.write('E8', 'Risk Priority', small_head)
        # # sheet.write('F8', 'Year 1', small_head)
        # # sheet.write('G8', 'Year 2', small_head)
        # # sheet.write('H8', 'Year 3', small_head)
        # row = 6
        # col = 1
        # # for line in plan.line_ids:
        # #     teams = ""
        # sheet.write(row, col, plan.owner.name, txt)
        # sheet.write(row, col + 1,plan.probability, txt)
        # sheet.write(row, col + 2, plan.impact, txt)
        # sheet.write(row, col + 3, plan.severity, txt)
        # sheet.write(row, col + 4, plan.status, txt)
        # sheet.write(row, col + 5, plan.last_date, date)
        # sheet.write(row, col + 6, plan.next_date, date)
        #
        #
        # #     for team in line.team_ids:
        # #         teams += team.name
        # #     sheet.write(row, col + 2, teams, txt)
        # #     sheet.write(row, col + 3, line.risk_priority_rating, txt)
        # #     sheet.write(row, col + 4, 'Yes' if line.year_1 else 'No', txt)
        # #     sheet.write(row, col + 5, 'Yes' if line.year_2 else 'No', txt)
        # #     sheet.write(row, col + 6, 'Yes' if line.year_3 else 'No', txt)
        #
        # row += 1
        # workbook.close()
        # output.seek(0)
        # response.stream.write(output.read())
        # output.close()


class RiskCategory(models.Model):
    _name = "risk.category"
    _description = "Risk Category"

    name = fields.Char(string='Name', tracking=True)
    active = fields.Boolean(string="Active", default=True, copy= False)
    color = fields.Integer(string="Color")
    color_2 = fields.Char(string="Color 2")
    sequence = fields.Integer(string="Sequence",  default=1)

    def copy(self, default=None):
        if default is None:
            default = {}
        if not default.get('name'):
            default['name'] = _("%s (copy)", self.name)
            default['sequence'] = 10
        return super(RiskCategory, self).copy(default)

    _unique_tag_name = models.Constraint(
        'unique (name)',
        'Name must be unique.',
    )
    _check_sequence = models.Constraint(
        'check (sequence > 0)',
        'Sequence must be non zero positive number.',
    )