import requests
import logging
from odoo import models, fields, api
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class FacebookConfig(models.Model):
    _name = 'facebook.config'
    _description = 'Facebook Integration Config'

    name = fields.Char(string='App Name', required=True)
    app_id = fields.Char(string='Facebook App ID', required=True)
    app_secret = fields.Char(string='Facebook App Secret', required=True)
    access_token = fields.Char(string='Access Token', readonly=True)

    def create_ticket_from_fb_message(self):
        """
        Fetch and store a long-lived page access token.
        """
        if not self.app_id or not self.app_secret:
            raise ValidationError("Missing Facebook App ID or App Secret.")

        try:
            r = requests.get("https://graph.facebook.com/v7.0/me/accounts",
                             params={'access_token': self.access_token}).json()
            if r.get('error'):
                raise ValidationError(r['error']['message'])
            if not r.get('data'):
                return
            _logger.info("page data: %s",  r['data'])
            for p in r['data']:
                # create ticket for facebook message
                url = f"https://graph.facebook.com/v7.0/{p.get('id')}/conversations"
                params = {
                    'access_token': p.get('access_token'),
                    'fields': 'id,messages{message,from,created_time}'
                }

                response = requests.get(url, params=params).json()
                _logger.info("create ticket for facebook message response: %s", response)
                if response.get('error'):
                    _logger.error(f"Error fetching Messenger conversations: {response['error']['message']}")
                    return
                conversations = response.get('data', [])
                _logger.info("create ticket for facebook message conversations: %s", conversations)
                for conversation in conversations:
                    messages = conversation.get('messages', {}).get('data', [])
                    for message in messages:
                        sender_name = message.get('from', {}).get('name', 'Unknown User')
                        sender_id = message.get('from', {}).get('id', '')
                        message_text = message.get('message', '')
                        message_id = message.get('id', '')

                        if sender_id != p.get('id') and message_text:  # Ignore messages from the page itself
                            self._handle_facebook_message(sender_id, sender_name, message_text, message_id, p.get('id'))

                # Sync comments from page posts.
                url = f"https://graph.facebook.com/v7.0/{p.get('id')}/feed"
                params = {
                    'access_token': p.get('access_token'),
                    'fields': 'id,comments{message,from,id,created_time}'
                }

                response = requests.get(url, params=params).json()
                _logger.info("Sync comments from page response: %s", response)
                if response.get('error'):
                    _logger.error(f"Error fetching comments: {response['error']['message']}")
                    return
                posts = response.get('data', [])
                _logger.info("Sync comments from page posts: %s", posts)
                for post in posts:
                    comments = post.get('comments', {}).get('data', [])

                    for comment in comments:
                        commenter_name = comment.get('from', {}).get('name', 'Unknown User')
                        commenter_id = comment.get('from', {}).get('id', '')
                        comment_text = comment.get('message', '')
                        comment_id = comment.get('id', '')

                        if commenter_id != p.get('id') and comment_text:  # Ignore comments from the page itself
                            self._handle_facebook_message(commenter_id, commenter_name, comment_text, comment_id,
                                                          p.get('id'))
        except Exception as e:
                _logger.error(f"Error fetching Facebook token: {e}")
                raise ValidationError(f"Error fetching Facebook token: {e}")

    def _handle_facebook_message(self, sender_id, sender_name, message_text, message_id, page_id):
        """
        Create a helpdesk ticket or add a log note if the sender already has a ticket.
        """
        HelpdeskTicket = self.env['helpdesk.ticket'].sudo()

        # Check if message already processed
        if HelpdeskTicket.search([('facebook_message_id', '=', message_id)], limit=1):
            return

        # Find an existing ticket for the same sender (enquirer)
        existing_ticket = HelpdeskTicket.search([('facebook_sender_id', '=', sender_id)], limit=1)

        if existing_ticket:
            # Add a log note if the ticket already exists
            existing_ticket.message_post(body=f"New message from {sender_name}: {message_text}")
            _logger.info(f"Added log note to existing ticket for sender: {sender_name}")
        else:
            # Create a new ticket if no existing ticket is found
            HelpdeskTicket.create({
                'team_id': self.env.ref('customer_care.customer_carehelpdesk_team').id,
                'name': f"Facebook Inquiry from {sender_name}",
                'description': message_text,
                'enquirer_name': sender_name,
                'facebook_message_id': message_id,
                'facebook_sender_id': sender_id,
                'channel': 'facebook',
                'facebook_page_id': page_id,
            })
            _logger.info(f"Helpdesk ticket created from Facebook message: {message_text}")

    def fetch_facebook_message(self):
        for fb in self:
            fb.create_ticket_from_fb_message()
        return True