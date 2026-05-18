/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { CloudJsTreeContainer } from "@cloud_base/components/cloud_jstree_container/cloud_jstree_container";
import { Domain } from "@web/core/domain";
import { NodeJsTreeContainer } from "@cloud_base/components/node_jstree_container/node_jstree_container";

import { Component } from "@odoo/owl";
const componentModel = "ir.attachment";
const searchSections = { "folders": _t("Folder"), "tags": _t("Tags") }


export class CloudNavigation extends Component {
    /*
    * Re-write to import required services and update props on the component start
    */
    setup() {
        this.jsTreeDomain = [];
        this.jsTreeDomains = {};
    }
    /*
    * The method to prepare jstreecontainer props
    */
    getJsTreeProps(key) {
        return {
            jstreeId: key,
            onUpdateSearch: this.onUpdateSearch.bind(this),
            kanbanView: true,
            parentModel: this.props.kanbanModel,
        }
    }
    /*
    * The method to prepare jstreecontainer props
    */
    getNodeJsTreeProps(key) {
        return {
            jstreeTitle: searchSections[key],
            jstreeId: key,
            kanbanModel: this.props.kanbanList.model,
            onUpdateSearch: this.onUpdateSearch.bind(this),
        }
    }
    /*
    * The method to prepare the domain by all JScontainers and notify searchmodel
    */
    onUpdateSearch(jstreeId, domain) {
        var jsTreeDomain = this._prepareJsTreeDomain(jstreeId, domain)
        if (this.jsTreeDomain != jsTreeDomain) {
            this.jsTreeDomain = jsTreeDomain;
            this.env.searchModel.toggleJSTreeDomain(this.jsTreeDomain);
        };
    }
    /*
    * The method to prepare domain based on all jstree components
    */
    _prepareJsTreeDomain(jstreeId, domain) {
        var jsTreeDomain = [];
        this.jsTreeDomains[jstreeId] = domain;
        const js_tree = this.jsTreeDomains;
        console.log(this, 'js tree domain...');

        Object.values(js_tree).forEach(function (val_domain) {
            jsTreeDomain = Domain.and([jsTreeDomain, val_domain]);
        });
        return jsTreeDomain
    }
};

CloudNavigation.template = "cloud_base.CloudNavigation";
CloudNavigation.components = { CloudJsTreeContainer, NodeJsTreeContainer }
