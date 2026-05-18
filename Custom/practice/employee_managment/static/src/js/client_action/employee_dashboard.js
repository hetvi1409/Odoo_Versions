import { registry } from "@web/core/registry"

alert('js calling>>>>>>>>>');

export class EmployeeDashboard extends Component {
    static template = "employee_managment.employee_managment_template";

}    

registry.category("actions").add("employee_dashboard", EmployeeDashboard)
