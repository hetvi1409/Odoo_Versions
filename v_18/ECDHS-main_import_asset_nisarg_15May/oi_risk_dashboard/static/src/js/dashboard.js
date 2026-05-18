/** @odoo-module */
import { registry} from '@web/core/registry';
import { useService } from "@web/core/utils/hooks";
const { Component, onWillStart} = owl
import { rpc } from "@web/core/network/rpc";
import { _t } from "@web/core/l10n/translation";
import { onMounted, useRef, useState} from "@odoo/owl";

export class RiskDashboard extends Component {
    /**
     * Setup method to initialize required services and register event handlers.
     */
	setup() {
		this.action = useService("action");
		this.orm = useService("orm");
		this.departments = useRef("departments");
		this.department = "";
		this.top_risk = useRef("top_risk");
		this.state = useState({
            projects : '',
            employees: "",
            risks: [],
            risk_options: [],
            departments: [],
            selected_risks: [],
        });
		this.rpc = this.env.services.rpc
		onWillStart(async () => {
		    await this.willStart();
		});
		onMounted(async () => {
		    await this.mounted()
		});
	}
	/**
     * Event handler for the 'onWillStart' event.
     */
	async willStart() {
		await this.fetch_data();
		await this.fetch_departments();
		await this.fetch_risk_options();
	}
	async fetch_risk_options() {
        const res = await rpc('/get/risk/options');
        this.state.risk_options = res.risks;
        console.log("\n\n====risk_options===",this.state.risk_options)
    }
	async fetch_departments() {
        const res = await rpc('/get/risk/departments');
        this.state.departments = res.departments;
        console.log("\n\n====department===",this.state.departments)
    }
    async onDepartmentChange(ev) {
        const dept_id = ev.target.value ? parseInt(ev.target.value) : null;
        this.department = dept_id;

        const selected_risks = this.state.selected_risks;

        await this.fetch_data(dept_id, selected_risks);
        await this.render_top_risks_bar(dept_id, selected_risks);
    }

    onRiskCheckboxChange(ev) {
        const risk_id = parseInt(ev.target.value);
        let selected = [...this.state.selected_risks];  // copy current

        if (ev.target.checked) {
            if (!selected.includes(risk_id)) {
                selected.push(risk_id);
            }
        } else {
            selected = selected.filter(id => id !== risk_id);
        }
        this.state.selected_risks = selected;

        // reload with selected risks
        this.fetch_data(this.department, selected);
        this.render_top_risks_bar(this.department, selected);
    }

    async fetch_data(department_id = null, risk_ids = null) {
        const params = {};
        if (department_id) params.department_id = department_id;
        if (risk_ids) params.risk_ids = risk_ids;
        const res = await rpc('/get/risk/data', params);
        this.state.risks = res.risk;
        console.log("\n\n====risks===",this.state.risks)
        this.render(true);
    }
	 /**
     * Event handler for the 'onMounted' event.
     * Renders various components and charts after fetching data.
     */
	async mounted() {
		// Render other components after fetching data
		this.render_top_risks_bar();
	}

	async render_top_risks_bar(department_id = null, risk_ids = null) {
        const ctx = this.top_risk;
//        const params = department_id ? { department_id } : {};
        const params = {};
        if (department_id) params.department_id = department_id;
        if (risk_ids) params.risk_ids = risk_ids;
        const arrays = await rpc('/risk/top', params);

        const datasets = arrays[1].map((label, i) => ({
            label: label,
            data: [arrays[0][i]],
            backgroundColor: [
                "#4CAF50", "#2196F3", "#FF9800", "#9C27B0", "#F44336",
                "#00BCD4", "#8BC34A", "#FFEB3B", "#795548", "#607D8B"
            ][i % 10],
        }));

        const data = {
            labels: ["Risk"],
            datasets: datasets,
        };

        const options = {
            responsive: true,
            plugins: {
                legend: { position: "left", labels: { usePointStyle: true } },
                title: { display: true, text: "Top Risks", font: { size: 18 } }
            },
            scales: {
                x: { title: { display: true, text: "Risks" }, stacked: true },
                y: {
                    min: 0,
                    max: 6,
                    beginAtZero: true,
                    title: { display: true, text: "Risk Score" },
                    ticks: {
                        stepSize: 1,
                        callback: value => Number.isInteger(value) ? value : null
                    }
                }
            }
        };

        // Destroy old chart before creating new one (important when filtering)
        if (this.chartInstance) {
            this.chartInstance.destroy();
        }

        this.chartInstance = new Chart(ctx.el, {
            type: "bar",
            data: data,
            options: options,
        });
    }
    async printPdf() {

        const dashboardElement = document.querySelector(".risk_dashboard");
        const { jsPDF } = window.jspdf;
        const canvas = await html2canvas(dashboardElement, { scale: 2 });
        const imgData = canvas.toDataURL("image/png");

        const pdf = new jsPDF("p", "mm", "a4");
        const pdfWidth = pdf.internal.pageSize.getWidth();
        const pdfHeight = (canvas.height * pdfWidth) / canvas.width;

        pdf.addImage(imgData, "PNG", 0, 0, pdfWidth, pdfHeight);
        pdf.save("risk_analysis.pdf");
    }
    async printRiskDetailsPdf() {
        console.log("asdfg")
        const Element = document.querySelector(".risk_table_details");
        const { jsPDF } = window.jspdf;
        const canvas = await html2canvas(Element, { scale: 2 });
        const imgData = canvas.toDataURL("image/png");

        const pdf = new jsPDF("p", "mm", "a4");
        const pdfWidth = pdf.internal.pageSize.getWidth();
        const pdfHeight = (canvas.height * pdfWidth) / canvas.width;

        pdf.addImage(imgData, "PNG", 0, 0, pdfWidth, pdfHeight);
        pdf.save("risk_analysis.pdf");
    }

    async printRiskDetailsGraphPdf() {
        console.log("asdfg")
        const Element = document.querySelector(".risk_table_details_graph");
        const { jsPDF } = window.jspdf;
        const canvas = await html2canvas(Element, { scale: 2 });
        const imgData = canvas.toDataURL("image/png");

        const pdf = new jsPDF("p", "mm", "a4");
        const pdfWidth = pdf.internal.pageSize.getWidth();
        const pdfHeight = (canvas.height * pdfWidth) / canvas.width;

        pdf.addImage(imgData, "PNG", 0, 0, pdfWidth, pdfHeight);
        pdf.save("risk_analysis.pdf");
    }

}
RiskDashboard.template = "RiskDashboard"
registry.category("actions").add("risk_dashboard", RiskDashboard)
