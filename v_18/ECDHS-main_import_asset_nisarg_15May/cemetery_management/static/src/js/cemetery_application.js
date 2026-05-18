/** @odoo-module **/
import publicWidget from "@web/legacy/js/public/public_widget";
import { jsonrpc } from "@web/core/network/rpc_service";
publicWidget.registry.CemeteryApplication = publicWidget.Widget.extend({
    selector: '.cemetery_application',
    events: {
        'click .foreigner': '_oNClickForeigner',
        'click .click-next': '_onClickNext',
        'change select[name="interment_type"]': '_onIntermentTypeChange',
        'click .trash_one': '_onClickTrashOne',
        'click .trash_two': '_onClickTrashTwo',
        'click .trash_three': '_onClickTrashThree',
        'click .trash_four': '_onClickTrashFour',
    },
    _onIntermentTypeChange: function (ev) {
       if (ev.target.value=== 'burial'){
            document.getElementById('cemetery_details').classList.remove('d-none');
            document.getElementById('burial_details').classList.remove('d-none');
       }
       else if (ev.target.value=== 'memorial'){
            document.getElementById('cemetery_details').classList.add('d-none');
            document.getElementById('burial_details').classList.add('d-none');
       }
       else if (ev.target.value=== 'cremation'){
            document.getElementById('cemetery_details').classList.add('d-none');
            document.getElementById('burial_details').classList.add('d-none');
       }
    },
    start: function(){
        var page = this.$el.find('#page-name').val();
        if (page == 'second'){
            this.$el.find('#interment-type-section').addClass("active")
        }
        if (page == 'third'){
            this.$el.find('#interment-type-section').addClass("active")
            this.$el.find('#burial').addClass("active")
        }
        if (page == 'fourth'){
            this.$el.find('#interment-type-section').addClass("active")
            this.$el.find('#burial').addClass("active")
            this.$el.find('#plot').addClass("active")
        }
        if (page == 'fifth'){
            this.$el.find('#interment-type-section').addClass("active")
            this.$el.find('#documents').addClass("active")
            this.$el.find('#burial').addClass("active")
            this.$el.find('#plot').addClass("active")
        }
    },
    _oNClickForeigner: function (ev) {
        console.log("_oNClickForeigner", ev.target.value)

        if (ev.target.value=== 'yes'){
            document.getElementById('passport_number').classList.remove('d-none');
            document.getElementById('id_number_').classList.add('d-none');
       }
       else if (ev.target.value=== 'no'){
            document.getElementById('passport_number').classList.add('d-none');
            document.getElementById('id_number_').classList.remove('d-none');
       }
    },
    _onClickNext(page, button) {
        console.log("_onClickNext")
    },
    _onClickTrashOne: function (ev) {
        const fileInput = document.getElementById("burial_order");
        fileInput.value = "";
    },
    _onClickTrashTwo: function (ev) {
        const fileInput = document.getElementById("deceased_id");
        fileInput.value = "";
    },
    _onClickTrashThree: function (ev) {
        const fileInput = document.getElementById("next_of_kin_id");
        fileInput.value = "";
    },
    _onClickTrashFour: function (ev) {
        const fileInput = document.getElementById("death_certificate");
        fileInput.value = "";
    },
});
