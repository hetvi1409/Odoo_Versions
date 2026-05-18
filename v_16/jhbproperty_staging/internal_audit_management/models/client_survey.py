import base64
import io
import xlsxwriter
from werkzeug import urls
from odoo import api, fields, models,_
from odoo.exceptions import UserError, ValidationError
from odoo.tools import date_utils
from odoo.tools.safe_eval import json


class SurveyQuestions(models.Model):
    """Individual questions within sections"""
    _name = 'survey.questions'
    _description = 'Survey Questions'
    _order = 'sequence, id'

    name = fields.Text(string='Question Text', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    active = fields.Boolean(string='Active', default=True)
    # For display purposes
    question_display = fields.Char(string='Display',
                                   compute='_compute_question_display')

    @api.depends('name')
    def _compute_question_display(self):
        for rec in self:
            # Add bullet point if not already there
            if rec.name and not rec.name.strip().startswith('*'):
                rec.question_display = f'* {rec.name}'
            else:
                rec.question_display = rec.name


class ClientSurvey(models.Model):

    _name = "client.survey"
    _rec_name = "project"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    client_survey_id = fields.Many2one('project.task',string='Task')
    survey_number = fields.Char(string='W/P Reference')
    auditee = fields.Many2one('res.users',string='Auditee',required=True)
    auditor = fields.Many2one('res.users',string='Auditor',default=lambda self: self.env.user)
    team_leader = fields.Many2one('res.users',string='Team Leader',required=True)
    reviewer = fields.Many2one('res.users',string='Reviewer',required=True)
    comments_ids = fields.Many2many('client.comments',default=lambda self: self._get_default_comment_lines())
    comment_ones = fields.Char(string='Comment')
    comment_sec = fields.Char(string='Comment')
    comment_third = fields.Char(string='Comment')
    comment_fourth = fields.Char(string='Comment')
    comment_fifth = fields.Char(string='Comment')
    project = fields.Many2one('project.project',string='Project')
    project_name = fields.Char(string='Project Name', readonly=False,related='project.name')
    subject = fields.Char(string='Subject', readonly=False,related='project.name')
    rating_one = fields.Selection([('default',''),('one', 'Not acceptable performance.'), ('two', "Meet some expectations."), ('three','Meet expectations.'), ('four','Exceed expectations.'), ('five','Exceptional performance.')],string='Rating',ondelete='cascade')
    rating_sec = fields.Selection([('default',''),('one', 'Not acceptable performance.'), ('two', "Meet some expectations."), ('three','Meet expectations.'), ('four','Exceed expectations.'), ('five','Exceptional performance.')],string='Rating',ondelete='cascade')
    rating_third = fields.Selection([('default',''),('one', 'Not acceptable performance.'), ('two', "Meet some expectations."), ('three','Meet expectations.'), ('four','Exceed expectations.'), ('five','Exceptional performance.')],string='Rating',ondelete='cascade')
    rating_fourth = fields.Selection([('default',''),('one', 'Not acceptable performance.'), ('two', "Meet some expectations."), ('three','Meet expectations.'), ('four','Exceed expectations.'), ('five','Exceptional performance.')],string='Rating',ondelete='cascade')
    rating_fifth = fields.Selection([('default',''),('one', 'Not acceptable performance.'), ('two', "Meet some expectations."), ('three','Meet expectations.'), ('four','Exceed expectations.'), ('five','Exceptional performance.')],string='Rating',ondelete='cascade')
    completed_by = fields.Many2one('res.users',string='Completed By:', related='auditee')
    position = fields.Char(string='Position:', related='auditee.partner_id.function')
    date = fields.Date(string='Date:')
    state = fields.Selection([('draft', 'Draft'),
                              ('preparer', "Preparer"),
                              ('in_progress', "Reviewed"),
                              ('completed', 'Approved'),
                              ('submitted', 'Submitted to Client'),
                              ('reverted', 'Reverted'),
                              ('rejected', 'Rejected'),
                              ], default='draft')
    feedback = fields.Char(string="Audit Reverts/ Review Notes", tracking=True)
    document_ids = fields.Many2many('ir.attachment', string="Documents")
    project_task_id = fields.Many2one('project.task',string='Project Task')


    municipal_manager_name = fields.Many2one('res.users',string="Municipal Manager")
    client_id = fields.Many2one('hr.employee',string="Client Name")
    response_ids = fields.One2many('survey.response','survey_id',string='Responses')

    # Additional fields for questionnaire
    improvement_suggestions = fields.Text(
        string='Where could we improve our service?')
    other_comments = fields.Text(string='Other comments')
    questionnaire_completed_by = fields.Char(
        string='Questionnaire Completed By')
    questionnaire_signature = fields.Char(string='Questionnaire Signature')
    questionnaire_date = fields.Date(string='Questionnaire Date')

    # Header table fields
    enquiries_person = fields.Many2one('res.users',string='Enquiries Person')
    reference_number = fields.Char(string='Reference Number', default='01/2/2')
    your_reference = fields.Char(string='Your Reference', default='Policies')

    questionnaire_content = fields.Html(string='Questionnaire Content', default="""
    <p style="margin-bottom:15px;">
                            In the quest towards continuous improvement and to
                            add more value to our service, please complete this
                            evaluation questionnaire and forward to the
                            attention of, <strong>The Office Manager : Internal
                            Audit Unit
                        </strong> (See covering letter):
                        </p>
    """)

    intro_content = fields.Html(string='Introduction Content', default="""
            <p>
                During the quarter ending 31 July 2003 we conducted two audit assignments 
                in your organisation and issued reports, the contents of which were discussed 
                with you and/or your managers and management comments solicited before each 
                final report was issued.
            </p>
            <p>
                In order to evaluate our quality of service to your functional area and the 
                organisation as a whole, Internal Audit Unit has developed the attached 
                questionnaire. You are kindly requested to complete and provide any appropriate 
                input with a view to help us to gauge the effectiveness of our recent audit.
            </p>
            <p>
                A score of "one" indicates that the point in question was completely useless 
                or wholly unsatisfactory. A "three" means that it was satisfactory but with 
                room for improvement and a "five" means that it was extremely well done or 
                perfectly handled.
            </p>
            <p>
                In order to help us to help you, written comments on how we, the internal 
                auditors, can improve our service to you, you are requested. In the process 
                of completing the questionnaire, please feel free to criticise constructively, 
                highlight shortfalls or bring to my attention any area which the Internal 
                Audit Unit needs to improve.
            </p>
            <p>
                It would be appreciated if this questionnaire could be returned within 5 
                days after receipt.
            </p>
            <p>
                Your co-operation in this regard will be much appreciated bearing in mind 
                that the objective behind this exercise is to produce an efficient, effective 
                and highly professional Internal Audit Unit.
            </p>
        """)



    def action_revert(self):
        return {
            'name': 'Audit Reverts/ Review Notes',
            'type': 'ir.actions.act_window',
            'res_model': 'internal.audit.revert.wizard',
            'context': {
                'default_client_survey_id': self.id
            },
            'view_mode': 'form',
            'target': 'new',
        }

    @api.model
    def _get_default_comment_lines(self):
        return [
            (0, 0, {
                'description': "1. Planning the Work The audit objectives were focused on the risks and operations of your department and were communicated to yourself."}),
            (0, 0, {
                'description': "2. Execution of Work Work was performed efficiently and effectively in an acceptable amount of time and the goals and objectives agreed were achieved."}),
            (0, 0, {
                'description': "3. Findings and Reporting Findings were communicated, recommendations provided were workable and reports were issued within reasonable time."}),
            (0, 0, {
                'description': "4. Personnel demonstrated competence and exhibited a high standard of professionalism as a result I would ask IAU personnel for help in a situation warranting its attention."}),
            (0, 0, {
                'description': "5. Overall What is your overall evaluation of SIAU's performance of the audit project?"}),
        ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['survey_number'] = self.env['ir.sequence'].next_by_code(
                'client.survey')
        surveys = super(ClientSurvey, self).create(vals_list)
        for survey in surveys:
            survey._create_response_records()
        return surveys

    def get_form_url(self):
        """Method for create the url."""
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        Urls = urls.url_join(base_url,
                             'web#id=%s&model=client.survey&view_type=form' % self.id)
        return Urls

    def action_preparer(self):
        mail_template = self.env.ref(
            'internal_audit_management.email_template_client_survey')
        mail_template.send_mail(self.id, force_send=True)
        self.state = 'preparer'

    def action_review(self):
        mail_template = self.env.ref(
            'internal_audit_management.email_template_client_survey_completed')
        mail_template.send_mail(self.id, force_send=True)
        self.state = 'in_progress'

    def action_approve(self):
        # mail_template = self.env.ref(
        #     'internal_audit_management.email_template_client_survey_completed')
        # mail_template.send_mail(self.id, force_send=True)
        self.state = 'completed'


    def action_send_client(self):
        print('hhhhhhhhh',)
        mail_template = self.env.ref(
            'internal_audit_management.email_template_client_survey_client')
        mail_template.send_mail(self.id, force_send=True)
        self.state = 'submitted'

    def action_print_client_survey(self):
        self.ensure_one()
        data = {
            'model_id': self.id,
        }
        return self.env.ref(
            'internal_audit_management.action_print_survey'
        ).report_action(self, data=data)

    def action_view_records(self):
        """Method for view records"""
        return {
            'name': 'Audit Reverts/ Review Notes',
            'type': 'ir.actions.act_window',
            'res_model': 'audit.revert',
            'domain': [('res_id', '=', self.id), ('res_model', '=', self._name)],
            'view_mode': 'tree,form',
            'target': 'current',
        }

    def action_update(self):
        self.state = 'in_progress'

    def action_mark_discrepancy(self):
        self.state = 'rejected'

    def action_excel_report(self):
        """Print excel reports"""
        plan = self.id
        data = {
            'model_id': self.id,
            'method': plan
        }
        return {
            'type': 'ir.actions.report',
            'data': {'model': self._name,
                     'options': json.dumps(data,
                                           default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'report_name': 'Customer Satisfaction Survey',
                     },
            'report_type': 'xlsx',
        }

    def get_xlsx_report(self, data, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet()

        method = self.env[self._name].browse(int(data['method']))
        cell_format = workbook.add_format(
            {'font_size': '12px', 'align': 'center'})
        head = workbook.add_format(
            {'align': 'center', 'bold': True, 'font_size': '20px'})
        small_head = workbook.add_format(
            {'align': 'center', 'font_size': '11px'})
        txt = workbook.add_format({'font_size': '10px', 'align': 'center',
                                   'valign': 'vcenter', 'text_wrap': True})
        date = workbook.add_format({'num_format': 'd-m-yyyy'})
        sheet.set_column(1, 11, 12, txt)

        image_data = io.BytesIO(base64.b64decode(self.env.company.logo))
        sheet.insert_image('M3', "image.png", {
            'image_data': image_data,
            'x_scale': 0.5,  # Scale image if needed
            'y_scale': 0.5,
            'positioning': 1  # Move and resize with cells
        })
        sheet.write('H1', "Report Date", txt)
        sheet.write('I1', fields.Date.today(), date)
        sheet.merge_range('E2:L3', 'Customer Satisfaction Survey', head)
        sheet.merge_range('F5:K6', 'Umzimkhulu Local Municipality', head)
        sheet.merge_range('F7:K8', 'Internal Audit Unit', head)
        sheet.write('D10', "Name : ", small_head)
        sheet.merge_range('E10:F10', method.survey_number, txt)
        sheet.write('D12', "Auditee : ", small_head)
        sheet.merge_range('E12:F12', method.auditee.name, txt)
        sheet.write('D14', "Project : ", small_head)
        sheet.merge_range('E14:F14', method.project.name, txt)
        sheet.write('D16', "Team Leader : ", small_head)
        sheet.merge_range('E16:F16', method.team_leader.name, txt)


        sheet.merge_range('I10:J10', "Project Name : ", small_head)
        sheet.merge_range('K10:L10', method.project.name, txt)
        sheet.merge_range('I12:J12', "Reviewer : ", small_head)
        sheet.merge_range('K12:L12', method.reviewer.name, txt)
        sheet.merge_range('I14:J14', "Subject : ", small_head)
        sheet.merge_range('K14:L14', method.subject, txt)

        sheet.merge_range('G18:J18', 'Client Feedback', txt)
        sheet.merge_range('F19:K21', 'Your input is essential to our improvement and success. Please mark the box which best describes the level at which we performed during the audit project. For unsatisfactory responses, provide details and recommendations. Thank you!', txt)
        sheet.merge_range('G23:J23', 'Ratings :', txt)
        sheet.merge_range('G24:J24', '1. Not acceptable performance', txt)
        sheet.merge_range('G25:J25', '2. Meet some expectations', txt)
        sheet.merge_range('G26:J26', '3. Meet expectations', txt)
        sheet.merge_range('G27:J27', '4. Exceed expectations', txt)
        sheet.merge_range('G28:J28', '5. Exceptional performance', txt)

        teams = method.comments_ids
        if teams:
            sheet.write('D30', 'Description: ', small_head)
            sheet.write('K30', 'Comment', small_head)
            sheet.write('L30', 'Rating', small_head)
            row = 30
            col = 3
            for plan in teams:
                sheet.merge_range(row, col, row + 2, col + 5, plan.description, txt)
                sheet.write(row, col + 7, plan.comment_client, txt)
                sheet.write(row, col + 8, plan.rating_client, txt)
                row += 3

        sheet.write('D50', "Completed by : ", small_head)
        sheet.merge_range('E50:F50', method.completed_by.name, txt)
        sheet.write('I50', "Position : ", small_head)
        sheet.merge_range('J50:K50', method.position, txt)

        reverts = self.env['audit.revert'].search(
            [('res_id', '=', method.id), ('res_model', '=', method._name)])
        if method.feedback:
            sheet.write('F51', 'Revert Comments', small_head)
            sheet.merge_range('G51:H51', method.feedback, txt)
        if reverts:
            sheet.write('F53', 'Revert Name', small_head)
            sheet.write('G53', 'Created Date', small_head)
            sheet.write('H53', 'Review Comments', small_head)
            sheet.write('I53', 'Audit Proposal', small_head)
            sheet.write('J53', 'State', small_head)
            row = 54
            col = 5
            for revert in reverts:
                sheet.write(row, col, revert.name, txt)
                sheet.write(row, col + 1, revert.date, date)
                sheet.write(row, col + 2, revert.comments, txt)
                sheet.write(row, col + 3, revert.audit_findings, txt)
                sheet.write(row, col + 4, revert.state, txt)
                row = + 1
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()

    def _create_response_records(self):
        """Create a response record for each active question"""
        self.ensure_one()
        questions = self.env['survey.questions'].search([('active', '=', True)])
        for question in questions:
            self.env['survey.response'].create({
                'survey_id': self.id,
                'question_id': question.id,
            })

    def action_regenerate_responses(self):
        """Regenerate response records (useful after adding new questions)"""
        self.ensure_one()
        existing_questions = self.response_ids.mapped('question_id')
        all_questions = self.env['survey.questions'].search(
            [('active', '=', True)])
        new_questions = all_questions - existing_questions

        for question in new_questions:
            self.env['survey.response'].create({
                'survey_id': self.id,
                'question_id': question.id,
            })



class ClientComments(models.Model):
    _name = "client.comments"
    _rec_name = "description"

    description = fields.Char()
    comment_client = fields.Char(string='Comment')
    rating_client = fields.Selection(
        [('default', ''), ('one', 'Not acceptable performance.'),
         ('two', "Meet some expectations."),
         ('three', 'Meet expectations.'), ('four', 'Exceed expectations.'),
         ('five', 'Exceptional performance.')], string='Rating',
        ondelete='cascade')


class SurveyResponse(models.Model):
    """Individual responses for each question in a survey"""
    _name = 'survey.response'
    _description = 'Survey Response'

    survey_id = fields.Many2one('client.survey', string='Survey',
                                ondelete='cascade',requred=True)
    question_id = fields.Many2one('survey.questions', string='Question',
                                  requred=True)

    # Rating (stored value)
    rating = fields.Selection([
        ('1', 'Inadequate'),
        ('2', 'Marginal'),
        ('3', 'Satisfactory'),
        ('4', 'Very Good'),
        ('5', 'Excellent'),
    ], string='Rating')

    # Display checkboxes (computed from rating)
    check_1 = fields.Boolean(string='1', compute='_compute_checks',
                             inverse='_inverse_check_1')
    check_2 = fields.Boolean(string='2', compute='_compute_checks',
                             inverse='_inverse_check_2')
    check_3 = fields.Boolean(string='3', compute='_compute_checks',
                             inverse='_inverse_check_3')
    check_4 = fields.Boolean(string='4', compute='_compute_checks',
                             inverse='_inverse_check_4')
    check_5 = fields.Boolean(string='5', compute='_compute_checks',
                             inverse='_inverse_check_5')
    sequence = fields.Integer(
        string="Sequence",
        help="Gives the sequence order when displaying a list of sale quote lines.",
        default=10)

    display_type = fields.Selection(
        selection=[
            ('line_section', "Section"),
            ('line_note', "Note"),
        ],
        default=False)
    name = fields.Char()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('display_type'):
                vals.update({
                    'question_id': False,
                    'rating': False,
                })
        return super().create(vals_list)

    def write(self, values):
        if 'display_type' in values and self.filtered(
                lambda line: line.display_type != values.get('display_type')):
            raise UserError(
                _("You cannot change the line type. Please delete the line and create a new one.")
            )
        return super().write(values)

    @api.depends('rating')
    def _compute_checks(self):
        for rec in self:
            rec.check_1 = (rec.rating == '1')
            rec.check_2 = (rec.rating == '2')
            rec.check_3 = (rec.rating == '3')
            rec.check_4 = (rec.rating == '4')
            rec.check_5 = (rec.rating == '5')

    def _inverse_check_1(self):
        for rec in self:
            rec.rating = '1' if rec.check_1 else False

    def _inverse_check_2(self):
        for rec in self:
            rec.rating = '2' if rec.check_2 else False

    def _inverse_check_3(self):
        for rec in self:
            rec.rating = '3' if rec.check_3 else False

    def _inverse_check_4(self):
        for rec in self:
            rec.rating = '4' if rec.check_4 else False

    def _inverse_check_5(self):
        for rec in self:
            rec.rating = '5' if rec.check_5 else False

    @api.constrains('display_type', 'rating', 'question_id')
    def _check_required_fields(self):
        for rec in self:
            if rec.display_type:
                # Section or note line
                if rec.rating or rec.question_id:
                    raise ValidationError(
                        _("Sections/Notes cannot have rating or question.")
                    )
            else:
                # Normal response line
                if not rec.question_id:
                    raise ValidationError(
                        _("Please select a question for this response line.")
                    )