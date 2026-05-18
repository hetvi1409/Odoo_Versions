/** @odoo-module **/

import { Component, onMounted, useRef } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class AssetDashboard extends Component {
    static template = "Dashboard";

    setup() {
        this.orm = useService("orm");
        this.rootRef = useRef("root");

        onMounted(() => {
            // DOM + AssetTable are READY here
            this.renderAll();
        });
    }

    // ------------------------------------------------------------
    async renderAll() {
        await this.renderMovableAsset();
        await this.renderMovableAssetGraph();
        await this.renderOverallVerification();
        await this.renderAssetVerificationNumber();
        await this.renderAssetVerificationCarryingValue();
        await this.renderConditionAsset();
        await this.renderAssetVerified();
        await this.renderAssetVerifiedCondition();
        await this.renderAssetVerificationProgress();
        await this.renderAssetVerificationLocation();
//        await this.renderAssetType();
    }

    get root() {
        return this.rootRef.el;

    }

    // ------------------------------------------------------------
    async renderMovableAsset() {
        const tbody = this.rootRef.el?.querySelector("#movable_asset tbody");
        // undefined check
        if (!tbody) return;

        const result = await this.orm.call(
            "account.asset",
            "get_movable_asset_details",
            []
        );
        console.log('RESULT>>>',result);

        tbody.innerHTML = "";
        result.forEach(r => {
            tbody.insertAdjacentHTML(
                "beforeend",
                `<tr>
                    <td>${r[0]}</td>
                    <td>${r[1]}</td>
                    <td>${r[2].toLocaleString()}</td>
                </tr>`
            );
        });
    }

    async renderMovableAssetGraph() {
        const canvas = this.root?.querySelector("#canvas_movable");
        if (!canvas) return;

        const result = await this.orm.call(
            "account.asset",
            "get_movable_asset_graph_details",
            []
        );
        // console.log('renderMovableAssetGraph--RESULT>>>',result);

        new Chart(canvas, {
            type: "bar",
            data: {
                labels: result.category,
                datasets: [{
                    label: "Carrying value",
                    data: result.sum,
                    // give here dynamic colors
                    backgroundColor: "#003f5c",
                }],
            },
            options: { responsive: true, maintainAspectRatio: false },
        });
    }

    async renderOverallVerification() {
        const tbody = this.root?.querySelector("#overall_verification tbody");
        if (!tbody) return;

        const result = await this.orm.call(
            "account.asset",
            "get_overall_movable_asset_details",
            []
        );
        console.log('overall_verification RESULT>>>',result);

        tbody.innerHTML = "";
        result.forEach(r => {
            tbody.insertAdjacentHTML(
                "beforeend",
                `<tr>
                    <td>${r[0]}</td>
                    <td>${r[1]}</td>
                    <td>${r[2].toLocaleString()}</td>
                    <td>${r[3]}</td>
                    <td>${r[4].toLocaleString()}</td>
                    <td>${r[5]}</td>
                    <td>${r[6].toLocaleString()}</td>
                </tr>`
            );
        });
    }

    async renderAssetVerificationNumber() {
        const canvas = this.root?.querySelector("#asset_verification_number");
        if (!canvas) return;

        const result = await this.orm.call(
            "account.asset",
            "get_asset_verification_number",
            []
        );

        new Chart(canvas, {
            type: "pie",
            data: {
                labels: ["Verified", "Not Verified"],
                datasets: [{
                    data: Object.values(result.value),
                    backgroundColor: ["#f95d6a", "#2f4b7c"],
                }],
            },
        });
    }

    async renderAssetVerificationCarryingValue() {
        const canvas = this.root?.querySelector(
            "#asset_verification_carrying_value"
        );
        if (!canvas) return;

        const result = await this.orm.call(
            "account.asset",
            "get_asset_verification_carrying_value",
            []
        );
        console.log('renderAssetVerificationCarryingValue RESULT>>>', result);

        if (canvas._chartInstance) {
            canvas._chartInstance.destroy();
        }

        const chart = new Chart(canvas.getContext("2d"), {
            type: "pie",
            data: {
                labels: ["Verified", "Not Verified"],
                datasets: [{
                    data: Object.values(result.value),
                    backgroundColor: ["#ffa600", "#665191"],
                    borderWidth: 1,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false, // 🔥 MOST IMPORTANT
                plugins: {
                    legend: {
                        position: "bottom",
                    },
                    tooltip: {
                        enabled: true,
                    },
                },
            },
        });

        // store instance for cleanup
        canvas._chartInstance = chart;
    }


    async renderConditionAsset() {
        const canvas = this.root?.querySelector("#condition_asset");
        if (!canvas) return;

        const result = await this.orm.call(
            "account.asset",
            "get_graph_condition_asset",
            []
        );

        new Chart(canvas, {
            type: "pie",
            data: {
                labels: result.condition,
                datasets: [{
                    data: result.count,
                    backgroundColor: ["#003f5c", "#bc5090", "#ffa600"],
                }],
            },
        });
    }

    async renderAssetVerified() {
        const canvas = this.root?.querySelector("#graph_asset_verified");
        if (!canvas) return;

        const result = await this.orm.call(
            "account.asset",
            "get_asset_not_verified",
            []
        );
        // console.log('NOT ASSET VERIFIED RESULT>>>', result);

        new Chart(canvas, {
            type: "bar",
            data: {
                labels: result.categ,
                datasets: [
                {
                    label: "Not Verified Count",
                    data: result.count,
                    backgroundColor: "#bc5090",
                }
                ],
            },
        });
    }

    async renderAssetVerifiedCondition() {
        const canvas = this.root?.querySelector("#graph_asset_verified_condition");
        if (!canvas) return;

        const result = await this.orm.call(
            "account.asset",
            "get_asset_verified_condition",
            []
        );
        console.log('renderAssetVerifiedCondition RESULT>>>', result);

        new Chart(canvas, {
            type: "bar",
            data: {
                labels: result.condition,
                datasets: [{
                    label: "Count",
                    data: result.count,
                    // data: ['45', '30', '25', '15', '10'],
                    backgroundColor: "#ff6361",
                }],
            },
        });
    }


    async renderAssetVerificationProgress() {
        const canvas = this.root?.querySelector("#graph_asset_verification_progress");
        if (!canvas) return;

        const result = await this.orm.call(
            "account.asset",
            "get_asset_verification_progress",
            []
        );
        console.log('renderAssetVerificationProgress RESULT>>>', result);

        new Chart(canvas, {
            type: "bar",
            data: {
                labels: ["Assets"],
                datasets: [
                    {
                        label: "Movable Assets",
                        data: [result.movable_assets],
                        backgroundColor: "#2f4b7c",
                    },
                    {
                        label: "Immovable Assets",
                        data: [result.immovable_assets],
                        backgroundColor: "#f95d6a",
                    },
                    {
                        label: "Intangible Assets",
                        data: [result.intangible_assets],
                        backgroundColor: "#ffa600",
                    },
                ],
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: "top",
                    },
                },
                scales: {
                    y: {
                        beginAtZero: true,
                    },
                },
            },
        });
    }



    async renderAssetVerificationLocation() {
        const canvas = this.root?.querySelector("#graph_asset_verification_location");
        if (!canvas) return;

        const result = await this.orm.call(
            "account.asset",
            "get_asset_verification_location",
            []
        );
        // console.log('location RESULT>>>', result);

        new Chart(canvas, {
            type: "bar",
            data: {
                labels: result.location,
                datasets: [
                    {
                        label: "Verified Assets",
                        data: result.count_verified,
                        backgroundColor: "#003f5c",
                    },
                    {
                        label: "Non-Verified Assets",
                        data: result.count,
                        backgroundColor: "#7a7a7a",
                    },
                ],
            },
            options: {
                responsive: true,
                scales: {
                    x: {
                        ticks: {
                            maxRotation: 90,  // Rotate labels 90 degrees if needed
                            minRotation: 45,  // Minimum rotation if needed
                        },
                    },
                },
            },
        });
    }



    async renderAssetType() {
        const canvas = this.root?.querySelector("#asset_type");
        if (!canvas) return;

        const result = await this.orm.call(
            "account.asset",
            "get_asset_type",
            []
        );
        console.log('renderAssetType RESULT>>>', result);

        if (canvas._chartInstance) {
            canvas._chartInstance.destroy();
        }

        const chart = new Chart(canvas.getContext("2d"), {
            type: "pie",
            data: {
                labels: ["Minor Assets", "Major Assets"],
                datasets: [{
                    data: Object.values(result.value),
                    backgroundColor: ["#008000", "#800080"],
                    borderWidth: 1,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: "bottom",
                    },
                    tooltip: {
                        enabled: true,
                    },
                },
            },
        });

        // store instance for cleanup
        canvas._chartInstance = chart;
    }








}

// ------------------------------------------------------------
registry.category("actions").add("asset_dashboard", AssetDashboard);
