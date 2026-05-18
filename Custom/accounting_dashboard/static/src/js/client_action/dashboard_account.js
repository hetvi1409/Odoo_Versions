/** @odoo-module **/
alert('File calling-->')

import { _t } from "@web/core/l10n/translation";
import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { standardActionServiceProps } from "@web/webclient/actions/action_service";
import { loadJS, loadCSS } from "@web/core/assets";
import { loadBundle } from "@web/core/assets";
import { session } from "@web/session";
import { onMounted } from "@odoo/owl";




export class AccountingDashboard extends Component {
    static template = "accounting_dashboard.accounting_dashboard_template";
    static props = { ...standardActionServiceProps };

    setup() {
        super.setup(...arguments);
        this.notification = useService("notification");
        this.orm = useService("orm");
        this.rpc = useService("rpc");

        const currentYear = new Date().getFullYear();
        const startYear = currentYear - 5;
        const endYear = currentYear + 5;

        const yearRange = [];
        for (let year = startYear; year <= endYear; year++) {
            yearRange.push(year);
        }

        this.state = useState({
            year: currentYear,
            year_range: yearRange,
            data: {
                net_profit: "Loading...",
            },
        });
        console.log('this.state--->',this.state);

        onMounted(() => {
//            this.loadNetProfit(this.state.year);
            this.loadRevenue(this.state.year);
            this.loadGrossProfit(this.state.year);
            this.loadCostOfRevenue(this.state.year);
            this.loadDepreciationExpense(this.state.year);
            this.loadExpense(this.state.year);

            this.loadRevenueVsGrossMonthly(this.state.year);

            this.loadIncomeVsExpense(this.state.year);

            this.renderCharts();
        });
    }

    async onYearChange(event) {
        // Get the selected year from the dropdown
        const selectedYear = event.target.value;
        console.log('selectedYear>>',selectedYear)
        // Update the state with the selected year
        this.state.year = selectedYear;
        console.log('this.state.year>>>',this.state.year);

        // Load the new revenue data for the selected year
        await this.loadRevenue(selectedYear);

        // Optionally, you can load other data that is related to the selected year here.
        this.loadGrossProfit(selectedYear);
        this.loadCostOfRevenue(selectedYear);
        this.loadDepreciationExpense(selectedYear);
        this.loadExpense(selectedYear);
        this.loadRevenueVsGrossMonthly(selectedYear);
        this.loadIncomeVsExpense(selectedYear);
    }

//EXPENSEEEE
    async loadExpense(year) {
        try {
            const response = await fetch(`/dashboard/expenses`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ year: year }),
            });
            const expense_result = await response.json();
            this.state.data.expense = expense_result.result.expense;
            console.log("Expense Value >>>", this.state.data.expense);
        } catch (error) {
            console.error("Failed to load Expense >>>", error);
            this.notification.add("Failed to load Expense from P&L report", { type: "danger" });
        }
    }

//DEPRECIATION EXPENSE
    async loadDepreciationExpense(year) {
        try {
            const response = await fetch(`/dashboard/depreciation`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ year: year }),
            });
            const depreciation_result = await response.json();
            this.state.data.depreciation = depreciation_result.result.depreciation;
            console.log("depreciation Value >>>", this.state.data.depreciation);
        } catch (error) {
            console.error("Failed to load depreciation >>>", error);
            this.notification.add("Failed to load depreciation from P&L report", { type: "danger" });
        }
    }


async loadRevenue(year) {
    try {
        const response = await fetch(`/dashboard/revenue`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ year: year }),  // Pass the selected year to the backend
        });
        const revenue_result = await response.json();
        this.state.data.revenue = revenue_result.result.revenue; // Fixing this line to access 'revenue'
        console.log("loadRevenue Value >>>", this.state.data.revenue);
    } catch (error) {
        console.error("Failed to load loadRevenue >>>", error);
        this.notification.add("Failed to load loadRevenue from P&L report", { type: "danger" });
    }
}



// REVENUEE
//    async loadRevenue(year) {
//            try {
//                const response = await fetch(`/dashboard/revenue`, {
//                    method: 'POST',
//                    headers: {
//                        'Content-Type': 'application/json',
//                    },
//                    body: JSON.stringify({ year: year }),
//                });
//                const revenue_result = await response.json();
//                this.state.data.revenue = revenue_result.result.revenue;
//                console.log("loadRevenue Value >>>", this.state.data.revenue);
//            } catch (error) {
//                console.error("Failed to load loadRevenue >>>", error);
//                this.notification.add("Failed to load loadRevenue from P&L report", { type: "danger" });
//            }
//        }


//*********************************************
    async loadRevenueVsGrossMonthly(year) {
        try {
            const response = await fetch(`/dashboard/revenue_vs_gross_monthly`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ year: year }),
            });

            const result = await response.json();
            const monthlyData = result.result.data;

            const labels = monthlyData.map(item => item.month);
            const revenueData = monthlyData.map(item => item.revenue);
            const grossProfitData = monthlyData.map(item => item.gross_profit);

            this.renderRevenueVsGrossMonthlyChart(labels, revenueData, grossProfitData);

        } catch (error) {
            console.error("Failed to load monthly Revenue vs Gross Profit >>>", error);
            this.notification.add("Failed to load monthly Revenue vs Gross Profit chart", { type: "danger" });
        }
    }

    renderRevenueVsGrossMonthlyChart(labels, revenueData, grossProfitData) {
        const ctx = document.getElementById("revenueGrossChart").getContext("2d");

        if (this.revenueGrossChart) {
            this.revenueGrossChart.destroy();
        }

        this.revenueGrossChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,  // ["Jan", "Feb", ..., "Dec"]
                datasets: [
                    {
                        label: "Revenue",
                        borderColor: "#007bff",
                        backgroundColor: "rgba(0,123,255,0.1)",
                        data: revenueData,
                        tension: 0.3,
                        fill: false,
                    },
                    {
                        label: "Gross Profit",
                        borderColor: "#28a745",
                        backgroundColor: "rgba(40,167,69,0.1)",
                        data: grossProfitData,
                        tension: 0.3,
                        fill: false,
                    }
                ]
            },
            options: {
                responsive: true,
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.dataset.label + ": " + context.raw.toLocaleString();
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return value.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
    }


//*************************************************************************************

    async loadIncomeVsExpense(year) {
        try {
            const response = await fetch(`/dashboard/income_vs_expense`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ year: year }),
            });

            const result = await response.json();
            const monthlyData = result.result.data;

            const labels = monthlyData.map(item => item.month);
            const incomeData = monthlyData.map(item => item.income);
            const expenseData = monthlyData.map(item => item.expense);

            this.renderIncomeVsExpenseChart(labels, incomeData, expenseData);

        } catch (error) {
            console.error("Failed to load Income vs Expense >>>", error);
            this.notification.add("Failed to load Income vs Expense chart", { type: "danger" });
        }
    }

    renderIncomeVsExpenseChart(labels, incomeData, expenseData) {
        const ctx = document.getElementById("incomeExpenseChart").getContext("2d");

        if (this.incomeExpenseChart) {
            this.incomeExpenseChart.destroy();
        }

        this.incomeExpenseChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: "Income (Gross Profit)",
                        backgroundColor: "#28a745",
                        data: incomeData,
                    },
                    {
                        label: "Expenses",
                        backgroundColor: "#dc3545",
                        data: expenseData,
                    }
                ]
            },
            options: {
                responsive: true,
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.dataset.label + ": " + context.raw.toLocaleString();
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return value.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
    }








//****************************************************************************


//OTHER INCOME
    async loadGrossProfit(year) {
            try {
                const response = await fetch(`/dashboard/other_income`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ year: year }),
                });
                const other_income_result = await response.json();
                this.state.data.other_income = other_income_result.result.other_income;
                console.log("loadGrossProfit Value >>>", this.state.data.other_income);
            } catch (error) {
                console.error("Failed to load loadGrossProfit >>>", error);
                this.notification.add("Failed to load loadGrossProfit from P&L report", { type: "danger" });
            }
        }

//Cost of Revenue
    async loadCostOfRevenue(year) {
        try {
            const response = await fetch(`/dashboard/expense_cost`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ year: year }),
            });
            const expense_cost_result = await response.json();
            this.state.data.expense_cost = expense_cost_result.result.expense_cost;
            console.log("expense_cost Value >>>", this.state.data.expense_cost);
        } catch (error) {
            console.error("Failed to load loadCostOfRevenue >>>", error);
            this.notification.add("Failed to load EXPENSE COST from P&L report", { type: "danger" });
        }
    }



//        async loadNetProfitMargin(year) {
//            try {
//                const netProfitMarginData = await this.rpc("/dashboard/net_profit_margin", {
//                    year: year,
//                });
//
//                if (netProfitMarginData.error) {
//                    console.error("Error fetching data:", netProfitMarginData.error);
//                    this.notification.add("Error fetching Net Profit Margin", { type: "danger" });
//                } else {
//                    this.state.data.net_profit_margin = netProfitMarginData.net_profit_margin;
//                    console.log("Net Profit Margin >>>", netProfitMarginData.net_profit_margin);
//
//                }
//            } catch (error) {
//                console.error("Failed to load Net Profit Margin >>>", error);
//                this.notification.add("Failed to load Net Profit Margin", { type: "danger" });
//            }
//        }




    renderCharts() {

        // Quick Ratio Gauge
        new Chart(document.getElementById("quickGauge"), {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [1.31, 2 - 1.31],  // assuming target=2
                    backgroundColor: ["#007bff", "#e9ecef"]
                }]
            },
            options: {
                rotation: -90,
                circumference: 180,
                cutout: "70%",
                plugins: { legend: { display: false } }
            }
        });

        // Current Ratio Gauge
        new Chart(document.getElementById("currentGauge"), {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [1.75, 2 - 1.75],
                    backgroundColor: ["#ffc107", "#e9ecef"]
                }]
            },
            options: {
                rotation: -90,
                circumference: 180,
                cutout: "70%",
                plugins: { legend: { display: false } }
            }
        });

        new Chart(document.getElementById("ratioLineChart"), {
            type: 'line',
            data: {
                labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
                datasets: [
                    {
                        label: "Quick Ratio",
                        borderColor: "#007bff",
                        backgroundColor: "rgba(0,123,255,0.1)",
                        data: [1.3, 1.45, 1.1, 1.7, 1.2, 1.9, 1.4, 1.8, 1.6, 1.7, 1.9, 2.0],
                        tension: 0.3,
                        fill: false
                    },
                    {
                        label: "Current Ratio",
                        borderColor: "#ffc107",
                        backgroundColor: "rgba(255,193,7,0.1)",
                        data: [1.6, 1.7, 1.5, 2.0, 1.8, 2.2, 1.9, 2.3, 2.1, 2.4, 2.5, 2.6],
                        tension: 0.3,
                        fill: false
                    }
                ]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        suggestedMax: 3
                    }
                }
            }
        });


        // Revenue vs Gross Profit (Line Chart)
//        new Chart(document.getElementById("revenueGrossChart"), {
//            type: 'line',
//            data: {
//                labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
//                datasets: [
//                    {
//                        label: "Revenue",
//                        borderColor: "#007bff",
//                        backgroundColor: "rgba(0,123,255,0.1)",
//                        data: [5.1, 3.3, 4.2, 3.8, 5.5, 6.1, 5.8, 7.2, 6.4, 7.3, 7.8, 8.1],
//                    },
//                    {
//                        label: "Gross Profit",
//                        borderColor: "#28a745",
//                        backgroundColor: "rgba(40,167,69,0.1)",
//                        data: [1.5, 1.2, 1.8, 1.7, 2.0, 2.3, 2.1, 2.6, 2.4, 2.8, 3.0, 3.2],
//                    }
//                ]
//            }
//        });

        // Revenue Target (Donut)
        new Chart(document.getElementById("revenueTargetChart"), {
            type: 'doughnut',
            data: {
                labels: ["Achieved", "Remaining"],
                datasets: [{
                    data: [90, 10],
                    backgroundColor: ["#007bff", "#e9ecef"]
                }]
            },
            options: { cutout: "70%" }
        });

        // Gross Profit Target (Donut)
        new Chart(document.getElementById("grossTargetChart"), {
            type: 'doughnut',
            data: {
                labels: ["Achieved", "Remaining"],
                datasets: [{
                    data: [87, 13],
                    backgroundColor: ["#28a745", "#e9ecef"]
                }]
            },
            options: { cutout: "70%" }
        });

        // Quick vs Current Ratio (Bar)
        new Chart(document.getElementById("ratioChart"), {
            type: 'bar',
            data: {
                labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul"],
                datasets: [
                    {
                        label: "Quick Ratio",
                        backgroundColor: "#007bff",
                        data: [1.3, 1.5, 0.9, 1.7, 1.4, 1.6, 1.2]
                    },
                    {
                        label: "Current Ratio",
                        backgroundColor: "#ffc107",
                        data: [1.7, 1.8, 1.2, 2.0, 1.9, 2.1, 1.5]
                    }
                ]
            }
        });

        // Income vs Expense (Bar)
//        new Chart(document.getElementById("incomeExpenseChart"), {
//            type: 'bar',
//            data: {
//                labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul"],
//                datasets: [
//                    {
//                        label: "Income",
//                        backgroundColor: "#28a745",
//                        data: [5.4, 4.9, 6.1, 5.8, 6.3, 6.5, 6.0]
//                    },
//                    {
//                        label: "Expenses",
//                        backgroundColor: "#dc3545",
//                        data: [3.1, 3.6, 3.9, 3.7, 4.1, 4.4, 4.0]
//                    }
//                ]
//            }
//        });
    }
}
registry.category("actions").add("accounting_dashboard.dashboard_account", AccountingDashboard);
