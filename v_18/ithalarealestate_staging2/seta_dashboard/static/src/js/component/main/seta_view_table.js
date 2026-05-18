/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
const Widget = publicWidget.Widget;

var SETAViewTable = Widget.extend({
    template: 'SETAViewTable',
    events: {
        'click input': '_onClickInput',
        'click button': '_onClickButton',
    },

    /**
     * @override
     */
    init: function (parent) {
        this._super.apply(this, arguments);

        this.parent = parent;
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

    /**
     * Private Method
     */
    _onClickInput: function (ev) {
        var self = this;
    },

    _onClickButton: function (ev) {
        var self = this;
    },

    _getOwl: function () {
        var cur_obj = this;
        while (cur_obj) {
            if (cur_obj.__owl__) {
                return cur_obj;
            }
            cur_obj = cur_obj.parent;
        }
        return undefined;
    },
});

export default SETAViewTable;