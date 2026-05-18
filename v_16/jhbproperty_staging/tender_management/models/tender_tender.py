from odoo import models, fields, api, _
from odoo.exceptions import UserError
from werkzeug import urls
from datetime import datetime
from odoo.addons.http_routing.models.ir_http import slug


class Tender(models.Model):
    """
    Model representing a tender.
    """
    _name = 'tender.tender'
    _description = 'Tender'
    _inherit = [
        'mail.thread',
        'mail.activity.mixin',
        'website.published.mixin',
        'website.seo.metadata',
        'website.cover_properties.mixin',
        'website.searchable.mixin',
    ]

    def _compute_website_url(self):
        super(Tender, self)._compute_website_url()
        for blog_post in self:
            blog_post.website_url = "/tender/%s" % (slug(blog_post))

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        """Expose readonly field metadata for non-draft records across UI views."""
        result = super().fields_get(allfields=allfields, attributes=attributes)

        active_id = self.env.context.get('active_id') or self.env.context.get('id')
        params = self.env.context.get('params') or {}
        active_id = active_id or params.get('id') or params.get('res_id')
        if not active_id:
            return result

        try:
            active_id = int(active_id)
        except (TypeError, ValueError):
            return result

        record = self.browse(active_id)
        if not record.exists() or record.state == 'draft':
            return result

        for field_name, field_def in result.items():
            if field_name == 'state':
                continue
            field_def['readonly'] = True
        return result

    def _ensure_allowed_state(self, allowed_states, action_name):
        invalid_records = self.filtered(lambda record: record.state not in allowed_states)
        if invalid_records:
            raise UserError(
                _("You can only use '%(action)s' when status is: %(states)s.")
                % {
                    'action': action_name,
                    'states': ', '.join(allowed_states),
                }
            )

    def _ensure_rfq_documents_present(self, action_name):
        """Block workflow transitions when RFQ documents are missing."""
        missing_docs_records = self.filtered(lambda record: not record.rfq_document_ids)
        if missing_docs_records:
            record_names = ', '.join(missing_docs_records.mapped('name'))
            raise UserError(
                _(
                    "You cannot use '%(action)s' because RFQ Documents are required before changing status. "
                    "Please upload RFQ Documents for: %(records)s"
                ) % {
                    'action': action_name,
                    'records': record_names,
                }
            )

    def _ensure_editable_in_draft(self, vals):
        """Lock record editing outside draft, except controlled workflow/system updates."""
        allowed_non_draft_fields = {
            'state',
            'is_tender_published',
            'is_published',
            'start_time',
            'website_published',
            'website_url',
        }
        if set(vals).issubset(allowed_non_draft_fields):
            return

        blocked_records = self.filtered(lambda record: record.state != 'draft')
        if blocked_records:
            raise UserError(
                _("You can only edit tender fields while status is Draft. Use status buttons for workflow changes.")
            )

    website_id = fields.Many2one('website', readonly=False, store=True)
    name = fields.Char(string='Tender Name', required=True,
                       help='The name of the tender')
    description = fields.Text(string='Description',
                              help='Description of the tender')
    category_id = fields.Many2one('tender.category',
                                  string='Category',
                                  help='Category of the tender')
    document_ids = fields.One2many('tender.document', 'tender_id',
                                   string='Documents',
                                   help='Documents related to the tender')
    rfq_document_ids = fields.One2many('tender.document', 'tender_rfq_id',
                                   string='RFQ Documents',
                                   help='RFQ Documents related to the tender')
    bid_ids = fields.One2many('tender.bid', 'tender_id', string='Bids',
                              help='Bids related to the tender')
    start_time = fields.Datetime(string='Tender Opening Date',
                                 help='Date and time when the tender will be '
                                      'opened')
    closing_date = fields.Datetime(string='Closing Date Time', required=True,
                                   help='Date and time when the tender will be '
                                        'closed')
    state = fields.Selection(
        [('draft', 'Draft'),
         ('submit', 'Submit'), ('verify', 'Verified'),
         ('approve', 'Approved'), ('rejected', 'Rejected'),
         ('open', 'Publish'), ('closed', 'Closed'),
         ('adjudication_in_progress', 'Adjudication in Progress'),
         ('awarded', 'Awarded')],
        string='Status', default='draft', help='Status of the tender')
    sequence_number = fields.Char(string='Sequence Number', readonly=True,
                                  copy=False, default=lambda self: _('New'))
    procurement_id = fields.Many2one('procurement.entity',
                                     string='Procurement Entity')
    company_id = fields.Many2one('res.company', string='Company',
                                 readonly=True,
                                 help="Company Name",
                                 default=lambda self: self.env.company)
    type = fields.Selection([('rfi', 'RFI'), ('rfp', 'RFP'),
                             ('rfq', 'RFQ')], string='Type', required=True,
                            help='The bid Type')
    is_tender_published = fields.Boolean(string='Is Tender Published')
    allow_bidding = fields.Boolean(
        string='Allow Bidding',
        default=False,
        help='If enabled, vendors can proceed to bid submission from the tender detail page.'
    )
    publish_date = fields.Date(
        string='Publish Date',
        help='Date when the tender will be published on the website'
    )

    # New fields for briefing session
    briefing_session = fields.Boolean(string="Is there a briefing session?", required=True)
    briefing_compulsory = fields.Boolean(string="Is it compulsory?")
    briefing_date_time = fields.Datetime(string="Briefing Date and Time")
    briefing_venue = fields.Char(string="Briefing Venue")

    @api.model
    def default_get(self, fields_list):
        """Keep Closing Date Time empty by default in create forms/lists."""
        defaults = super().default_get(fields_list)
        if 'closing_date' in fields_list:
            defaults['closing_date'] = False
        return defaults

    @api.model_create_multi
    def create(self, vals_list):
        """
        Override create method to generate sequence number for the tender.
        """
        for vals in vals_list:
            if vals.get('name'):
                name = vals['name']
            else:
                name = _('New Tender')

            year = fields.Datetime.now().year
            tender_type = ''
            closing_date = vals.get('closing_date')
            if closing_date:
                if isinstance(closing_date, str):
                    dt = datetime.strptime(closing_date, '%Y-%m-%d %H:%M:%S')
                else:
                    dt = closing_date  # already a datetime object
                year = dt.year

            company = self.env.company.name
            if company in ['Joburg Property Company Soc Ltd', 'JPC']:
                company_name = 'JPC'
            else:
                company_name = "PO"
            if vals.get('type') == 'rfq':
                sequence_number = self.env['ir.sequence'].next_by_code(
                    'tender.rfq')
                tender_type = "RFQ"
            elif vals.get('type') == 'rfp':
                sequence_number = self.env['ir.sequence'].next_by_code(
                    'tender.rfp')
                tender_type = "RFP"
            elif vals.get('type') == 'rfi':
                sequence_number = self.env['ir.sequence'].next_by_code(
                    'tender.rfi')
                tender_type = "RFI"
            else:
                sequence_number = self.env['ir.sequence'].next_by_code(
                    'tender.tender') or _('New')
                vals['sequence_number'] = '{} - {}'.format(name, sequence_number)

            vals['sequence_number'] = f'{tender_type}{sequence_number}/{year}FY/{company_name}'
        return super(Tender, self).create(vals_list)

    def write(self, vals):
        self._ensure_editable_in_draft(vals)
        return super(Tender, self).write(vals)

    def action_open(self):
        """
        Action to open the tender.
        """
        self._ensure_rfq_documents_present('Publish')
        self._ensure_allowed_state(['approve'], 'Publish')
        for record in self:
            record.is_tender_published = True
            if not record.start_time:
                record.start_time = fields.Datetime.now()
            record.state = 'open'
            record.is_published = True

    def get_list_url(self):
        """Method for create the url."""
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        urls_value = urls.url_join(
            base_url,
            'web#id=%s&model=tender.tender&view_type=tree' % self.id,
        )
        return urls_value

    def action_submit(self):
        self._ensure_rfq_documents_present('Submit')
        self._ensure_allowed_state(['draft'], 'Submit')
        self.state = 'submit'
        template = self.env.ref('tender_management.email_template_tender_submitted')
        template.send_mail(self.id, force_send=True)

    def action_verify(self):
        self._ensure_rfq_documents_present('Verify')
        self._ensure_allowed_state(['submit'], 'Verify')
        self.state = 'verify'
        template = self.env.ref('tender_management.email_template_tender_submitted')
        template.send_mail(self.id, force_send=True)

    def action_start_adjudication(self):
        self._ensure_rfq_documents_present('Adjudication in Progress')
        self._ensure_allowed_state(['closed'], 'Adjudication in Progress')
        self.state = 'adjudication_in_progress'

    def action_award(self):
        self._ensure_rfq_documents_present('Award')
        self._ensure_allowed_state(['adjudication_in_progress'], 'Award')
        self.state = 'awarded'

    def action_approve(self):
        self._ensure_rfq_documents_present('Approve')
        self._ensure_allowed_state(['verify'], 'Approve')
        self.state = 'approve'

    def action_reject(self):
        self._ensure_rfq_documents_present('Reject')
        self._ensure_allowed_state(['verify'], 'Reject')
        self.state = 'rejected'

    def action_reset_draft(self):
        self._ensure_rfq_documents_present('Reset to Draft')
        self._ensure_allowed_state(['submit', 'verify', 'approve', 'rejected', 'open'], 'Reset to Draft')
        for record in self:
            record.state = 'draft'
            record.is_tender_published = False
            record.is_published = False

    def check_tender_status(self):
        """
        Check the status of the tender and close it if the closing date is
        reached.
        """
        now = fields.Datetime.now()
        tenders_to_close = self.search(
            [('state', '=', 'open'), ('closing_date', '<=', now)])
        for tender in tenders_to_close:
            tender.state = 'closed'

    def get_tender_details(self):
        all_tender = self.search([])
        return {
            'all_tender': len(all_tender)}

    def all_tender_selection(self):
        all_tender = self.search([])
        return {
            'all_tender': len(all_tender)}

    def _get_access_action(self, access_uid=None, force_website=False):
        """ Instead of the classic form view, redirect to the post on website
        directly if user is an employee or if the post is published. """
        self.ensure_one()
        user = self.env['res.users'].sudo().browse(access_uid) if access_uid else self.env.user
        if not force_website and user.share and not self.sudo().website_published:
            return super(Tender, self)._get_access_action(access_uid=access_uid, force_website=force_website)
        return {
            'type': 'ir.actions.act_url',
            'url': self.website_url,
            'target': 'self',
            'target_type': 'public',
            'res_id': self.id,
        }