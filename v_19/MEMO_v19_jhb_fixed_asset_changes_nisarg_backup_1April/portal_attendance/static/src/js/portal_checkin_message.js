odoo.define('portal_attendance.portal_checkin_message', function (require) {
    "use strict";
    var PublicWidget = require('web.public.widget');
    var currentTime = new Date().getHours();

    var Slider = PublicWidget.Widget.extend({
        selector: '.flex-grow-1',
        start: function () {
            var self = this;
            self.leaving_message();
            self.welcome_message();
        },
        leaving_message: function () {
            var leavingNoteElement = this.$el.find("#leaving_message");
            if (leavingNoteElement.length) {
                if (currentTime < 12) {
                    leavingNoteElement.text("Have a good day!");
                } else if (currentTime < 18) {
                    leavingNoteElement.text("Have a great lunch!");
                } else if (currentTime < 24) {
                    leavingNoteElement.text("Have a good tea time!");
                } else {
                    leavingNoteElement.text("Have a great sleep!");
                }
            }
        },
        welcome_message: function () {
            var welcomeNoteElement = this.$el.find(".welcome_note");
            if (welcomeNoteElement.length) {
                if (currentTime < 12) {
                    welcomeNoteElement.text("Good Morning!");
                } else if (currentTime < 18) {
                    welcomeNoteElement.text("Good Afternoon!");
                } else if (currentTime < 24) {
                    welcomeNoteElement.text("Good Evening!");
                } else {
                    welcomeNoteElement.text("Good Night!");
                }
            }
        },
    });
    PublicWidget.registry.banner = Slider;
    return Slider;
});