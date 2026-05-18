/** @odoo-module **/

import { DiscussContainer } from '@mail/components/discuss_container/discuss_container';
import { patch } from "@web/core/utils/patch";
// import { CalendarArchParser } from "@web/views/calendar/calendar_arch_parser";

patch(DiscussContainer.prototype, 'whatsapp_custom_edit', {
    _willDestroy() {
        if (this.discuss && DiscussContainer.currentInstance === this) {
            console.log("discuss", this.discuss);
            this.discuss.close();
            // this.discuss = undefined;
        }
    }
})