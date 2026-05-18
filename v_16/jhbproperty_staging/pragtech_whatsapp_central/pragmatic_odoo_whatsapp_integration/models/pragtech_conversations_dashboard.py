from datetime import datetime
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import ValidationError
from .. import wizards
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.osv import expression
from collections import defaultdict

ODOO_CHANNEL_TYPES = ["chat", "channel", "livechat", "group"]


class MailChannel(models.Model):
    _inherit = 'mail.channel'

    is_pinned = fields.Boolean(
        "Visible for me",
        compute="_compute_is_pinned",
        inverse="_inverse_is_pinned",
        help="Refresh page after updating",
    )

    def facebook_channel_create(self, name, privacy='public'):
        new_channel = self.env['mail.channel'].sudo().create({
            'name': 'Chat with {}'.format(name),
            'public': privacy,
            'email_send': False,
            'channel_type': 'multi_livechat_NAMEs'
        })
        notification = _(
            '<div class="o_mail_notification">created <a href="#" class="o_channel_redirect" data-oe-id="%s">#%s</a></div>',
            new_channel.id, new_channel.name)
        new_channel.with_context(from_odoobot=True).message_post(body=notification, message_type="notification", subtype_xmlid="mail.mt_comment")
        channel_info = new_channel.channel_info('creation')[0]
        self.env['bus.bus'].sendone((self._cr.dbname, 'res.partner', self.env.user.partner_id.id), channel_info)
        open_form = {
                'name': 'Send a WhatsApp Message',
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': self.env.ref('pragtech_whatsapp_messenger.send_whatsapp_msg_send_res_partner_view_form').id,
                'res_model': 'whatsapp.msg.send.partner',
                'type': 'ir.actions.act_window',
                'target': 'new',
                #'domain': [('partner_id', '=', record.name)],
            }
        return channel_info

    @api.model
    def _prepare_multi_livechat_channel_vals(
            self, channel_type, channel_name, partner_ids
    ):
        return {
            "channel_partner_ids": [(4, pid) for pid in partner_ids],
            "public": "groups",
            "group_public_id": self.env.ref("base.group_user").id,
            "channel_type": channel_type,
            "email_send": False,
            "name": channel_name,
        }

    def _compute_is_pinned(self):
        # TODO: make batch search via read_group
        for r in self:
            r.is_pinned = self.env["mail.channel.member"].search_count(
                [
                    ("partner_id", "=", self.env.user.partner_id.id),
                    ("channel_id", "=", r.id),
                    ("is_pinned", "=", True),
                ]
            )

    def _inverse_is_pinned(self):
        # TODO: make batch search via read_group
        for r in self:
            channel_partner = self.env["mail.channel.member"].search(
                [
                    ("partner_id", "=", self.env.user.partner_id.id),
                    ("channel_id", "=", r.id),
                ]
            )
            # TODO: can channel_partner be empty or more than 1 record?
            channel_partner.is_pinned = r.is_pinned

    def _compute_is_chat(self):
        super(MailChannel, self)._compute_is_chat()
        for record in self:
            if record.channel_type not in ODOO_CHANNEL_TYPES:
                record.is_chat = True

    @api.model
    def channel_fetch_slot(self):
        values = super(MailChannel, self).channel_fetch_slot()
        domain = [("channel_type", "not in", ODOO_CHANNEL_TYPES)]
        pinned_channels = self.env["mail.channel.member"].search([("partner_id", "=", self.env.user.partner_id.id), ("is_pinned", "=", True),]).mapped("channel_id")
        domain += [("id", "in", pinned_channels.ids)]
        channel_infos = self.search(domain).channel_info()
        for info in channel_infos:
            key = info["channel_type"]
            values.setdefault(key, [])
            values[key].append(info)
        return values

    @api.model
    def multi_livechat_info(self):
        field = self.env["mail.channel"]._fields["channel_type"]

        return {
            "channel_types": {
                key: value
                for key, value in field.selection
                if key not in ODOO_CHANNEL_TYPES
            }
        }
    
    @api.model
    def multi_livechat_messages(self):
        whatsapp_channels = self.env["mail.channel"].sudo().search([('channel_type', 'not in', ODOO_CHANNEL_TYPES)])
        # messages = self.env['mail.message'].sudo().search([])
        # messages = whatsapp_channels.message_ids
        all_messages = []
        for channel in whatsapp_channels:
            for message in channel.message_ids:
                all_messages.append({
                    'id': message.id,
                    'message_seen': message.message_seen,
                    'whatsapp_message_id': message.whatsapp_message_id
                })

        return all_messages

    def get_channels(self):
        channels = self.env["mail.channel"].sudo().search([])
        user_root = self.env.ref('base.user_root')
        all_needed_members = self.channel_partner_ids
        members_by_channel = defaultdict(lambda: self.env['mail.channel.partner'])
        invited_members_by_channel = defaultdict(lambda: self.env['mail.channel.member'])
        for member in all_needed_members:
            members_by_channel[member.channel_id] |= member
            invited_members_by_channel[member.channel_id] |= member
        # all_needed_members_domain = expression.OR([
        #     [('channel_id.channel_type', '!=', 'channel')],
        #     [('rtc_inviting_session_id', '!=', False)],
        #     [('partner_id', '=', self.env.user.partner_id.id)] if self.env.user and self.env.user.partner_id else expression.FALSE_LEAF,
        # ])
        # all_needed_members = self.env['mail.channel.partner'].search(expression.AND([[('channel_id', 'in', self.ids)], all_needed_members_domain]))
        # member_of_current_user_by_channel = defaultdict(lambda: self.env['mail.channel.partner'])
        # for member in all_needed_members:
        #     if self.env.user and self.env.user.partner_id and member.partner_id == self.env.user.partner_id:
        #         member_of_current_user_by_channel[member.channel_id] = member
        all_channels = []
        channel_last_message_ids = dict((r['id'], r['message_id']) for r in self._channel_last_message_ids())
        member_of_current_user_by_channel = defaultdict(lambda: self.env['mail.channel.member'])
        for channel in channels:
            if channel.channel_type in ["multi_livechat_NAME", "multi_livechat_NAMEs", "multi_livechat_NAME2", "multi_livechat_sent_channel"]:
                members_by_channel = defaultdict(lambda: self.env['mail.channel.member'])
                all_needed_members = self.env['mail.channel.member'].search([('channel_id', '=', channel.id)])
                partner_format_by_partner = all_needed_members.partner_id.mail_partner_format()
                member = member_of_current_user_by_channel.get(channel, self.env['mail.channel.member']).with_prefetch([m.id for m in member_of_current_user_by_channel.values()])
                for member in all_needed_members:
                    members_by_channel[member.channel_id] |= member
                all_channels.append({
                        'avatarCacheKey': channel._get_avatar_cache_key(),
                        'channel_type': channel.channel_type,
                        'create_uid': user_root.id,
                        'custom_channel_name': False,
                        'channel': {
                            'anonymous_country': [('clear',)],
                            'anonymous_name': False,
                            'avatarCacheKey': channel._get_avatar_cache_key(),
                            'channel_type': channel.channel_type,
                            'channelMembers': [('insert', list(member._mail_channel_member_format().values()))],
                            'custom_channel_name': channel.name,
                            'id': channel.id,
                            'memberCount': 5,
                            'serverMessageUnreadCounter': 0,
                        },
                        'defaultDisplayMode': False,
                        'description': 'Facebook chat.',
                        'group_based_subscription': True,
                        'id': channel.id,
                        'invitedGuests': [('insert', [])],
                        'invitedPartners': [('insert', [{'id': member.partner_id.id, 'name': member.partner_id.name} for member in invited_members_by_channel[channel] if member.partner_id])],
                        'is_minimized': False,
                        'is_pinned': True,
                        'last_interest_dt': datetime.strftime(fields.Datetime.now(), '%Y-%m-%d %H:%M:%S'), #.filtered(lambda p: p.partner_id == self.env.ref('base.group_user').users[0].partner_id).last_interest_dt.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                        'last_message_id': channel_last_message_ids.get(channel.id, False),
                        'memberCount': len(self.env.ref('base.group_user').users | user_root),
                        'channelMembers': [('insert', list(member._mail_channel_member_format().values()))],
                        'message_needaction_counter': 0,
                        'message_unread_counter': 5,
                        'name': channel.name,
                        'public': 'public',
                        'rtcSessions': [('insert', [])],
                        'seen_message_id': False,
                        'state': 'open',
                        'uuid': channel.uuid,
                    })
        return all_channels

    # channel_type = fields.Selection(
    #     selection_add=[("multi_livechat_NAME", "Facebook Chat"), ("whatsapp_channel", "Whatsapp Chat")],
    #     ondelete={"multi_livechat_NAME": "cascade"}
    # )
    channel_type = fields.Selection(selection_add=[("multi_livechat_sent_channel", "Sent Messages")],
                                         ondelete={"multi_livechat_sent_channel": "cascade"})



class ConversationsDashboard(models.Model):
    _name = 'conversations.dashboard'
    _inherit = ['mail.thread']
    _description = 'My Skype'

    facebook_id = fields.Char(string='Facebook Username')
    whatsapp_id = fields.Char(string='Whatsapp Username')
    instagram_id = fields.Char(string='Instagram Username')
