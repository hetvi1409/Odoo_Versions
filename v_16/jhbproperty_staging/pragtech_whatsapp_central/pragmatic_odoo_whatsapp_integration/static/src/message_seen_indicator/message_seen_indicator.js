/** @odoo-module **/

import { useService } from '@web/core/utils/hooks';
import { registerMessagingComponent } from '@mail/utils/messaging_component';
import rpc from 'web.rpc';
import ajax from 'web.ajax';
const { Component } = owl;
import { useUpdate } from '@mail/component_hooks/use_update';
import { useModels } from '@mail/component_hooks/use_models';
import { LegacyComponent } from "@web/legacy/legacy_component";

export class MessageSeenDashboard extends Component {

    /**
     * @override
     */
    async setup() {
        super.setup();
        useModels();
        this.message_seen;
        this.rpc = useService('rpc');
        await this.willStart();
        console.log("message seen setup===== ",this.message_seen);
        console.log("message seen indicator setup===== ",this.messageSeenIndicatorView);
        // useUpdate({ func: () => this._update() });
        // message.update({ author: this.messaging.currentPartner })
        // this.message_seen;
        // await this.messageSeenIndicator();
    }

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------


    /**
     * @returns {mail.message}
     */

    get message() {
        console.log("message props ====", this.messaging.models['Message'].all());
        return this.messaging.models['Message'].all(thread => thread.localId === this.props.record && thread.is_discussion);
    }

    // set message_seen(message_seen){
    //     // var self = this;
    //     this.message_seen = message_seen
    // }

    /**
     * @returns {mail.message_seen_indicator}
     */
    async messageSeenIndicator() {
        // if (!this.thread || this.thread.model !== 'mail.channel') {
        //     return undefined;
        // }
        var self = this;
        self.message_seen;
        console.log(this.message);
        this.message[0].checkSeen();
        console.log("====== ",this);
        // var def = this.rpc({
        //     model: 'mail.message',
        //     method: 'check_seen',
        //     args:  ["",this.message[0].id],
        // }, {
        //     timeout: 7500,
        //     shadow: false,
        // })
        // .then(function (res) {
        //     console.log("result ===== ",res)
        //     self.message_seen = res;
        //     return Promise.resolve(self.message_seen);
        //     // if (res == true && self.message){
        //     //     self.message[0].markAsRead();
        //     // }
        // });
        // console.log();
        // console.log("def===== ",def);
        await ajax.jsonRpc("/whatsapp_dashboard/find_message_seen", 'call', {'message_id': this.message[0].id})
        .then(async function(res){
            console.log("result ===== ",res);
            await res;
            self.message_seen = res;
        });

        console.log("message seen===== ",this.message_seen);
        // this.message_seen = self.message_seen;

        return self.message_seen;
    }

    /**
     * @returns {MessageSeenIndicator}
     */
    get messageSeenIndicatorView() {
        var self = this;
        // console.log("getting indicator ====",this.messageSeenIndicator());
        console.log("getting seen ====",this.message[0].checkSeen());
        console.log("getting seen ====",this.message[0].message_seen);
        return this.message[0].message_seen;
    }

    async willStart () {
        var self = this;
        var def = await ajax.jsonRpc("/whatsapp_dashboard/find_message_seen", 'call', {'message_id': this.message[0].id})
        .then(async function (res) {
            await res;
            console.log("result ===== ",res);
            self.message_seen = res;
            return res;
        });
        console.log("message seen start===== ",this.message_seen);

        return Promise.all([
            def
        ]);
    }

    // /**
    //  * @returns {mail.Thread}
    //  */
    // get thread() {
    //     return this.messaging && this.messaging.models['mail.thread'].get(this.props.threadLocalId);
    // }
    _update() {
        if (!this.messageSeenIndicatorView.exists()) {
            // this.discussView.destroy();
            return;
        }
        // await this.discussView;
        if (this.messaging.models) {
            console.log("this el ", this.messageSeenIndicatorView)
            this.messageSeenIndicatorView = this.message[0].message_seen;
        }
    }
}

Object.assign(MessageSeenDashboard, {
    props: { record: String },
    template: 'dashboard.MessageSeenIndicator',
});

registerMessagingComponent(MessageSeenDashboard);
