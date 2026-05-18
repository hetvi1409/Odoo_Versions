/** @odoo-module **/

import { registerMessagingComponent } from '@mail/utils/messaging_component';

const { Component } = owl;

export class WhatsappSidebarCategoryItem extends Component {

    /**
     * @returns {WhatsappSidebarCategoryItem}
     */
    get categoryItem() {
        return this.props.record;
    }

}

Object.assign(WhatsappSidebarCategoryItem, {
    props: { record: Object },
    template: 'mail.WhatsappSidebarCategoryItem',
});

registerMessagingComponent(WhatsappSidebarCategoryItem);
