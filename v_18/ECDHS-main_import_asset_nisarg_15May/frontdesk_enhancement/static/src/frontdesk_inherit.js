/** @odoo-module **/

import { rpc } from "@web/core/network/rpc";
import { registry } from "@web/core/registry";
import { VisitorForm } from "@frontdesk/visitor_form/visitor_form";
import { WelcomePage } from "@frontdesk/welcome_page/welcome_page";
import { RegisterPage } from "@frontdesk/register_page/register_page";
import { DrinkPage } from "@frontdesk/drink_page/drink_page";
import { Navbar } from "@frontdesk/navbar/navbar";
import { HostPage } from "@frontdesk/host_page/host_page";
import { EndPage } from "@frontdesk/end_page/end_page";
import { QuickCheckIn } from "@frontdesk/quick_check_in/quick_check_in";

import { Component, useState, onWillStart, markup } from "@odoo/owl";

import { Frontdesk } from '@frontdesk/frontdesk';
import { patch } from '@web/core/utils/patch';

patch(Frontdesk.prototype, {
    setup() {
        super.setup();
        this.state.departments = [];
    },

//    async onWillStart() {
////        await this._super();
//        super.onWillStart(...arguments);
//        const depts = await rpc("/frontdesk/get_departments", {});
//        this.state.departments = depts || [];
//    },
    async onWillStart() {
        this.frontdeskData = await rpc(`${this.frontdeskUrl}/get_frontdesk_data`);
        this.station = this.frontdeskData.station[0];
        const depts = await rpc("/frontdesk/get_departments", {});
        this.state.departments = depts || [];
    },

    async createVisitor() {
        const result = await rpc(`${this.frontdeskUrl}/prepare_visitor_data`, {
            name: this.visitorData.visitorName,
            phone: this.visitorData.visitorPhone,
            email: this.visitorData.visitorEmail,
            company: this.visitorData.visitorCompany,
            category: this.visitorData.category,
            department_id: this.visitorData.department_id,
            visitor_leptop_register: this.visitorData.visitor_leptop_register,
            surname: this.visitorData.surname,
            make: this.visitorData.make,
            serial_number_or_tag: this.visitorData.serial_number_or_tag,
            id_number: this.visitorData.id_number,
            office_visiting: this.visitorData.office_visiting,
            x_has_firearm: this.visitorData.x_has_firearm,
            x_firearm_name: this.visitorData.x_firearm_name,
            x_firearm_serial: this.visitorData.x_firearm_serial,
            purpose_of_the_meeting: this.visitorData.purpose_of_the_meeting,
            host_ids: this.hostData ? [this.hostData.hostId] : [],
        });
        this.visitorId = result.visitor_id;
    },

    setVisitorData(name, phone, email, company,category, department_id, visitor_leptop_register,surname,make, serial_number_or_tag, id_number,office_visiting, purpose_of_the_meeting,x_firearm_serial,x_has_firearm,x_firearm_name) {
        this.visitorData = {
            visitorName: name,
            visitorPhone: phone,
            visitorEmail: email,
            visitorCompany: company,
            category:category,
            department_id:department_id,
            visitor_leptop_register:visitor_leptop_register,
            surname:surname,
            make:make,
            serial_number_or_tag:serial_number_or_tag,
            id_number:id_number,
            office_visiting:office_visiting,
            purpose_of_the_meeting:purpose_of_the_meeting,
            x_firearm_serial:x_firearm_serial,
            x_has_firearm:x_has_firearm,
            x_firearm_name:x_firearm_name,
        };
    },

     selectedDepartment(ev) {
        if (!this.visitorData) this.visitorData = {};
        this.visitorData.department_id = parseInt(ev.target.value);
    },

    get frontdeskProps() {
        let props = {};
        if (this.state.currentComponent === WelcomePage) {
            props = {
                showScreen: this.showScreen.bind(this),
                resetData: this.resetData.bind(this),
                onChangeLang: this.onChangeLang.bind(this),
                token: this.token,
                companyName: this.frontdeskData.company.name,
                stationInfo: this.station,
                langs: this.frontdeskData.langs.length > 1 ? this.frontdeskData.langs : false,
                currentLang: this.props.currentLang,
            };
        } else if (this.state.currentComponent === VisitorForm) {
            props = {
                onChangeLang: this.onChangeLang.bind(this),
                showScreen: this.showScreen.bind(this),
                clearUpdatePlannedVisitors: this.clearUpdatePlannedVisitors.bind(this),
                setVisitorData: this.setVisitorData.bind(this),
                updatePlannedVisitors: this.updatePlannedVisitors.bind(this),
                visitorData: this.visitorData || false,
                isMobile: this.props.isMobile,
                currentComponent: this.state.currentComponent.name,
                isPlannedVisitors: this.state.plannedVisitors.length ? true : false,
                stationInfo: this.station,
                langs: this.frontdeskData.langs.length > 1 ? this.frontdeskData.langs : false,
                currentLang: this.props.currentLang,
                theme: this.station.theme,
                departments: this.state.departments,
                setDepartment: this.selectedDepartment.bind(this),
            };
        } else if (this.state.currentComponent === HostPage) {
            props = {
                stationId: this.station.id,
                token: this.token,
                showScreen: this.showScreen.bind(this),
                setHostData: this.setHostData.bind(this),
            };
        } else if (this.state.currentComponent === RegisterPage) {
            props = {
                showScreen: this.showScreen.bind(this),
                onClose: this.onClose.bind(this),
                createVisitor: this.createVisitor.bind(this),
                theme: this.station.theme,
                isMobile: this.props.isMobile,
                isDrinkVisible: this.frontdeskData.drinks?.length ? true : false,
                plannedVisitorData: this.plannedVisitorData,
                hostData: this.hostData,
            };
        } else if (this.state.currentComponent === DrinkPage) {
            props = {
                showScreen: this.showScreen.bind(this),
                setDrink: this.setDrink.bind(this),
                theme: this.station.theme,
                drinkInfo: this.frontdeskData.drinks,
                stationId: this.props.id,
                token: this.token,
                visitorId: this.plannedVisitorData
                    ? this.plannedVisitorData.plannedVisitorId
                    : this.visitorId,
            };
        } else if (this.state.currentComponent === EndPage) {
            props = {
                showScreen: this.showScreen.bind(this),
                onClose: this.onClose.bind(this),
                isMobile: this.props.isMobile,
                isDrinkSelected: this.isDrinkSelected,
                theme: this.station.theme,
                plannedVisitorData: this.plannedVisitorData,
                hostData: this.hostData,
            };
        }
        return props;
    }
});
