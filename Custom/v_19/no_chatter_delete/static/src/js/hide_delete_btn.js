/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { messageActionsRegistry } from "@mail/core/common/message_actions";

/*
 * Hide delete from chatter for regular users.
 * For admins, replace delete behavior with reason wizard.
 */
const deleteAction = messageActionsRegistry.get("delete");

patch(deleteAction, {
    condition(params) {
        if (!this.store?.env?.services?.user?.isSystem) {
            return false;
        }
        return super.condition(params);
    },

    async onSelected({ message, owner }) {
        await owner.env.services.action.doAction("no_chatter_delete.action_delete_reason_wizard", {
            additionalContext: {
                default_message_id: message.id,
            },
            onClose: () => {
                message.thread?.fetchNewMessages();
            },
        });
    },
});
