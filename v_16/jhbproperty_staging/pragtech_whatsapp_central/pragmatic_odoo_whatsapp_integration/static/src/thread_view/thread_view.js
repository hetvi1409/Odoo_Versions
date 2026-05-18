/** @odoo-module **/

import { registerMessagingComponent } from '@mail/utils/messaging_component';

const { Component } = owl;

export class WhatsappThreadView extends Component {

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * @returns {WhatsappThreadView}
     */
    get whatsappthreadView() {
        return this.props.record;
    }

}

Object.assign(WhatsappThreadView, {
    props: { record: Object },
    template: 'whatsapp.ThreadView',
});

registerMessagingComponent(WhatsappThreadView);
