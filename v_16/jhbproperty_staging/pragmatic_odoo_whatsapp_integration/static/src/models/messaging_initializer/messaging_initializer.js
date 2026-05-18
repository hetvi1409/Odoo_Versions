/** @odoo-module **/

import { registerPatch } from '@mail/model/model_core';
import { insert } from '@mail/model/model_field_command';

const ODOO_CHANNEL_GROUPS = [
    "channel_channel",
    "channel_direct_message",
    "channel_private_group",
    "channel_livechat",
];

registerPatch({
    name: 'MessagingInitializer',
    recordMethods: {
        async restartWhatsapp(thread) {
            this.messaging.device.start();
            const discuss = this.messaging.discuss;
            const data = await this.performInitRpc();
            if (!this.exists()) {
                return;
            }
            await this._init(data);
            if (!this.exists()) {
                return;
            }
            // console.log("unseen mess ", this.messaging.messages_data.filter((data) => data.message_seen === false));
            for (const key in this.messaging.messages_data.filter((data) => data.message_seen === false)){
                await this._updateMessageSeen({
                    id: this.messaging.messages_data[key].id,
                    message_seen: this.messaging.messages_data[key].message_seen,
                })
                // }
            }
            if (discuss.discussView) {
                discuss.openThread(thread);
            }
        },

        async _init(data) {
            await this._super(data);
            // TODO: find a better way
            console.log("this==== ",this);
            console.log("data==== ",data);
            console.log(data.multi_livechat);
            this.messaging.multi_livechat = data.multi_livechat;
            this.messaging.messages_data = data.messages;
            // await this.async(() => this._initChannels(data.multi_livechat));
        },
        async _initChannels(channelsData) {
            await this._super(channelsData);
            console.log("initializing facebook channels", channelsData)
            let channel_list = [];
            for (const key in channelsData) {
                const startsWith = key.lastIndexOf("multi_livechat_") === 0;
                if (startsWith && !(key in ODOO_CHANNEL_GROUPS)) {
                    channel_list = channel_list.concat(channelsData[key]);
                }
            }
            // TODO: multi_livechat_types: channel_type -> Channel Name
            console.log("channel list are", channel_list)
            return this.messaging.executeGracefully(
                channel_list.map((data) => () => {
                    const channel = this.messaging.models["Thread"].insert(
                        this.messaging.models["Thread"].convertData(data)
                    );
                    if (!channel.isPinned) {
                        channel.pin();
                    }
                })
            );
        },
        async _updateMessageSeen({ id, message_seen }) {
            // for (const key in this.messaging.messages_data){
                // console.log("message int seen", message_seen)
                var attachment_ids = [];
                // const messageData = await this.messaging.rpc({
                //     route: '/dashboard/message/update_content',
                //     params: {
                //         message_seen,
                //         attachment_ids,
                //         message_id: id,
                //     },
                // });
                if (!this.messaging) {
                    return;
                }
                var data = {
                    'id': id,
                    'message_seen': message_seen,
                }
                this.messaging.models['Message'].insert(data);
            // }
        },
    }
});

