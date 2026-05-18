odoo.define('network_drives.copy_path', function (require) {
    "use strict";

    var core = require('web.core');
    var ListController = require('web.ListController');
    var FormController = require('web.FormController');
    var _t = core._t;

    // Add copy button to list view
    ListController.include({
        renderButtons: function () {
            this._super.apply(this, arguments);
            if (this.$buttons && this.modelName === 'network.drive') {
                this.$buttons.on('click', '.o_copy_path_button', this._onCopyPath.bind(this));
            }
        },

        _onCopyPath: function (ev) {
            var self = this;
            var record = this.getSelectedRecords()[0];
            if (record) {
                var path = record.data.path;
                navigator.clipboard.writeText(path).then(function() {
                    self.do_notify(_t('Success'), _t('Path copied to clipboard'));
                }).catch(function() {
                    self.do_warn(_t('Error'), _t('Failed to copy path'));
                });
            }
        }
    });

    // Add copy button to form view
    FormController.include({
        _onCopyPath: function () {
            var self = this;
            var path = this.model.get(this.handle).data.path;
            navigator.clipboard.writeText(path).then(function() {
                self.do_notify(_t('Success'), _t('Path copied to clipboard'));
            }).catch(function() {
                self.do_warn(_t('Error'), _t('Failed to copy path'));
            });
        }
    });
});