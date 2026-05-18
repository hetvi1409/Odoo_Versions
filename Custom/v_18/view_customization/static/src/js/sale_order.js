/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";
import { useService } from "@web/core/utils/hooks";

patch(FormController.prototype, {

    setup() {
        super.setup(...arguments);
        this.notification = useService("notification");
    },

    async beforeExecuteActionButton(clickParams) {
        // Call original first
        const result = await super.beforeExecuteActionButton(clickParams);
        return result;
    },

    async afterExecuteActionButton(clickParams) {
        const result = await super.afterExecuteActionButton(...arguments);

        // Only for sale.order model
        if (
            this.model.root.resModel === "sale.order" &&
            clickParams.name === "action_confirm"
        ) {
            const record = this.model.root;
            const name = record.data.name;
            const amount = record.data.amount_total;
            console.log('Amount>>>',amount)
            console.log('Amount>>>',record)
            console.log('Amount>>>',record.data)

            this.notification.add(
                `Order ${name} confirmed! Total: ₹${amount}`,
                {
                    title: "✅ Order Confirmed!",
                    type: "success",   // success | warning | danger | info
                    sticky: false,     // auto dismiss
                }
            );
        }

        return result;
    },
});