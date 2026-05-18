/** @odoo-module */
import { registry } from "@web/core/registry";
import { BinaryField } from "@web/views/fields/binary/binary_field";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";

patch(BinaryField.prototype, "BinaryFieldWidget", {
    setup() {
        this._super.apply(this, arguments);
        this.rpc = useService("rpc");
        this.orm = useService("orm");
        this.actionService = useService("action");
    },
    async open_images(ev) {
        if (!this.props.value) {
            alert("No file uploaded!");
            return;
        }
        console.log((this), 'fddfzd')
        console.log((this.props), 'dsf')

        var data = ""
        if (this.props.record.resModel == 'ir.attachment'){
            data = {
                'value': this.props.record.data.id,
                'model': this.props.record.resModel
            }
        }
        else {
            data = {
                    'value': this.props.value,
                    'model': this.props.record.resModel,
                    'id': this.props.record.data.id,
                    'field_name': this.props.name,
                }
        }
        var data = await this.orm.call('image.preview', 'action_open_images', [1, data]);
        console.log(data)
        this.actionService.doAction({
            type: "ir.actions.act_window",
            name: _t("Image Preview"),
            res_model: "image.preview",
            res_id: data,
            views: [[false, "form"]],
            target: "new",
//            context: {
//                default_file: this.props.value,
//                default_pdf: this.props.value,
//            },
        });
    },
});
