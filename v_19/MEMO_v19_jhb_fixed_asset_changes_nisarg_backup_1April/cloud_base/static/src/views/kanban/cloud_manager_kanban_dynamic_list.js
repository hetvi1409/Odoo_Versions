/** @odoo-module **/

import { DynamicRecordList } from "@web/model/relational_model/dynamic_record_list";
console.log('kanban dynamic....')
export class CloudManagerKanbanDynamicRecordList extends DynamicRecordList {
    /*
    * Re-write to trigger toggle selection for the old selection
    */
    async load() {
        await super.load();
        const selectedRecords = this.model.selectedRecords;
        const records = this.records;

        Object.values(records).forEach(function (record) {
            if (selectedRecords.find(rec => rec.id === record.resId)) {
                record.toggleSelection(true, true);
            }
        });
    }
    /*
    * Overwrite to save selected records to state
    */
    exportState() {
        const state = {
            ...super.exportState(),
            selectedRecords: this.model.selectedRecords,
        };
        return state
    }
}
