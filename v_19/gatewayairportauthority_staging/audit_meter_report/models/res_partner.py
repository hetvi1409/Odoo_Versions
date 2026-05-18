from odoo import api, fields, models , _
import zipfile
import io
import base64
import logging
_logger = logging.getLogger(__name__)

class AuditLines(models.Model):
    """Adding new features for audit line"""
    _name = "audit.line"

    partner_id = fields.Many2one('res.partner')
    audit_user_id = fields.Many2one('res.users')
    inspection_status = fields.Selection([('Successful','Successful'),('Failed','Failed')])
    note = fields.Html()



class ResPartner(models.Model):
    """Adding new features for audit meter"""
    _inherit = "res.partner"

    route_name = fields.Char(string="Route Name")
    audit_date = fields.Datetime(string="Audit Date")
    sg_label = fields.Char(string="SG Label")
    twentyone_key = fields.Char(string="TwentyOne Key")
    address = fields.Text(string="Address")
    can_audit = fields.Boolean(string="Can Audit")
    can_audit_remark = fields.Text(string="Can Audit Remark")
    suspected_tamper = fields.Boolean(string="Suspected Tamper")
    suspected_tamper_reason = fields.Text(string="Suspected Tamper Reason")
    owner_surname = fields.Char(string="Owner Surname")
    owner_account_number = fields.Char(string="Owner Account Number")
    dwelling_type = fields.Selection(
        [('residential', 'Residential'), ('commercial', 'Commercial')],
        string="Dwelling Type"
    )
    meter_position = fields.Char(string="Meter Position")
    meter_type = fields.Char(string="Meter Type")
    meter_phases = fields.Char(string="Meter Phases")
    meter_sealed = fields.Boolean(string="Meter Sealed")
    meter_cover_sealed = fields.Char(string="Meter Cover Sealed")
    ct_ratio = fields.Char(string="CT/Ratio")
    breaker_size = fields.Char(string="Breaker Size")
    remarks = fields.Text(string="Remarks")
    street_number = fields.Char(string="Street Number")
    street_name = fields.Char(string="Street Name")
    suburb = fields.Char(string="Suburb")
    city = fields.Char(string="City")
    country = fields.Char(string="Country")
    zip_code = fields.Char(string="Zip Code")
    audit_line_count = fields.Integer(compute="_compute_audit_line_count")

    meter_box_outside_photo = fields.Binary(string="Meter Box Outside Photo")
    renewable_photo = fields.Binary(string="Renewable Photo")
    meter_seals_photo = fields.Binary(string="Meter Seals Photo")
    meter_box_inside_photo = fields.Binary(string="Meter Box Inside Photo")
    meter_photo = fields.Binary(string="Meter Photo")
    suspected_tamper_photo = fields.Binary(string="Suspected Tamper Photo")
    dwelling_photo = fields.Binary(string="Dwelling Photo")
    audit_line_count = fields.Integer(
        string="Audit Line Count",
        compute="_compute_audit_line_count",
        store=True
    )
    audit_line_ids = fields.One2many('audit.line','partner_id')
    x_studio_selection_field_1oh_1i5pnt5e5 = fields.Selection([
        ('audited', 'Audited'),
        ('not_audited', 'Not Audited'),('partially_verified', 'Partially Verified')
    ], string="Audit Status")

    def _compute_audit_line_count(self):
        for record in self:
            record.audit_line_count = len(self.env['audit.line'].search([('partner_id','=',record.id)]))


    def action_view_audit_lines(self):
        return {
            'name': _('Audit Lines'),
            'view_mode': 'list,form',
            'res_model': 'audit.line',
            'domain': [('partner_id', '=', self.id)],
            'type': 'ir.actions.act_window',
        }

    # def update_customer_status(self):
    #     partners = self.sudo().search([('x_studio_selection_field_1oh_1i5pnt5e5','=','audited'),('user_id','=',False)])
    #     for partner in partners:
    #         partner.user_id = partner.create_uid

    @api.depends('audit_line_ids')
    def _compute_audit_line_count(self):
        for partner in self:
            partner.audit_line_count = self.env['audit.line'].search_count([('partner_id', '=', partner.id)])

    def action_create_audit_line(self):
        # Opens a new form to create an audit line for the current partner

        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Audit Line',
            'res_model': 'audit.line',
            'view_mode': 'form',
            'view_id': False,
            'target': 'current',
            'context': {
                'default_partner_id': self.id  # Pre-fill partner_id with the current partner
            },
        }

    # @api.onchange('x_studio_inspection_success_report')
    # def onchange_x_studio_inspection_success_report(self):
    #     """"On change the fields it changes te values in x_studio_selection_field_1oh_1i5pnt5e5"""
    #     if self.x_studio_inspection_success_report == 'Successful':
    #         self.x_studio_selection_field_1oh_1i5pnt5e5 = 'audited'
    #     elif self.x_studio_inspection_success_report == 'Failed':
    #         self.x_studio_selection_field_1oh_1i5pnt5e5 = 'partially_verified'

    @api.model
    def action_inspection_status_check(self):
        """Check the inspection status"""
        meter_audit = self.env['res.partner'].search([('x_studio_inspection_success_report', '=', 'Successful'), ('x_studio_selection_field_1oh_1i5pnt5e5', '!=', 'audited')])
        for rec in meter_audit:
            rec.x_studio_selection_field_1oh_1i5pnt5e5 = 'audited'
        audit_meter = self.env['res.partner'].search([('x_studio_inspection_success_report', '=', 'Failed'), ('x_studio_selection_field_1oh_1i5pnt5e5', '!=', 'partially_verified')])
        for rec in audit_meter:
            rec.x_studio_selection_field_1oh_1i5pnt5e5 = 'partially_verified'

    def action_download_pdfs(self):
        docids = self.env.context.get('active_ids')  # Get the active IDs from the context
        zip_filename = 'audit_reports.zip'

        # Redirect to the custom controller for download
        return {
            'type': 'ir.actions.act_url',
            'url': f'/download/pdf_reports?filename={zip_filename}&docids={",".join(map(str, docids))}',
            'target': 'self',
        }

    def generate_zip_of_pdfs(self, docids):
        # Create in-memory ZIP
        zip_buffer = io.BytesIO()
        docs = self.browse(docids)

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            for doc in docs:
                try:

                    # pdf = self.env['ir.actions.report'].with_context(force_report_rendering=True)._render_qweb_pdf(
                    #     'audit_meter_report.action_report_partner_custom', res_ids=doc.id)
                    # # Extract PDF content and name
                    # pdf_content = pdf[0]  # This is the bytes content of the PDF
                    # pdf_name = f'report_{doc.id}.pdf'

                    # Fetch the binary image content for each docid
                    image_content = doc.x_studio_property_image  # Assuming this contains the image data as bytes
                    if not image_content:
                        raise ValueError(f"No image content found for document ID: {doc.id}")

                    try:
                        image_content = base64.b64decode(image_content)
                    except Exception as decode_error:
                        raise ValueError(f"Error decoding base64 content for docid {doc.id}: {decode_error}")

                    # Define the image name in the ZIP
                    image_name = f'image_{doc.id}.png'  # Assuming it's a PNG image, adjust the extension as needed

                    # Add the image directly to the ZIP archive
                    zf.writestr(image_name, image_content)

                except Exception as e:
                    # Log the error or handle it appropriately
                    _logger.error(f"Error adding image for docid {doc.id}: {e}")

        # Ensure to seek back to the start of the buffer before returning
        zip_buffer.seek(0)
        return zip_buffer



