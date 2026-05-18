/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useRef, onMounted, onWillStart } from "@odoo/owl";
import { Many2One } from "./many2one/many2one";
import { hotkeyService } from "@web/core/hotkeys/hotkey_service";
import { useService } from "@web/core/utils/hooks";
// Ensure the hotkey service is registered
if (!registry.category("services").contains("hotkey")) {
    registry.category("services").add("hotkey", hotkeyService);
}
import ajax from "web.ajax";
// Ensure the hotkey service is registered
//registry.category("services").add("hotkey", hotkeyService);
export class HostPage extends Component {
    setup() {
        this.buttonRef = useRef("button");
        this.inputPropertyType = useRef("PropertyType");
        this.department = useRef("Department");
        this.rpc = useService("rpc"); // ✅ defined inside setup()

        this.state = {
            departments: [],
        };

        onWillStart(async () => {
            const url = `/frontdesk/${this.props.stationId}/${this.props.token}/get_department`;
            const departments = await this.env.services.rpc({
                route: url,
                params: {},
            });
            this.state.departments = departments;
        });
        debugger;
    }

    /**
     * This method disables the confirm button.
     * When the text in the input field is not present in the selection.
     *
     * @param {Boolean} isDisable
     */
    disableButton(isDisable) {
        this.buttonRef.el.disabled = isDisable;
    }

    /**
     * This method is triggered when the confirm button is clicked.
     * It sets the host data and displays the RegisterPage component.
     *
     * @private
     */
    async _onConfirm() {
        this.props.inputPropertyType = this.inputPropertyType.el?.value;
        console.log(this)

        const result = await this.rpc({
                model: 'frontdesk.frontdesk',
                method: 'get_host_data_frontdesk',
                args: [[], this.props.stationId],
            });
        this.host = result
        this.host.inputPropertyType = this.inputPropertyType.el?.value;
        this.props.setHostData(this.host);
        this.inputPropertyType = this.inputPropertyType.el?.value;
//        this.host.inputDepartment = this.department.el?.value;
        console.log(this, 'hostpage')
        console.log(this.props, 'hostpage props')
        this.props.showScreen("RegisterPage");
    }

    /**
     * @param {Object} host
     */
    async selectedHost(host) {
        this.host = host;
        console.log(host, 'aaaaaaaaaaaa')
        const result = await this.rpc({
                model: 'frontdesk.frontdesk',
                method: 'get_host_data_frontdesk',
                args: [[], this.props.action.context.station_id],
            });
        this.inputPropertyType = this.inputPropertyType.el?.value || false;
        console.log(this.inputPropertyType, 'inputPropertyType')
        this.host.inputDepartment = this.department.el?.value || false;

    }
}

HostPage.template = "frontdesk.HostPage";
HostPage.components = { Many2One };
HostPage.props = {
    setHostData: Function,
    showScreen: Function,
    stationId: Number,
    token: String,
};

registry.category("frontdesk_screens").add("HostPage", HostPage);
