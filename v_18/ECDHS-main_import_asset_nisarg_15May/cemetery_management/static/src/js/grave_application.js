/** @odoo-module **/
import publicWidget from "@web/legacy/js/public/public_widget";
import { jsonrpc } from "@web/core/network/rpc_service";
publicWidget.registry.GraveApplication = publicWidget.Widget.extend({
    selector: '.grave_application',
    events: {
        'change .interment_type': 'onSelectionIntermentType',
        'change .attended_by': 'OnChangeAttendedBy',
        'change #lease_purchase': 'OnChangeLeasePurchase',
        'click #same-as': '_onClickIsSame',
    },
    start: function(){
        this.onSelectionIntermentType();
        this.OnChangeAttendedBy();
        this.OnChangeLeasePurchase();
        var page = this.$el.find('#page-name').val();
        if (page == 'second'){
            this.$el.find('#applicant').addClass("active")
            this.$el.find('#authorisation').removeClass("active")
            this.$el.find('#parties').removeClass("active")
        }if (page == 'third'){
            this.$el.find('#applicant').addClass("active")
            this.$el.find('#authorisation').addClass("active")
            this.$el.find('#parties').removeClass("active")
        }if (page == 'fourth'){
            this.$el.find('#applicant').addClass("active")
            this.$el.find('#authorisation').addClass("active")
            this.$el.find('#parties').addClass("active")
        }
    },
    onSelectionIntermentType: function (ev) {
        var interment_type = this.$el.find('#interment_type').val();
        if (interment_type == 'memorial'){
            this.$el.find('#grave-number').removeClass("d-none")
            this.$el.find('#no-attendees').addClass("d-none")
            this.$el.find('#attended-by').addClass("d-none")
        }if (interment_type == 'burial'){
            this.$el.find('#grave-number').addClass("d-none")
            this.$el.find('#attended-by').addClass("d-none")
        }if (interment_type == 'cremation'){
            this.$el.find('#attended-by').removeClass("d-none")
            this.$el.find('#grave-number').addClass("d-none")
        }

    },
    OnChangeAttendedBy: function(ev){
        var interment_type = this.$el.find('#interment_type').val();
        var attended_by = this.$el.find('#attended_by').val();
        if (interment_type == 'cremation'){
            if (attended_by == 'family'){}
                this.$el.find('#no-attendees').removeClass("d-none")
            }
            if (attended_by != 'family'){
                this.$el.find('#no-attendees').addClass("d-none")
        }
    },
    OnChangeLeasePurchase: function(ev){
        var lease_purchase = this.el.querySelector('#lease_purchase')
        if(lease_purchase){
                const isChecked = lease_purchase.checked;

        if (isChecked){
            this.el.querySelector('#lease_and_purchase').innerHTML='Lease'
            this.el.querySelector('#lease_purchase_type').value='lease'
        }
        else{
            this.el.querySelector('#lease_and_purchase').innerHTML='Purchases'
            this.el.querySelector('#lease_purchase_type').value='purchase'
        }
        }
    },
    _onClickIsSame: function(ev){
        console.log('_onClickIsSame')
    }
});