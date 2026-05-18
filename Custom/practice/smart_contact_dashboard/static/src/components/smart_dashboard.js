import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { standardActionServiceProps } from "@web/webclient/actions/action_service";

export class SmartDashboard extends Component {
    static template = "smart_contract_dashboard.smart_dashboard";
    static props = { ...standardActionServiceProps };

    setup(){
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.state = useState({
            count : 0,
            partners:[],
            loading: true,
            newPartner : {
                name: "",
                email: "",
            }
        });
        onWillStart(async () => {
            this.state.loading = true;

            await this.get_partner();

            this.state.loading = false;

        });
//        onWillStart(async () => {
//            this.partners = await this.orm.searchRead(
//                "res.partner",
//                [],  // domain
//                ["name", "email","phone"]  // fields
//            );
//            console.log('this.partners>>>>>>',this.partners);
//        });
    }

    async get_partner() {
        this.state.loading = true;
        this.state.partners = await this.orm.searchRead(
                "res.partner",
                [],  // domain
                ["name", "email","phone"]  // fields
            );
        console.log('this.partners>>>>>>',this.partners);
        this.state.loading = false;


    }

    onInputChange(ev) {
        console.log('ev>>>',ev);
        const field = ev.target.name;
        this.state.newPartner[field] = ev.target.value;
    }

    async createPartner(ev) {
        ev.preventDefault();

        const data = this.state.newPartner;
        console.log('DATA>>>>',data)

        if (!data.name) {
            alert("Name is required");
            return;
        }

        await this.orm.create("res.partner", [data]);

        // reset form
        this.state.newPartner = { name: "", email: "" };

        // refresh list
        await this.get_partner();

        this.notification.add("Partner is created.", { type: "success" });
    };

    increment() {
        this.state.count++;
    }
    decrement() {
        this.state.count--;
    }

}
registry.category("actions").add("smart_contract_dashboard", SmartDashboard);
