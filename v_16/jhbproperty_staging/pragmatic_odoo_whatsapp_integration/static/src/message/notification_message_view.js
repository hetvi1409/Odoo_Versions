/** @odoo-module **/

import { registerMessagingComponent } from '@mail/utils/messaging_component';

const { Component } = owl;

class WhatsappNotificationView extends Component {

    /**
     * @returns {NotificationMessageView}
     */
    get notificationMessageView() {
        console.log("notify ", this.props.record);
        return this.props.record;
    }

    get rawBody(){
        var body = this.props.record.message.body.replace("<p>", "");
        var rawBody = body.replace("</p>", "");
        rawBody = rawBody.replaceAll(" ", "%20");
        var rawBody_str = rawBody.replaceAll("&amp;", "&");
        return rawBody_str;
    }

}

Object.assign(WhatsappNotificationView, {
    props: { record: Object },
    template: 'whatsapp.NotificationMessageView',
});

registerMessagingComponent(WhatsappNotificationView);
