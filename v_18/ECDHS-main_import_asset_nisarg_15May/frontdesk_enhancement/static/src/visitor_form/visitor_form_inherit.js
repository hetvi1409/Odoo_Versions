/** @odoo-module **/

import { patch } from '@web/core/utils/patch';
import { VisitorForm as BaseVisitorForm } from '@frontdesk/visitor_form/visitor_form';

import { Component, useState, onMounted, onWillUnmount, useRef } from "@odoo/owl";

patch(BaseVisitorForm.prototype, {
    props: {
        ...BaseVisitorForm.props,
        departments: Array,
        setDepartment: Function,
    },
    setup() {
        super.setup();
//        this.state.category = this.props.visitorData?.category || "";
//        this.state.visitor_leptop_register = this.props.visitorData?.visitor_leptop_register || false;
        this.inputCategoryRef = useRef("inputCategory");
        this.inputDepartmentRef = useRef("inputDepartment");
        this.inputLaptopRef = useRef("inputLaptop");
        this.inputSurnameRef = useRef("inputSurname");
        this.inputMakeRef = useRef("inputMake");
        this.inputSerialRef = useRef("inputSerial");
        this.inputFirearmSerialRef = useRef("inputFirearmSerial");
        this.inputFirearmName = useRef("inputFirearmName");
        this.inputIdNumberRef = useRef("inputIdNumber");
        this.inputOfficeVisitingRef = useRef("inputOfficeVisiting");
        this.inputPurposeRef = useRef("inputPurpose");
        this.state = useState({
            category: this.props.visitorData?.category || "",
            inputFirearm: this.props.visitorData?.inputFirearm || "",
            visitor_leptop_register: this.props.visitorData?.visitor_leptop_register || false,
        });
    },

    onCategoryChange(ev) {
        this.state.category = ev.target.value;
    },

    onLaptopCheckChange(ev) {
        this.state.visitor_leptop_register = ev.target.value;
    },

    onFirearmChange(ev) {
        this.state.inputFirearm = ev.target.value;
    },

    _onSubmit() {
        const visitorData = {
            visitorName: this.inputNameRef.el?.value || "",
            visitorPhone: this.inputPhoneRef.el?.value || false,
            visitorEmail: this.inputEmailRef.el?.value || false,
            visitorCompany: this.inputCompanyRef.el?.value || false,
            category: this.state.category,
            department_id: this.inputDepartmentRef.el?.value
                ? parseInt(this.inputDepartmentRef.el.value)
                : false,
            visitor_leptop_register: this.state.visitor_leptop_register,
            x_has_firearm: this.state.inputFirearm,
            surname: this.inputSurnameRef.el?.value || false,
            make: this.inputMakeRef.el?.value || false,
            serial_number_or_tag: this.inputSerialRef.el?.value || false,
            id_number: this.inputIdNumberRef.el?.value || false,
            office_visiting: this.inputOfficeVisitingRef.el?.value || false,
            purpose_of_the_meeting: this.inputPurposeRef.el?.value || false,
            x_firearm_serial: this.inputFirearmSerialRef.el?.value || false,
            x_firearm_name: this.inputFirearmName.el?.value || false,
        };
        this.props.setVisitorData(
            visitorData.visitorName,
            visitorData.visitorPhone,
            visitorData.visitorEmail,
            visitorData.visitorCompany,
            visitorData.category,
            visitorData.department_id,
            visitorData.visitor_leptop_register,
            visitorData.surname,
            visitorData.make,
            visitorData.serial_number_or_tag,
            visitorData.id_number,
            visitorData.office_visiting,
            visitorData.purpose_of_the_meeting,
            visitorData.x_firearm_serial,
            visitorData.x_has_firearm,
            visitorData.x_firearm_name
        );
        // Show the HostPage component, if the host_selection field is true from the backend
        this.props.stationInfo.host_selection
            ? this.props.showScreen("HostPage")
            : this.props.showScreen("RegisterPage");
    },
});
