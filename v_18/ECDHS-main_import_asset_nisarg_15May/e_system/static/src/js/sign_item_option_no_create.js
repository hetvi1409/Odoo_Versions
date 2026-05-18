/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { SignItemCustomPopover } from "@sign/backend_components/sign_template/sign_item_custom_popover";

/**
 * Disable the inline "Create …" quick-create option that appears in the
 * Options many2many-tags field of the Selection sign-item popover.
 * Users must manage options through Configuration > Sign Item Options.
 */
patch(SignItemCustomPopover.prototype, {
    getOptionsProps(record, fieldName) {
        return {
            ...super.getOptionsProps(record, fieldName),
            canQuickCreate: false,
            canCreate: false,
            canCreateEdit: false,
        };
    },
});
