from odoo import api, fields, models,_
from werkzeug import urls



class AuditFollowUp(models.Model):
    """Communicate Audit Followup"""
    _name = "audit.followup"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Audit Followup"
    _rec_name = 'followup_name'

    followup_name = fields.Char(string='Follow up audit Name:')
    audit_number = fields.Char(string='Follow up audit Number:',readonly=True)
    project_id = fields.Many2one('project.project',string='Project')
    start_date = fields.Date(string='Start date')
    end_date = fields.Date(string='End date')
    subject = fields.Char(string='Subject', related='project_id.name', readonly=False)
    date_audit = fields.Date(string='Date')
    user_preparer_ids = fields.Many2one('res.users',
                                        string="Preparer", tracking=True)
    user_reviewer_1_ids = fields.Many2one('res.users',
                                          string="First Reviewer",
                                          tracking=True)
    user_reviewer_2_ids = fields.Many2one('res.users',
                                          string="Second Reviewer ",
                                          tracking=True)
    user_approver_ids = fields.Many2one('res.users', string="Approver",
                                        tracking=True)
    stage = fields.Selection([('preparer', 'Preparer'),
                              ('first_reviewer', 'First Reviewer'),
                              ('second_reviewer', 'Second Reviewer'),
                              ('follow_up','Send follow up audit'),
                              ('audit_response','Follow up audit response'),
                              ('audit_conclusion','Follow up audit conclusion'),
                              ('reverted', 'Reverted')],
                             copy=False,
                             default='preparer')
    state = fields.Selection([('01_in_progress','Preparer'),('02_changes_requested','First Reviewer'),('03_approved','Second Reviewer'),('1_done','Approver')])
    follow_up_setting = fields.One2many('audit.followup.setting','follow_up_setting_id')
    internal_audit_capturing = fields.One2many('audit.capturing','audit_capturing_id')
    management_capturing = fields.One2many('management.capturing','management_capturing_id')
    audit_captur = fields.One2many('audit.capt','audit_capt_id')
    previous_state = fields.Selection([
        ('first_reviewer', 'First Reviewer'),
        ('second_reviewer', 'Second Reviewer')])
    feedback = fields.Char(string="Audit Reverts / Review Notes", tracking=True)
    document_ids = fields.Many2many('ir.attachment', string="Documents")
    edms_template = fields.Many2one('memo.template', string='EDMS Template')
    background_body = fields.Html("Background", copy=False)

    @api.onchange('edms_template')
    def _onchange_type(self):
        """Auto-fill background when type changes."""
        if self.sudo().edms_template and self.sudo().edms_template.background_body:
            self.background_body = self.sudo().edms_template.background_body
        else:
            self.background_body = ''

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:

            if vals.get('edms_template') and not vals.get('background_body'):
                edms_template = self.env['memo.template'].sudo().browse(vals['edms_template'])
                if edms_template and edms_template.background_body:
                    vals[
                        'background_body'] = edms_template.background_body
            if not vals.get('audit_number'):
                vals['audit_number'] = self.env['ir.sequence'].next_by_code('audit.followup')
        return super().create(vals_list)

    def get_form_url(self):
        """Method for create the url."""
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        Urls = urls.url_join(base_url,
                             'web#id=%s&model=audit.followup&view_type=form' % self.id)
        return Urls

    def action_review(self):
        """First Review"""
        mail_template = self.env.ref(
            'internal_audit_management.email_template_audit_followup')
        mail_template.send_mail(self.id, force_send=True)
        self.stage = 'first_reviewer'

    def action_2nd_review(self):
        """Second Review"""
        mail_template = self.env.ref(
            'internal_audit_management.email_template_audit_followup_sec')
        mail_template.send_mail(self.id, force_send=True)
        self.stage = 'second_reviewer'

    def action_approve(self):
        """Approve"""
        mail_template = self.env.ref(
            'internal_audit_management.email_template_audit_followup_approve')
        mail_template.send_mail(self.id, force_send=True)
        self.stage = 'follow_up'

    def action_sent_manager(self):
        mail_template = self.env.ref(
            'internal_audit_management.email_template_audit_followup_mngr')
        mail_template.send_mail(self.id, force_send=True)
        self.stage = 'audit_response'
        mgmt_capturing = self.internal_audit_capturing.ids
        if len(mgmt_capturing) > 0:
            for record in self.internal_audit_capturing:
                self.env['management.capturing'].create({
                    'management_capturing_id': self.id,
                    'follow_num': record.follow_up_num,
                })

    def action_audit_conclusion(self):
        mail_template = self.env.ref(
            'internal_audit_management.email_template_audit_followup_auditor')
        mail_template.send_mail(self.id, force_send=True)
        self.stage = 'audit_conclusion'
        mgmt_capturing = self.internal_audit_capturing.ids
        if len(mgmt_capturing) > 0:
            for record in self.internal_audit_capturing:
                self.env['audit.capt'].create({
                    'audit_capt_id': self.id,
                    'follow_num': record.follow_up_num,
                })

    def action_revert(self):
        """Action SEND BACK TO REVIEW"""
        return {
            'name': 'Audit Reverts / Review Notes',
            'type': 'ir.actions.act_window',
            'res_model': 'internal.audit.revert.wizard',
            'context': {
                'default_audit_followup_id': self.id
            },
            'view_mode': 'form',
            'target': 'new',
        }

    def action_update(self):
        self.stage = self.previous_state

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

class AuditFollowUpSetting(models.Model):
    """Communicate Audit Followup Setting"""
    _name = "audit.followup.setting"

    follow_up_setting_id = fields.Many2one('audit.followup')
    follow_up_number = fields.Char(string='No', readonly=True)
    audit_area = fields.Char(string='Audit Area')
    title_of_finding = fields.Char(string='Title of Finding')
    recommendation = fields.Html(string='Recommendation')
    responsible_mngr = fields.Many2one('res.users',string='Responsible Manager')
    mgmt_action_plan = fields.Html(string="Management's Action Plan")
    poe = fields.Char(string='POE')
    main_stage = fields.Selection(related='follow_up_setting_id.stage', default='preparer')
    action_date = fields.Date(string='Action Date')
    attach_poe = fields.Many2many('ir.attachment',
                                      string="Attach POE")
    implement_not_implement = fields.Selection([('implemented','Implemented'),('not_implemented','Not Implemented')])
    follow_up = fields.Html(string='Follow Up')

    @api.model_create_multi
    def create(self, vals_list):
        """Create multiple records and assign sequence numbers."""
        for vals in vals_list:
            if not vals.get('follow_up_number'):
                vals['follow_up_number'] = self.env['ir.sequence'].next_by_code(
                    'audit.followup.setting')
        res = super(AuditFollowUpSetting, self).create(vals_list)
        return res


class AuditCapturing(models.Model):
    _name = "audit.capturing"

    audit_capturing_id = fields.Many2one('audit.followup')
    follow_up_num = fields.Char(string='No', readonly=True)
    aud_area = fields.Char(string='Audit Area')
    title_of_find = fields.Char(string='Title of Finding')
    recommend = fields.Html(string='Recommendation')
    responsible_manager = fields.Many2one('res.users',string='Responsible Manager')

    @api.model_create_multi
    def create(self, vals_list):
        """Create multiple records and assign sequence numbers."""
        for vals in vals_list:
            if not vals.get('follow_up_num'):
                vals['follow_up_num'] = self.env['ir.sequence'].next_by_code('audit.capturing')
        res = super(AuditCapturing, self).create(vals_list)
        return res


class ManagementCapturing(models.Model):
    _name = "management.capturing"

    management_capturing_id = fields.Many2one('audit.followup')
    mgmt_act_plan = fields.Html(string="Management's Action Plan")
    p_o_e = fields.Char(string='POE')
    follow_num = fields.Char(string='Follow Number', readonly=True)
    act_date = fields.Date(string='Action Date')
    attachment_poe = fields.Many2many('ir.attachment',
                                  string="Attach POE")

class AuditCapt(models.Model):
    _name = "audit.capt"

    audit_capt_id = fields.Many2one('audit.followup')
    impment_not_imple = fields.Selection([('implemented', 'Implemented'),
                                                ('not_implemented', 'Not Implemented')],string='Implemented or not Implemented')
    follow_up = fields.Html(string='Follow Up')
    follow_num = fields.Char(string='Follow Number',readonly=True)
