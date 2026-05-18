/** @odoo-module **/
import { registry } from "@web/core/registry";
import { BlockUI } from "@web/core/ui/block_ui";
import { download } from "@web/core/network/download";
registry.category('ir.actions.report handlers').add('xlsx_reports',
    async(action)=> {
        if (action.report_type === 'xlsx_reports') {
            BlockUI;
            await download({
                url: '/xlsx_reports',
                data: action.data,
                completed: () => unblockUI,
                error: (error) => self.call('crash_manger', 'rpc_error', error),
            });
            return true
        }
});