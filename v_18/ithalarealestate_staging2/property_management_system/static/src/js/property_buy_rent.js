/** @odoo-module **/
import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.PropertyBuyRent = publicWidget.Widget.extend({
    selector: '.property_discover',
    events: {
        'click .buy' : '_onClickBuying',
        'click .rent' : '_onClickRenting',
        'click .sell' : '_onClickSelling',
    },
    _onClickBuying: function (ev) {
        console.log('_onClickBuying')
        this.$el.find('.buy').addClass("active")
        this.$el.find('.rent').removeClass("active")
        this.$el.find('.sell').removeClass("active")
        document.getElementById('buying').classList.add('active')
        document.getElementById('renting').classList.remove('active')
        document.getElementById('selling').classList.remove('active')
    },
    _onClickRenting: function (ev) {
        console.log('_onClickRenting')
        this.$el.find('.buy').removeClass("active")
        this.$el.find('.rent').addClass("active")
        this.$el.find('.sell').removeClass("active")
        document.getElementById('renting').classList.add('active')
        document.getElementById('buying').classList.remove('active')
        document.getElementById('selling').classList.remove('active')
    },
    _onClickSelling: function (ev) {
        console.log('_onClickSelling')
        this.$el.find('.buy').removeClass("active")
        this.$el.find('.rent').removeClass("active")
        this.$el.find('.sell').addClass("active")
        document.getElementById('selling').classList.add('active')
        document.getElementById('renting').classList.remove('active')
        document.getElementById('buying').classList.remove('active')
    },

});
