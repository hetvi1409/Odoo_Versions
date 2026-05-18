/** @odoo-module **/

import { KanbanRecord } from "@web/views/kanban/kanban_record";
import { KANBAN_CARD_ATTRIBUTE } from "@web/views/kanban/kanban_arch_parser";
import { FileUploadProgressBar } from "@web/core/file_upload/file_upload_progress_bar";
import { useBus, useService } from "@web/core/utils/hooks";
import { useState, xml } from "@odoo/owl";
const CANCEL_GLOBAL_CLICK = ["a", ".dropdown", ".oe_kanban_action"].join(",");
console.log(KanbanRecord,'kanban rec...')
export class CloudManagerKanbanRecord extends KanbanRecord {
    static components = {
        ...KanbanRecord.components,
        FileUploadProgressBar,
    };
    static defaultProps = {
        ...KanbanRecord.defaultProps,
    };
    static template = xml`
        <div
            role="article"
            t-att-class="getRecordClasses()"
            t-att-data-id="props.canResequence and props.record.id"
            t-att-tabindex="props.record.model.useSampleModel ? -1 : 0"
            t-on-click.synthetic="onGlobalClick"
            t-on-keydown.synthetic="onKeydown"
            t-ref="root">
            <t t-call="{{ templates[this.constructor.KANBAN_CARD_ATTRIBUTE] }}" t-call-context="this.renderingContext"/>
        </div>`;
    setup() {
        super.setup();
        // File upload
        const { bus, uploads } = useService("file_upload");
        this.documentUploads = uploads;
        useBus(bus, "FILE_UPLOAD_ADDED", (ev) => {
            if (ev.detail.upload.data.get("document_id") == this.props.record.resId) {
                this.render(true);
            }
        });
        this.drag = useState({ state: "none" });

        // Pdf Thumbnail
        this.pdfService = useService("documents_pdf_thumbnail");
        this.pdfService.enqueueRecords([this.props.record]);
    }
    /*
    * Re-write to add its own classes for selected kanban record
    */
    getRecordClasses() {
        let result = super.getRecordClasses();
        if (this.props.record.selected) {
            result += " jstr-kanban-selected";
        }
        return result;
    }
    /*
    * The method to manage clicks on kanban record
    */
    onGlobalClick(ev) {
        if (ev.target.closest(CANCEL_GLOBAL_CLICK)) {
            return;
        }
        // Preview is clicked
        if (ev.target.closest("div[name='document_preview']")) {
            this.props.record.onClickPreview(ev);
            if (ev.cancelBubble) {
                return;
            }
        }
        this.props.record.onRecordClick(ev);
    }
    get renderingContext() {
        const context = super.renderingContext;
        context.encodeURIComponent = encodeURIComponent;
        console.log(this,'this....')
        return context;
    }
    /*
    * The method to manage key presses on kanban view (always add to selection)
    */
    onKeydown(ev) {
        if (ev.key !== "Enter" && ev.key !== " ") {
            return;
        }
        ev.preventDefault();
        return this.props.record.onRecordClick(ev, {});
    }
};

