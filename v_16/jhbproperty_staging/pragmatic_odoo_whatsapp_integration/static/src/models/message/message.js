/** @odoo-module **/

import { addFields, patchFields } from '@mail/model/model_core';
import { registerPatch } from '@mail/model/model_core';
import { attr, one } from '@mail/model/model_field';
import { clear, insert } from '@mail/model/model_field_command';


registerPatch({
    name: 'Message',
    recordMethods: {
        async performInitRpc() {
            return await this.messaging.rpc({
                route: '/whatsapp_dashboard/find_message_data',
            }, { shadow: true });
        },
        /**
         * Fetch messaging data initially to populate the store specifically for
         * the current user. This includes pinned channels for instance.
         */
        async start() {
            // this.messaging.device.start();
            console.log("starting");
            const discuss = this.messaging.discuss;
            const data = await this.performInitRpc();
            console.log("data ==gitten", data);
            if (!this.exists()) {
                return;
            }
            // await this._init(data);
            // if (!this.exists()) {
            //     return;
            // }
            
        },

        async checkSeen() {
            console.log("==live data", this)
            const def = await this.messaging.rpc({
                model: 'mail.message',
                method: 'check_seen',
                args: [[this.id]]
            })
            console.log("==live def", def);
            // if (!def) {
            //     this.message_seen = def;
            //     // this.update({ data: clear() });
            //     // deleteCookie("im_livechat_session");
            //     // this.messaging.publicLivechatGlobal.chatWindow.widget.renderChatWindow();
            // } else {
            //     console.log("==live data", this)
            //     // this.update({ data: livechatData });
            //     this.message_seen = def;
            //     // this.updateSessionCookie();
            // }
            // .then(async function (res) {
            //     this.update({ data: livechatData });
            //     self.message_seen = res;
            //     return res;
            // });
            return def;
        },
    },
    fields: {
        message_seen: attr({
            // {
            // /**
            //  * The method does not attempt to cover all possible cases of empty
            //  * messages, but mostly those that happen with a standard flow. Indeed
            //  * it is preferable to be defensive and show an empty message sometimes
            //  * instead of hiding a non-empty message.
            //  *
            //  * The main use case for when a message should become empty is for a
            //  * message posted with only an attachment (no body) and then the
            //  * attachment is deleted.
            //  *
            //  * The main use case for being defensive with the check is when
            //  * receiving a message that has no textual content but has other
            //  * meaningful HTML tags (eg. just an <img/>).
            //  */
                compute() {
                    if (!this.messaging.messages_data) {
                        return;
                    }
                    console.log("message this====", this)
                    const def = this.messaging.messages_data.find((message) => message.id === this.id);
                    console.log("compute def==", def);
                    if (def){
                        return def.message_seen;
                    } else {
                        return false;
                    }
                },
                default: false
            }
        ),
    }
});
