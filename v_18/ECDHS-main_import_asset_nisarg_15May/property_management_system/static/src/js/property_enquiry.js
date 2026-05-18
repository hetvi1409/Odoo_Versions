/** @odoo-module **/
import publicWidget from "@web/legacy/js/public/public_widget";


publicWidget.registry.PropertyEnquiry = publicWidget.Widget.extend({
    selector: '.property_enquiry',
    events: {
        'change select[name="property_type"]': '_onPropertyTypeChange',
    },
    _onPropertyTypeChange: function (ev) {
        console.log(ev.target.value, 'asdffdsasdf')
       if (ev.target.value=== 'mooring'){
            document.getElementById('area_fields').classList.add('d-none');
            document.getElementById('mooring_fields').classList.remove('d-none');
       }
       else if (ev.target.value != 'mooring'){
            document.getElementById('area_fields').classList.remove('d-none');
            document.getElementById('mooring_fields').classList.add('d-none');
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

});
