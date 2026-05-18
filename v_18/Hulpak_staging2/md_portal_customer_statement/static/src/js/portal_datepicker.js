/** @odoo-module */

import PublicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from "@web/core/network/rpc";

export const PortalDatePicker = PublicWidget.Widget.extend({
    selector: ".o-portal-datetimepicker",
    disabledInEditableMode: false,
    /**
     * @override
     */
    start() {
        this.disableDateTimePicker = this.call("datetime_picker", "create", {
            target: this.el,
            onChange: (newDate) => {
                const { accessToken, orderId, lineId } = this.el.dataset;
            },
            pickerProps: {
                type: "date",
                value: false,
            },
        }).enable();
    },
    /**
     * @override
     */
    destroy() {
        this.disableDateTimePicker();
        return this._super(...arguments);
    },
});

PublicWidget.registry.PortalDatePicker = PortalDatePicker;
