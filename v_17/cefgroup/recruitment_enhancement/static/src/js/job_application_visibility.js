/** @odoo-module */
import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.portalDetails = publicWidget.Widget.extend({
    selector: '#jobs_section, #create_profile_section',
    events: {
        'change select[name="disability"]': '_onDisabilityChange',
//        'input input[name="passport"]': '_onPassportInput'
    },
    _onDisabilityChange: function () {
       if (document.getElementById('disability').value=== 'yes'){
       document.getElementById('desc_disability_visible').style.display='block';
       }
       else if (document.getElementById('disability').value=== 'no'){
              document.getElementById('desc_disability_visible').style.display='none';
       }
    },
//    _onPassportInput: function (ev) {
//        const inputField = ev.target;
//        let value = inputField.value;
//        value = value.replace(/\D/g, '').slice(0, 13);
//        inputField.value = value;
//        console.log('_onPassportInput', value);
//        console.log('_onPassportInput length:', value.length);
//        if (value.length >= 6) {
//            const firstSixDigits = value.slice(0, 6);
//            const year = '19' + firstSixDigits.slice(0, 2);
//            const month = firstSixDigits.slice(2, 4);
//            const day = firstSixDigits.slice(4, 6);
//            const formattedDate = `${year}-${month}-${day}`;
//            if (month <= 12 && day <= 31) {
//                const dateField = document.querySelector('input[name="date_of_birth"]');
//                if (dateField) {
//                    dateField.value = formattedDate;
//                }
//                console.log('Formatted Date:', formattedDate);
//            } else {
//                alert('Invalid Identification Number.');
//            }
//        }
//        const genderDigits = value.slice(6, 10);
//        if (genderDigits) {
//            const genderNumber = parseInt(genderDigits, 10);
//            const genderField = document.querySelector('select[name="gender"]'); // Replace with your gender field name
//            if (genderField) {
//                if (genderNumber >= 0 && genderNumber <= 4999) {
//                    genderField.value = 'female'; // Set to "female" (adjust value as per your system)
//                    console.log('Gender: Female');
//                } else if (genderNumber >= 5000 && genderNumber <= 9999) {
//                    genderField.value = 'male'; // Set to "male" (adjust value as per your system)
//                    console.log('Gender: Male');
//                } else {
//                    genderField.value = 'other';
//                    console.warn('Gender: Otherther');
//                }
//            }
//        }
//        if (value.length === 13) {
//            alert('You have entered 13 digits.');
//        }
//    },
});