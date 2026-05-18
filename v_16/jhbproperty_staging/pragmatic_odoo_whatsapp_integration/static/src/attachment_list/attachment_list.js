/** @odoo-module **/

import { registerMessagingComponent } from '@mail/utils/messaging_component';

const { Component } = owl;

export class WhatsappAttachmentList extends Component {

    /**
     * @returns {AttachmentList}
     */
    get attachmentList() {
        return this.props.record;
    }

}

Object.assign(WhatsappAttachmentList, {
    props: { record: Object },
    template: 'whatsapp.AttachmentList',
});

registerMessagingComponent(WhatsappAttachmentList);
