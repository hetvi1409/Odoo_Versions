/** @odoo-module **/
import publicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from "@web/core/network/rpc";
publicWidget.registry.SubsidyApplication = publicWidget.Widget.extend({
    selector: '.housing_subsidy_application',
    events: {
        'click .trash_one': '_onClickTrashOne',
        'click .trash_two': '_onClickTrashTwo',
        'click .trash_three': '_onClickTrashThree',
        'click .trash_four': '_onClickTrashFour',
        'click .trash_five': '_onClickTrashFive',
        'click .trash_six': '_onClickTrashSix',
        'click .trash_seven': '_onClickTrashSeven',
        'click .trash_eight': '_onClickTrashEight',
        'click .trash_nine': '_onClickTrashNine',
        'click .trash_ten': '_onClickTrashTen',
        'click .trash_eleven': '_onClickTrashEleven',
        'click .trash_twelve': '_onClickTrashTwelve',
        'click .trash_thirteen': '_onClickTrashThirteen',
        'input .applicant_income': '_computeTotals',
        'input .spouse_income': '_computeTotals',
        'input .funding_input': '_computeFundingTotal',
        'change #country_id': '_onCountryChange',
        'change #district': '_onDistrictChange',
    },
    setup() {
        this.store = useStore();
    },
    _onClickTrashOne: function (ev) {
        const fileInput = document.getElementById("mrg_certificate");
        fileInput.value = "";
    },
    _onClickTrashTwo: function (ev) {
        const fileInput = document.getElementById("identity_doc_self");
        fileInput.value = "";
    },
    _onClickTrashThree: function (ev) {
        const fileInput = document.getElementById("identity_doc_spouse");
        fileInput.value = "";
    },
    _onClickTrashFour: function (ev) {
        const fileInput = document.getElementById("divorce_certificate");
        fileInput.value = "";
    },
    _onClickTrashFive: function (ev) {
        const fileInput = document.getElementById("spouse_death_certificate");
        fileInput.value = "";
    },
    _onClickTrashSix: function (ev) {
        const fileInput = document.getElementById("proof_of_disability");
        fileInput.value = "";
    },
    _onClickTrashSeven: function (ev) {
        const fileInput = document.getElementById("proof_of_loan");
        fileInput.value = "";
    },
    _onClickTrashEight: function (ev) {
        const fileInput = document.getElementById("agreement_of_sale");
        fileInput.value = "";
    },
    _onClickTrashNine: function (ev) {
        const fileInput = document.getElementById("compact_agreement");
        fileInput.value = "";
    },
    _onClickTrashTen: function (ev) {
        const fileInput = document.getElementById("agreement_with_conveyancer");
        fileInput.value = "";
    },
    _onClickTrashEleven: function (ev) {
        const fileInput = document.getElementById("building_contract_certificate");
        fileInput.value = "";
    },
    _onClickTrashTwelve: function (ev) {
        const fileInput = document.getElementById("proof_of_income_certificate");
        fileInput.value = "";
    },
    _onClickTrashThirteen: function (ev) {
        const fileInput = document.getElementById("residence_certificate");
        fileInput.value = "";
    },
    _computeTotals: function () {
        let applicantTotal = 0;
        let spouseTotal = 0;

        document.querySelectorAll('.applicant_income').forEach((el) => {
            const val = parseFloat(el.value.replace(/[^0-9.]/g, '')) || 0;
            applicantTotal += val;
        });

        document.querySelectorAll('.spouse_income').forEach((el) => {
            const val = parseFloat(el.value.replace(/[^0-9.]/g, '')) || 0;
            spouseTotal += val;
        });

        const aTotal = document.getElementById('applicant_total');
        const sTotal = document.getElementById('spouse_total');
        const jTotal = document.getElementById('joint_total');

        if (aTotal) aTotal.value = applicantTotal.toFixed(2);
        if (sTotal) sTotal.value = spouseTotal.toFixed(2);
        if (jTotal) jTotal.value = (applicantTotal + spouseTotal).toFixed(2);
    },
    _computeFundingTotal: function () {
        let total = 0;
        document.querySelectorAll('.funding_input').forEach((el) => {
            const val = parseFloat(el.value.replace(/[^0-9.]/g, '')) || 0;
            total += val;
        });

        const totalField = document.getElementById('funding_total');
        if (totalField) totalField.value = total.toFixed(2);
    },
    _onCountryChange: function (ev) {
        const countryId = ev.currentTarget.value;
        const stateSelect = document.getElementById("state_id");
        stateSelect.innerHTML = '<option value="">Loading...</option>';

        rpc('/get/states', { country_id: countryId }).then((data) => {
            stateSelect.innerHTML = '<option value="">Select State</option>';
            data.forEach((state) => {
                const option = document.createElement("option");
                option.value = state.id;
                option.text = state.name;
                stateSelect.appendChild(option);
            });
        });
    },
    _onDistrictChange: function (ev) {
        const districtId = ev.currentTarget.value;
        const municipalitySelect = document.getElementById("municipality_id");

        municipalitySelect.innerHTML = '<option value="">Loading...</option>';

        if (districtId) {
            rpc("/get/municipalities", {
                district_id: districtId
            }).then(data => {
                municipalitySelect.innerHTML = '<option value="">Select Municipality</option>';
                data.forEach(m => {
                    const option = document.createElement("option");
                    option.value = m.id;
                    option.text = m.name;
                    municipalitySelect.appendChild(option);
                });
            });
        } else {
            municipalitySelect.innerHTML = '<option value="">Select Municipality</option>';
        }
    }

});