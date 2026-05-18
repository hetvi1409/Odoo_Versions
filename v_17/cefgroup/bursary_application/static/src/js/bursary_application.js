/** @odoo-module */
import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.portalDetails = publicWidget.Widget.extend({
    selector: '#bursary_application',
    events: {
        'click #disability': '_onDisabilityChange',
        'click #parent_deceased': '_onParentDeceasedChange',
        'click #received_bursary': '_onReceivedBursaryChange',
    },
    _onDisabilityChange: function (ev) {
        if (ev.target.value === 'yes'){
            document.getElementById('disability_type').classList.remove('d-none');
        }
        else if (ev.target.value != 'no'){
            document.getElementById('disability_type').classList.add('d-none');
        }
    },
    _onParentDeceasedChange: function (ev) {
        if (ev.target.value === 'yes'){
            document.getElementById('death_certificate').classList.remove('d-none');
        }
        else if (ev.target.value != 'no'){
            document.getElementById('death_certificate').classList.add('d-none');
        }
    },
    _onReceivedBursaryChange: function (ev) {
        console.log($('#received_bursary').is(":checked"), 'aaaaa')
        if (ev.target.value === 'yes'){
            document.getElementById('bursary_details').classList.remove('d-none');
        }
        else if (ev.target.value === 'no'){
            document.getElementById('bursary_details').classList.add('d-none');
        }
    },
});