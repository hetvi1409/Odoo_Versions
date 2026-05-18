
from odoo import http
from odoo.http import request

from odoo.addons.mail.controllers.discuss import DiscussController


class MultiLivechatMailController(DiscussController):
    @http.route()
    def mail_init_messaging(self):
        values = super().mail_init_messaging()
        channels_data = request.env["mail.channel"].get_channels()
        for channels in channels_data:
            values["channels"].append(channels)
        values["multi_livechat"] = request.env["mail.channel"].multi_livechat_info()
        values["messages"] = request.env["mail.channel"].multi_livechat_messages()
        return values
