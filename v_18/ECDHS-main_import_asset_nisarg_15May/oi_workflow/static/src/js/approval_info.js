/** @odoo-module */

import { Dialog } from "@web/core/dialog/dialog";
import { _lt } from "@web/core/l10n/translation";
import { useAutofocus } from "@web/core/utils/hooks";

const { Component } = owl;

export class ApprovalInfoDialog extends Component {
    setup() {
        useAutofocus();
    }
}

ApprovalInfoDialog.template = "oi_workflow.approval_info";
ApprovalInfoDialog.components = { Dialog };
ApprovalInfoDialog.defaultProps = {
    title: _lt("Approval Info"),
};
