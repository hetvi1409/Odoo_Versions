/** @odoo-module */
import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.HouseDetails = publicWidget.Widget.extend({
    selector: '#housing_land',
    events: {
        'change select[name="is_land"]': '_onChangeLand',
    },
    _onChangeLand: function (ev) {
        console.log("aaaaaaaaaaaAA")
       if (ev.target.value=== 'yes'){
            document.getElementById('is_land_details').classList.remove('d-none');
       }
       else if (ev.target.value=== 'no'){
            document.getElementById('is_land_details').classList.add('d-none');
       }
    },
});
