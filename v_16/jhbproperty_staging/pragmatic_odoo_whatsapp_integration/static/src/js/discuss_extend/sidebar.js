/** @odoo-module **/

import { useRefToModel } from '@mail/component_hooks/use_ref_to_model';
import { useUpdate } from '@mail/component_hooks/use_update';
import { registerMessagingComponent } from '@mail/utils/messaging_component';
import { getMessagingComponent } from "@mail/utils/messaging_component";
import { useModels } from '@mail/component_hooks/use_models';
import '@pragmatic_odoo_whatsapp_integration/discuss_sidebar_category/discuss_sidebar_category';

const { Component } = owl;
// const { useRef } = owl.hooks;
const ODOO_CHANNEL_TYPES = ["channel", "chat", "livechat", "group"];

export class DiscussConversationSidebar extends Component {

    /**
     * @override
     */
     setup() {
        useModels();
        super.setup();
        useRefToModel({ fieldName: 'quickSearchInputRef', refName: 'quickSearchInput' });
        useUpdate({ func: () => this._update() });
    }

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * @returns {DiscussView}
     */
     get discussView() {
        return this.props.record;
    }

    get MultiLivechatGroups() {
        let allChats = this.messaging.models["Thread"]
            .all(thread => thread.description === "Facebook chat." && thread.isPinned && thread.model === "mail.channel")
            .sort((c1, c2) => {
                // Sort by: last message id (desc), id (desc)
                if (c1.lastMessage && c2.lastMessage) {
                    return c2.lastMessage.id - c1.lastMessage.id;
                }
                // A channel without a last message is assumed to be a new
                // channel just created with the intent of posting a new
                // message on it, in which case it should be moved up.
                if (!c1.lastMessage) {
                    return -1;
                }
                if (!c2.lastMessage) {
                    return 1;
                }
                return c2.id - c1.id;
            });
            console.log(allChats);
        let qsVal = this.discussView.discuss.sidebarQuickSearchValue;
        // console.log("DiscussView",this.discussView.discuss);
        if (qsVal) {
            qsVal = qsVal.toLowerCase();
            allChats = allChats.filter((chat) => {
                const nameVal = chat.displayName.toLowerCase();
                return nameVal.includes(qsVal);
            });
        }
        const groups = {};
        _.each(this.messaging.multi_livechat.channel_types, function (
            name,
            channel_type
        ) {
            // console.log(name, channel_type)
            groups[channel_type] = {
                channel_type: channel_type,
                name: name,
                // chats: [],
                chats: undefined,
            };
        });
        console.log(groups)

        _.each(allChats, (chat) => {
            console.log(chat)
            if (groups[chat.channel.channel_type]) {
                // groups[chat.channel.channel_type].chats.push(chat);
                groups[chat.channel.channel_type].chats = chat;
            }
        });
        console.log("sidebar ",groups)

        return _.map(groups, (value) => value);
    }

    get FunctionGroups() {
        console.log("multichat groups", this.MultiLivechatGroups)
        let allChats = this.messaging.models["Thread"]
            .all(thread => thread.description === 'Sent Messages' && thread.isPinned && thread.model === "mail.channel")
            .sort((c1, c2) => {
                // Sort by: last message id (desc), id (desc)
                if (c1.lastMessage && c2.lastMessage) {
                    return c2.lastMessage.id - c1.lastMessage.id;
                }
                // A channel without a last message is assumed to be a new
                // channel just created with the intent of posting a new
                // message on it, in which case it should be moved up.
                if (!c1.lastMessage) {
                    return -1;
                }
                if (!c2.lastMessage) {
                    return 1;
                }
                return c2.id - c1.id;
            });
            console.log(allChats);
        let qsVal = this.discussView.discuss.sidebarQuickSearchValue;
        //console.log(qsVal)
        if (qsVal) {
            qsVal = qsVal.toLowerCase();
            allChats = allChats.filter((chat) => {
                const nameVal = chat.displayName.toLowerCase();
                return nameVal.includes(qsVal);
            });
        }
        const groups = {};
        _.each(this.messaging.multi_livechat.channel_types, function (
            name,
            channel_type
        ) {
            // console.log(name, channel_type)
            groups[channel_type] = {
                channel_type: channel_type,
                name: name,
                chats: [],
            };
        });
        console.log(groups)

        _.each(allChats, (chat) => {
            console.log(chat)
            if (groups[chat.channel.channel_type]) {
                groups[chat.channel.channel_type].chats.push(chat);
            }
        });
        console.log(groups)

        return _.map(groups, (value) => value);
    }

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @private
     */
     _update() {
        console.log("discuss view",this.discussView);
        // if (this.discussview.discuss.categoryMultichat) {
        if (!this.discussview) {
            // this.discussView.destroy();
            return;
        }
        // await this.discussView;
        if (this.discussView.quickSearchInputRef.el) {
            this.discussView.quickSearchInputRef.el.value = this.discussView.discuss.sidebarQuickSearchValue;
        }

    }

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     * @param {KeyboardEvent} ev
     */
    _onInputQuickSearch(ev) {
        ev.stopPropagation();
        this.discuss.onInputQuickSearch(this._quickSearchInputRef.el.value);
    }

    _onClickChannelAdd(ev) {
        ev.stopPropagation();
        // this.discussview.update({ isAddingChannel: true });
        return this.env.bus.trigger('do-action', {
            action: {
                name: 'Send a WhatsApp Message',
                type: 'ir.actions.act_window',
                res_model: 'whatsapp.msg.send.partner',
//                    res_id: this.thread.id,
                views: [[false, 'form']],
                target: 'new'
            },
        });
    }

    async _onClickRefresh(ev) {
        ev.stopPropagation();
        var self = this;
        const discuss_new = self.discussView
        console.log("===active id==", discuss_new);
        console.log("===this sidebar===", this);
        this.messaging.initializer.restartWhatsapp(this.MultiLivechatGroups[0].chats);
        console.log("after start");
        // await this.MultiLivechatGroups[0].chats.onClick();
        
        // return this.env.bus.trigger('do-action', {
        //     action: {
        //         'type': 'ir.actions.client',
        //         'tag': 'reload',
        //     },
        // });
    }

}

Object.assign(DiscussConversationSidebar, {
    props: { record: Object },
    components: { WhatsappSidebarCategory: getMessagingComponent('WhatsappSidebarCategory') },
    template: 'conversations.Sidebar',
});

registerMessagingComponent(DiscussConversationSidebar);
