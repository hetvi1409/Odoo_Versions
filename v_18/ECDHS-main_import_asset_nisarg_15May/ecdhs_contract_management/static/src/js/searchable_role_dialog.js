/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { Dialog } from "@web/core/dialog/dialog";
import { Component, useState } from "@odoo/owl";

export class SearchableRoleDialog extends Component {
    static template = "ecdhs_contract_management.SearchableRoleDialog";
    static components = {
        Dialog,
    };
    static props = {
        addRole: Function,
        close: Function,
        roles: Object,
        responsible: Number,
        pageCount: Number,
        title: { type: String, optional: true },
    };

    setup() {
        this.state = useState({
            query: "",
            selectedRole: this.props.responsible,
        });
    }

    get rolesAsList() {
        return Object.entries(this.props.roles)
            .map(([id, role]) => ({ id: Number(id), ...role }))
            .sort((a, b) => (a.name || "").localeCompare(b.name || ""));
    }

    get filteredRoles() {
        const query = (this.state.query || "").trim().toLowerCase();
        if (!query) {
            return this.rolesAsList;
        }
        return this.rolesAsList.filter((role) => (role.name || "").toLowerCase().includes(query));
    }

    onSelectRole(ev) {
        this.state.selectedRole = Number(ev.target.value || this.props.responsible);
    }

    onAddOnceClick() {
        this.props.addRole(this.state.selectedRole || this.props.responsible, false);
        this.props.close();
    }

    onAddToAllPagesClick() {
        this.props.addRole(this.state.selectedRole || this.props.responsible, true);
        this.props.close();
    }

    get dialogProps() {
        return {
            size: "md",
            title: this.props.title || _t("Select Responsible"),
        };
    }
}
