/** @odoo-module **/

import { Component, onMounted, useRef, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { user } from "@web/core/user";



export class PerformanceContractDashboard extends Component {
    static template = "performanance_contract_dashboard";

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");

        this.user = user;
        console.log("login User this:", this.user);


        this.state = useState({
            inProgressCount: 0,
            pendingApprovalsCount: 0,
        });

        onMounted(() => {
            this.loadInProgressContracts();
            this.loadPendingApprovals();
            this.loadPendingEmployeeSignatures();
            this.loadPendingManagerSignatures();
        });
    }

    async loadInProgressContracts() {
        console.log("Performance Contract Dashboard");
        const login_user_id = this.user.userId;
        const contracts = await this.orm.searchRead(
            "performance.contract",
            [['state', '=', 'in_process'],['employee_id.user_id', '=', login_user_id]],
            ["id","employee_id"]
        );
        console.log("Performance Contracts:", contracts);
        this.state.inProgressCount = contracts.length;
        console.log("In Progress Contracts Count:", this.state.inProgressCount);
    }

    openInProgressContracts() {
        console.log("Opening In Progress Contracts");
        const login_user_id = this.user.userId;
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "In Progress Contracts",
            res_model: "performance.contract",
            domain: [['state', '=', 'in_process'],['employee_id.user_id', '=', login_user_id]],
            views: [[false, "list"], [false, "form"]],
            target: "current",
        });
    }

    async loadPendingApprovals() {
        console.log("Loading Pending Approvals");
        const login_user_id = this.user.userId;
        console.log("Login User ID:", login_user_id);
        const contracts = await this.orm.searchRead(
            "performance.contract",
            // [['state', '=', 'approval_in_process'], ['current_approver_id', '=', login_user_id]],
            [['current_approver_id', '=', login_user_id]],
            ["id"]
        ).then((contracts) => {
            console.log("Pending Approval Contracts:", contracts);
            this.state.pendingApprovalsCount = contracts.length;
            console.log("Pending Approvals Count:", this.state.pendingApprovalsCount);
        });

    }

    openPendingApprovals() {
        console.log("Opening Pending Approvals");

        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Pending Approvals",
            res_model: "performance.contract",
            domain: [['current_approver_id', '=', this.user.userId]],
            views: [[false, "list"], [false, "form"]],
            target: "current",
        });

    }

    async loadPendingEmployeeSignatures() {
        console.log("Loading Pending Signatures");
        const login_user_id = this.user.userId;
        console.log("Login User ID:", login_user_id);
        const contracts = await this.orm.searchRead(
            "performance.contract",
            [['employee_id.user_id', '=', login_user_id], ['signed_by_employee', '!=', true],['state', 'in', ['in_process','signed_by_manager']]],
            ["id"]
        ).then((contracts) => {
            console.log("Pending Signature Contracts:", contracts);
            this.state.pendingEmployeeSignaturesCount = contracts.length;
            console.log("Pending Signatures Count:", this.state.pendingEmployeeSignaturesCount);
        });

    }

    openPendingEmployeeSignatures() {
        console.log("Opening Pending Employee Signatures");
        const login_user_id = this.user.userId;
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Pending Employee Signatures",
            res_model: "performance.contract",
            domain: [['employee_id.user_id', '=', login_user_id], ['signed_by_employee', '!=', true],['state', 'in', ['in_process','signed_by_manager']]],
            views: [[false, "list"], [false, "form"]],
            target: "current",
        });

    }

    async loadPendingManagerSignatures() {
        console.log("Loading Pending Manager Signatures");
        const login_user_id = this.user.userId;
        console.log("Login User ID:", login_user_id);
        const contracts = await this.orm.searchRead(
            "performance.contract",
            [['employee_id.parent_id.user_id', '=', login_user_id], ['signed_by_manager', '!=', true],['state', 'in', ['in_process','signed_by_employee']]],
            ["id"]
        ).then((contracts) => {
            console.log("Pending Manager Signature Contracts:", contracts);
            this.state.pendingManagerSignaturesCount = contracts.length;
            console.log("Pending Manager Signatures Count:", this.state.pendingManagerSignaturesCount);
        });


    }

    openPendingManagerSignatures() {
        console.log("Opening Pending Manager Signatures");
        const login_user_id = this.user.userId;
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Pending Manager Signatures",
            res_model: "performance.contract",
            domain: [['employee_id.parent_id.user_id', '=', login_user_id], ['signed_by_manager', '!=', true],['state', 'in', ['in_process','signed_by_employee']]],
            views: [[false, "list"], [false, "form"]],
            target: "current",
        });

    }


}

registry.category("actions").add("performance_contract_dashboard", PerformanceContractDashboard);

