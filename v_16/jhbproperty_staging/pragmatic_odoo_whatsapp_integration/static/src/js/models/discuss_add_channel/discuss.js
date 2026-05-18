odoo.define('pragmatic_odoo_whatsapp_integration/static/src/models/discuss.discuss.js', function (require) {
'use strict';

const { registerNewModel } = require('mail/static/src/model/model_core.js');
const { attr, many2many, many2one, one2many, one2one } = require('mail/static/src/model/model_field.js');
const { clear } = require('mail/static/src/model/model_field_command.js');
const throttle = require('mail/static/src/utils/throttle/throttle.js');
const Timer = require('mail/static/src/utils/timer/timer.js');
const { cleanSearchTerm } = require('mail/static/src/utils/utils.js');
const mailUtils = require('mail.utils');
const { registerInstancePatchModel } = require('mail/static/src/model/model_core.js');

registerInstancePatchModel('mail.discuss', 'pragmatic_odoo_whatsapp_integration/static/src/models/discuss.discuss.js', {
//extends for mail.discuss

    async performRpcCreateChannel2({ name, privacy }) {
        const device = this.env.messaging.device;
        console.log(name)
        const data = await this.env.services.rpc({
            model: 'mail.channel',
            method: 'facebook_channel_create',
            args: ['this', name, privacy],
            kwargs: {
                context: Object.assign({}, this.env.session.user_content, {
                    // optimize the return value by avoiding useless queries
                    // in non-mobile devices
                    isMobile: device.isMobile,
                }),
            },
        });
        return this.env.models['mail.thread'].insert(
            this.env.models['mail.thread'].convertData(data)
        );
    },

    async handleAddChannelAutocompleteSelect2(ev, ui) {
        const name = this.addingChannelValue;
        const channel_type = 'multi_livechat_NAME';
        console.log("adding channel");
        this.clearIsAddingItem();
        if (ui.item.special) {
            const channel = await this.async(() =>
                this.performRpcCreateChannel2({
                    name,
                    privacy: ui.item.special,
                })
            );
            channel.open();
        } else {
            const channel = await this.async(() =>
                this.env.models['mail.thread'].performRpcJoinChannel({
                    channelId: ui.item.id,
                })
            );
            channel.open();
        }
    },
});

});

