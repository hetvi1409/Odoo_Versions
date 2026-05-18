import { messageActionsRegistry } from "@mail/core/common/message_actions";
import { Composer } from "@mail/core/common/composer";
import { patch } from "@web/core/utils/patch";

const DeleteBtn = messageActionsRegistry.get("delete");

messageActionsRegistry.add("delete", {
    ...DeleteBtn,
    condition: (params) => {
        const { message, store } = params;
        // only show delete btn if the user is admin
        if (!store.self.main_user_id?.is_admin) {
            return false;
        }
        return message.editable;
    },

    onSelected: async ({ message, owner, store, thread }) => {
        const action = await store.env.services.orm.call(
            "mail.message",
            "action_open_delete_reason_wizard",
            [[message.id]]
        );
        if (!action || action.type !== "ir.actions.act_window") {
            return;
        }
        const safeAction = {
            ...action,
            views: action.views || [[action.view_id || false, "form"]],
        };
        owner.env.services.action.doAction(safeAction, {
            onClose: () => thread?.fetchNewMessages?.(),
        });
    },
}, { force: true });

patch(Composer.prototype, {
    async editMessage() {
        if (this.askDeleteFromEdit) {
            const composer = this.props.composer;
            const message = composer?.message;
            if (!message) {
                return super.editMessage(...arguments);
            }
            const store = message.store;
            if (!store?.self?.main_user_id?.is_admin) {
                return super.editMessage(...arguments);
            }
            // Open the wizard instead of the confirm dialog
            const action = await store.env.services.orm.call(
                "mail.message",
                "action_open_delete_reason_wizard",
                [[message.id]]
            );
            if (!action || action.type !== "ir.actions.act_window") {
                return super.editMessage(...arguments);
            }
            const safeAction = {
                ...action,
                views: action.views || [[action.view_id || false, "form"]],
            };
            const thread = message.thread;
            this.env.services.action.doAction(safeAction, {
                onClose: () => {
                    message.exitEditMode?.(thread);
                    thread?.fetchNewMessages?.();
                },
            });
            return;
        }
        return super.editMessage(...arguments);
    },
});