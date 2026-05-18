/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { SettingsModal } from "./settings_modal";

export class HomeCustomizerSystray extends Component {
    setup() {
        this.dialog = useService("dialog");
    }

    onClick() {
        this.dialog.add(SettingsModal, {
            title: _t("Appearance Settings"),
        });
    }
}

HomeCustomizerSystray.template = "home_customizer.SystrayItem";

export const systrayItem = {
    Component: HomeCustomizerSystray,
};

registry.category("systray").add("HomeCustomizerSystray", systrayItem, { sequence: 100 });