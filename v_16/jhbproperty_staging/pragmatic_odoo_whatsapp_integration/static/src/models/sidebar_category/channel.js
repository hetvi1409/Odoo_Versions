/** @odoo-module **/

import { addFields, patchFields } from '@mail/model/model_core';
import { registerPatch } from '@mail/model/model_core';
import { attr, one } from '@mail/model/model_field';

registerPatch({
    name: 'Channel',
    fields: {
        discussSidebarCategory: {
            compute() {
                if (this.channel_type === 'multi_livechat_NAMEs') {
                    return this.messaging.discuss.categoryMultichat;
                }
                else if (this.channel_type === 'multi_livechat_sent_channel') {
                    return this.messaging.discuss.categoryMultichat;
                }
                return this._super();
            },
        },
        displayName: {
            compute() {
                if (!this.thread) {
                    return;
                }
                if (this.channel_type === 'multi_livechat_NAMEs' && this.correspondent) {
                    if (!this.correspondent.is_public && this.correspondent.country) {
                        return `${this.thread.getMemberName(this.correspondent.persona)} (${this.correspondent.country.name})`;
                    }
                    if (this.anonymous_country) {
                        return `${this.thread.getMemberName(this.correspondent.persona)} (${this.anonymous_country.name})`;
                    }
                    return this.thread.getMemberName(this.correspondent.persona);
                }
                else if (this.channel_type === 'multi_livechat_sent_channel') {
                    if (!this.correspondent.is_public && this.correspondent.country) {
                        return `${this.thread.getMemberName(this.correspondent.persona)} (${this.correspondent.country.name})`;
                    }
                    if (this.anonymous_country) {
                        return `${this.thread.getMemberName(this.correspondent.persona)} (${this.anonymous_country.name})`;
                    }
                    return this.thread.getMemberName(this.correspondent.persona);
                }
                return this._super();
            },
        },
    },
});
