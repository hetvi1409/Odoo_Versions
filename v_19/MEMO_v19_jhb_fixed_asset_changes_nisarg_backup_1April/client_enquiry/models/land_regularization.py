from odoo import api, fields, models
from werkzeug import urls

class LandRegularization(models.Model):
    """Land Regularization"""
    _name = 'land.regularization'
    _description = 'Land Regularization'
    _rec_name = 'type'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name')
    type = fields.Selection([('church','Church'),('shop','Shop')])
    date_regularisation = fields.Date(string='Date')
    state = fields.Selection([('requested_doc','Request additional Documents'), ('review_doc','Review Documents'),('send_doc','Send Documents')],default='draft')
    requester_info = fields.Char(string='Requester Info')
    requester_infos = fields.Many2one('res.users',string='Requester Info')
    enquiry_id = fields.Many2one('client.enquiry')
    assessment_id = fields.Many2one('enquiry.assessment')
    assessment_result = fields.Selection([('supported', 'Supported'), ('not_supported','Not Supported')])
    requested_doc = fields.One2many('request.document','request_doc_id')
    supporting_doc = fields.Many2many('ir.attachment','supporting_doc_id',string='Supporting Document')
    review_doc = fields.Many2many('ir.attachment','review_attachment_id',string='Review Document')
    deed_details_id = fields.One2many('deed.details','deed_details_id',string='Deed')
    hand_over_ids = fields.One2many('hand.over','hand_over_id',string='Hand Over')
    case_handling_ids = fields.One2many('case.handling','case_handling_id',string='Case Handling')
    church_const_doc = fields.Many2many('ir.attachment',
                                        'church_con_attach_rel',
                                        string='Constitution')
    church_photo_doc = fields.Many2many('ir.attachment',
                                        'church_pho_attach_rel',
                                        string='Photos')
    church_corner_doc = fields.Many2many('ir.attachment',
                                         'church_cor_attach_rel',
                                         string='Cornerstone')
    church_bishop_doc = fields.Many2many('ir.attachment',
                                         'church_bis_attach_rel',
                                         string="Bishop's letter")
    church_other_doc = fields.Many2many('ir.attachment',
                                         'church_other_attach_rel',
                                         string="Other Documents")
    shop_license_doc = fields.Many2many('ir.attachment',
                                        'shop_lice_attach_rel',
                                        string="License")
    shop_permit_doc = fields.Many2many('ir.attachment',
                                       'shop_per_attach_rel',
                                       string="Permit")
    shop_id_doc = fields.Many2many('ir.attachment', 'shop_id_atth_rel',
                                   string="ID")
    shop_death_doc = fields.Many2many('ir.attachment', 'shop_dea_attach_rel',
                                      string="Death Certificate")
    shop_affidavit_doc = fields.Many2many('ir.attachment',
                                          'shop_affi_attach_rel',
                                          string="Affidavit")
    shop_other_doc = fields.Many2many('ir.attachment',
                                        'shop_other_attach_rel',
                                        string="Other Documents")
    user_id = fields.Many2one('res.users', string='Assignee')
    last_stage_updated = fields.Datetime('Last Stage Updated', readonly=True)

    def get_list_url(self):
        """Returns the url for the list view"""
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        Urls = urls.url_join(base_url,
                             'web#id=%s&model=land.regularization&view_type=form' % self.id)
        return Urls

    @api.model
    def create(self, values):
        res = super(LandRegularization, self).create(values)
        res.last_stage_updated = fields.Datetime.now()
        return res

    def action_request_document(self):
        self.state = 'requested_doc'

    def action_review_document(self):
        self.state = 'review_doc'
        mail_template = self.env.ref(
            'client_enquiry.email_template_review_document')
        mail_template.send_mail(self.id,
                                force_send=True)

    def action_send_document(self):
        self.state = 'send_doc'


class RequestDocument(models.Model):
    """Request Document"""
    _name = 'request.document'

    request_doc_id = fields.Many2one('land.regularization')
    land_type = fields.Selection([('church','Church'),('shop','Shop')], related='request_doc_id.type',store=True)
    department = fields.Selection([('entitlement','Entitlement'),('province','Province')],string='Department')
    document_type_church = fields.Selection(
        [('constitution', 'Constitution'), ('photos', 'Photos'),
         ('cornerstone', 'Cornerstone'), ('bishop_letter', "Bishop's Letter")],
        string='Document Type')
    document_type_shop = fields.Selection(
        [('license', 'License'), ('permit', 'Permit'), ('id_doc', 'ID'),
         ('death_certificate', "Death Certificate"),
         ('affidavit', 'Affidavit')], string='Document')
    department_id = fields.Many2one('hr.department',string='Department')
    document_type = fields.Char(string='Document Type')
    document_ids = fields.Many2many('ir.attachment','request_doc_ids',string='Additional Documents')
    approve = fields.Boolean(string='Approved')

class DeedDetails(models.Model):
    """Deed Details"""
    _name = 'deed.details'

    deed_details_id = fields.Many2one('land.regularization')
    deed_number = fields.Char(string='Deed Number')
    deed_date = fields.Date(string='Deed Date')

class HandOver(models.Model):
    """Hand Over"""
    _name = 'hand.over'

    hand_over_id = fields.Many2one('land.regularization')
    hand_date = fields.Date(string='Date')
    participants = fields.Many2one('res.users',string='Participants')

class CaseHandling(models.Model):
    """Case Handling"""
    _name = 'case.handling'

    case_handling_id = fields.Many2one('land.regularization')
    year = fields.Char(string='Year')
    procedure = fields.Char(string='Procedure')
    procedures = fields.Selection([('entitlement','Entitlement'),('province','Province')],string='Procedure')
