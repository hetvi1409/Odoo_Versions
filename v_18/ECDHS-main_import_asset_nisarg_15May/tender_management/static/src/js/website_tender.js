/** @odoo-module **/
import publicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from "@web/core/network/rpc";

export const Timer = publicWidget.Widget.extend({
    selector: '.tender_timer_id',

    start: function () {
        this._super.apply(this, arguments);


        let tender = $('input[name="tender_id"]').val();
        var self = this;
        rpc('/tender/timer', {
            'tender': tender
            }).then((timer_data) => {
            if(timer_data){
                   var timerIdCount = setInterval(function() {
                        console.log("after then set---", timer_data)
                        var time_key = timer_data['end_time'] ? 'end_time' : false;
                        console.log("time_key", time_key)
                        var time_remaining = new Date(timer_data[time_key]) - new Date()
                        var days = Math.floor(time_remaining / (1000 * 60 * 60 * 24));
                        var hours = Math.floor((time_remaining / (1000 * 60 * 60)) % 24);
                        var minutes = Math.floor((time_remaining / (1000 * 60)) % 60);
                        var seconds = Math.floor((time_remaining / 1000) % 60);
                        if (self.el.querySelector('#tender_timer_count')) {
                            self.el.querySelector('#tender_timer_count').innerHTML = days + "d." + " " + hours + "h." + " " + minutes + "m." + " " + seconds + "s."
                        }
                        if (time_remaining <= 0) {
                            clearInterval(timerIdCount);
                        }
                    }, 1000);
                    var time_key = timer_data['end_time'] ? 'end_time' : false;
                    var time_remaining = new Date(timer_data[time_key]) - new Date()
//                    if (time_remaining <= 0) {
//                        window.location.href = '/shop';
//                    }
                    }
            })


}

});

publicWidget.registry.Timer = Timer;

// Vendor Registration Form Handler
export const VendorRegistration = publicWidget.Widget.extend({
    selector: '#vendor_registration_form',
    events: {
        'change #vendor_type': '_onVendorTypeChange',
        'change #country_id': '_onCountryChange',
    },

    start: function () {
        this._super.apply(this, arguments);
        // Trigger initial state based on vendor type
        this._onVendorTypeChange();
    },

    _onVendorTypeChange: function () {
        const vendorType = this.$('#vendor_type').val();
        const companyFields = this.$('#company_fields');

        if (vendorType === 'company') {
            companyFields.show();
        } else {
            companyFields.hide();
        }
    },

    _onCountryChange: function () {
        const countryId = this.$('#country_id').val();
        const stateSelect = this.$('#state_id');

        if (countryId) {
            rpc('/shop/country_infos/' + countryId, {
                mode: 'shipping',
            }).then((data) => {
                // Clear existing options
                stateSelect.empty();
                stateSelect.append('<option value="">Select your state</option>');

                // Add states if available
                if (data.states && data.states.length > 0) {
                    data.states.forEach((state) => {
                        stateSelect.append(`<option value="${state[0]}">${state[1]}</option>`);
                    });
                    stateSelect.parent().show();
                } else {
                    stateSelect.parent().hide();
                }
            });
        } else {
            stateSelect.empty();
            stateSelect.append('<option value="">Select your state</option>');
        }
    },
});

publicWidget.registry.VendorRegistration = VendorRegistration;
