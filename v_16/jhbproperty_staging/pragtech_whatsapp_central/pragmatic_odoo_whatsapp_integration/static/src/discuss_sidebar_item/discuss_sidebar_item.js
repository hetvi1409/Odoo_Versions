/** @odoo-module **/

import { registerMessagingComponent } from '@mail/utils/messaging_component';

// const components = {
//     EditableText: require('mail/static/src/components/editable_text/editable_text.js'),
//     ThreadIcon: require('mail/static/src/components/thread_icon/thread_icon.js'),
// };
// const { isEventHandled } = require('mail/static/src/utils/utils.js');

// const Dialog = require('web.Dialog');

const { Component } = owl;

export class DiscussSidebarItem extends Component {

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * Get the counter of this discuss item, which is based on the thread type.
     *
     * @returns {integer}
     */
    get counter() {
        if (this.thread.model === 'mail.box') {
            return this.thread.counter;
        } else if (this.thread.channel_type === 'channel') {
            return this.thread.message_needaction_counter;
        } else if (this.thread.channel_type === 'chat') {
            return this.thread.localMessageUnreadCounter;
        }
        return 0;
    }

    /**
     * @returns {mail.discuss}
     */
    get discuss() {
        return this.messaging && this.messaging.discuss;
    }

    /**
     * @returns {boolean}
     */
    hasUnpin() {
        return this.thread.channel_type === 'chat';
    }

    /**
     * @returns {mail.thread}
     */
    get thread() {
        // console.log(this.messaging.models['mail.thread'].get(this.props.threadLocalId))
        return this.messaging.models['mail.thread'].get(this.props.threadLocalId);
        // return this.messaging.models['mail.discuss_sidebar_category_item'].get(this.props.threadLocalId);
    }

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------


    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    _onCancelRenaming(ev) {
        this.discuss.cancelThreadRenaming(this.thread);
    }

    /**
     * @private
     * @param {MouseEvent} ev
     */
    _onClick(ev) {
        if (isEventHandled(ev, 'EditableText.click')) {
            return;
        }
        this.thread.open();
    }

    /**
     * Stop propagation to prevent selecting this item.
     *
     * @private
     * @param {CustomEvent} ev
     */
    _onClickedEditableText(ev) {
        ev.stopPropagation();
    }

}

Object.assign(DiscussSidebarItem, {
    props: {
        threadLocalId: String,
    },
    template: 'mail.DiscussSidebarItemdashboard',
});

registerMessagingComponent(DiscussSidebarItem);

