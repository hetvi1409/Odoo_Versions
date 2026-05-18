/** @odoo-module **/

import { registerPatch } from '@mail/model/model_core';
import { one } from '@mail/model/model_field';
import { clear } from '@mail/model/model_field_command';

registerPatch({
    name: 'DiscussSidebarCategory',
    fields: {
        categoryItemsOrderedByLastAction: {
            compute() {
                if (this.discussAsMultichat) {
                    return this.categoryItems;
                }
                return this._super();
            },
        },
        discussAsMultichat: one('Discuss', {
            identifying: true,
            inverse: 'categoryMultichat',
        }),
        isServerOpen: {
            compute() {
                // there is no server state for non-users (guests)
                if (!this.messaging.currentUser) {
                    return clear();
                }
                if (!this.messaging.currentUser.res_users_settings_id) {
                    return clear();
                }
                if (this.discussAsMultichat) {
                    return this.messaging.currentUser.res_users_settings_id.is_discuss_sidebar_category_livechat_open;
                }
                return this._super();
            },
        },
        name: {
            compute() {
                if (this.discussAsMultichat) {
                    return this.env._t("Multichat");
                }
                return this._super();
            },
        },
        orderedCategoryItems: {
            compute() {
                if (this.discussAsMultichat) {
                    return this.categoryItemsOrderedByLastAction;
                }
                return this._super();
            },
        },
        serverStateKey: {
            compute() {
                if (this.discussAsMultichat) {
                    return 'is_discuss_sidebar_category_multichat_open';
                }
                return this._super();
            },
        },
        supportedChannelTypes: {
            compute() {
                if (this.discussAsMultichat) {
                    return ['multi_livechat_NAMEs'];
                }
                return this._super();
            },
        },
    }
});

