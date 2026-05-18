// /** @odoo-module **/

// import { patch } from "@web/core/utils/patch";
// import { KanbanRecord } from "@web/views/kanban/kanban_record";

// patch(KanbanRecord.prototype, {
//     get moveLines() {
//         const record = this.props.record.data;
//         console.log('record>>>',record);

//         if (!record.move_ids_without_package) {
//             return [];
//         }

//         return record.move_ids_without_package.records.map((move) => {
//             return {
//                 product: move.data.product_id
//                     ? move.data.product_id[1]
//                     : "Unknown",
//                 qty: move.data.product_uom_qty || 0,
//             };
//         });
//     },
// });