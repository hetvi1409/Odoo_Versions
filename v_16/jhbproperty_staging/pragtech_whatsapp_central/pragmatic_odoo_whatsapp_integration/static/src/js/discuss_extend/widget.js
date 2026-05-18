/** @odoo-module **/

import AbstractAction from 'web.AbstractAction';
import { getMessagingComponent } from "@mail/utils/messaging_component";
import { DiscussCoverse } from '@pragmatic_odoo_whatsapp_integration/js/discuss_extend/discuss_component';
import { useModels } from '@mail/component_hooks/use_models';
import '@pragmatic_odoo_whatsapp_integration/js/discuss_extend/discuss_component';
import '@mail/components/discuss/discuss';
import { ComponentWrapper } from 'web.OwlCompatibility';
import { registry } from '@web/core/registry';
import dialogs from 'web.view_dialogs';
import ajax from 'web.ajax';
import core from 'web.core';
// import QWeb from 'core.qweb';

const { Component } = owl;
// const QWeb = core.qweb;


export const DiscussWidget = AbstractAction.extend({
    template: 'mail.widgets.Conversation2',
    /**
     * @override {web.AbstractAction}
     * @param {web.ActionManager} parent
     * @param {Object} action
     * @param {Object} [action.context]
     * @param {string} [action.context.active_id]
     * @param {Object} [action.params]
     * @param {string} [action.params.default_active_id]
     * @param {Object} [options={}]
     */
    events: {
        'click #create_products': 'create_products',
        'click #create_contacts': 'create_contacts',
        'click #create_purchases': 'create_purchases',
        'click #create_sale': 'create_sales',
        'click #create_invoice': 'create_invoices',
        'click #product-search-button': 'search_product',
        'click #contact-search-button': 'search_contact',
        'click #purchase-search-button': 'search_purchase',
        'click #sale-search-button': 'search_sale',
        'click #invoicing-search-button': 'search_invoice',
        'click #product_searchclear': 'clear_product_search',
        'click #contact_searchclear': 'clear_contact_search',
        'click #purchase_searchclear': 'clear_purchase_search',
        'click #sale_searchclear': 'clear_sale_search',
        'click #invoicing_searchclear': 'clear_invoicing_search',
        'click #next_button': 'next_page',
        'click #previous_button': 'previous_page',
        'click #purchase_next_button': 'next_page_purchase',
        'click #purchase_previous_button': 'previous_page_purchase',
        'click #contact_next_button': 'next_page_contact',
        'click #contact_previous_button': 'previous_page_contact',
        'click #sale_next_button': 'next_page_sale',
        'click #sale_previous_button': 'previous_page_sale',
        'click #send_report': 'send_sale_report',
        'click #send_invoice_report': 'send_invoice_report',
        'click #send_purchase_report': 'send_purchase_report',
        'click #send_answers': 'send_default_answer',
        'click .product_record': 'edit_product',
        'click .purchase_record': 'edit_purchase',
        'click .contact_record': 'edit_contact',
        'click .sale_record': 'edit_sale',
        'click .invoice_record': 'edit_invoice',
        'click .delete-item-chart': 'delete_chart_item',
        'click .edit-item-chart': 'edit_item_chart',
    },

    init: function (parent, action, options) {
        this._super(...arguments);
        options = options || {};

        // control panel attributes
        // var self= this;
        // if (action.context.active_id){
        //     self.dashboard_board_id = action.context.active_id;
        // }
        // else{
        //     self.dashboard_board_id = action.params.dashboard_board_id;
        // }
        this.action = action;
        this.actionManager = parent;
        this.discuss = undefined;
        this.options = options;
        this.products = undefined;
        this.messaging = undefined;

        this.component = undefined;

        this._lastPushStateActiveThread = null;
        this.env = Component.env;
        Component.env.services.messaging.modelManager.messagingCreatedPromise.then(async () => {
            this.messaging = Component.env.services.messaging.modelManager.messaging;
            const initActiveId = 
                (this.action.context && this.action.context.active_id) ||
                (this.action.params && this.action.params.default_active_id) ||
                'mail.box_inbox';
            this.messaging.discuss.open();
            this.discuss = this.messaging.discuss;
            console.log("messaging discuss", this.messaging.discuss)
            this.discuss.update({
                discussView: {
                    actionId: this.action.id,
                },
                initActiveId, 
                // isOpen: true 
            });
            // Wait for messaging to be initialized to make sure the system
            // knows of the "init thread" if it exists.
            await this.messaging.initializedPromise;
            if (!this.discuss.isInitThreadHandled) {
                this.discuss.update({ isInitThreadHandled: true });
                if (!this.discuss.activeThread) {
                    this.discuss.openInitThread();
                }
            }
        });
    },

    /**
     * Starts the legacy widget (not in the DOM yet)
     *
     * @override
     */
    willStart() {
        var self = this;
        var products = this._rpc({
            model: 'product.template',
            method: 'search_read',
            domain: [['detailed_type', '=', 'consu']],
        })
        .then(function (res) {
            self.products = res;
        });
        var products_count = this._rpc({
            model: 'product.template',
            method: 'search_count',
            args: [[[1, '=', 1]]],
        })
        .then(function (res) {
            self.products_count = res;
            self.first_index = 1;
        });

        var purchases = this._rpc({
            model: 'purchase.order',
            method: 'search_read',
            domain: [],
        })
        .then(function (res) {
            self.purchases = res;
        });

        var purchases_count = this._rpc({
            model: 'purchase.order',
            method: 'search_count',
            args: [[[1, '=', 1]]],
        })
        .then(function (res) {
            self.purchases_count = res;
            self.purchase_first_index = 1;
        });

        var invoices = this._rpc({
                model: 'account.move',
                method: 'search_read',
                domain: [],
                fields: ['name', 'invoice_date', 'invoice_date_due', 'partner_id', 'currency_symbol', 'amount_total', 'state', 'id'],
            })
            .then(function (res) {
                self.invoices = res;
            });

        var sales = this._rpc({
                model: 'sale.order',
                method: 'search_read',
                domain: [],
            })
            .then(function (res) {
                self.sales = res;
            });
        
        var sales_count = this._rpc({
                model: 'sale.order',
                method: 'search_count',
                args: [[[1, '=', 1]]],
            })
            .then(function (res) {
                self.sales_count = res;
                self.sales_first_index = 1;
            });

        var contacts = this._rpc({
                model: 'res.partner',
                method: 'search_read',
                domain: [],
            })
            .then(function (contact) {
                self.contacts = contact;
            });

        var contacts_count = this._rpc({
                model: 'res.partner',
                method: 'search_count',
                args: [[[1, '=', 1]]],
            })
            .then(function (contact) {
                self.contacts_count = contact;
                self.contacts_first_index = 1;
            });
        
        return Promise.all([
            this._super.apply(this, arguments),contacts,products,purchases,sales,sales_count,contacts_count,products_count,purchases_count,invoices//,def
        ]);
    },

    next_page: function(){
        var self = this;
        self.$("#previous_button").prop('disabled', false);
        // self.$("#next_button").prop('disabled', true);
        self.$("#o_product_pager_limit").text(self.products_count);
        self.first_index = self.first_index + 20;
        var last_index = self.first_index + 19;
        if (self.products_count >= last_index){
            last_index = last_index;
        }
        else {
            last_index = self.products_count;
            self.$("#next_button").prop('disabled', true);
        }
        self.$("#o_product_pager_value").text(`${self.first_index}-${last_index}`);
        this._rpc({
            model: 'product.template',
            method: 'search_read',
            domain: [],//[['detailed_type', '=', 'consu']],
        })
        .then(function (res) {
            self.$("#productstack").remove();
            self.$(".product-container").append("<div class='o_kanban_renderer o_renderer o_kanban_ungrouped' id='productstack' style='display: contents;'></div>")
            self.products = res.slice(self.first_index-1, last_index);
            self._render_products();
        });
    },

    previous_page: function(){
        var self = this;
        self.$("#next_button").prop('disabled', false);
        self.$("#o_product_pager_limit").text(self.products_count);
        self.first_index = self.first_index - 20;
        var last_index = self.first_index + 19;
        if (self.first_index <= 1) {
            self.$("#previous_button").prop('disabled', true);
        }
        self.$("#o_product_pager_value").text(`${self.first_index}-${last_index}`);
        this._rpc({
            model: 'product.template',
            method: 'search_read',
            domain: [],//[['detailed_type', '=', 'consu']],
        })
        .then(function (res) {
            // console.log(res);
            self.$("#productstack").remove();
            self.$(".product-container").append("<div class='o_kanban_renderer o_renderer o_kanban_ungrouped' id='productstack' style='display: contents;'></div>")
            self.products = res.slice(self.first_index-1, last_index);
            self._render_products();
        });
    },

    next_page_purchase: function(){
        var self = this;
        self.$("#purchase_previous_button").prop('disabled', false);
        // self.$("#next_button").prop('disabled', true);
        self.$("#o_purchase_pager_limit").text(self.purchases_count);
        self.purchase_first_index = self.purchase_first_index + 20;
        var last_index = self.purchase_first_index + 19;
        if (self.purchases_count >= last_index){
            last_index = last_index;
        }
        else {
            last_index = self.purchases_count;
            self.$("#purchase_next_button").prop('disabled', true);
        }
        self.$("#o_purchase_pager_value").text(`${self.purchase_first_index}-${last_index}`);
        this._rpc({
            model: 'purchase.order',
            method: 'search_read',
            domain: [],//[['detailed_type', '=', 'consu']],
        })
        .then(function (res) {
            self.$("#purchasebody").remove();
            self.$(".purchase-container").append("<tbody class='ui-sortable' id='purchasebody'></tbody>")
            self.purchases = res.slice(self.purchase_first_index-1, last_index);
            self._render_purchases();
        });
    },

    previous_page_purchase: function(){
        var self = this;
        self.$("#purchase_next_button").prop('disabled', false);
        self.$("#o_purchase_pager_limit").text(self.purchases_count);
        self.purchase_first_index = self.purchase_first_index - 20;
        var last_index = self.purchase_first_index + 19;
        if (self.purchase_first_index <= 1) {
            self.$("#purchase_previous_button").prop('disabled', true);
        }
        self.$("#o_purchase_pager_value").text(`${self.purchase_first_index}-${last_index}`);
        this._rpc({
            model: 'purchase.order',
            method: 'search_read',
            domain: [],//[['detailed_type', '=', 'consu']],
        })
        .then(function (res) {
            // console.log(res);
            self.$("#purchasebody").remove();
            self.$(".purchase-container").append("<tbody class='ui-sortable' id='purchasebody'></tbody>")
            self.purchases = res.slice(self.purchase_first_index-1, last_index);
            self._render_purchases();
        });
    },

    next_page_contact: function(){
        var self = this;
        self.$("#contact_previous_button").prop('disabled', false);
        // self.$("#next_button").prop('disabled', true);
        self.$("#o_contact_pager_limit").text(self.contacts_count);
        self.contacts_first_index = self.contacts_first_index + 20;
        var last_index = self.contacts_first_index + 19;
        if (self.contacts_count >= last_index){
            last_index = last_index;
        }
        else {
            last_index = self.contacts_count;
            self.$("#contact_next_button").prop('disabled', true);
        }
        self.$("#o_contact_pager_value").text(`${self.contacts_first_index}-${last_index}`);
        this._rpc({
            model: 'res.partner',
            method: 'search_read',
            domain: [],//[['detailed_type', '=', 'consu']],
        })
        .then(function (res) {
            self.$("#contactstack").remove();
            self.$(".contact-container").append("<div class='o_kanban_renderer o_renderer o_kanban_ungrouped o_res_partner_kanban' id='contactstack' style='display: contents;'></div>")
            self.contacts = res.slice(self.contacts_first_index-1, last_index);
            self._render_contacts();
        });
    },

    previous_page_contact: function(){
        var self = this;
        self.$("#contact_next_button").prop('disabled', false);
        self.$("#o_contact_pager_limit").text(self.contacts_count);
        self.contacts_first_index = self.contacts_first_index - 20;
        var last_index = self.contacts_first_index + 19;
        if (self.contacts_first_index <= 1) {
            self.$("#contact_previous_button").prop('disabled', true);
        }
        self.$("#o_contact_pager_value").text(`${self.contacts_first_index}-${last_index}`);
        this._rpc({
            model: 'res.partner',
            method: 'search_read',
            domain: [],//[['detailed_type', '=', 'consu']],
        })
        .then(function (res) {
            // console.log(res);
            self.$("#contactstack").remove();
            self.$(".contact-container").append("<div class='o_kanban_renderer o_renderer o_kanban_ungrouped o_res_partner_kanban' id='contactstack' style='display: contents;'></div>")
            self.contacts = res.slice(self.contacts_first_index-1, last_index);
            self._render_contacts();
        });
    },

    next_page_sale: function(){
        var self = this;
        self.$("#sale_previous_button").prop('disabled', false);
        // self.$("#next_button").prop('disabled', true);
        self.$("#o_sale_pager_limit").text(self.sales_count);
        self.sales_first_index = self.sales_first_index + 20;
        var last_index = self.sales_first_index + 19;
        if (self.sales_count >= last_index){
            last_index = last_index;
        }
        else {
            last_index = self.sales_count;
            self.$("#sale_next_button").prop('disabled', true);
        }
        self.$("#o_sale_pager_value").text(`${self.sales_first_index}-${last_index}`);
        this._rpc({
            model: 'sale.order',
            method: 'search_read',
            domain: [],//[['detailed_type', '=', 'consu']],
        })
        .then(function (res) {
            self.$("#salesbody").remove();
            self.$(".sale-container").append("<tbody class='ui-sortable' id='salesbody'></tbody>")
            self.sales = res.slice(self.sales_first_index-1, last_index);
            self._render_sales();
        });
    },

    previous_page_sale: function(){
        var self = this;
        self.$("#sale_next_button").prop('disabled', false);
        self.$("#o_sale_pager_limit").text(self.sales_count);
        self.sales_first_index = self.sales_first_index - 20;
        var last_index = self.sales_first_index + 19;
        if (self.sales_first_index <= 1) {
            self.$("#sale_previous_button").prop('disabled', true);
        }
        self.$("#o_sale_pager_value").text(`${self.sales_first_index}-${last_index}`);
        this._rpc({
            model: 'sale.order',
            method: 'search_read',
            domain: [],//[['detailed_type', '=', 'consu']],
        })
        .then(function (res) {
            // console.log(res);
            self.$("#salesbody").remove();
            self.$(".sale-container").append("<tbody class='ui-sortable' id='salesbody'></tbody>")
            self.sales = res.slice(self.sales_first_index-1, last_index);
            self._render_sales();
        });
    },

    clear_product_search: function(){
        var self = this;
        self.$("#search-input-product").val('');
        ajax.jsonRpc("/whatsapp_dashboard/remove_search_chart", 'call', {'model': 'product.template'})
        .then(function(res){
           self.$("#productstack").remove();
            self.$(".product-container").append("<div class='o_kanban_renderer o_renderer o_kanban_ungrouped' id='productstack' style='display: contents;'></div>")
            self.products = res;
            self._render_products();
        });
    },

    clear_contact_search: function(){
        var self = this;
        self.$("#search-input-contact").val('');
        ajax.jsonRpc("/whatsapp_dashboard/remove_search_chart", 'call', {'model': 'res.partner'})
        .then(function(res){
           self.$("#contactstack").remove();
            self.$(".contact-container").append("<div class='o_kanban_renderer o_renderer o_kanban_ungrouped o_res_partner_kanban' id='contactstack' style='display: contents;'></div>")
            self.contacts = res;
            self._render_contacts();
        });
    },

    clear_purchase_search: function(){
        var self = this;
        self.$("#search-input-purchase").val('');
        ajax.jsonRpc("/whatsapp_dashboard/remove_search_chart", 'call', {'model': 'purchase.order'})
        .then(function(res){
           self.$("#purchasebody").remove();
            self.$(".purchase-container").append("<tbody class='ui-sortable' id='purchasebody'></tbody>")
            self.purchases = res;
            self._render_purchases();
        });
    },

    clear_sale_search: function(){
        var self = this;
        self.$("#search-input-sale").val('');
        ajax.jsonRpc("/whatsapp_dashboard/remove_search_chart", 'call', {'model': 'sale.order'})
        .then(function(res){
            self.$("#salesbody").remove();
            self.$(".sale-container").append("<tbody class='ui-sortable' id='salesbody'></tbody>")
            self.sales = res;
            self._render_sales();
        });
    },

    clear_invoicing_search: function(){
        var self = this;
        self.$("#search-input-invoicing").val('');
        ajax.jsonRpc("/whatsapp_dashboard/remove_search_chart", 'call', {'model': 'account.move'})
        .then(function(res){
            self.$("#invoicebody").remove();
            self.$(".invoicing-container").append("<tbody class='ui-sortable' id='invoicebody'></tbody>")
            self.invoices = res;
            self._render_invoices();
        });
    },

    search_product: function(){
        var self = this;
        var search_input = self.$("#search-input-product").val();
        ajax.jsonRpc("/whatsapp_dashboard/search_input_chart", 'call', {'search_input': search_input, 'model_name': 'product.template'})
        .then(function(res){
            self.$("#productstack").remove();
            self.$(".product-container").append("<div class='o_kanban_renderer o_renderer o_kanban_ungrouped' id='productstack' style='display: contents;'></div>")
            self.products = res;
            self._render_products();
        });
    },

    search_contact: function(){
        var self = this;
        var search_input = self.$("#search-input-contact").val();
        ajax.jsonRpc("/whatsapp_dashboard/search_input_chart", 'call', {'search_input': search_input, 'model_name': 'res.partner'})
        .then(function(res){
            self.$("#contactstack").remove();
            self.$(".contact-container").append("<div class='o_kanban_renderer o_renderer o_kanban_ungrouped o_res_partner_kanban' id='contactstack' style='display: contents;'></div>")
            self.contacts = res;
            self._render_contacts();
        });
    },

    search_purchase: function(){
        var self = this;
        var search_input = self.$("#search-input-purchase").val();
        ajax.jsonRpc("/whatsapp_dashboard/search_input_chart", 'call', {'search_input': search_input, 'model_name': 'purchase.order'})
        .then(function(res){
            self.$("#purchasebody").remove();
            self.$(".purchase-container").append("<tbody class='ui-sortable' id='purchasebody'></tbody>")
            self.purchases = res;
            self._render_purchases();
        });
    },

    search_sale: function(){
        var self = this;
        var search_input = self.$("#search-input-sale").val();
        ajax.jsonRpc("/whatsapp_dashboard/search_input_chart", 'call', {'search_input': search_input, 'model_name': 'sale.order'})
        .then(function(res){
            self.$("#salesbody").remove();
            self.$(".sale-container").append("<tbody class='ui-sortable' id='salesbody'></tbody>")
            self.sales = res;
            self._render_sales();
        });
    },

    search_invoice: function(){
        var self = this;
        var search_input = self.$("#search-input-invoicing").val();
        ajax.jsonRpc("/whatsapp_dashboard/search_input_chart", 'call', {'search_input': search_input, 'model_name': 'account.move'})
        .then(function(res){
            self.$("#invoicebody").remove();
            self.$(".invoicing-container").append("<tbody class='ui-sortable' id='invoicebody'></tbody>")
            self.invoices = res;
            self._render_invoices();
        });
    },


    create_products: function(){
        this.env.bus.trigger('do-action', {
            action: {
                name: 'Create a new product',
                type: 'ir.actions.act_window',
                res_model: 'product.template',
//                    res_id: this.thread.id,
                views: [[false, 'form']],
                target: 'new'
            },
        });
    },

    create_contacts: function(){
        this.env.bus.trigger('do-action', {
            action: {
                name: 'Create a new contact',
                type: 'ir.actions.act_window',
                res_model: 'res.partner',
//                    res_id: this.thread.id,
                views: [[false, 'form']],
                target: 'new'
            },
        });
    },

    create_purchases: function(){
        this.env.bus.trigger('do-action', {
            action: {
                name: 'Create a new purchase',
                type: 'ir.actions.act_window',
                res_model: 'purchase.order',
//                    res_id: this.thread.id,
                views: [[false, 'form']],
                target: 'new'
            },
        });
    },

    create_sales: function(){
        this.env.bus.trigger('do-action', {
            action: {
                name: 'Create a new sale',
                type: 'ir.actions.act_window',
                res_model: 'sale.order',
//                    res_id: this.thread.id,
                views: [[false, 'form']],
                target: 'new'
            },
        });
    },

    create_invoices: function(){
        this.env.bus.trigger('do-action', {
            action: {
                name: 'Create a new invoice',
                type: 'ir.actions.act_window',
                res_model: 'account.move',
//                    res_id: this.thread.id,
                views: [[false, 'form']],
                target: 'new'
            },
        });
    },

    edit_product: function(event){
        // console.log(event);
        var self = this;
        var product_id = event.currentTarget.id.split('g')[1];

        var options= {
            title: 'Edit product',
            res_model: 'product.template',
            res_id: Number(product_id),
            context: event.context || self.context,
            on_saved: function () {
                this.close;
            },
        }
        new dialogs.FormViewDialog(this, options).open();
    },

    edit_purchase: function(event){
        var self = this;
        var purchase_id = event.currentTarget.id.split('r_')[1];
        console.log(purchase_id);
//         this.env.bus.trigger('do-action', {
//             action: {
//                 name: 'Edit purchase',
//                 type: 'ir.actions.act_window',
//                 res_model: 'purchase.order',
//                 res_id: Number(purchase_id),
// //                    res_id: this.thread.id,
//                 views: [[false, 'form']],
//                 target: 'new'
//             },
//         });
        var options= {
            title: 'Edit Purchase',
            res_model: 'purchase.order',
            res_id: Number(purchase_id),
            context: event.context || self.context,
            on_saved: function () {
                this.close;
            },
        }
        new dialogs.FormViewDialog(this, options).open();
    },

    edit_contact: function(event){
        var self = this;
        var contact_id = event.currentTarget.id.split('r_')[1];
        console.log(contact_id);

        var options= {
            title: 'Edit contact',
            res_model: 'res.partner',
            res_id: Number(contact_id),
            context: event.context || self.context,
            on_saved: function () {
                this.close;
            },
        }
        new dialogs.FormViewDialog(this, options).open();
    },

    edit_sale: function(event){
        var self = this;
        var sale_id = event.currentTarget.id.split('r_')[1];
        console.log(sale_id);
        this.env.bus.trigger('do-action', {
            action: {
                name: 'Edit Sale',
                type: 'ir.actions.act_window',
                res_model: 'sale.order',
                res_id: Number(sale_id),
//                    res_id: this.thread.id,
                views: [[false, 'form']],
                target: 'new',
            },
        });
        var options= {
            title: 'Edit Sale',
            res_model: 'sale.order',
            res_id: Number(sale_id),
            context: event.context || self.context,
            on_saved: function () {
                this.close;
            },
        }
        // new dialogs.FormViewDialog(this, options).open();
    },

    edit_invoice: function(event){
        var self = this;
        var invoice_id = event.currentTarget.id.split('e_')[1];
        console.log(invoice_id);

        this.env.bus.trigger('do-action', {
            action: {
                name: 'Edit Invoice',
                type: 'ir.actions.act_window',
                res_model: 'account.move',
                res_id: Number(invoice_id),
//                    res_id: this.thread.id,
                views: [[false, 'form']],
                target: 'new',
            },
        });

        var options= {
            title: 'Edit Invoice',
            res_model: 'account.move',
            res_id: Number(invoice_id),
            context: event.context || self.context,
            on_saved: function () {
                this.close;
            },
        }
        // new dialogs.FormViewDialog(this, options).open();
    },

    /**
     * Starts the legacy widget (not in the DOM yet)
     *
     * @override
     */

    start: function () {
        var self = this;
        var options = {};
        self._render_chart();
        self._render_answers();
        self._render_products();
        self._render_purchases();
        self._render_invoices();
        self._render_sales();
        self._render_contacts();
        return this._super();
    },
    /**
     * @override {web.AbstractAction}
     */
    destroy() {
        if (this.component) {
            this.component.destroy();
            this.component = undefined;
        }
        if (this.$buttons) {
            this.$buttons.off().remove();
        }
        this._super(...arguments);
    },
    /**
     * @override {web.AbstractAction}
     */
    on_attach_callback() {
        this._super(...arguments);
        if (this.component) {
            // prevent twice call to on_attach_callback (FIXME)
            return;
        }
        const DiscussComponent = getMessagingComponent("DiscussCoverse");
        const messaging = this.env.services.messaging.modelManager.messaging
        
        messaging.discuss.open();
        this.component = new ComponentWrapper(this, DiscussComponent, { record: messaging.discuss.discussView });
        this._pushStateActionManagerEventListener = ev => {
            ev.stopPropagation();
            if (this._lastPushStateActiveThread === this.discuss.thread) {
                return;
            }
            this._pushStateActionManager();
            this._lastPushStateActiveThread = this.discuss.thread;
        };
        this._showRainbowManEventListener = ev => {
            ev.stopPropagation();
            this._showRainbowMan();
        };
        this.el.addEventListener(
            'o-push-state-action-manager',
            this._pushStateActionManagerEventListener
        );
        this.el.addEventListener(
            'o-show-rainbow-man',
            this._showRainbowManEventListener
        );
        return this.component.mount(this.el);
    },
    /**
     * @override {web.AbstractAction}
     */
    on_detach_callback() {
        this._super(...arguments);
        if (this.component) {
            this.component.destroy();
        }
        this.component = undefined;
        this.el.removeEventListener(
            'o-push-state-action-manager',
            this._pushStateActionManagerEventListener
        );
        this.el.removeEventListener(
            'o-show-rainbow-man',
            this._showRainbowManEventListener
        );
    },

    _render_purchases: function(){
        var self = this;
        // this.getProducts();
        // console.log(this.products);
        // console.log(self.purchases);
        self.purchases.forEach(function (purchase) {
            self.generate_purchase_view(purchase);
        });
    },

    _render_invoices: function(){
        var self = this;
        console.log("invoice==== ", self.invoices);
        self.invoices.forEach(function (invoice) {
            console.log("invoices==== ", invoice);
            self.generate_invoice_view(invoice);
        });
    },

    _render_sales: function(){
        var self = this;
        self.sales.forEach(function (sale) {
            self.generate_sale_view(sale);
        });
    },

    _render_answers: function(){
        var self = this;
        var options = {};
        ajax.jsonRpc("/whatsapp_dashboard/get_default_answers", 'call')
        .then(function (res) {
            self.answer_data = res
            console.log(res)
            for (var rec in res) {
                self.generate_answers(rec);
            }                
        });
    },

    _render_chart: function(){
        var self = this;
        var options = {};
        ajax.jsonRpc("/whatsapp/get_message_dashboard", 'call')
        .then(function (res) {
            self.dashboard_data = res
            // self.dashboard_data.forEach(function (rec) {
            //     self.generate_graph(rec, rec.id);
            // })
            for (let i = 0; i < res.length; i++) {
                var rec = res[i]
                self.generate_graph(rec, rec.id);
            }                
        });
    },

    _render_products: function(){
        var self = this;
        // console.log(self.products);
        self.products.forEach(function (product) {
            self.generate_product_view(product);
        });
    },

    _render_contacts: function(){
        var self = this;
        // console.log("contacts ",self.contacts);
        self.contacts.forEach(function (contact) {
            self.generate_contact_view(contact);
        });
    },
    generate_sale_view: function(dict_data){
        var self = this;
        var sales_stack = self.$('#salesbody');
        sales_stack.append(`<tr class="o_data_row sale_record" id="sale_order_${dict_data.id}" draggable="true" ondragstart="dragStartSale(event)">`)
        var check_box = self.$('#salesbody').find(`[id='sale_order_${dict_data.id}']`)
        check_box.append(`<td class="o_list_record_selector">
            <div class="custom-control custom-checkbox">
                <input type="checkbox" id="checkbox-sale-${dict_data.id}" class="custom-control-input"/>
                <label for="checkbox-sale-${dict_data.id}" class="custom-control-label">​</label>
            </div>
        </td>`)
        var reference_field = self.$('#salesbody').find(`[id='sale_order_${dict_data.id}']`)
        reference_field.append(`<td class="o_data_cell o_field_cell o_list_char o_readonly_modifier o_required_modifier font-weight-bold" tabindex="-1" title="${dict_data.name}" name="name">
        ${dict_data.name}
        </td>`)
        var creation_date_field = self.$('#salesbody').find(`[id='sale_order_${dict_data.id}']`)
        creation_date_field.append(`<td class="o_data_cell o_field_cell o_date_cell o_readonly_modifier" tabindex="-1">
            <span class="o_field_date o_field_widget o_quick_editable o_readonly_modifier" name="create_date">${dict_data.create_date}</span>
        </td>`)
        var customer_field = self.$('#salesbody').find(`[id='sale_order_${dict_data.id}']`)
        customer_field.append(`<td class="o_data_cell o_field_cell o_list_many2one o_readonly_modifier o_required_modifier" tabindex="-1" title="${dict_data.partner_id[1]}" name="partner_id">
        ${dict_data.partner_id[1]}
        </td>`)
        var salesperson_field = self.$('#salesbody').find(`[id='sale_order_${dict_data.id}']`)
        salesperson_field.append(`<td class="o_data_cell o_field_cell o_list_many2one o_many2one_avatar_user_cell" tabindex="-1">
            <div class="o_clickable_m2x_avatar o_field_many2one_avatar o_field_widget o_quick_editable" name="user_id">
                <div class="o_m2o_avatar">
                    <img src="/web/image/res.users/${dict_data.user_id[0]}/avatar_128" alt="${dict_data.user_id[1]}"/>
                    <span>${dict_data.user_id[1]}</span>
                </div>
            </div>
        </td>`)
        var total_field = self.$('#salesbody').find(`[id='sale_order_${dict_data.id}']`)
        total_field.append(`<td class="o_data_cell o_field_cell o_list_number o_monetary_cell o_readonly_modifier" tabindex="-1">
            <span class="o_field_monetary o_field_number o_field_widget o_quick_editable text-bf o_readonly_modifier" name="amount_total">
            ${dict_data.amount_total}${dict_data.currency_symbol}
            </span>
        </td>`)
        var status_field = self.$('#salesbody').find(`[id='sale_order_${dict_data.id}']`)
        status_field.append(`<td class="o_data_cell o_field_cell o_badge_cell o_readonly_modifier" tabindex="-1">
            <span class="badge badge-pill o_field_badge o_field_widget o_readonly_modifier bg-success-light" name="state">${dict_data.state}</span>
        </td>`)
        var report_field = self.$('#salesbody').find(`[id='sale_order_${dict_data.id}']`)
        report_field.append(`<td class="o_data_cell o_field_cell o_badge_cell o_readonly_modifier" tabindex="-1">
            <div aria-label="Preview" tabindex="0" data-mimetype="application/pdf" class="o_AttachmentCard_image o-attachment-viewable" 
            draggable="true" ondragstart="dragStartPDF(event)" style="background-image: url(/web/static/img/mimetypes/pdf.svg); max-height: 19px; max-width: 14px; margin: 0px;">
                <a href="/report/pdf/sale.report_saleorder/${dict_data.id}"></a>
            </div>
            <button class="btn btn-primary my-2 mr-4 mt-2 fa fa-paper-plane-o" type="button" id="send_report" name="${dict_data.name}" index="${dict_data.id}"></button>
        </td>`)
    },

    send_sale_report: function(event){
        event.stopPropagation();
        var self = this;
        console.log(event);
        //find a way to get the id of the sale order
        //find a way to get the name of the sale order
        // find a way to get the active dashboard channel id
        var name = event.target.name+".pdf";
        var id = Number(event.target.attributes.index.value);
        console.log(name)
        console.log(id)
        console.log(this.discuss)
        console.log(this.discuss.thread.id)
        var active_channel_id = this.discuss.thread.id;
        console.log(this.component)
        if(active_channel_id !== 'inbox'){
            self._rpc({
                model: 'mail.channel',
                method: 'upload_pdf',
                args: ["", name, "sale.report_saleorder", id, active_channel_id]
            })
        }
        // });
    },

    generate_purchase_view: function(dict_data){
        var self = this;
        // console.log(dict_data);
        var purchase_stack = self.$('#purchasebody');
        purchase_stack.append(`<tr class="o_data_row purchase_record text-info" id="purchase_order_${dict_data.id}" draggable="true" ondragstart="dragStartpurchase(event)">`);
        var check_box = self.$('#purchasebody').find(`[id='purchase_order_${dict_data.id}']`)
        check_box.append(`<td class="o_list_record_selector">
            <div class="custom-control custom-checkbox">
                <input type="checkbox" id="checkbox-${dict_data.id}" class="custom-control-input"/>
                <label for="checkbox-${dict_data.id}" class="custom-control-label">​</label>
            </div>
        </td>`)
        var reference_field = self.$('#purchasebody').find(`[id='purchase_order_${dict_data.id}']`);
        reference_field.append(`<td class="o_data_cell o_field_cell o_list_char o_readonly_modifier o_required_modifier font-weight-bold" tabindex="-1" title="${dict_data.name}" name="name">
        ${dict_data.name}
        </td>`)
        var creation_date_field = self.$('#purchasebody').find(`[id='purchase_order_${dict_data.id}']`);
        creation_date_field.append(`<td class="o_data_cell o_field_cell o_date_cell o_readonly_modifier" tabindex="-1">
            <span class="o_field_date o_field_widget o_quick_editable o_readonly_modifier" name="date_order">${dict_data.date_order}</span>
        </td>`)
        var vendor_field = self.$('#purchasebody').find(`[id='purchase_order_${dict_data.id}']`);
        vendor_field.append(`<td class="o_data_cell o_field_cell o_list_many2one o_readonly_modifier o_required_modifier" tabindex="-1" title="${dict_data.partner_id[1]}" name="partner_id">
        ${dict_data.partner_id[1]}
        </td>`)
        var representative_field = self.$('#purchasebody').find(`[id='purchase_order_${dict_data.id}']`);
        representative_field.append(`<td class="o_data_cell o_field_cell o_list_many2one o_many2one_avatar_user_cell" tabindex="-1">
            <div class="o_clickable_m2x_avatar o_field_many2one_avatar o_field_widget o_quick_editable" name="user_id">
                <div class="o_m2o_avatar">
                    <img src="/web/image/res.users/${dict_data.user_id[0]}/avatar_128" alt="${dict_data.user_id[1]}"/>
                    <span>${dict_data.user_id[1]}</span>
                </div>
            </div>
        </td>`)
        var total_field = self.$('#purchasebody').find(`[id='purchase_order_${dict_data.id}']`);
        total_field.append(`<td class="o_data_cell o_field_cell o_list_number o_monetary_cell o_readonly_modifier" tabindex="-1">
            <span class="o_field_monetary o_field_number o_field_widget o_quick_editable text-bf o_readonly_modifier" name="amount_total">
            ${dict_data.amount_total}${dict_data.currency_symbol}
            </span>
        </td>`)
        var status_field = self.$('#purchasebody').find(`[id='purchase_order_${dict_data.id}']`);
        status_field.append(`<td class="o_data_cell o_field_cell o_badge_cell o_readonly_modifier" tabindex="-1">
            <span class="badge badge-pill o_field_badge o_field_widget o_readonly_modifier bg-success-light" name="state">${dict_data.state}</span>
        </td>`)
        var report_link = self.$('#purchasebody').find(`[id='purchase_order_${dict_data.id}']`);
        report_link.append(`<td class="o_data_cell o_field_cell o_badge_cell o_readonly_modifier" tabindex="-1">
            <div aria-label="Preview" tabindex="0" data-mimetype="application/pdf" class="o_AttachmentCard_image o-attachment-viewable" 
            draggable="true" ondragstart="dragStartPDF(event)" style="background-image: url(/web/static/img/mimetypes/pdf.svg); max-height: 19px; max-width: 14px; margin: 0px;">
                <a href="/report/pdf/purchase.report_purchaseorder/${dict_data.id}"></a>
            </div>
            <button class="btn btn-primary my-2 mr-4 mt-2 fa fa-paper-plane-o" type="button" id="send_purchase_report" name="${dict_data.name}" index="${dict_data.id}"></button>
        </td>`)
    },

    send_purchase_report: function(event){
        event.stopPropagation();
        var self = this;
        console.log(event);
        // find a way to get the active dashboard channel id
        var name = event.target.name+".pdf";
        var id = Number(event.target.attributes.index.value);
        console.log(name)
        console.log(id)
        console.log(this.discuss)
        console.log(this.discuss.thread.id)
        var active_channel_id = this.discuss.thread.id;
        console.log(this.component)
        if(active_channel_id !== 'inbox'){
            self._rpc({
                model: 'mail.channel',
                method: 'upload_pdf',
                args: ["", name, "purchase.report_purchaseorder", id, active_channel_id]
            })
        }
        // });
    },

    generate_invoice_view: function(dict_data){
        var self = this;
        // console.log(dict_data);
        var purchase_stack = self.$('#invoicebody');
        purchase_stack.append(`<tr class="o_data_row invoice_record text-info" style="cursor: pointer;" id="account_move_${dict_data.id}" draggable="true" ondragstart="dragStartpurchase(event)">`);
        var check_box = self.$('#invoicebody').find(`[id='account_move_${dict_data.id}']`)
        check_box.append(`<td class="o_list_record_selector">
            <div class="custom-control custom-checkbox">
                <input type="checkbox" id="checkbox-${dict_data.id}" class="custom-control-input"/>
                <label for="checkbox-${dict_data.id}" class="custom-control-label">​</label>
            </div>
        </td>`)
        var reference_field = self.$('#invoicebody').find(`[id='account_move_${dict_data.id}']`);
        reference_field.append(`<td class="o_data_cell o_field_cell o_list_char o_readonly_modifier o_required_modifier font-weight-bold" tabindex="-1" title="${dict_data.name}" name="name">
        ${dict_data.name}
        </td>`)
        var creation_date_field = self.$('#invoicebody').find(`[id='account_move_${dict_data.id}']`);
        creation_date_field.append(`<td class="o_data_cell o_field_cell o_date_cell o_readonly_modifier" tabindex="-1">
            <span class="o_field_date o_field_widget o_quick_editable o_readonly_modifier" name="invoice_date">${dict_data.invoice_date}</span>
        </td>`)
        var vendor_field = self.$('#invoicebody').find(`[id='account_move_${dict_data.id}']`);
        vendor_field.append(`<td class="o_data_cell o_field_cell o_list_many2one o_readonly_modifier o_required_modifier" tabindex="-1" title="${dict_data.partner_id[1]}" name="partner_id">
        ${dict_data.partner_id[1]}
        </td>`)
        var representative_field = self.$('#invoicebody').find(`[id='account_move_${dict_data.id}']`);
        representative_field.append(`<td class="o_data_cell o_field_cell o_date_cell o_readonly_modifier" tabindex="-1">
            <span class="o_field_date o_field_widget o_quick_editable o_readonly_modifier" name="invoice_date_due">${dict_data.invoice_date_due}</span>
        </td>`)
        var total_field = self.$('#invoicebody').find(`[id='account_move_${dict_data.id}']`);
        total_field.append(`<td class="o_data_cell o_field_cell o_list_number o_monetary_cell o_readonly_modifier" tabindex="-1">
            <span class="o_field_monetary o_field_number o_field_widget o_quick_editable text-bf o_readonly_modifier" name="amount_total">
            ${dict_data.amount_total}${dict_data.currency_symbol}
            </span>
        </td>`)
        var status_field = self.$('#invoicebody').find(`[id='account_move_${dict_data.id}']`);
        status_field.append(`<td class="o_data_cell o_field_cell o_badge_cell o_readonly_modifier" tabindex="-1">
            <span class="badge badge-pill o_field_badge o_field_widget o_readonly_modifier bg-success-light" name="state">${dict_data.state}</span>
        </td>`)
        var report_link = self.$('#invoicebody').find(`[id='account_move_${dict_data.id}']`);
        report_link.append(`<td class="o_data_cell o_field_cell o_badge_cell o_readonly_modifier" tabindex="-1">
            <div aria-label="Preview" tabindex="0" data-mimetype="application/pdf" class="o_AttachmentCard_image o-attachment-viewable" 
            draggable="true" ondragstart="dragStartPDF(event)" style="background-image: url(/web/static/img/mimetypes/pdf.svg); max-height: 19px; max-width: 14px; margin: 0px;">
                <a href="/report/pdf/account.report_invoice/${dict_data.id}"></a>
            </div>
            <button class="btn btn-primary my-2 mr-4 mt-2 fa fa-paper-plane-o" type="button" id="send_invoice_report" name="${dict_data.name}" index="${dict_data.id}"></button>
        </td>`)
    },

    send_invoice_report: function(event){
        event.stopPropagation();
        var self = this;
        console.log(event);
        // find a way to get the active dashboard channel id
        var name = event.target.name+".pdf";
        var id = Number(event.target.attributes.index.value);
        console.log(name)
        console.log(id)
        console.log(this.discuss)
        console.log(this.discuss.thread.id)
        var active_channel_id = this.discuss.thread.id;
        console.log(this.component)
        if(active_channel_id !== 'inbox'){
            self._rpc({
                model: 'mail.channel',
                method: 'upload_pdf',
                args: ["", name, "account.report_invoice", id, active_channel_id]
            })
        }
        // });
    },

    generate_answers: function(data){
        var self = this;
        // console.log(data);
        // console.log(self.answer_data[data]);
        var answer_stack = self.$('#answerstack');
        answer_stack.append(`<div class="answer_record" style="width: 50%">
            <button class="btn btn-primary my-2 mr-4 mt-2" type="button" id="send_answers" name="${data}">Send</button>
            <b>${data}</b>
        </div>`)
    },

    send_default_answer: function(event){
        event.stopPropagation();
        var self = this;
        console.log(event);
        var name = event.target.name;
        var active_channel_id = this.discuss.thread.id;
        var answer = self.answer_data[name]
        if(active_channel_id !== 'inbox'){
            self._rpc({
                model: 'mail.channel',
                method: 'send_default_amswer',
                args: ["", active_channel_id, answer]
            })
        }
    },

    generate_contact_view: function(dict_data){
        var self = this;
        var contacts_stack = self.$('#contactstack');
        // console.log(contacts_stack);
        // console.log(dict_data);
        contacts_stack.append(`<div id="article_${dict_data.id}" role="article" class="o_kanban_record flex-grow-1 flex-md-shrink-1 flex-shrink-0" tabindex="0" style="max-width: 265px; min-width: 260px; min-height: 138px; max-height: 140px; margin-left: auto; display: inline-block;"></div>`)
        var contacts_record = self.$('#contactstack').find(`[id='article_${dict_data.id}']`)
        contacts_record.append(`<div id="res_partner_${dict_data.id}" class="oe_kanban_global_click o_kanban_record_has_image_fill o_res_partner_kanban contact_record" style="max-width: 265px; min-width: 260px; min-height: 138px; max-height: 140px;"></div>`)
        if (!dict_data.is_company) {
            var main_image = self.$('#contactstack').find(`[id='res_partner_${dict_data.id}']`)
            main_image.append(`<div class="o_kanban_image_fill_left d-none d-md-block" style="background-image:url('/web/image/res.partner/${dict_data.id}/avatar_128')" draggable="true" ondragstart="dragStartImg(event)">
                <img class="o_kanban_image_inner_pic" alt="${dict_data.parent_id}" src="/web/image/res.partner/${dict_data.id}/avatar_128" draggable="true" ondragstart="dragStartImg(event)"/>
            </div>`)
            var small_image = self.$('#contactstack').find(`[id='res_partner_${dict_data.id}']`)
            small_image.append(`<div class="o_kanban_image d-md-none">
                <img class="o_kanban_image_inner_pic" t-if="record.parent_id" alt="${dict_data.parent_id}" src="/web/image/res.partner/${dict_data.id}/avatar_128" draggable="true" ondragstart="dragStartImg(event)"/>
            </div>`)
        }
        else {
            var main_image = self.$('#contactstack').find(`[id='res_partner_${dict_data.id}']`)
            main_image.append(`<img class="o_kanban_image_fill_left o_kanban_image_full" style="max-height: 130px; min-height: 125px; max-width: 100px;" src="/web/image/res.partner/${dict_data.id}/avatar_128" role="img" draggable="true" ondragstart="dragStartImg(event)"/>`)
        }
        var details_div = self.$('#contactstack').find(`[id='res_partner_${dict_data.id}']`)
        details_div.append(`<div class="oe_kanban_details d-flex flex-column" draggable="true" ondragstart="dragStart(event)"></div>`)
        var display_name = self.$('#contactstack').find(`[id='res_partner_${dict_data.id}']`).find('.oe_kanban_details')
        display_name.append(`<strong class="o_kanban_record_title oe_partner_heading">
        ${dict_data.display_name}
        </strong>`)

        var display_tags = self.$('#contactstack').find(`[id='res_partner_${dict_data.id}']`).find('.oe_kanban_details');
        display_tags.append(`<div class="o_kanban_tags_section oe_kanban_partner_categories"/>`);
        var other_details = self.$('#contactstack').find(`[id='res_partner_${dict_data.id}']`).find('.oe_kanban_details');
        other_details.append(`<ul></ul>`);
        var other_details_ul = self.$('#contactstack').find(`[id='res_partner_${dict_data.id}']`).find('.oe_kanban_details').find('ul');
        // console.log(other_details_ul);
        if (dict_data.parent_id!=false){
            other_details_ul.append(`<li>${dict_data.parent_name}</li>`)
        }
        if (!dict_data.parent_id && dict_data.function){
            other_details_ul.append(`<li>${dict_data.function}</li>`)
        }
        if (dict_data.parent_id && dict_data.function){
            other_details_ul.append(`<li>${dict_data.function} at ${dict_data.parent_name}</li>`)
        }
        if (dict_data.city || dict_data.country_id){
            if (dict_data.city) {
                other_details_ul.append(`<li>${dict_data.city}, ${dict_data.country_id[1]}</li>`)
            }
            else {
                other_details_ul.append(`<li>${dict_data.country_id[1]}</li>`)
            }
        }
        if (dict_data.email) {
            other_details_ul.append(`<li class="o_text_overflow">${dict_data.email}</li>`)
        }
    },

    generate_product_view: function(dict_data){
        var self = this;
        // console.log(dict_data);
        var product_stack = self.$('#productstack');
        product_stack.append(`<div id="article_${dict_data.id}" role="article" class="o_kanban_record flex-grow-1 flex-md-shrink-1 flex-shrink-0" tabindex="0" style="max-width: 260px; min-width: 255px; min-height: 100px; max-height: 130px; margin-left: auto; display: inline-block;"></div>`)
        var products_record = self.$('#productstack').find(`[id='article_${dict_data.id}']`)
        // product_stack.append($(QWeb.render('basic.listsView', {record: dict_data})));
        products_record.append(`<div class='oe_kanban_global_click product_record' id='kanbandrag${dict_data.id}' style="max-width: 260px;min-width: 255px;min-height: 95px;max-height: 125px;"/></div>`);
        var new_card = self.$("#productstack").find(`[id='kanbandrag${dict_data.id}']`);
        new_card.append(`<div class='o_kanban_image mr-1'/></div>`);
        new_card.append(`<div class="oe_kanban_details" draggable="true" ondragstart="dragStart(event)"></div>`);
        var product_image = self.$("#productstack").find(`[id='kanbandrag${dict_data.id}']`).find('.o_kanban_image')
        product_image.append(`<img src='/web/image/product.template/${dict_data.id}/image_128' alt="Product" class="o_image_64_contain" draggable="true" ondragstart="dragStartImg(event)"/>`)
        var product_details = self.$("#productstack").find(`[id='kanbandrag${dict_data.id}']`).find('.oe_kanban_details')
        product_details.append(`<div class="o_kanban_record_top mb-0"></div>`);
        var product_name_div = self.$("#productstack").find(`[id='kanbandrag${dict_data.id}']`).find('.oe_kanban_details').find('.o_kanban_record_top')
        product_name_div.append(`<div class="o_kanban_record_headings"><strong class="o_kanban_record_title">${dict_data.name}</strong></div>`);
        if (dict_data.default_code){
            product_details.append(`[${dict_data.default_code}]`)
        }
        if (dict_data.product_variant_count > 1){
            product_details.append(`<strong>${dict_data.product_variant_count} Variants</strong>`);
        }
        product_details.append(`<div name="product_lst_price" class="product_lst_price mt-1"></div>`)
        var product_price_div = self.$("#productstack").find(`[id='kanbandrag${dict_data.id}']`).find('.oe_kanban_details').find('.product_lst_price')
        if (dict_data.currency_id){
            product_price_div.append(`${dict_data.list_price} ${dict_data.currency_symbol}`)
        }
        else {
            product_price_div.append(`${dict_data.list_price}`)
        }
    },

    generate_graph: function(dict_data, dashboard_item_id){
        var self = this;
        var dataset = JSON.parse(dict_data.chart_data);
        // console.log(dict_data.chart_dashboard_positions);
        var grid_path = null;
        var new_grid = null;
        var options_grid = {
            alwaysShowResizeHandle: /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent),
            staticGrid: true,
            float: false,
            margin: '100px',
        };
        self.$('.grid-stack').gridstack(options_grid);
        var grid_stack = self.$('.grid-stack');
        // var widget_stack = self.$('.o_widget_Discuss').prevObject;
        // var widget_stack2 = widget_stack[0];
        // var widget_stack3 = widget_stack2.childNodes;
        // console.log(grid_stack);
        self.grid = self.$('.grid-stack').data('gridstack');
        // self.grid.enableMove(false, true);
        // self.grid.enableResize(false, true);
        grid_stack.append(`<div class='chart-container box' id='chart_item_${dashboard_item_id}' /></div>`)
        var serizize_data = null;
        if (dict_data.chart_dashboard_positions){
            var dict_obj = JSON.parse((dict_data.chart_dashboard_positions))
            serizize_data = [{id: `chart_item_${dashboard_item_id}`, x: dict_obj.chart_x, y: dict_obj.chart_y, w: dict_obj.chart_width, h:dict_obj.chart_height}]
        }
        else{
            serizize_data = [{id: `chart_item_${dashboard_item_id}`, x: 0, y: 200, w: 12, h:5}]
        }
        var items = GridStackUI.Utils.sort(serizize_data);
        // console.log(items);
        items.forEach(node=>{
            var containerElt = $("#" + node.id);
            containerElt.attr("data-gs-id", node.id);
            containerElt.attr("data-gs-width", node.w);
            containerElt.attr("data-gs-height", node.h);
            containerElt.attr("data-gs-x", node.x);
            containerElt.attr("data-gs-y", node.y);
            grid_path = self.grid.makeWidget(containerElt)
        });

        var options = {
            series: dataset.data_list,
            chart: {
                type: dict_data.chart_type == 'column'? 'bar': dict_data.chart_type,
                height : '100%',
                background: dict_data.chart_theme == 'custom' ? dict_data.chart_background_color : false,
                foreColor: dict_data.chart_theme == 'custom' ? dict_data.chart_fore_color : false,
                redrawOnParentResize: true,
                redrawOnWindowResize: true,
                toolbar: {
                    show: false
                },
            },
            title: {
                text: dict_data.name,
            },
            theme: {
                mode: dict_data.chart_theme == 'custom' ? false : dict_data.chart_theme,
                palette: dict_data.color_palette,
            },
        };
        if (dict_data.chart_type == 'bar' || dict_data.chart_type == 'column'){
            options['xaxis'] = {
                categories: dataset.model_label_list,
            }
            options['plotOptions'] =  {
                bar: {
                    horizontal: dict_data.chart_type == 'column'? false : true,
                    columnWidth: '75%',
                    distributed: dict_data.is_distributed_chart,
                }
            }
        }
        else if (dict_data.chart_type == 'pie'){
            options['labels'] = dataset.model_label_list
            options['responsive'] = [{
                breakpoint: 480,
                options: {
                    chart: {
                        width: 200,
                        height: 350
                    },
                }
            }]
        }
        else if (dict_data.chart_type == 'donut'){
            options['labels'] = dataset.model_label_list
            options['responsive'] = [{
                breakpoint: 480,
                options: {
                    chart: {
                        type: 'donut',
                        width: 200,
                        height: 350,
                    },
                }
            }]
        }
        else if (dict_data.chart_type == 'line'){
            options['xaxis'] = {
                categories: dataset.model_label_list,
            }
            options['chart'] = {
                type: 'line',
                height: 350,
            }
        }
        else if (dict_data.chart_type == 'area'){
            options['xaxis'] = {
                categories: dataset.model_label_list,
            }
            options['chart'] = {
                type: 'area',
                height: 350,
            }
        }
        else if (dict_data.chart_type == 'treemap'){
            // options['xaxis'] = {
            //     categories: dataset.model_label_list,
            // }
            options['series'] = [{
                data: dataset.data_list
            }]
            options['chart'] = {
                type: 'treemap',
                height: 350,
            }
        }
        else if (dict_data.chart_type == 'radar'){
            options['xaxis'] = {
                categories: dataset.model_label_list,
            }
            options['chart'] = {
                type: 'radar',
                height: 350,
            }
        }
        var new_chart = self.$(".grid-stack").find(`[id='chart_item_${dashboard_item_id}']`)
        new_chart.append('<div class="grid-stack-item-content"></div>')
        var new_grid_item = self.$(".grid-stack").find(`[id='chart_item_${dashboard_item_id}']`).find('.grid-stack-item-content')
        // console.log(new_grid_item[0]);
        var chart = new ApexCharts(new_grid_item[0], options);
        chart.render();
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    _pushStateActionManager() {
        this.actionManager.do_push_state({
            action: this.action.id,
            active_id: this.discuss.activeId,
        });
    },
    /**
     * @private
     */
    _showRainbowMan() {
        this.trigger_up('show_effect', {
            message: this.env._t("Congratulations, your inbox is empty!"),
            type: 'rainbow_man',
        });
    },
});
core.action_registry.add('mail.widgets.conversation', DiscussWidget);
return DiscussWidget;
// registry.category('actions').add('mail.widgets.conversation', DiscussWidget);