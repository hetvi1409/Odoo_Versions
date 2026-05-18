odoo.define('webp_attachments.media', function (require) {
    const {ImageWidget} = require('wysiwyg.widgets.media');
    ImageWidget.include({
        _onURLInputChange: function () {
            console.log('Url changed');
            var inputValue = this.$urlInput.val();
            var emptyValue = (inputValue === '');
            var isURL = /^.+\..+$/.test(inputValue); // TODO improve
            var isImage = _.any(['.gif', '.jpeg', '.jpe', '.jpg', '.png', '.webp'], function (format) {
                return inputValue.endsWith(format);
            });
            this._updateAddUrlUi(emptyValue, isURL, isImage);
        },
    });
});
