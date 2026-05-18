/** @odoo-module */
import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.portalDetails = publicWidget.Widget.extend({
    selector: '#jobs_section, #create_profile_section',
    events: {
        'change select[name="disability"]': '_onDisabilityChange',
        'change select[name="disability_specify"]': '_onDisabilitySpecifyChange',
        'change select[name="is_sa_citizen"]': '_onIsSACitizenChange',
        'change select[name="higher_qualification"]': '_onHigherQualChange',
        'change select[name="field_of_study"]': '_onFieldOfStudyChange',
        'change select[name="criminal_record"]': '_onCriminalRecordChange',
        'change input[name="sa_id_number"]': '_onSAIDNumberInput'
    },
    _onDisabilityChange: function () {
       console.log("\n===document.getElementById('disability').value==",document.getElementById('disability').value)
       if (document.getElementById('disability').value=== 'yes'){
           document.getElementById('desc_disability_visible').style.display='block';
//           document.getElementById('desc_disability_visible').addClass("s_website_form_required");
       }
       else if (document.getElementById('disability').value=== 'no'){
            document.getElementById('desc_disability_visible').style.display='none';
//            document.getElementById('desc_disability_visible').removeClass("s_website_form_required");
       }
    },
    _onDisabilitySpecifyChange: function () {
       if (document.getElementById('disability_specify').value=== 'other'){
           document.getElementById('desc_disability_other_visible').style.display='block';
//           document.getElementById('desc_disability_other_visible').addClass("s_website_form_required");
       }
       else {
            document.getElementById('desc_disability_other_visible').style.display='none';
//            document.getElementById('desc_disability_other_visible').removeClass("s_website_form_required");
       }
    },
    _onIsSACitizenChange: function () {
       if (document.getElementById('is_sa_citizen').value=== 'by_birth'){
           document.getElementById('sa_identity_number').style.display='block';
           document.getElementById('date_of_naturalisation').style.display='none';
           document.getElementById('passport_number').style.display='none';
//           document.getElementById('sa_identity_number').addClass("s_website_form_required");
//           document.getElementById('date_of_naturalisation').removeClass("s_website_form_required");
//           document.getElementById('passport_number').removeClass("s_website_form_required");
       }
       else if (document.getElementById('is_sa_citizen').value=== 'by_naturalisation'){
           document.getElementById('sa_identity_number').style.display='none';
           document.getElementById('date_of_naturalisation').style.display='block';
           document.getElementById('passport_number').style.display='none';
//           document.getElementById('sa_identity_number').removeClass("s_website_form_required");
//           document.getElementById('date_of_naturalisation').addClass("s_website_form_required");
//           document.getElementById('passport_number').removeClass("s_website_form_required");
       }
       else if (document.getElementById('is_sa_citizen').value=== 'no'){
           document.getElementById('sa_identity_number').style.display='none';
           document.getElementById('date_of_naturalisation').style.display='none';
           document.getElementById('passport_number').style.display='block';
//           document.getElementById('sa_identity_number').removeClass("s_website_form_required");
//           document.getElementById('date_of_naturalisation').removeClass("s_website_form_required");
//           document.getElementById('passport_number').addClass("s_website_form_required");
       }
    },
    _onHigherQualChange: function () {
       if (document.getElementById('higher_qualification').value=== 'other'){
            document.getElementById('other_higher_qualification').style.display='block';
//            document.getElementById('other_higher_qualification').addClass("s_website_form_required");
       }
       else {
            document.getElementById('other_higher_qualification').style.display='none';
//            document.getElementById('other_higher_qualification').removeClass("s_website_form_required");
       }
    },
    _onFieldOfStudyChange: function () {
       if (document.getElementById('field_of_study').value=== 'Other'){
            document.getElementById('other_field_of_study').style.display='block';
//            document.getElementById('other_field_of_study').addClass("s_website_form_required");
       }
       else {
            document.getElementById('other_field_of_study').style.display='none';
//            document.getElementById('other_field_of_study').removeClass("s_website_form_required");
       }
    },
    _onCriminalRecordChange: function () {
       if (document.getElementById('criminal_record').value=== 'yes'){
            document.getElementById('type_criminal_act').style.display='block';
            document.getElementById('criminal_case_finalised_date').style.display='block';
            document.getElementById('criminal_outcome_judgment').style.display='block';
//            document.getElementById('type_criminal_act').addClass("s_website_form_required");
//            document.getElementById('criminal_case_finalised_date').addClass("s_website_form_required");
//            document.getElementById('criminal_outcome_judgment').addClass("s_website_form_required");
       }
       else {
            document.getElementById('type_criminal_act').style.display='none';
            document.getElementById('criminal_case_finalised_date').style.display='none';
            document.getElementById('criminal_outcome_judgment').style.display='none';
//            document.getElementById('type_criminal_act').addClass("s_website_form_required");
//            document.getElementById('criminal_case_finalised_date').addClass("s_website_form_required");
//            document.getElementById('criminal_outcome_judgment').addClass("s_website_form_required");
       }
    },
    _onSAIDNumberInput: function (ev) {
        const inputField = ev.target;
        let idNumber = inputField.value;

        // Only run validation if exactly 13 digits are entered
//        if (idNumber.length !== 13) {
//            return; // Wait until user completes input
//        }
         // Check if the input is exactly 13 digits long
        if (!/^\d{13}$/.test(idNumber)) {
            if (!inputField.dataset.invalidShown) {
                alert("The R.S.A. Identification Number should be a 13-digit number.");
                $("#sa_id_number").val('');
                $("#sa_id_number").focus();
                inputField.dataset.invalidShown = "1";
            }
            return;
        }

        delete inputField.dataset.invalidShown; // Reset once it's valid
        // South African ID check digit verification
        var checkIDNumber = function(idNumber) {
            var a = 0, b = 0, c = 0, d;

            // Sum digits in even positions (0-indexed odd positions in the array)
            for (var i = 0; i < 6; i++) {
                a += parseInt(idNumber[i * 2], 10); // Even positions
            }

            // Build a number from digits in odd positions, double it, and sum its digits
            for (var i = 0; i < 6; i++) {
                b = b * 10 + parseInt(idNumber[2 * i + 1], 10); // Odd positions
            }
            b = b * 2;

            // Sum the digits of the resulting number
            while (b > 0) {
                c += b % 10;
                b = Math.floor(b / 10);
            }

            // Add the sum of the even-position digits
            c += a;

            // Calculate the check digit
            d = 10 - (c % 10);
            if (d === 10) d = 0;

            // Compare the check digit with the last digit of the ID number
            return d === parseInt(idNumber[12], 10);
        };
        if (!checkIDNumber(idNumber)) {
            alert("Invalid R.S.A. ID number (check digit failed).");
            $("#sa_id_number").val('');
            $("#sa_id_number").focus();
            return;
        }
        // Proceed with the rest of the validations if the check digit is valid
        // Extract and validate date
        var year = idNumber.substring(0, 2);
        var month = idNumber.substring(2, 4);
        var day = idNumber.substring(4, 6);
        var fullYear = parseInt(year) <= 20 ? '20' + year : '19' + year;
        var formattedDate = `${fullYear}-${month}-${day}`;

        var daysInMonth = [31, (fullYear % 4 === 0 ? 29 : 28), 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
        if (month < 1 || month > 12 || day < 1 || day > daysInMonth[parseInt(month) - 1]) {
            alert("Invalid birthdate in the R.S.A. ID number.");
            $("#sa_id_number").val('');
            $("#sa_id_number").focus();
            return;
        }

        // Gender
        var genderDigits = parseInt(idNumber.substring(6, 10));
        if (genderDigits <= 4999) {
            $("#gender option:contains('Female')").prop('selected', true);
        } else {
            $("#gender option:contains('Male')").prop('selected', true);
        }

        // Set date of birth
        // Validate the resulting date
        const dobDate = new Date(formattedDate);
        if (dobDate instanceof Date && !isNaN(dobDate)) {
            const dobInput = document.getElementById("date_of_birth");
            if (dobInput) {
                dobInput.value = formattedDate;
            }
        }
    },
     _onPassportInput: function (ev) {
        console.log(ev.target.value)
        const inputField = ev.target;
        let value = inputField.value;
        value = value.replace(/\D/g, '').slice(0, 13);
        inputField.value = value;
        console.log('_onPassportInput', value);
        console.log('_onPassportInput length:', value.length);
        if (value.length >= 6) {
            const firstSixDigits = value.slice(0, 6);
            const year = '19' + firstSixDigits.slice(0, 2);
            const month = firstSixDigits.slice(2, 4);
            const day = firstSixDigits.slice(4, 6);
            const formattedDate = `${year}-${month}-${day}`;
            if (month <= 12 && day <= 31) {
                const dateField = document.querySelector('input[name="date_of_birth"]');
                if (dateField) {
                    dateField.value = formattedDate;
                }
                console.log('Formatted Date:', formattedDate);
            } else {
                alert('Invalid Identification Number.');
            }
        }
        const genderDigits = value.slice(6, 10);
        if (genderDigits) {
            const genderNumber = parseInt(genderDigits, 10);
            const genderField = document.querySelector('select[name="gender"]');
            if (genderField) {
                if (genderNumber >= 0 && genderNumber <= 4999) {
                    genderField.value = 'female';
                    console.log('Gender: Female');
                } else if (genderNumber >= 5000 && genderNumber <= 9999) {
                    genderField.value = 'male';
                    console.log('Gender: Male');
                } else {
                    alert('Invalid Identification Number.');
                    console.warn('Gender: Other');
                }
            }
        }
    if (value.length > 13) {
        alert('You have entered more than 13 digits.');
        event.target.value = value.slice(0, 13);
    }
    },
});
