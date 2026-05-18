import logging
from odoo import models, api

_logger = logging.getLogger(__name__)

class WhatsAppTicket(models.Model):
    _inherit = 'whatsapp.account'

    def _process_messages(self, value):
        """Extend message processing to create Helpdesk Tickets."""
        super()._process_messages(value)  # Ensure we keep the original logic.

        # Extract message information
        for message in value.get('messages', []):
            sender_mobile = message['from']
            sender_name = value.get('contacts', [{}])[0].get('profile', {}).get('name')
            message_text = message.get('text', {}).get('body', '')

            # Check if a ticket already exists for this sender
            existing_ticket = self.env['helpdesk.ticket'].sudo().search([
                ('contact_number', '=', sender_mobile),
                ('stage_id.is_close', '=', False)
            ], limit=1)

            if existing_ticket:
                _logger.info(f"Updating existing ticket for {sender_mobile}")
                existing_ticket.sudo().write({
                    'description': f"{existing_ticket.description}\n\nNew Message: {message_text}"
                })
            else:
                _logger.info(f"Creating new helpdesk ticket for {sender_mobile}")
                self.env['helpdesk.ticket'].sudo().create({
                    'team_id': self.env.ref('customer_care.customer_carehelpdesk_team').id,
                    'name': f"WhatsApp Inquiry from {sender_name or sender_mobile}",
                    'description': message_text,
                    'channel': 'whatsapp',
                    'contact_number': sender_mobile,
                    'enquirer_name': sender_name or 'Unknown',
                })
