/** @odoo-module **/

import { registerPatch } from '@mail/model/model_core';
import { clear } from '@mail/model/model_field_command';

registerPatch({
    name: 'DiscussSidebarCategoryItem',
    fields: {
        avatarUrl: {
            compute() {
                if (this.channel.channel_type === 'multi_livechat_NAMEs') {
                    if (this.channel.correspondent && !this.channel.correspondent.is_public) {
                        return this.channel.correspondent.avatarUrl;
                    }
                }
                else if (this.channel_type === 'multi_livechat_sent_channel') {
                    if (this.channel.correspondent && !this.channel.correspondent.is_public) {
                        return this.channel.correspondent.avatarUrl;
                    }
                }
                return this._super();
            },
        },
        categoryCounterContribution: {
            compute() {
                if (this.channel.channel_type === 'multi_livechat_NAMEs') {
                    return this.channel.localMessageUnreadCounter > 0 ? 1 : 0;
                }
                else if (this.channel_type === 'multi_livechat_sent_channel') {
                    return this.channel.localMessageUnreadCounter > 0 ? 1 : 0;
                }
                return this._super();
            },
        },
        counter: {
            compute() {
                if (this.channel.channel_type === 'multi_livechat_NAMEs') {
                    return this.channel.localMessageUnreadCounter;
                }
                else if (this.channel_type === 'multi_livechat_sent_channel') {
                    return this.channel.localMessageUnreadCounter;
                }
                return this._super();
            },
        },
        hasUnpinCommand: {
            compute() {
                if (this.channel.channel_type === 'multi_livechat_NAMEs') {
                    return !this.channel.localMessageUnreadCounter;
                }
                else if (this.channel_type === 'multi_livechat_sent_channel') {
                    return !this.channel.localMessageUnreadCounter;
                }
                return this._super();
            },
        },
        hasThreadIcon: {
            compute() {
                if (this.channel.channel_type === 'multi_livechat_NAMEs') {
                    return clear();
                }
                else if (this.channel_type === 'multi_livechat_sent_channel') {
                    return clear();
                }
                return this._super();
            },
        },
    },
});
