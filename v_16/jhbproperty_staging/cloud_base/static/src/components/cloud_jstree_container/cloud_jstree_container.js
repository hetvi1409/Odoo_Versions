/** @odoo-module **/

import { _lt } from "@web/core/l10n/translation";
import { Domain } from "@web/core/domain";
import { FormViewDialog } from "@web/views/view_dialogs/form_view_dialog";
import { loadCSS, loadJS } from "@web/core/assets";
import { registerMessagingComponent } from "@mail/utils/messaging_component";
import { useService } from "@web/core/utils/hooks";
const { Component, onWillStart, onMounted, onPatched, useState } = owl;

const componentModel = "clouds.folder";


export class CloudJsTreeContainer extends Component {
    /*
    * Re-write to import required services and update props on the component start
    */
    setup() {
        this.state = useState({ treeData: null });
        this.orm = useService("orm");
        this.actionService = useService("action");
        this.dialogService = useService("dialog");
        this.userService = useService("user");
        this.searchString = "";
        this.lastSearch = false;
        onWillStart(async () => {
            const proms = [
                loadJS("/cloud_base/static/lib/jstree/jstree.min.js"),
                loadCSS("/cloud_base/static/lib/jstree/themes/default/style.css"),
                this._loadTreeData(this.props),
                this._loadSettings(this.props),
            ]
            return Promise.all(proms);
        });
        onMounted(() => {
            this.jsTreeAnchor = $("#"+this.id);
            this.jsTreeSearchInput = $("#jstr_input_" + this.id)[0];
            this._renderJsTree();
        })
    }
    /*
    * Getter for id (jstree_key unique reference)
    */
    get id() {
        return this.props.jstreeId;
    }
    /*
    * The method to update jsTree data
    */
    async _loadTreeData(props) {
        const jstreeData = await this.orm.call(
            componentModel, "action_get_hierarchy", [this.id, props.resModel, props.resId],
        );
        Object.assign(this.state, { treeData: jstreeData });
    }
    /*
    * The method to get settings
    */
    async _loadSettings(props) {
        if (props.kanbanView) { this.fileManagerRigths = false }
        else { this.fileManagerRigths = await this.userService.hasGroup("cloud_base.group_cloud_base_user") };
    }
    /*
    * The method to get context_menu options
    */
    _getJsTreeContextMenu() {
        var self = this;
        return {
            "select_node": false,
            "items": function($node) {
                const jsTreeAnchor = self.jsTreeAnchor.jstree(true);
                var items = {};
                if ($node.data) {
                    items.downloadZip = {
                        "label": _lt("Download as archive"),
                        "action": function (obj) { window.location = "/cloud_base/folder_upload/" + $node.id }
                    };                            
                };
                if ($node.data && $node.data.edit_right) {
                    items.createNew = {
                        "separator_after": true,
                        "label": _lt("Create subfolder"),
                        "action": function (obj) {
                            $node = jsTreeAnchor.create_node($node);
                            jsTreeAnchor.edit($node);
                        }
                    };
                };
                if ($node.data && $node.data.url) {
                    items.openInClouds = {
                        "label": _lt("Open in clouds"),
                        "action": function (obj) {                              
                            if ($node.data && $node.data.url) {
                                window.open($node.data.url, "_blank").focus();
                            }
                            else {
                                alert(_lt("This folder is not synced yet"))
                            };
                        }
                    };
                };
                if ($node.data && self.props.kanbanView && $node.data.res_model && $node.data.res_id) {
                    items.openParentObject = {
                        "label": _lt("Open linked object"),
                        "action": function (obj) {                                  
                            self._onOpenOdooObject($node);
                        }
                    };
                };
                if (self.fileManagerRigths && $node.data) {
                    items.openParentObject = {
                        "label": _lt("Open in File Manager"),
                        "action": function (obj) {                                  
                            var resId = parseInt($node.id);
                            self._onOpenFileManager(resId);
                        }
                    };
                };
                if ($node.data && ($node.data.rule_related || !$node.data.edit_right)) {
                    items.openNode = {
                        "label": _lt("Settings"),
                        "action": function (obj) { self._onEditNodeForm(jsTreeAnchor, $node, true) }
                    };
                }
                else {
                    items.renameNode = {
                        "label": _lt("Rename"),
                        "action": function (obj) { jsTreeAnchor.edit($node) }
                    };
                    items.editNode = {
                        "label": _lt("Edit Settings"),
                        "action": function (obj) { self._onEditNodeForm(jsTreeAnchor, $node, false) }
                    };
                    items.archiveNode = {
                        "separator_before": true,
                        "label": _lt("Archive"),
                        "action": function (obj) { jsTreeAnchor.delete_node($node) }
                    };
                };                        
                return items
            },
        };
    }
    /*
    * The method to initiate jstree
    */
    async _renderJsTree() {
        var self = this,
            defaultChosenFolder = false;
        if (this.props.parentModel.rootParams && this.props.parentModel.rootParams.context) {
            defaultChosenFolder = this.props.parentModel.rootParams.context.default_chosen_folder
        };
        const jsTreeKey = (this.props.resModel && this.props.resId) ? this.id + "_" + this.props.resModel + "_" + this.props.resId : this.id;
        const jsTreeOptions = {
            "core" : {
                "check_callback" : function (operation, node, node_parent, node_position, more) {
                    if (operation === "move_node") {
                        if (!node_parent || !node_parent.data || !node_parent.data.edit_right) {
                            return false
                        };
                    };
                    return true
                },
                "themes": {"icons": true},
                "stripes" : true,
                "multiple" : false,
                "data": this.state.treeData,
                "strings": {"New node": _lt("New Folder"),},
            },
            "plugins" : [
                "state",
                "changed",
                "search",
                "dnd",
                "contextmenu",
            ],  
            "state" : { "key" : jsTreeKey },
            "search": {
                "case_sensitive": false,
                "show_only_matches": true,
                "fuzzy": false,
                "show_only_matches_children": true,
            },
            "dnd": {
                "is_draggable" : function(node) {
                    if (!node[0].data.edit_right || node[0].data.rule_related) {
                        return false;
                    }
                    return true;
                }                    
            },
            "contextmenu": this._getJsTreeContextMenu(),
        };
        const jsTree = this.jsTreeAnchor.jstree(jsTreeOptions);
        const jsTreeAnchor = this.jsTreeAnchor.jstree(true);

        this.jsTreeAnchor.on("rename_node.jstree", self, function (event, data) {
            // This also includes "create" event. Since each time created, a node is updated then
            self._onUpdateNode(jsTreeAnchor, data, false);
        });
        this.jsTreeAnchor.on("move_node.jstree", self, function (event, data) {
            self._onUpdateNode(jsTreeAnchor, data, true);
        });
        this.jsTreeAnchor.on("delete_node.jstree", self, function (event, data) {
            self._onDeleteNode(data);
        });
        this.jsTreeAnchor.on("copy_node.jstree", self, function (event, data) {
            self._onUpdateNode(jsTreeAnchor, data, true);
        });

        this.jsTreeAnchor.on("state_ready.jstree", self, function (event, data) {
            self.jsTreeAnchor.on("changed.jstree", self, function (event, data) {
                self._onUpdateDomain(jsTreeAnchor);
            })
            self.jsTreeAnchor.on("open_node.jstree", self, function (event, data) {
                // On each opening we should recalculate highlighted parents
                self._highlightParent(jsTreeAnchor, jsTreeAnchor.get_selected(), "#"+self.id);
            })
            self.jsTreeAnchor.on("search.jstree", self, function (event, data) {
                // On each opening we should recalculate highlighted parents
                if (data.res.length != 0) {
                    self.lastSearch = data.res[0];
                }
            })
            self.jsTreeAnchor.on("clear_search.jstree", self, function (event, data) {
                self.lastSearch = false;
            })
            if (!defaultChosenFolder) { self._onUpdateDomain(jsTreeAnchor) }
            else {
                // we get here with chosen folder in context
                jsTreeAnchor.deselect_all(true);
                jsTreeAnchor.select_node(defaultChosenFolder);
                self._onUpdateDomain(jsTreeAnchor); // since no change yet
            };
        });
    }
    /*
    * The method to calculate domain based on checks and trigger the parent search model to reload
    */
    async _onUpdateDomain(jsTreeAnchor) {
        const checkedTreeItems = jsTreeAnchor.get_selected();
        if (!checkedTreeItems || checkedTreeItems.length == 0) {
            // if no selection > it is preferable to make that
            var firstShowParentNode = false;
            if (this.lastSearch) {
                // if search results > select the first found
                firstShowParentNode = this.lastSearch;
            }
            else {
                // otherwise the very first shown parent
                firstShowParentNode = jsTreeAnchor.get_node("#").children.find(node => !jsTreeAnchor.is_hidden(node));                
            };
            if (firstShowParentNode) {
                jsTreeAnchor.deselect_all(true); // doesn't trigger change
                jsTreeAnchor.select_node(firstShowParentNode); // triggers change
                return
            }
        };
        this._highlightParent(jsTreeAnchor, checkedTreeItems, "#"+this.id);
        await this.props.onUpdateSearch(this.id, this._getDomain(checkedTreeItems));
    }
    /*
    * The method to get change in the search input and save it
    */
    _onSearchChange(event) {
        this.searchString = event.currentTarget.value;
    }
    /*
    * The method to execute search in jsTree
    */
    _onSearchExecute() {
        const jsTreeAnchor = this.jsTreeAnchor.jstree(true);
        jsTreeAnchor.deselect_all(true); // doesn't trigger change
        if (this.searchString) { this.jsTreeAnchor.jstree("search", this.searchString) }
        else { this.jsTreeAnchor.jstree("clear_search") };
        this._onUpdateDomain(jsTreeAnchor); // so unchecked leaves are reflected
    }
    /*
     * The method to manage keyup on search input > if enter then make search
    */
    _onSearchkeyUp(event) {
        if (event.keyCode === 13) {
            this._onSearchExecute();
        };
    }
    /*
     * The method to clear seach input and clear jstree search
    */
    _onSearchClear() {
        this.jsTreeSearchInput.value = "";
        this.searchString = "";
        this.jsTreeAnchor.jstree("clear_search");
    }
    /*
     * The method to trigger update of jstree node
    */
    async _onUpdateNode(jsTreeAnchor, data, position) {
        var newNodeId;
        if (data.node.id === parseInt(data.node.id).toString()) {
            // node exists in tree (no need for refreshing)
            if (position) {
                // that a node move
                position = parseInt(data.position);
            };
            newNodeId = await this.orm.call(
                componentModel, "action_update_node", [parseInt(data.node.id), data.node, position],
            );
        }
        else {
            // brand new node
            newNodeId = await this.orm.call(componentModel, "action_create_node", [data.node]);
        };
        this._refreshNodeAfterUpdate(data.node, newNodeId)
    }
    /*
     * The method to trigger unlink of jstree node 
    */
    async _onDeleteNode(data) {
        await this.orm.call(componentModel, "action_delete_node", [parseInt(data.node.id)]);
    }
    /*
     * The method to add a new root jstree item
    */
    _onAddRootTag() {
        const jsTreeAnchor = this.jsTreeAnchor.jstree(true);
        var selectedNode = jsTreeAnchor.get_selected();
        selectedNode = jsTreeAnchor.create_node("#");
        if(selectedNode) {
            jsTreeAnchor.edit(selectedNode);
        };
    }
    /*
     * The method to open the folder edit form
    */
    async _onEditNodeForm(jsTreeAnchor, node, nodePreventEdit) {
        var self = this;
        this.dialogService.add(FormViewDialog, {
            resModel: componentModel,
            resId: parseInt(node.id),
            title: _lt("Settings"),
            preventCreate: true,
            preventEdit: nodePreventEdit,
            onRecordSaved: async (formRecord) => {
                jsTreeAnchor.set_text(node, formRecord.data.name);
                if (formRecord.data.parent_id && formRecord.data.parent_id.length != 0) {
                    const newParent = formRecord.data.parent_id[0].toString();
                    if (newParent != node.parent) {
                        jsTreeAnchor.move_node(node, newParent);
                    };
                };
                const newNodeId = await self.orm.call(
                    componentModel, "action_js_format_folder_for_js_tree", [[parseInt(node.id)]],
                );
                self._refreshNodeAfterUpdate(node, newNodeId)
            },
        });
    }
    /*
     * The method to show linked object form
    */
    async _onOpenOdooObject($node) {
        var self = this;
        this.dialogService.add(FormViewDialog, {
            resModel: $node.data.res_model,
            resId: $node.data.res_id,
            preventCreate: true,
        });                 
    }
    /*
     * The method to open file manager with a default selected folder
    */
    async _onOpenFileManager(resId) {
        this.actionService.doAction("cloud_base.ir_attachment_action", {
            additionalContext: { default_chosen_folder: resId },
        });
    }
    /*
     * The method to refresh updated node and select it
    */   
    _refreshNodeAfterUpdate(node, new_data) {
        const jsTreeAnchor = this.jsTreeAnchor.jstree(true);
        jsTreeAnchor.set_id(node, new_data.id);
        jsTreeAnchor.set_text(node, new_data.text);
        jsTreeAnchor.set_icon(node, new_data.icon);
        node.data = new_data.data;
        jsTreeAnchor.deselect_all(true);
        jsTreeAnchor.select_node(node);
    }
    /*
    * The method to calculate domain based on JsTree values
    */
    _getDomain(checkedTreeItems) {
        if (this.id == "folders") {
            return this._getFolderDomain(checkedTreeItems, "clouds_folder_id");
        };
        return []
    }
    /*
    * The method to prepare the domain for M2O '=' domain. It assumes that there might be a single selected record only
    */
    _getFolderDomain(checkedTreeItems, field) {
        const checkedIds = checkedTreeItems.map(function(checkedItem) {return parseInt(checkedItem)});
        this.props.parentModel.cloudsFolderId = checkedIds.length != 0 ? checkedIds[0] : false;
        return [[field, "=", this.props.parentModel.cloudsFolderId || -1]]
    }
    /*
    * The method to highlight not selected parent nodes that have selected children
    * That's triggered when a node is selected or opened. The reason for the latter is that not loaded nodes get
    * class from state while we do not want to always iterate over those
    */
    _highlightParent(jsTreeAnchor, checkedNodes, jsSelector) {
        $(jsSelector + "* .jstr-selected-parent").removeClass("jstr-selected-parent");
        var allParentNodes = [];
        _.each(checkedNodes, function (node) {
            const thisNodeParents = jsTreeAnchor.get_path(node, false, true);
            allParentNodes = allParentNodes.concat(thisNodeParents);
        });
        allParentNodes = [... new Set(allParentNodes)];
        _.each(allParentNodes, function(nodeID) {
            $(jsSelector + " * .jstree-node#" + nodeID).addClass("jstr-selected-parent");
        });
    } 
};

Object.assign(CloudJsTreeContainer, {
    defaultProps: { jstreeKey: "folders" },
    props: {
        jstreeId: { type: String, optional: false },
        kanbanView: { type: Boolean, optional: true },
        parentModel: { type: Object, optional: true },
        resModel: { type: String, optional: true },
        resId: { type: Number, optional: true },
        onUpdateSearch: {type: Function, optional: false},
    },
    template: "cloud_base.CloudJsTreeContainer",
});

registerMessagingComponent(CloudJsTreeContainer);
