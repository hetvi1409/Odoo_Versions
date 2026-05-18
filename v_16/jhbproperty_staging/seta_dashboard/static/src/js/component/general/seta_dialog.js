odoo.define('seta_dashboard.setaDialog', function (require) {
    "use strict";

    var Widget = require('web.Widget');
    
    var setaDialog = Widget.extend({
        template: 'setaDialog',
        events: {
            'click .seta_dialog_bg': '_onClickBackground',
        },

        /**
         * @override
         */
        init: function (parent, $content) {
            this._super.apply(this, arguments);
            
            this.parent = parent;
            this.$content = $content;
        },

        willStart: function () {
            var self = this;

            return this._super.apply(this, arguments).then(function () {
                return self.load();
            });
        },

        load: function () {
            var self = this;
        },

        start: function() {
            var self = this;
            this._super.apply(this, arguments);

            // Add Content
            if (self.$content)
                self.$el.find('.seta_dialog_content').append(self.$content)
        },

        /**
         * Private Method
         */
         _onClickBackground: function(ev) {
            var self = this;
            self.destroy();
        },
    });

    return setaDialog;
});