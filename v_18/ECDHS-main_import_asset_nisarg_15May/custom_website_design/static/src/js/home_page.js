/** @odoo-module */
import publicWidget from '@web/legacy/js/public/public_widget';
publicWidget.registry.custom_website_design = publicWidget.Widget.extend({
    templates: 'custom_website_design.eastern_homepage',
    selector: '.custom-homepage',  // Select the correct container
    events: {
        'click .description-toggle': 'toggleDescription',
    },

    toggleDescription: function (ev) {
        ev.preventDefault();
        console.log('Toggling description');

        let $description = $(ev.currentTarget).siblings('.description');
        $description.toggleClass('d-none');
    }
});

export default publicWidget.registry.custom_website_design;

