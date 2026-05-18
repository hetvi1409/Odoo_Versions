odoo.define('dashboard.ChatListView', function (require) {
    "use strict";
    
    var LunchListController = require('dashboard.ChatListController');
    var LunchListRenderer = require('dashboard.ChatListRenderer');
    
    var core = require('web.core');
    var ListView = require('web.ListView');
    var view_registry = require('web.view_registry');
    
    var _lt = core._lt;
    
    var LunchListView = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Controller: LunchListController,
            Renderer: LunchListRenderer,
        }),
        display_name: _lt('Lunch List'),
    
        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------
    
        /**
         * @override
         */
        _createSearchModel(params, extraExtensions = {}) {
            Object.assign(extraExtensions, { Lunch: {} });
            return this._super(params, extraExtensions);
        },
    
    });
    
    Object.assign(LunchListView, {
        props: {},
        template: 'listview.Dashboard',
    });

});
    