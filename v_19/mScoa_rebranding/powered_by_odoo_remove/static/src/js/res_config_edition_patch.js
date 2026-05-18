/** @odoo-module **/

import { session } from "@web/session";
import { patch } from "@web/core/utils/patch";
import { resConfigEdition } from "@web/webclient/settings_form_view/widgets/res_config_edition";

patch(resConfigEdition.component.prototype, {
    setup() {
        super.setup();
        this.poweredByText = session.powered_by_text || "";
        this.replacePoweredBy = session.replace_powered_by_odoo || false;
    },
});
