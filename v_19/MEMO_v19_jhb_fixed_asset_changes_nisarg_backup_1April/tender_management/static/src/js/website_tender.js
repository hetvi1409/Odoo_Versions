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
