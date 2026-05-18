/** @odoo-module **/
import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.PropertyBuyRent = publicWidget.Widget.extend({
    selector: '.enquiry_crm_form',
    events: {
        'change select[name="company_type"]': '_onCompanyTypeChange',
    },
    _onCompanyTypeChange: function (ev) {
       if (ev.target.value=== 'person'){
            document.getElementById('company_type_person').classList.remove('d-none');
            document.getElementById('company_type_company').classList.add('d-none');
            document.getElementById('company_type_trust').classList.add('d-none');

            document.getElementById('person_document_type').classList.remove('d-none');
            document.getElementById('company_document_type').classList.add('d-none');
            document.getElementById('trust_document_type').classList.add('d-none');
       }
       if (ev.target.value=== 'company'){
            document.getElementById('company_type_company').classList.remove('d-none');
            document.getElementById('company_type_person').classList.add('d-none');
            document.getElementById('company_type_trust').classList.add('d-none');

            document.getElementById('person_document_type').classList.add('d-none');
            document.getElementById('company_document_type').classList.remove('d-none');
            document.getElementById('trust_document_type').classList.add('d-none');
       }
       if (ev.target.value=== 'trust'){
            document.getElementById('company_type_trust').classList.remove('d-none');
            document.getElementById('company_type_company').classList.add('d-none');
            document.getElementById('company_type_person').classList.add('d-none');

            document.getElementById('person_document_type').classList.add('d-none');
            document.getElementById('company_document_type').classList.add('d-none');
            document.getElementById('trust_document_type').classList.remove('d-none');
       }
       if (ev.target.value === '') {
            document.getElementById('company_type_trust').classList.add('d-none');
            document.getElementById('company_type_company').classList.add('d-none');
            document.getElementById('company_type_person').classList.add('d-none');

            document.getElementById('person_document_type').classList.add('d-none');
            document.getElementById('company_document_type').classList.add('d-none');
            document.getElementById('trust_document_type').classList.add('d-none');
       }
   },

})