/** @odoo-module **/

import { registry } from "@web/core/registry";
import { NameAndSignature } from "@web/core/signature/name_and_signature";

NameAndSignature.defaultProps.fontColor = "Black";

//// Extend the original component
//export class CustomNameAndSignature extends NameAndSignature {
//    static defaultProps = {
//        ...NameAndSignature.defaultProps,
//        fontColor: "Black",  // override default font color
//    };
//}
//
//// Register your custom component if used directly via template
//registry.category("components").add("CustomNameAndSignature", CustomNameAndSignature);
