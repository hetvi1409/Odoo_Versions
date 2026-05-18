from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError
from odoo.tools import html_escape
from werkzeug import urls
import logging
_logger = logging.getLogger(__name__)


class EmergencyHousing(models.Model):
    """Emergency Housing"""
    _name = "housing.emergency"
    _description = "Housing Emergency"
    _inherit = ['mail.activity.mixin', 'mail.thread']

    province_id = fields.Many2one("res.province", string="Province", required=True)
    name = fields.Char(string="Name")
    state = fields.Selection([('draft', 'Draft'), ('submit', 'Submitted'), ('review', "Review"), ('approve', 'Approve'), ('reject', 'Rejected')], default="draft",tracking=True,)
    department_id = fields.Many2one(
        'hr.department', string='Department', copy=True)
    municipality_id = fields.Many2one('res.municipality',string='Municipality')
    date = fields.Date(string="Date Of Disaster", required=True)
    latitude = fields.Float(digits=(10, 7), copy=False)
    longitude = fields.Float(digits=(10, 7), copy=False)

    street = fields.Char(string="Street", help="Name of the street")
    street2 = fields.Char(string="Street 2", help="Additional address line")
    postal_code = fields.Char(string="Postal Code", help="Postal code")
    city_id = fields.Many2one('res.country.city', string="City",
                              help="Name of the city")
    physical_street = fields.Char(string="Street", help="Name of the street")
    physical_street2 = fields.Char(string="Street 2", help="Additional address line")
    physical_postal_code = fields.Char(string="Postal Code", help="Postal code")
    physical_city_id = fields.Many2one('res.country.city', string="City",
                              help="Name of the city")

    partner_id = fields.Many2one("res.partner", string="Contact Person Name")
    surname = fields.Char("Surname")
    designation = fields.Char(string="Designation")
    telephone = fields.Char(string="Telephone")
    fax_number = fields.Char(string="Fax Number")
    email = fields.Char(string="Email")

    emergency_housing_situation = fields.Char(string="Emergency Housing Situation",
                                              help="Brief description of the emergency housing situation, e.g., flood, fire, or other reasons.")
    location_and_cause = fields.Char(string="Location and Cause", help="Description of location and cause of the emergency housing situation (attach location map).")
    level_destitution = fields.Char(string="Level of Destitution/Displacement", help="Describe level of destitution /displacement and impact on persons.")
    nature_scope = fields.Char(string="Nature and Scope", help="Nature, scope, and extent of the emergency housing situation:")
    mec_agreed = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Has the MEC agreed to this application", required=False)
    informed_disaster = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Provincial Disaster Management Centre been informed of this application")

    number_affected_person = fields.Integer(string="The number of affected persons, households, and families")
    income_profile = fields.Float(string="An income profile of the families")
    number_person_unemployed = fields.Integer(string="The number of persons unemployed.")
    reason_relocation = fields.Char(string="Whether relocation / resettlement is required, and, if so, full reasons")

    is_land = fields.Boolean(string="Land is required")
    settlement_id = fields.Many2one("house.settlement", string="Whether the current settlement")
    before_settlement_id = fields.Many2one("house.settlement", string="Settlement pattern before the occurrence of the event which caused the emergency housing situation")
    property_nature_id = fields.Many2one('property.nature', string="Nature of Property Type")
    consulted = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string="Have the affected persons been consulted?")
    consent_obtained = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string="Has their consent and cooperation been obtained?")
    line_ids = fields.One2many('housing.line', 'emergency_id', string="Consulted Details")

    land_street = fields.Char(string="Street", help="Name of the street")
    land_street2 = fields.Char(string="Street 2",
                                   help="Additional address line")
    land_postal_code = fields.Char(string="Postal Code", help="Postal code")
    land_city_id = fields.Many2one('res.country.city', string="City",
                                       help="Name of the city")

    land_ownership_id = fields.Many2one('res.partner',
        string="Ownership of the Land"
    )

    land_availability_basis = fields.Selection([
        ('donation', 'Donation'),
        ('lease', 'Lease'),
        ('purchase', 'Purchase'),
        ('other', 'Other')
    ], string="Basis for Land Availability")
    housing = fields.Selection([('housing_development', 'Housing Development'),
                                ('housing_purposes', 'Housing Purposes')], string="Housing Development/Housing Purposes")
    timeframe = fields.Float(string="Timeframe of preparing for are settlement")
    cost = fields.Float(string="Cost of preparing for are settlement")

    municipal_services = fields.Char(string="Municipal Services required")
    reasons = fields.Char(string="Detailed reasons for the necessity to provide")
    estimated_costs = fields.Float(string="Estimated costs of, and the manner in which it is intended to install")

    basic_services_details = fields.Text(
        string="Details of basic municipal services (tariffs, timelines, scope)")
    bulk_services_details = fields.Text(
        string="Details of bulk/connector services (infrastructure readiness, source, timelines)")

    no_of_person_shelter = fields.Char(string="the number of persons for whom the shelters will be erected")
    nature_shelter = fields.Integer(string="The nature and description of the proposed structure that will be erected")
    no_of_shelter = fields.Integer(string="The number of shelters to be erected")
    material_ids = fields.Many2many('product.product', string="All material required for the construction of the shelter")
    estimated_cost_shelter = fields.Float(string="Estimated costs involved in the provision of shelter")
    manner_provide_shelter = fields.Char(string="Manner in which it is intended to provide shelter")
    other_cost_shelter = fields.Float(string="Others costs required to execute the project")

    actions_taken_ids = fields.One2many(
        'emergency.housing.action', 'case_id',
        string="Actions Taken"
    )
    interest_party_ids = fields.One2many(
        'emergency.housing.interest', 'case_id',
        string="Interested Persons or Institutions"
    )
    disaster_declared = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ], string="Declared as Disaster (Disaster Management Act, 2002)?",
        )
    action_description = fields.Text(string="Description of Action",)
    brief_description = fields.Text(string="Brief Description for Institutional Capacity")
    financial_brief_description = fields.Text(string="Brief Description for Financial Capacity")
    cash_flow_funds = fields.Char(string="Cash Flow Projections outlining the utilisation of the funds")
    capacity_augmentation_plan = fields.Text(
        string="Plan to Augment Capacity (if insufficient)")

    linked_to_any_other_programmes = fields.Char(string="Linked to any other public or private programmes, housing or otherwise")
    detailed_plan_solution = fields.Char(string="Detailed plan on achieving a permanent housing solution")

    further_information = fields.Char(string="further information relating to the emergency housing situation")

    @api.model
    def create(self, values):
        """Method for generating consumer number for the contacts"""
        values['name'] = self.env['ir.sequence'].next_by_code(
            'housing.emergency')
        res = super(EmergencyHousing, self).create(values)
        return res

    def _check_group(self, group_xmlid):
        if not self.env.user.has_group(group_xmlid):
            raise AccessError(_("You are not allowed to perform this action."))

    def _record_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        Urls = urls.url_join(base_url,
                             'web#id=%s&model=housing.emergency&view_type=form' % self.id)
        return Urls

    def _queue_email(self, email_to, subject, body_html):
        if not email_to:
            return
        email_from = (
                self.env.user.company_id.email
                or self.env.user.email
                or "noreply@localhost"
        )
        try:
            self.env["mail.mail"].sudo().create(
                {
                    "subject": subject,
                    "body_html": body_html,
                    "email_to": email_to,
                    "email_from": email_from,
                    "auto_delete": False,
                }
            )
        except Exception:
            _logger.exception("Failed to queue email for housing.emergency %s", self.id)

    def _group_emails(self, group_xmlid):
        group = self.env.ref(group_xmlid, raise_if_not_found=False)
        if not group:
            return []
        emails = group.users.filtered(lambda u: u.active).mapped("partner_id.email")
        return sorted({e for e in emails if e})

    def _email_group(self, group_xmlid, subject, body_html):
        emails = self._group_emails(group_xmlid)
        self._queue_email(",".join(emails), subject, body_html)

    def _email_applicant(self, subject, body_html):
        self.ensure_one()
        self._queue_email(self.email, subject, body_html)

    # Called by portal controller after create
    def portal_mark_submitted(self):
        self.ensure_one()
        self.write({"state": "submit"})
        self.message_post(body=_("Application submitted via Website Portal."))

        url = self._record_url()
        subject = _("New Emergency Housing Grant Application: %s") % (self.name or "")
        body = "<p>%s</p><p><a href='%s'>Open Application</a></p>" % (
            html_escape(_("A new application was submitted and needs Municipality review.")),
            html_escape(url),
        )
        self._email_group(
            "emergency_housing.group_emergency_housing_municipality_officer",
            subject,
            body,
        )

        if self.email:
            self._email_applicant(
                _("Your application %s was received") % (self.name or ""),
                "<p>%s</p><p>%s: <strong>%s</strong></p>"
                % (
                    html_escape(_("Thank you. We received your Emergency Housing Grant application.")),
                    html_escape(_("Application Number")),
                    html_escape(self.name or ""),
                ),
            )

    # Internal: municipality can also submit drafts created in backend
    def action_submit(self):
        for rec in self:
            rec._check_group("emergency_housing.group_emergency_housing_municipality_officer")
            if rec.state != "draft":
                raise UserError(_("Only Draft applications can be submitted."))
            rec.write({"state": "submit"})
            rec.message_post(body=_("Application submitted by %s.") % rec.env.user.name)

    # Municipality: forward to province
    def action_review(self):
        for rec in self:
            rec._check_group("emergency_housing.group_emergency_housing_municipality_officer")
            if rec.state != "submit":
                raise UserError(_("Only Submitted applications can be forwarded to Province."))
            rec.write({"state": "review"})
            rec.message_post(
                body=_("Reviewed by Municipality and forwarded to Province by %s.") % rec.env.user.name)

            url = rec._record_url()
            rec._email_group(
                "emergency_housing.group_emergency_housing_province_officer",
                _("Emergency Housing Grant %s: Ready for Province Approval") % (rec.name or ""),
                "<p>%s</p><p><a href='%s'>Open Application</a></p>"
                % (html_escape(_("A Municipality has reviewed an application; Province approval is required.")),
                   html_escape(url)),
            )

    # Municipality: send feedback to applicant (keeps state as 'submit')
    def municipality_send_feedback(self, comments):
        self.ensure_one()
        self._check_group("emergency_housing.group_emergency_housing_municipality_officer")
        if self.state != "submit":
            raise UserError(_("Feedback can only be sent while the application is Submitted."))

        safe_comments = html_escape(comments or "")
        self.message_post(body=_("Municipality feedback sent to applicant:<br/>%s") % safe_comments)

        if self.email:
            self._email_applicant(
                _("Feedback on your Emergency Housing Grant application %s") % (self.name or ""),
                "<p>%s</p><p><strong>%s</strong></p><p>%s</p>"
                % (
                    html_escape(_("Municipality has reviewed your application and requests the following:")),
                    html_escape(_("Comments")),
                    safe_comments,
                ),
            )

    # Province: approve
    def action_approved(self):
        for rec in self:
            rec._check_group("emergency_housing.group_emergency_housing_province_officer")
            if rec.state != "review":
                raise UserError(_("Only Municipality-Reviewed applications can be approved."))
            rec.write({"state": "approve"})
            rec.message_post(body=_("Approved by Province (%s).") % rec.env.user.name)

            if rec.email:
                rec._email_applicant(
                    _("Your Emergency Housing Grant application %s is approved") % (rec.name or ""),
                    "<p>%s</p><p>%s: <strong>%s</strong></p>"
                    % (
                        html_escape(_("Your application has been approved by the Province.")),
                        html_escape(_("Application Number")),
                        html_escape(rec.name or ""),
                    ),
                )

    # Province: reject
    def action_rejected(self):
        for rec in self:
            rec._check_group("emergency_housing.group_emergency_housing_province_officer")
            if rec.state != "review":
                raise UserError(_("Only Municipality-Reviewed applications can be rejected."))
            rec.write({"state": "reject"})
            rec.message_post(body=_("Rejected by Province (%s).") % rec.env.user.name)

            if rec.email:
                rec._email_applicant(
                    _("Your Emergency Housing Grant application %s is rejected") % (rec.name or ""),
                    "<p>%s</p><p>%s: <strong>%s</strong></p>"
                    % (
                        html_escape(_("Your application has been rejected by the Province.")),
                        html_escape(_("Application Number")),
                        html_escape(rec.name or ""),
                    ),
                )

    def action_review_feedback(self):
        self.ensure_one()
        self._check_group("emergency_housing.group_emergency_housing_municipality_officer")
        if self.state != "submit":
            raise UserError(_("Feedback can only be sent while the application is Submitted."))
        return {
            "type": "ir.actions.act_window",
            "name": _("Send Feedback"),
            "view_mode": "form",
            "target": "new",
            "res_model": "housing.grant.review",
            "context": {"default_case_id": self.id},
        }

    # def action_submit(self):
    #     """Action Submit"""
    #     self.state = "submit"
    #     self.message_post(
    #         body=_('Emergency Housing Grant is submitted by %s',
    #                self.env.user.name))
    #
    # def action_review(self):
    #     """Action Review"""
    #     self.state = "review"
    #     self.message_post(
    #         body=_('Emergency Housing Grant is reviewed by %s',
    #                self.env.user.name))
    #
    # def action_review_feedback(self):
    #     """Review Feedback"""
    #     self.ensure_one()
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Review',
    #         'view_mode': 'form',
    #         'target': 'new',
    #         'res_model': 'housing.grant.review',
    #         'context': {
    #             'default_case_id': self.id
    #         }
    #     }
    # def action_approved(self):
    #     """Action approve"""
    #     self.state = "approve"
    #     self.message_post(
    #         body=_('Emergency Housing Grant is approved by %s',
    #                self.env.user.name))
    #
    # def action_rejected(self):
    #     """Action Reject"""
    #     self.state = "reject"
    #     self.message_post(
    #         body=_('Emergency Housing Grant is rejected by %s',
    #                self.env.user.name))

    def action_reset_draft(self):
        """Action Draft"""
        self.state = "draft"

class EmergencyHousingLine(models.Model):
    """Emergency Housing"""
    _name = "housing.line"
    _description = "Housing Line"

    emergency_id = fields.Many2one('housing.emergency', string="Emergency")
    comments = fields.Text(string="Comments")
    time_frame = fields.Float(string="Time frame for each step")

class EmergencyHousingAction(models.Model):
    _name = 'emergency.housing.action'
    _description = 'Actions Taken to Address Emergency Housing Situation'

    case_id = fields.Many2one('housing.emergency', string="Emergency Case", required=True, ondelete='cascade')
    actor_id = fields.Many2one('res.partner', string="Person/Institution Responsible")
    description = fields.Text(string="Description of Action")
    date_taken = fields.Date(string="Date of Action")
    status = fields.Selection([
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string="Status", default="completed")


class InterestedParty(models.Model):
    _name = 'emergency.housing.interest'
    _description = 'Interested Persons or Institutions'

    case_id = fields.Many2one('housing.emergency', string="Emergency Case",
                              required=True, ondelete='cascade')

    name = fields.Char(string="Name of Person or Institution", required=True)
    party_type = fields.Selection([
        ('person', 'Person'),
        ('institution', 'Institution')
    ], string="Type", required=True)
    interest_details = fields.Text(string="Details of Interest", required=True)
    remarks = fields.Text(string="Additional Remarks")


