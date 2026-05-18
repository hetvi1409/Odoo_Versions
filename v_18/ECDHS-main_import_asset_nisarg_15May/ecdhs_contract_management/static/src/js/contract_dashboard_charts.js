/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onMounted, onWillUnmount, onPatched, useRef } from "@odoo/owl";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

const CHART_JS_URL = "https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js";

let _chartJsPromise = null;

function loadChartJs() {
    if (_chartJsPromise) return _chartJsPromise;
    if (window.Chart) {
        _chartJsPromise = Promise.resolve(window.Chart);
        return _chartJsPromise;
    }
    _chartJsPromise = new Promise((resolve, reject) => {
        const script = document.createElement("script");
        script.src = CHART_JS_URL;
        script.onload = () => resolve(window.Chart);
        script.onerror = () => reject(new Error("Failed to load Chart.js"));
        document.head.appendChild(script);
    });
    return _chartJsPromise;
}

export class ContractChartField extends Component {
    static template = "ecdhs_contract_management.ContractChartField";
    static props = { ...standardFieldProps };

    setup() {
        this.canvasRef = useRef("canvas");
        this.chart = null;
        onMounted(() => this._renderChart());
        onPatched(() => { this._destroyChart(); this._renderChart(); });
        onWillUnmount(() => this._destroyChart());
    }

    _destroyChart() {
        if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }

    async _renderChart() {
        const raw = this.props.record.data[this.props.name];
        if (!raw || !this.canvasRef.el) return;

        let config;
        try { config = JSON.parse(raw); } catch { return; }

        let Chart;
        try { Chart = await loadChartJs(); } catch { return; }
        if (!Chart || !this.canvasRef.el) return;

        const defaultOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: "bottom", labels: { boxWidth: 12, padding: 10, font: { size: 11 } } },
            },
        };
        const options = Object.assign({}, defaultOptions, config.options || {});
        if (config.options?.plugins) Object.assign(options.plugins, config.options.plugins);
        if (config.options?.scales) options.scales = config.options.scales;

        this.chart = new Chart(this.canvasRef.el.getContext("2d"), {
            type: config.type,
            data: config.data,
            options,
        });
    }
}

ContractChartField.supportedTypes = ["char"];

registry.category("fields").add("contract_chart", {
    component: ContractChartField,
    supportedTypes: ["char"],
});


    static props = { ...standardFieldProps };

    setup() {
        this.canvasRef = useRef("canvas");
        this.chart = null;

        onMounted(() => this._renderChart());
        onPatched(() => this._refreshChart());
        onWillUnmount(() => this._destroyChart());
    }

    _destroyChart() {
        if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }

    _refreshChart() {
        this._destroyChart();
        this._renderChart();
    }

    async _renderChart() {
        const rawJson = this.props.record.data[this.props.name];
        if (!rawJson || !this.canvasRef.el) return;

        let config;
        try {
            config = JSON.parse(rawJson);
        } catch (e) {
            console.warn("[ContractChartField] Invalid JSON in field", this.props.name, e);
            return;
        }

        let Chart;
        try {
            Chart = await ensureChart();
        } catch (e) {
            console.warn("[ContractChartField] Chart.js not available:", e);
            return;
        }

        if (!Chart || !this.canvasRef.el) return;

        const baseOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: "bottom",
                    labels: { boxWidth: 12, padding: 10, font: { size: 11 } },
                },
            },
        };

        const mergedOptions = Object.assign({}, baseOptions, config.options || {});
        if (config.options && config.options.plugins) {
            mergedOptions.plugins = Object.assign({}, baseOptions.plugins, config.options.plugins);
        }
        if (config.options && config.options.scales) {
            mergedOptions.scales = config.options.scales;
        }

        const ctx = this.canvasRef.el.getContext("2d");
        this.chart = new Chart(ctx, {
            type: config.type,
            data: config.data,
            options: mergedOptions,
        });
    }
}

ContractChartField.supportedTypes = ["char"];

registry.category("fields").add("contract_chart", {
    component: ContractChartField,
    supportedTypes: ["char"],
});
