/** @odoo-module **/

import { registerMessagingComponent } from '@mail/utils/messaging_component';

const { Component } = owl;

export class WhatsappSidebarCategory extends Component {

    /**
     * @returns {WhatsappSidebarCategory}
     */
    get category() {
        // console.log("category",this.props.record);
        return this.props.record;
    }
}

Object.assign(WhatsappSidebarCategory, {
    props: { record: Object },
    template: 'mail.WhatsappSidebarCategory',
});

registerMessagingComponent(WhatsappSidebarCategory);
