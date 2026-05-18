/** @odoo-module */
import { registry} from '@web/core/registry';
import { useService } from "@web/core/utils/hooks";
const { Component, useState, onWillStart, onMounted} = owl
import { rpc } from "@web/core/network/rpc";
import { _t } from "@web/core/l10n/translation";
import { session } from "@web/session";
import { WebClient } from "@web/webclient/webclient";

export class TenderDashboard extends Component {
    /**
     * Sets up the Tender Dashboard component.
     * Initializes required services and lifecycle hooks.
     */
     setup() {
        this.action = useService("action");
        this.orm = useService("orm");
        this.state = useState({
            all_tenders: [],
            total_tender_count: [],
        });
       }
    all_tenders(e) {
        var self = this;
        e.stopPropagation();
        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.action.doAction({
            name: _t("Tenders"),
            type: 'ir.actions.act_window',
            res_model: 'tender.tender',
            view_mode: 'list,form,calendar',
            views: [
                [false, 'list'],
                [false, 'form']
            ],
            domain: [],
            target: 'current',
        }, options)
    }
    procurement_document(e) {
        var self = this;
        e.stopPropagation();
        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.action.doAction({
            name: _t("Tenders"),
            type: 'ir.actions.act_window',
            res_model: 'tender.document',
            view_mode: 'list,form',
            views: [
                [false, 'list'],
                [false, 'form']
            ],
            domain: [],
            target: 'current',
        }, options)
    }
    bid_records(e) {
        var self = this;
        e.stopPropagation();
        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.action.doAction({
            name: _t("Tenders"),
            type: 'ir.actions.act_window',
            res_model: 'tender.bid',
            view_mode: 'list,form',
            views: [
                [false, 'list'],
                [false, 'form']
            ],
            domain: [],
            target: 'current',
        }, options)
    }
    tot_sale(e) {
        var self = this;
        e.stopPropagation();
        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.action.doAction({
            name: _t("Supplier Verification"),
            type: 'ir.actions.act_window',
            res_model: 'supplier.verification',
            view_mode: 'list,form',
            views: [
                [false, 'list'],
                [false, 'form']
            ],
            domain: [],
            target: 'current',
        }, options)
    }
    bid_evaluation(e) {
        var self = this;
        e.stopPropagation();
        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.action.doAction({
            name: _t("Tenders"),
            type: 'ir.actions.act_window',
            res_model: 'bid.evaluation',
            view_mode: 'list,form',
            views: [
                [false, 'list'],
                [false, 'form']
            ],
            domain: [],
            target: 'current',
        }, options)
    }
    request_received(e) {
        var self = this;
        e.stopPropagation();
        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.action.doAction({
            name: _t("Request Received"),
            type: 'ir.actions.act_window',
            res_model: 'purchase.order',
            view_mode: 'list,form',
            views: [
                [false, 'list'],
                [false, 'form']
            ],
            domain: [],
            target: 'current',
        }, options)
    }

    orders_raised(e) {
        var self = this;
        e.stopPropagation();
        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.action.doAction({
            name: _t("Orders Raised"),
            type: 'ir.actions.act_window',
            res_model: 'purchase.order',
            view_mode: 'list,form',
            views: [
                [false, 'list'],
                [false, 'form']
            ],
            domain: [],
            target: 'current',
        }, options)
    }

    request_quotation(e) {
        var self = this;
        e.stopPropagation();
        e.preventDefault();
        var options = {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb,
        };
        this.action.doAction({
            name: _t("Request for proposal/Quotation"),
            type: 'ir.actions.act_window',
            res_model: 'purchase.order',
            view_mode: 'list,form',
            views: [
                [false, 'list'],
                [false, 'form']
            ],
            domain: [],
            target: 'current',
        }, options)
    }

}
TenderDashboard.template = "TenderDashboard"
registry.category("actions").add("tender_dashboard", TenderDashboard)
