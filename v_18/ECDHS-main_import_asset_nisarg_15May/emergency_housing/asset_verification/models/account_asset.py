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




    quarter = fields.Selection([
        ('Q1', 'Q1 (Jan - Mar)'),
        ('Q2', 'Q2 (Apr - Jun)'),
        ('Q3', 'Q3 (Jul - Sep)'),
        ('Q4', 'Q4 (Oct - Dec)'),
    ], string='Quarter', default='Q1', required=True, help="Select the quarter for which the asset is being verified.")

    account_verification_job_id = fields.Many2one('asset.verification.job')

    custodian_id = fields.Many2one('hr.employee','Custodian',tracking = True, required=True)

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

class Image(models.Model):
    _name = 'asset.verification.image'

    image_id = fields.Many2one('account.asset')
    image = fields.Binary(string='Picture')

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

