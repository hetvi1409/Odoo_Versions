/** @odoo-module */
import {registry} from "@web/core/registry";
import framework from "web.framework";
import session from "web.session";

registry.category("ir.actions.report handlers").add("xlsx_asset_verify", async (action) => {

    if (action.report_type === 'xlsx_asset') {
        framework.blockUI();
        var def = $.Deferred();
        session.get_file({
            url: '/xlsx_asset_reports',
            data: action.data,
            success: def.resolve.bind(def),
            complete: framework.unblockUI,
        });
    return def;
    }
})