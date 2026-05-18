odoo.define('pragmatic_odoo_whatsapp_integration.mainscript', function (require) {
   'use strict';
   var AbstractAction = require('web.AbstractAction');
   var core = require('web.core');
   var rpc = require('web.rpc');
   var QWeb = core.qweb;
   var ChatDash = AbstractAction.extend({
   template: 'ChatDashboard',
       events: {
       },
       init: function(parent, action) {
           this._super(parent, action);
       },
       start: function() {
           var self = this;
           console.log("Hello")
           self.load_data();
       },
       load_data: function () {
           var self = this;
             var self = this;
             self._rpc({
                 model: 'facebook.messenger',
                 method: 'get_chat_order',
                 args: [],
             }).then(function(datas) {
                 self.$('.scoop').html(QWeb.render('ChatTable', {
                            report_lines : datas,
                 }));
             });
           },
   });
   core.action_registry.add('pragtech.dashboard', ChatDash);
   return ChatDash;
});