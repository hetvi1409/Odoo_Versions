# -*- coding: utf-8 -*-
from odoo import api,fields, models,_
from odoo.exceptions import ValidationError, AccessError, UserError
from markupsafe import Markup


class RequestFileWizard(models.TransientModel):
    _name = 'request.file.wizard'
    _description = 'Request File Wizard'

    submission_id = fields.Many2one('physical.document.submission', string="Submission")
    location_id = fields.Many2one('custom.physical.location', string="Location")
    receiver_id = fields.Many2one('res.users', string="Receiver")
    document_name = fields.Char(string="Document Name", required=False)
    requested_attachment_ids = fields.One2many(
        'request.file.wizard.line',
        'wizard_id',
        string="Select Attachments"
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        submission_id = self.env.context.get('default_submission_id')
        if submission_id:
            submission = self.env['physical.document.submission'].browse(submission_id)
            res['requested_attachment_ids'] = [
                (0, 0, {
                    'attachment_id': att.id,
                    'name': att.name,
                    'selected': False,
                }) for att in submission.attachment_ids
            ]
        return res

    def action_confirm_request(self):
        """Send email to receiver with requested document details"""
        self.ensure_one()
        # template = self.env.ref('documents_file_plan.request_file_email_template', raise_if_not_found=False)
        #
        # if template:
        #     template.send_mail(self.id, force_send=True)
        # else:
        selected_attachments = self.requested_attachment_ids.filtered('selected')
        if not selected_attachments:
            raise UserError("Please select at least one file to request.")

        files = ', '.join(selected_attachments.mapped('name'))

        base_url = self.get_base_url()
        record_url = f"{base_url}/web#id={self.submission_id.id}&model=physical.document.submission&view_type=form"

        mail_values = {
            'subject': f"File Request",

            'body_html': f"""
                <p>Dear {self.receiver_id.name},</p>
                <p>A file has been requested from location <b>{self.location_id.display_name}</b>.</p>
                <p>Requested Documents: <b>{files}</b></p>
                <p><a href="{record_url}" style="background-color:#28a745;padding:8px 16px;text-decoration:none;color:#fff;border-radius:5px;">Open Submission</a></p>
            """,
            'email_to': self.receiver_id.email,
            'email_from': self.submission_id.sender_id.email,
        }
        self.env['mail.mail'].create(mail_values).send()

        action = self.env['ir.actions.act_window']._for_xml_id(
            'documents_file_plan.physical_document_submission_action')
        base_url = self.submission_id.get_base_url()
        url = base_url + '/odoo/' + action.get('path') + '/' + str(self.submission_id.id)
        partner_ids = [self.submission_id.receiver_id.partner_id.id]
        self.submission_id.sudo().message_post(
            body=Markup(
                '<p>Dear {name},</p><p>A file has been requested from location <b>{location}</b></p><p>Requested Documents: <b>{files}</b></p><br/><p><a href={link} style="background-color: #E8B90E; padding: 8px 16px 8px 16px; text-decoration: none; color: #fff; border-radius: 5px; font-size:13px;">Open Document</a></p> <br/>').format(
                name=self.receiver_id.name,
                location=self.location_id.display_name,
                files=files,
                link=url
            ),
            partner_ids=partner_ids,
            subject="File Submission Application Approved",
            email_from=self.env.user.partner_id.email or '',
            message_type='notification',
            subtype_xmlid='mail.mt_comment',
        )

        if self.submission_id:
            self.submission_id.write({'state': 'requested_document'})

        return {'type': 'ir.actions.act_window_close'}


class RequestFileWizardLine(models.TransientModel):
    _name = 'request.file.wizard.line'
    _description = 'Request File Wizard Line'

    wizard_id = fields.Many2one('request.file.wizard', string="Wizard")
    attachment_id = fields.Many2one('ir.attachment', string="Attachment")
    name = fields.Char(string="File Name")
    selected = fields.Boolean(string="Select")

