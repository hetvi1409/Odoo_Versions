from odoo import models, fields, api, _
from werkzeug import urls


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
        # 'website.cover_properties.mixin',
        'website.searchable.mixin',
    ]

    def _compute_website_url(self):
        super(Tender, self)._compute_website_url()
        for blog_post in self:
            blog_post.website_url = "/tender/%s" % (self.env['ir.http']._slug(blog_post))

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
    bid_ids = fields.One2many('tender.bid', 'tender_id', string='Bids',
                              help='Bids related to the tender')
    start_time = fields.Datetime(string='Opening Date Time',
                                 help='Date and time when the tender will be '
                                      'opened')
    closing_date = fields.Datetime(string='Closing Date Time', required=True,
                                   help='Date and time when the tender will be '
                                        'closed')
    state = fields.Selection(
        [('draft', 'Draft'),
         ('submit', 'Submit'), ('verify', 'Verified'),
         ('approve', 'Approved'), ('rejected', 'Rejected'),
         ('open', 'Publish'), ('closed', 'Closed')],
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
                             ('rfq', 'RFQ')], string='Type',
                            help='The bid Type')
    is_tender_published = fields.Boolean(string='Is Tender Published')

    # New fields for briefing session
    briefing_session = fields.Boolean(string="Is there a briefing session?", required=True)
    briefing_compulsory = fields.Boolean(string="Is it compulsory?")
    briefing_date_time = fields.Datetime(string="Briefing Date and Time")
    briefing_venue = fields.Char(string="Briefing Venue")

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
            sequence_number = self.env['ir.sequence'].next_by_code(
                'tender.tender') or _('New')
            vals['sequence_number'] = '{} - {}'.format(name, sequence_number)
        return super(Tender, self).create(vals_list)

    def action_open(self):
        """
        Action to open the tender.
        """
        for record in self:
            record.is_tender_published = True
            record.start_time = fields.Datetime.now()
            record.state = 'open'
            record.is_published = True


    def get_list_url(self):
        """Method for create the url."""
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        Urls = urls.url_join(base_url,
                             'web#id=%s&model=tender.tender&view_type=tree' % self.id)
        return Urls

    def action_submit(self):
        self.state = 'submit'
        template = self.env.ref('tender_management.email_template_tender_submitted')
        template.send_mail(self.id, force_send=True)

    def action_verify(self):
        self.state = 'verify'
        template = self.env.ref('tender_management.email_template_tender_submitted')
        template.send_mail(self.id, force_send=True)

    def action_approve(self):
        self.state = 'approve'

    def action_reject(self):
        self.state = 'reject'

    def check_tender_status(self):
        """
        Check the status of the tender and close it if the closing date is
        reached.
        """
        now = fields.Datetime.now()
        tenders_to_close = self.search(
            [('state', '!=', 'closed'), ('closing_date', '<=', now)])
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