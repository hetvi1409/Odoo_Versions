/** @odoo-module **/

import { Component, useState, onWillStart, useComponent, useEnv, markup } from '@odoo/owl';
import { VisitorForm } from "@frontdesk/visitor_form/visitor_form";
import { WelcomePage } from "@frontdesk/welcome_page/welcome_page";
import { RegisterPage } from "@frontdesk/register_page/register_page";
import { DrinkPage } from "@frontdesk/drink_page/drink_page";
import { Navbar } from "@frontdesk/navbar/navbar";
import { HostPage } from "@frontdesk/host_page/host_page";
import { EndPage } from "@frontdesk/end_page/end_page";
import { QuickCheckIn } from "@frontdesk/quick_check_in/quick_check_in";
import { useService } from "@web/core/utils/hooks";
import { registry } from '@web/core/registry';
import { QWeb } from 'web.core';

export class FrontdeskAction extends Component {
        setup() {
        const component = useComponent();
        const env = useEnv();
        console.log("\n\n===this.props.action.context===",this.props.action.context)
        this.rpc = useService("rpc");
        this.state = useState({
            currentComponent: !this.props.action.context.isMobile ? WelcomePage : VisitorForm,
            plannedVisitors: [],
        });
        const urlToken = window.location.href.split("/").findLast((s) => s);
        this.token = this.props.action.context?.token || null;
        this.frontdeskUrl = `/frontdesk/${this.props.action.context.station_id}/${this.token}`;
        onWillStart(this.onWillStart.bind(this));
        if (this.props.action.context.isMobile) {
            // Retrieve the saved component from sessionStorage
            const savedComponent = sessionStorage.getItem("currentComponent");
            if (savedComponent) {
                const component = registry.category("frontdesk_screens").get(savedComponent);
                this.state.currentComponent = component;
            }
            window.addEventListener("beforeunload", () => {
                // Before the page refresh, save the current component to sessionStorage
                sessionStorage.setItem("currentComponent", this.state.currentComponent.name);
            });
        }
    }

    async onWillStart() {
        try {
            const url = `${this.frontdeskUrl}/get_frontdesk_data`
            this.frontdeskData = await this.env.services.rpc({
                route: url,
                params: {},
            });
            this.station = this.frontdeskData.station[0];
        } catch (error) {
            console.error("Error fetching frontdesk data: ", error);
        }
    }

    /* This method updates the plannedVisitors */
    updatePlannedVisitors() {
        this._getPlannedVisitors();
        this.intervalId = setInterval(() => this._getPlannedVisitors(), 600000); // 10 minutes
    }

    async triggerClientAction() {
        const result = await this.getContextFromBackend();
        await this.trigger('do-action', {
            type: 'ir.actions.client',
            tag: 'frontdesk.frontdesk_action', // Tag for your client action
            context: result.context, // Context to be passed from the backend
        });
    }

    // This function simulates an RPC call to get context
    async getContextFromBackend() {
        // Assuming you have a way to retrieve the context, e.g., from a backend endpoint
        const stationId = document.querySelector('#frontdesk_id').value;
        const token = document.querySelector('#frontdesk_token').value;
        const lang = document.querySelector('#frontdesk_lang').value;

        // Simulate calling the backend API for context (Replace with your own logic)
        return {
            context: {
                station_id: stationId,
                token: token,
                lang: lang || 'en_US',
            }
        };
    }

    /**
     * Get the plannedVisitors from the backend through rpc call
     *
     * @private
     */
    async _getPlannedVisitors() {
        const url = `${this.frontdeskUrl}/get_planned_visitors`
        this.state.plannedVisitors  = await this.env.services.rpc({
            route: url,
            params: {},
        });
    }

    /* This method creates the visitor in the backend through rpc call */
    async createVisitor() {
        const url = `${this.frontdeskUrl}/prepare_visitor_data`

        const result = await this.env.services.rpc({
            route: url,
            params: {
                name: this.visitorData.visitorName,
                phone: this.visitorData.visitorPhone,
                email: this.visitorData.visitorEmail,
                company: this.visitorData.visitorCompany,
                property_type: this.inputPropertyType || this.hostData?.inputPropertyType || false,
                department: this.hostData?.inputDepartment || false,
                host_ids: this.hostData?.hostId ? [this.hostData.hostId] : [],
            },
        });
        this.visitorId = result.visitor_id;
    }

    onClose() {
        // Check if the device is mobile or not and show the screen accordingly
        !this.props.action.context.isMobile ? this.showScreen("WelcomePage") : this.showScreen("VisitorForm");
    }

    /**
     * @param {Event} ev
     */
    onChangeLang(ev) {
        window.location.href = window.location.pathname + `?lang=${encodeURIComponent(ev.currentTarget.value)}`;
    }

    /**
     * This method change the current screen
     *
     * @param {string} name
     */
    showScreen(name) {
        const component = registry.category("frontdesk_screens").get(name);
        this.state.currentComponent = component;
    }

    /* This method clears the interval for updatePlannedVisitors */
    clearUpdatePlannedVisitors() {
        clearInterval(this.intervalId);
    }

    /* Reset the data */
    resetData() {
        this.hostData = null;
        this.visitorData = null;
        this.plannedVisitorData = null;
        this.isDrinkSelected = false;
    }

    /**
     * @param {string} name
     * @param {string|false} phone
     * @param {string|false} email
     * @param {string|false} company
     */
    setVisitorData(name, phone, email, company) {
        this.visitorData = {
            visitorName: name,
            visitorPhone: phone,
            visitorEmail: email,
            visitorCompany: company,
        };
    }

    /**
     * @param {Object} host
     */
    setHostData(host) {
        this.hostData = {
            hostId: host.hostId,
            hostName: host.hostName,
            inputPropertyType: host.inputPropertyType,
            inputDepartment: host.inputDepartment,
        };
        this.inputDepartment = host.inputDepartment
        this.inputPropertyType = host.inputPropertyType

//    this.inputPropertyType = document.getElementById('property_type');
//        this.inputPropertyType = this.inputPropertyType.el?.value;
//        this.inputPropertyType = this.inputPropertyType.el?.value;
    }

    /**
     * @param {number} plannedVisitorId
     * @param {string|false} plannedVisitorMessage
     * @param {Array} plannedVisitorHosts
     */
    setPlannedVisitorData(plannedVisitorId, plannedVisitorMessage, plannedVisitorHosts) {
        this.plannedVisitorData = {
            plannedVisitorId: plannedVisitorId,
            plannedVisitorMessage: plannedVisitorMessage,
            plannedVisitorHosts: plannedVisitorHosts,
        };
    }

    /**
     * @param {boolean} boolean
     */
    setDrink(boolean) {
        this.isDrinkSelected = boolean;
    }

    // -------------------------------------------------------------------------
    // Getters
    // -------------------------------------------------------------------------

    get frontdeskProps() {
        let props = {};
        const currentLang = this.props.action.context.currentLang || 'en_US';
        if (this.state.currentComponent === WelcomePage) {
            props = {
                showScreen: this.showScreen.bind(this),
                resetData: this.resetData.bind(this),
                onChangeLang: this.onChangeLang.bind(this),
                token: this.token,
                companyName: this.frontdeskData.company.name,
                stationInfo: this.station,
                langs: this.frontdeskData.langs.length > 1 ? this.frontdeskData.langs : false,
                currentLang: currentLang,
            };
        } else if (this.state.currentComponent === VisitorForm) {
            props = {
                onChangeLang: this.onChangeLang.bind(this),
                showScreen: this.showScreen.bind(this),
                clearUpdatePlannedVisitors: this.clearUpdatePlannedVisitors.bind(this),
                setVisitorData: this.setVisitorData.bind(this),
                updatePlannedVisitors: this.updatePlannedVisitors.bind(this),
                visitorData: this.visitorData || false,
                isMobile: this.props.action.context.isMobile || false,
                currentComponent: this.state.currentComponent.name,
                isPlannedVisitors: this.state.plannedVisitors.length ? true : false,
                stationInfo: this.station,
                langs: this.frontdeskData.langs.length > 1 ? this.frontdeskData.langs : false,
                currentLang: currentLang,
                theme: this.station.theme,
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
                isMobile: this.props.action.context.isMobile || false,
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
                stationId: this.station.id,
                token: this.token,
                visitorId: this.plannedVisitorData
                    ? this.plannedVisitorData.plannedVisitorId
                    : this.visitorId,
            };
        } else if (this.state.currentComponent === EndPage) {
            props = {
                showScreen: this.showScreen.bind(this),
                onClose: this.onClose.bind(this),
                isMobile: this.props.action.context.isMobile || false,
                isDrinkSelected: this.isDrinkSelected,
                theme: this.station.theme,
                plannedVisitorData: this.plannedVisitorData,
                hostData: this.hostData,
            };
        }
        return props;
    }

    get navBarProps() {
        return {
            showScreen: this.showScreen.bind(this),
            currentComponent: this.state.currentComponent.name,
            companyInfo: this.frontdeskData.company,
            isMobile: this.props.action.context.isMobile || false,
            isPlannedVisitors: this.state.plannedVisitors.length ? true : false,
            theme: this.station.theme,
            onChangeLang: this.onChangeLang.bind(this),
            langs: this.frontdeskData.langs.length > 1 ? this.frontdeskData.langs : false,
            currentLang: currentLang,
        };
    }

    get quickCheckInProps() {
        return {
            setPlannedVisitorData: this.setPlannedVisitorData.bind(this),
            showScreen: this.showScreen.bind(this),
            stationId: this.props.action.context.id,
            token: this.token,
            plannedVisitors: this.state.plannedVisitors,
            theme: this.station.theme,
        };
    }

    get markupValue() {
        return markup(this.station.description);
//        return this.station?.description ? markup(this.station.description) : "";
    }

}

FrontdeskAction.template = "FrontdeskTem"; // The template to render
FrontdeskAction.components = {
    WelcomePage,
    Navbar,
    VisitorForm,
    QuickCheckIn,
    HostPage,
    RegisterPage,
    DrinkPage,
    EndPage,
};

registry.category("actions").add("frontdesk.frontdesk_action", FrontdeskAction);
export default FrontdeskAction;