import { registry } from "@web/core/registry";
import { kanbanView } from "@web/views/kanban/kanban_view";
import { CloudManagerKanbanController } from "./cloud_manager_kanban_controller";
import { CloudManagerKanbanModel } from "./cloud_manager_kanban_model";
import { CloudManagerKanbanRenderer } from "./cloud_manager_kanban_renderer";
import { CloudManagerSearchModel } from "../search/cloud_manager_search_model";
console.log("CloudManagerKanbanController",CloudManagerKanbanController)
console.log("CloudManagerKanbanModel",CloudManagerKanbanModel)
console.log("CloudManagerKanbanRenderer",CloudManagerKanbanRenderer)
console.log("CloudManagerSearchModel",CloudManagerSearchModel)

export const CloudManagerKanbanView = {
    ...kanbanView,
    SearchModel: CloudManagerSearchModel,
    Controller: CloudManagerKanbanController,
    Model: CloudManagerKanbanModel,
    Renderer: CloudManagerKanbanRenderer,
    searchMenuTypes: ["filter", "favorite"],
    buttonTemplate: "cloud_base.CloudBaseViewButtons",
};

registry.category("views").add("cloud_base_kanban", CloudManagerKanbanView);
