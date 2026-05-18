odoo.define('client_act.sale_cust', function (require) {
   'use strict';
   var AbstractAction = require('web.AbstractAction');
   var core = require('web.core');
   var rpc = require('web.rpc');
   var QWeb = core.qweb;
   var SaleCustom = AbstractAction.extend({
   template: 'SaleCust',
       events: {
       },
       init: function(parent, action) {
           this._super(parent, action);
       },
       start: function() {
           var self = this;
           alert("Hello")
           self.load_data();
       },
       load_data: function () {
           var self = this;
                   var self = this;
                   self._rpc({
                       model: 'sale.custom',
                       method: 'get_sale_order',
                       args: [],
                   }).then(function(datas) {
                   console.log("dataaaaaa", datas)
                       self.$('.table_view').html(QWeb.render('SaleTable', {
                                  report_lines : datas,
                       }));
                   });
           },
   });
   core.action_registry.add("sale_cust", SaleCustom);
   return SaleCustom;
});