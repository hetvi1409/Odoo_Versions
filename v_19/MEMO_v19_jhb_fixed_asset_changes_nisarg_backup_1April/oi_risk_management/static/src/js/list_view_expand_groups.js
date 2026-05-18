odoo.define('oi_risk_management.list_view_expand_groups', function (require) {
    'use strict';

    var viewRegistry = require('web.view_registry');
    var ListView = require('web.ListView');
    var ListRenderer = require('web.ListRenderer');

    var ListRendererExpandGroups = ListRenderer.extend({
        init: function (parent, state, params) {
            var self = this;
            var res = this._super.apply(this, arguments);
            
            // has already been expanded
            this.has_expanded = false;
            return res;
        },

        _renderGroupRow: function (group, groupLevel) {
            var self = this;
            var res = this._super.apply(this, arguments);

            if (self.has_expanded === false) {
                if (group.isOpen === false) {
                    self.trigger_up('toggle_group', { group: group });
                }
            }
            return res;
        },


        _onRowClicked: function (event) {
            this.has_expanded = true;
            return this._super(event)
        },
    });

    var ListViewExpandGroups = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Renderer: ListRendererExpandGroups,
        }),
    });

    viewRegistry.add('list_view_expand_groups', ListViewExpandGroups);
});