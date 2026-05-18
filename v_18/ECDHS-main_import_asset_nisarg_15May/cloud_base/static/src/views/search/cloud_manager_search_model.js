/** @odoo-module **/

import { SearchModel } from "@web/search/search_model";
import { Domain } from "@web/core/domain";

export class CloudManagerSearchModel extends SearchModel {
    /*
    * Overwrite to introduce jsTreeDomain
    */
    setup(services) {
        this.jsTreeDomain = [];
        super.setup(...arguments);
    }
    /*
    * Overwrite to add our jsTree
    * Regretfully, none of child method can be triggered, so we have to redefine the whole return
    */
    _getDomain(params = {}) {
        let domain =  super._getDomain(...arguments);
        console.log(domain,'domain....')
        try {
            const jsTreeDomain = new Domain(this.jsTreeDomain || []);
            domain = Domain.and([domain, jsTreeDomain]);
            console.log("Merged domain:", domain);

            // Fixing the undefined context issue
            const userContext = this.userService ? this.userService.context : {};
            const globalContext = this.globalContext || {};
            const finalContext = Object.assign({}, globalContext, userContext);

            return params.raw ? domain : domain.toList(finalContext);
        } catch (error) {
            throw new Error(
                `${("Failed to evaluate the domain")} ${domain.toString()}.\n${
                    error.message
                }`
            );
        };
    }
    /*
    * The method to save received jsTree domain
    */
    toggleJSTreeDomain(domain) {
        this.jsTreeDomain = domain;
        this._notify();
    }
}
