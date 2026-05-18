from odoo import fields, models , _



class BuildingRemovalApproval(models.Model):
    _name = "asset.removal.approvals"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'assets_id'

    removal_date = fields.Date('Removal Request Date', required=True,default=lambda self: fields.Date.context_today(self))
    removal_reason = fields.Text('Reason for Removal')

    assets_id = fields.Many2one('account.asset', 'Asset', required=True,readonly=True)
    assets_ids = fields.Many2many('account.asset',string='Selected Assets',readonly=True)
    company_id = fields.Many2one('res.company', string="Company", groups="base.group_multi_company")
    disposal_reason = fields.Char("Reason for Disposal")
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('request_approval','Pending Approval'),
        ('approved', 'Approved'),
    ], string='Status', required=True, readonly=True, tracking=True, default='draft')

    redirect_url = fields.Char(compute="_compute_redirect_url", store=True)
    notes = fields.Html()
    disposal_method = fields.Selection([
        ('donation', 'Donation'),
        ('write_off', 'Write Off'),
        ('transfer', 'Transfer to another department')])
    transfer_department_id = fields.Many2one('hr.department',string="Transfer Department")

    user_id = fields.Many2one('res.users',default=lambda self: self.env.user,string="Submitted by",readonly=1)
    document_id = fields.Binary(string="Disposal register")
    appointment_letter_id = fields.Binary(string="Signed Appointment Letter")


    def action_approve(self):
        if self.disposal_method == 'transfer':
            self.message_post(
                body=_('Asset is transferred  from %s to %s', self.assets_id.custodian_department_id.name,
                       self.transfer_department_id.name))
        # manager_group = self.env.ref('assets_disposal.group_asset_evaluator')
        mail_values = {}
        partners = self.user_id
        for partner in partners:
            if partner.email:
                mail_values = {
                    'email_to': partner.login,
                }
        template = self.env.ref(
            'assets_disposal.emails_template_to_confirmation')
        template.send_mail(self.id, force_send=True, email_values=mail_values)
        for asset in self:
            message_body = (
                f" Asset {self.assets_id.name} has been approved.")
            # manager_group = self.env.ref(
            #     'assets_disposal.group_asset_evaluator')
            # partner_ids = self.user_id.login
            asset.message_post(
                body=message_body,
                message_type='email',
                subtype_xmlid='mail.mt_comment',
                # partner_ids=partner_ids,
            )

        self.state = 'approved'

        print("fff")

    # def action_reject(self):
    #     self.state = 'rejected'

    def action_set_to_draft(self):
        self.state = 'draft'

    def action_approve_request(self):
        print(self.assets_id.name,"sss")
        self.state = 'request_approval'

        # self.get_record_url()
        manager_group = self.env.ref('assets_disposal.group_asset_evaluator')
        mail_values = {}
        partners = manager_group.users.mapped('partner_id')
        for partner in partners:
            if partner.email:
                mail_values = {
                    'email_to': partner.email,
                }
        template = self.env.ref(
            'assets_disposal.emails_template_to_confirm_asset')
        template.send_mail(self.id, force_send=True, email_values=mail_values)
        for asset in self:
            message_body = (
                f" Asset {self.assets_id.name} has been submitted for approval.")
            manager_group = self.env.ref(
                'assets_disposal.group_asset_evaluator')
            partner_ids = manager_group.users.mapped('partner_id.id')
            asset.message_post(
                body=message_body,
                message_type='email',
                subtype_xmlid='mail.mt_comment',
                partner_ids=partner_ids,
            )
        #

