/** @odoo-module **/

import { registerMessagingComponent } from '@mail/utils/messaging_component';
import { LegacyComponent } from '@web/legacy/legacy_component';
import { useModels } from '@mail/component_hooks/use_models';
import { useUpdate } from '@mail/component_hooks/use_update';
import '@pragmatic_odoo_whatsapp_integration/js/discuss_extend/sidebar';
import '@mail/components/call_view/call_view';
import '@mail/components/message_list/message_list';
import '@pragmatic_odoo_whatsapp_integration/thread_view/thread_view';
import { getMessagingComponent } from "@mail/utils/messaging_component";
const { Component } = owl;

export class DiscussCoverse extends Component {

    setup() {
        // if (this.discuss && DiscussWidget.currentInstance === this) {
        //     this.discuss.close();
        // }
        useModels();
        super.setup();
        useUpdate({ func: () => this._update() });
    }
 
    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * @returns {whatsappView}
     */
    get whatsappView() {
        // console.log("component ", this.props.record);
        // console.log("services", this.env.services);
        return this.props.record;
    }

    get messaging() {
        // console.log("services", this.env.services);
        return this.env.services.messaging.modelManager.messaging;
    }
    // components: { DiscussConversationSidebar: getMessagingComponent('DiscussConversationSidebar'), 
    // WhatsappThreadView: getMessagingComponent('WhatsappThreadView')
    // },
    _update() {
        if (this.whatsappView) {
            this.props.record = this.env.services.messaging.modelManager.messaging.discuss.discussView;
        }
    }
}

Object.assign(DiscussCoverse, {
    props: { record: Object },
    components: { DiscussConversationSidebar: getMessagingComponent('DiscussConversationSidebar'), 
    MessageList: getMessagingComponent('MessageList'),
    CallView: getMessagingComponent('CallView'),
    WhatsappThreadView: getMessagingComponent('WhatsappThreadView')
    },
    template: 'conversation.Discuss',
});

registerMessagingComponent(DiscussCoverse);
