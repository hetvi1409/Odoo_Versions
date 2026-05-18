from odoo import api, models, fields


class AccountAsset(models.Model):
    _inherit = 'account.asset'
    """Inherited Account Asset fo asset verification"""

    major_group_description = fields.Char(string="Major Group Description",
                                          help="Major Group Description")
    barcode_past_year = fields.Char(string="Barcode Past Year",
                                    help="Barcode Past Year")
    current_condition_past_year = fields.Char(
        string="Current Condition Past Year",
        help="Current Condition Past Year")
    current_condition_this_year = fields.Char(
        string="Current Condition This Year",
        help="Current Condition This Year")
    name_installation = fields.Char(string="Name Installation",
                                    help="Name Installation")
    asset_component = fields.Char(string="Asset Component",
                                  help="Asset Component")
    parent_barcode = fields.Char(string="Parent Barcode", help="Parent Barcode")
    asset_size = fields.Char(string="Asset Size", help="Asset Size")
    asset_make_type = fields.Many2one("asset.type", help="Asset Make Type")
    estimated_useful_life_month = fields.Char(
        string="Estimated Useful Life Month",
        help="Estimated Useful Life Month")
    date_verification = fields.Date(string="Date of verification",
                       help="Date of verification")
    comments = fields.Char(string="Comments", help="Comments")
    inspector = fields.Char(string="Inspector", help="Inspector")
    asset_verification_user_id = fields.Many2one('res.users',
                                                 string="Verification User")
    is_verified = fields.Boolean(string="Verified", readonly=True)
    asset_type_id = fields.Many2one('asset.type')
    location_id = fields.Many2one('stock.location',string="Location", help="Location of the asset")
    history_ids = fields.One2many('asset.verification.history','history_id',string="History")

    condition = fields.Char(string='Condition', help='Condition of the asset', readonly=True, store=True, compute='_compute_condition')
    latest_verification_history_id = fields.Many2one('asset.verification.history', string="Latest Verification History",store=True, compute='_compute_condition')

    @api.depends('history_ids')
    def _compute_condition(self):
        for asset in self:
            all_histories = asset.history_ids
            latest_history = all_histories.sorted(key=lambda h: h.create_date or fields.Datetime.now(),reverse=True)[:1]
            asset.condition = latest_history.condition.name if latest_history else ''
            asset.latest_verification_history_id = latest_history.id if latest_history else False

    quarter = fields.Selection([
        ('Q1', 'Q1 (Jan - Mar)'),
        ('Q2', 'Q2 (Apr - Jun)'),
        ('Q3', 'Q3 (Jul - Sep)'),
        ('Q4', 'Q4 (Oct - Dec)'),
    ], string='Quarter', default='Q1', required=True, help="Select the quarter for which the asset is being verified.")

    account_verification_job_id = fields.Many2one('asset.verification.job')

    custodian_id = fields.Many2one('hr.employee','Custodian',tracking = True, required=False) # Make here required True, False for only import sheet purpose

    job_location_id = fields.Many2one('asset.verification.job.location','Job Location')
    image_ids = fields.One2many('asset.verification.image', 'image_id',string='Image')

    def open_employee_record(self):

        if self.custodian_id:

            employee_record = self.env['hr.employee'].search([('id','=',self.custodian_id.id)])

            return {
                'type': 'ir.actions.act_window',
                'res_model': 'hr.employee',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'current',
                'res_id': employee_record.id,
            }

    def open_asset_images(self):
        return {
            'name': 'Asset Verification Images',
            'type': 'ir.actions.act_window',
            'res_model': 'asset.verification.image',
            'view_mode': 'kanban,form',
            'domain': [('history_id.history_id.id', '=', self.id)],
            'target': 'current',
    }


    # def cron_fetch_latest_condition(self):
    #     assets = self.search([])
    #     for asset in assets:
    #         all_histories = asset.history_ids
    #         latest_history = all_histories.sorted(key=lambda h: h.create_date or fields.Datetime.now(),reverse=True)[:1]
    #         asset.condition = latest_history.condition.name if latest_history else ''

class Image(models.Model):
    _name = 'asset.verification.image'
    _description = 'Asset Verification Image'
    _rec_name = 'history_id'

    image_id = fields.Many2one('account.asset', string='Asset')
    image = fields.Binary(string='Picture', attachment=True)
    name = fields.Char(string='Image Name')
    mimetype = fields.Char(string='MIME Type')

    # Separate foreign keys for verification and history
    verification_id = fields.Many2one('asset.verification', string='Verification Reference', ondelete='cascade',)
    history_id = fields.Many2one('asset.verification.history', string='History Reference', ondelete='cascade',)

    def default_get(self, fields):
        print("\n\n\n\n Context in default_get:", self.env.context)
        res = super(Image, self).default_get(fields)
        res['verification_id'] = self.env.context.get('verification_id')
        res['history_id'] = self.env.context.get('default_history_id')
        print('res--->',res)
        return res

class AssetRemovalApproval(models.Model):
    _name = "asset.removal.approval"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'asset_id'

    removal_date = fields.Date('Removal Request Date', required=True,default=lambda self: fields.Date.context_today(self))
    removal_reason = fields.Text('Reason for Removal', required=True)
    asset_id = fields.Many2one('account.asset', 'Asset', required=True)
    company_id = fields.Many2one('res.company', string="Company", groups="base.group_multi_company")
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('send', 'Sent for Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string='Status', required=True, readonly=True, tracking=True, default='draft')

    redirect_url = fields.Char(compute="_compute_redirect_url", store=True)
    notes = fields.Html()
    user_id = fields.Many2one('res.users',default=lambda self: self.env.user)
    document_id = fields.Binary(string="Removal Document",required="True")


    @api.depends('state')
    def _compute_redirect_url(self):
        for record in self:
            base_url = self.env['ir.config_parameter'].get_param('web.base.url')
            if record.state != 'approved':
                base_url += '/web#id=%d&view_type=list&model=%s' % (record.id, 'asset.removal.approval')
            else:
                base_url += '/web#id=%d&view_type=list&model=%s' % (record.asset_id.id, 'account.asset')
            record.redirect_url = base_url

    def action_submit_for_approval(self):
        """ Submit the removal request for approval """
        self.write({'state': 'send'})
        manager_group = self.env.ref('asset_verification.group_staging_approval_manager')

        mail_values = {}
        partners = manager_group.users.mapped('partner_id')

        for partner in partners:
            if partner.email:
                mail_values = {'email_to': partner.email}

        template = self.env.ref('asset_verification.email_template_removal_to_confirm')
        template.send_mail(self.id, force_send=True, email_values=mail_values)

        for removal in self:
            message_body = f"Removal request for asset {removal.asset_id.name} has been submitted for approval."
            partner_ids = manager_group.users.mapped('partner_id.id')
            removal.message_post(body=message_body, message_type='email', subtype_xmlid='mail.mt_comment',
                                 partner_ids=partner_ids)

    def action_approve(self):
        """ Approve the removal request """
        for record in self:
            record.state = 'approved'
            record.asset_id.active = False  # Mark the asset as inactive (removed)

            message_body = f"Asset {record.asset_id.name} has been approved for removal."
            mail_values = {}
            if record.user_id.partner_id.email:
                mail_values = {'email_to': record.user_id.partner_id.email}

            template = self.env.ref('asset_verification.email_template_asset_removal_approved')
            template.send_mail(record.id, force_send=True, email_values=mail_values)

            record.message_post(body=message_body, message_type='email', subtype_xmlid='mail.mt_comment',
                                partner_ids=[record.user_id.partner_id.id])

    def action_reject(self):
        """ Reject the removal request """
        for record in self:
            record.state = 'rejected'

            message_body = f"Removal request for asset {record.asset_id.name} has been rejected."
            mail_values = {}
            if record.user_id.partner_id.email:
                mail_values = {'email_to': record.user_id.partner_id.email}

            template = self.env.ref('asset_verification.email_template_asset_removal_reject')
            template.send_mail(record.id, force_send=True, email_values=mail_values)

            record.message_post(body=message_body, message_type='email', subtype_xmlid='mail.mt_comment',
                                partner_ids=[record.user_id.partner_id.id])

