# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class TenderPublishWizard(models.TransientModel):
    """Wizard for publishing/advertising tender"""
    _name = 'sagovtender.publish.wizard'
    _description = 'Publish Tender Wizard'

    tender_id = fields.Many2one(
        'sagovtender.tender',
        string='Tender',
        required=True,
        default=lambda self: self.env.context.get('active_id'),
        options={'no_create': True, 'no_quick_create': True, 'no_create_edit': True}
    )
    advertisement_text = fields.Html(
        string='Advertisement Text',
        required=True
    )
    platform_ids = fields.Many2many(
        'sagovtender.advert.platform',
        string='Advertisement Platforms',
        required=True
    )
    closing_date = fields.Datetime(
        string='Closing Date/Time',
        required=True
    )
    opening_date = fields.Datetime(
        string='Opening Date/Time'
    )
    send_notification = fields.Boolean(
        string='Send Email Notifications',
        default=True
    )
    notification_message = fields.Text(
        string='Notification Message'
    )

    @api.onchange('tender_id')
    def _onchange_tender(self):
        """Load tender details"""
        if self.tender_id:
            self.advertisement_text = self.tender_id.advertisement_text or self._generate_advertisement()
            self.closing_date = self.tender_id.closing_date
            self.opening_date = self.tender_id.opening_date

    def _generate_advertisement(self):
        """Generate default advertisement text"""
        tender = self.tender_id
        return f"""
        <h3>TENDER ADVERTISEMENT</h3>
        <p><strong>Tender Number:</strong> {sagovtender.name}</p>
        <p><strong>Tender Title:</strong> {sagovtender.title}</p>
        <p><strong>Description:</strong></p>
        {sagovtender.description or ''}
        <p><strong>Closing Date:</strong> {sagovtender.closing_date}</p>
        <p><strong>Department:</strong> {sagovtender.department_id.name}</p>
        """

    def action_publish(self):
        """Publish tender"""
        self.ensure_one()

        # Update tender
        self.tender_id.write({
            'advertisement_text': self.advertisement_text,
            'advertisement_platform_ids': [(6, 0, self.platform_ids.ids)],
            'closing_date': self.closing_date,
            'opening_date': self.opening_date,
            'state': 'advertised',
            'publication_date': fields.Date.today()
        })

        # Send notifications if requested
        if self.send_notification:
            self._send_notifications()

        self.tender_id.message_post(
            body='Tender published/advertised.'
        )

        return {'type': 'ir.actions.act_window_close'}

    def _send_notifications(self):
        """Send email notifications"""
        # TODO: Implement email notifications to registered vendors
        pass
