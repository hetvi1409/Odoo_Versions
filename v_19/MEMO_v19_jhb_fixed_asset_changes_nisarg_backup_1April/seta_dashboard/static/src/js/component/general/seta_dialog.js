/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
const Widget = publicWidget.Widget;

var SETADialog = Widget.extend({
    template: 'SETADialog',
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

    start: function () {
        var self = this;
        this._super.apply(this, arguments);

        // Add class seta_view
        if (!(self.$el.hasClass('seta_view'))) {
            self.$el.addClass('seta_view');
        }

        // Add Content
        if (self.$content)
            self.$el.find('.seta_dialog_content').append(self.$content)
    },

    /**
     * Private Method
     */
    _onClickBackground: function (ev) {
        var self = this;
        self.destroy();
    },
});

export default SETADialog;