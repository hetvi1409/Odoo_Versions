/** @odoo-module */

import publicWidget from 'web.public.widget';
import { _t } from 'web.core';
import concurrency from 'web.concurrency';
import Dialog from "web.Dialog";

publicWidget.registry.HelpdeskTicketValidation = publicWidget.Widget.extend({
    selector: '#helpdesk_ticket_form',
    events: {
        'click .s_website_form_send': '_onSubmit',
    },

    init() {
        this._super.apply(this, arguments);
        this._dp = new concurrency.DropPrevious();
    },

    //-----------------------------------------------------------------------
    // Main validation logic
    //-----------------------------------------------------------------------

    async _onSubmit(ev) {
        ev.preventDefault();
        ev.stopImmediatePropagation();

        const $form = this.$el;
        let flag = true;
        const email = $form.find('input[name="partner_email"]').val()?.trim() || '';
        console.log("\n\n===email===",email)
        const teamId = parseInt($form.find('input[name="team_id"]').val()) || false;
        debugger;
        if (!teamId) {
            var message;
            message = _.str.sprintf(_t('No helpdesk team selected. Please contact the administrator.'));
            Dialog.alert(this, message);
            flag = false;
        }

        // Fetch team info
        const team = await this._rpc({
            route: '/get_helpdesk_team',
            params: { team_id: teamId },
        });

        if (!team || !team.name) {
            var message;
            message = _.str.sprintf(_t('Invalid team information. Please try again.'));
            Dialog.alert(this, message);
            flag = false;
        }

        // Apply validation only for "I.T Support"
        if (team.name === 'I.T Support') {
            // Check if employee with this email exists
            const employeeExists = await this._rpc({
                route: '/check_employee_email',
                params: { email: email },
            });
            if (!email.endsWith('@jhbproperty.co.za')) {
                var message;
                message = _.str.sprintf(_t('Please use a company email ending with @jhbproperty.co.za to submit I.T Support tickets.'));
                Dialog.alert(this, message);
                flag = false;
            }
            else if (!employeeExists) {
                var message;
                message = _.str.sprintf(_t('No employee found with this email address. Please use your registered company email.'));
                Dialog.alert(this, message);
                flag = false;
            }
        }

        // All checks passed
        if (flag){
            this.$el.trigger('submit');
        }
    },
});
