/**@odoo-module **/
import { registry } from "@web/core/registry";
import { Component } from  "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

const actionRegistry = registry.category("actions");
class CemeteryDashboard extends Component {
    setup() {
         super.setup()
         this.orm = useService('orm')
         this._fetch_data()
   }
    _fetch_data(){
        var self = this;
        this.orm.call('cemetery.cemetery', 'get_cemetery_details', [], {}).then(function(result){
            $('#cemetery_count').append('<span>' + result.cemetery_count + '</span>');
            $('#cemetery_section_count').append('<span>' + result.cemetery_section_count + '</span>');
            $('#grave_count').append('<span>' + result.grave_count + '</span>');
            $('#application_count').append('<span>' + result.application_count + '</span>');
            $('#submitted_application_count').append('<span>' + result.submitted_application_count + '</span>');
            $('#approved_application_count').append('<span>' + result.approved_application_count + '</span>');
            $('#burial_application_count').append('<span>' + result.burial_application_count + '</span>');
            $('#cremation_application_count').append('<span>' + result.cremation_application_count + '</span>');
            $('#grave_purchase_count').append('<span>' + result.grave_purchase_count + '</span>');
            $('#grave_lease_count').append('<span>' + result.grave_lease_count + '</span>');
            $('#submitted_grave_purchase_count').append('<span>' + result.submitted_grave_purchase_count + '</span>');
            $('#quotation_grave_purchase_count').append('<span>' + result.quotation_grave_purchase_count + '</span>');
            $('#approved_grave_purchase_count').append('<span>' + result.approved_grave_purchase_count + '</span>');
            $('#grave_submitted_lease_count').append('<span>' + result.grave_submitted_lease_count + '</span>');
            $('#grave_quotation_lease_count').append('<span>' + result.grave_quotation_lease_count + '</span>');
            $('#grave_approved_lease_count').append('<span>' + result.grave_approved_lease_count + '</span>');
        });
    };
    OpenCemetery(){
        this.env.services.action.doAction({
            name:'Cemeteries',
            type: 'ir.actions.act_window',
            res_model: 'cemetery.cemetery',
            view_mode: 'tree,form',
            views: [[false, 'list'],[false, 'form']],
        })
    }
    OpenCemeterySection(){
        this.env.services.action.doAction({
            name:'Cemetery Section',
            type: 'ir.actions.act_window',
            res_model: 'cemetery.section',
            view_mode: 'tree,form',
            views: [[false, 'list'],[false, 'form']],
        })
    }
    OpenGrave(){
        this.env.services.action.doAction({
            name:'Grave',
            type: 'ir.actions.act_window',
            res_model: 'grave.grave',
            view_mode: 'tree,form',
            views: [[false, 'list'],[false, 'form']],
        })
    }
    OpenCemeteryApplication(){
        this.env.services.action.doAction({
            name:'Cemetery Application',
            type: 'ir.actions.act_window',
            res_model: 'cemetery.application',
            view_mode: 'tree,form',
            views: [[false, 'list'],[false, 'form']],
        })
    }
    OpenSubmittedCemeteryApplication(){
        this.env.services.action.doAction({
            name:'Cemetery Application',
            type: 'ir.actions.act_window',
            res_model: 'cemetery.application',
            view_mode: 'tree,form',
            domain: [["state", "=", "submitted"]],
            views: [[false, 'list'],[false, 'form']],
        })
    }
    OpenApprovedCemeteryApplication(){
        this.env.services.action.doAction({
            name:'Cemetery Application',
            type: 'ir.actions.act_window',
            res_model: 'cemetery.application',
            view_mode: 'tree,form',
            domain: [["state", "=", "approved"]],
            views: [[false, 'list'],[false, 'form']],
        })
    }
    OpenBurialCemeteryApplication(){
        this.env.services.action.doAction({
            name:'Cemetery Application',
            type: 'ir.actions.act_window',
            res_model: 'cemetery.application',
            view_mode: 'tree,form',
            domain: [["interment_type", "=", "burial"]],
            views: [[false, 'list'],[false, 'form']],
        })
    }
    OpenCremationCemeteryApplication(){
        this.env.services.action.doAction({
            name:'Cemetery Application',
            type: 'ir.actions.act_window',
            res_model: 'cemetery.application',
            view_mode: 'tree,form',
            domain: [["interment_type", "=", "cremation"]],
            views: [[false, 'list'],[false, 'form']],
        })
    }
    GravePurchase(){
        this.env.services.action.doAction({
            name:'Grave Purchase',
            type: 'ir.actions.act_window',
            res_model: 'grave.booking',
            view_mode: 'tree,form',
            domain: [["type", "=", "purchase"]],
            views: [[false, 'list'],[false, 'form']],
        })
    }
    GraveLease(){
        this.env.services.action.doAction({
            name:'Grave Lease',
            type: 'ir.actions.act_window',
            res_model: 'grave.booking',
            view_mode: 'tree,form',
            domain: [["type", "=", "lease"]],
            views: [[false, 'list'],[false, 'form']],
        })
    }
    GraveSubmittedPurchase(){
        this.env.services.action.doAction({
            name:'Grave Lease',
            type: 'ir.actions.act_window',
            res_model: 'grave.booking',
            view_mode: 'tree,form',
            domain: [["type", "=", "purchase"], ['state', '=', 'submitted']],
            views: [[false, 'list'],[false, 'form']],
        })
    }
    GraveQuotationPurchase(){
        this.env.services.action.doAction({
            name:'Grave Lease',
            type: 'ir.actions.act_window',
            res_model: 'grave.booking',
            view_mode: 'tree,form',
            domain: [["type", "=", "purchase"], ['state', '=', 'quotation']],
            views: [[false, 'list'],[false, 'form']],
        })
    }
    GraveApprovedPurchase(){
        this.env.services.action.doAction({
            name:'Grave Lease',
            type: 'ir.actions.act_window',
            res_model: 'grave.booking',
            view_mode: 'tree,form',
            domain: [["type", "=", "purchase"], ['state', '=', 'approved']],
            views: [[false, 'list'],[false, 'form']],
        })
    }
    GraveSubmittedLease(){
        this.env.services.action.doAction({
            name:'Grave Lease',
            type: 'ir.actions.act_window',
            res_model: 'grave.booking',
            view_mode: 'tree,form',
            domain: [["type", "=", "lease"], ['state', '=', 'submitted']],
            views: [[false, 'list'],[false, 'form']],
        })
    }
    GraveQuotationLease(){
        this.env.services.action.doAction({
            name:'Grave Lease',
            type: 'ir.actions.act_window',
            res_model: 'grave.booking',
            view_mode: 'tree,form',
            domain: [["type", "=", "lease"], ['state', '=', 'quotation']],
            views: [[false, 'list'],[false, 'form']],
        })
    }
    GraveApprovedLease(){
        this.env.services.action.doAction({
            name:'Grave Lease',
            type: 'ir.actions.act_window',
            res_model: 'grave.booking',
            view_mode: 'tree,form',
            domain: [["type", "=", "lease"], ['state', '=', 'approved']],
            views: [[false, 'list'],[false, 'form']],
        })
    }
}

CemeteryDashboard.template = "cemetery_management.CemeteryDashboard";
//  Tag name that we entered in the first step.
actionRegistry.add("cemetery_dashboard", CemeteryDashboard);
