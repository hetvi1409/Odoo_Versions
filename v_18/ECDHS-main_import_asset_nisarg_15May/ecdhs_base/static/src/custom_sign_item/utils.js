/** @odoo-module **/

import * as SignUtils from "@sign/components/sign_request/utils";

// Backup original
const originalStartResize = SignUtils.startResize;

// Override
SignUtils.startResize = function (signItem, onResize) {
    const resizeHandleWidth = signItem.el.querySelector(".resize_width");
    const resizeHandleHeight = signItem.el.querySelector(".resize_height");
    const resizeHandleBoth = signItem.el.querySelector(".resize_both");

    // ✅ Your custom condition
    if (!resizeHandleWidth || !resizeHandleHeight || !resizeHandleBoth) {
        return;
    }

    // Call original if valid
    return originalStartResize(signItem, onResize);
};