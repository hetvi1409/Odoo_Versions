/** @odoo-module */
import { registry } from '@web/core/registry';
import { useService } from "@web/core/utils/hooks";
const { Component, onWillStart, onMounted, useState } = owl;
import { rpc } from "@web/core/network/rpc";
import { _t } from "@web/core/l10n/translation";
import { loadJS } from "@web/core/assets";

export class ProjectDashboard extends Component {

    setup() {
        this.action = useService("action");
        this.orm = useService("orm");
        this.rpc = this.env.services.rpc
        this.state = useState({
            rowsPerPage: 5,
            currentPage: 1, totalrows: 0,
            currentempPage: 1, totalemprows: 0,
        });
        this.dashboard_links = [];
        onWillStart(this.onWillStart);
        onMounted(this.onMounted);
    }

    async onWillStart() {
        await this.fetch_data();
        await this.getGreetings();
        await loadJS("https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js");
        this.dashboard_links = await rpc("/project/dashboard/links");
    }

    async onMounted() {
        if (this.is_configured) {
            var warning = document.getElementById("AlertBox");
            warning.style.display = "none";
        }
        this.render_all_task_data(this.state.rowsPerPage, this.state.currentPage);
        this.render_upcoming_table_data(this.state.rowsPerPage, this.state.currentPage);
        this.render_project_chart_data();
        this.render_project_filter();
    }

    async getGreetings() {
        const hours = new Date().getHours();
        if (hours >= 5 && hours < 12) this.greetings = "Good Morning";
        else if (hours >= 12 && hours < 18) this.greetings = "Good Afternoon";
        else this.greetings = "Good Evening";
    }

//    downloadReport(e) {
//        window.print();
//    }

    downloadReport(e) {
        // Ensure all charts are properly drawn before print
        if (window.Chart) {
            for (const chartId in Chart.instances) {
                const chart = Chart.instances[chartId];
                if (chart) chart.resize();
            }
        }
        setTimeout(() => window.print(), 500);
    }



    _downloadChart(e) {
        // Find the canvas inside the same card
        const canvas = e.target.closest(".card").querySelector("canvas");
        if (!canvas) return;

        // Map canvas.id → chart instance (stored earlier when rendering charts)
        const chartMap = {
            "project_health_chart_data": this.projectHealthChart,
            "missing_resource_allocation_chart_data": this.missingResourceChart,
            "governance_chart_data": this.governanceChart,
            "project_cost_chart_data": this.projectCostChart,
            "stages_chart_data": this.stagesChart,
            "project_chart_data": this.projectChart,
            "project_priority_chart_data": this.priorityChart,
            "project_source_chart_data": this.sourceChart,
        };

        const chartInstance = chartMap[canvas.id];

        if (chartInstance) {
            // Export chart as PNG with full styling
            const imageDataURL = chartInstance.toBase64Image("image/png", 1);
            const filename = canvas.id + "_ProjectDashboard.png";

            const link = document.createElement("a");
            link.href = imageDataURL;
            link.download = filename;
            link.click();
        } else {
            console.warn("No chart instance found for", canvas.id);
        }
    }


    // ========== Filters ==========
    render_project_filter() {
        rpc('/all_project_filter').then((data) => {
            var projects = data[0];
            var users = data[1];
            var partners = data[2];
            var stages = data[3];
            var durations = data[4];

            projects?.forEach(p => {
                const option = document.createElement('option');
                option.value = p?.id;
                option.textContent = p?.name;
                document.querySelector('#project_selection')?.appendChild(option);
            });
            users?.forEach(u => {
                const option = document.createElement('option');
                option.value = u?.id;
                option.textContent = u?.name;
                document.querySelector('#user_selections')?.appendChild(option);
            });
            partners?.forEach(c => {
                const option = document.createElement('option');
                option.value = c?.id;
                option.textContent = c?.name;
                document.querySelector('#partner_selection')?.appendChild(option);
            });
            stages?.forEach(s => {
                const option = document.createElement('option');
                option.value = s?.id;
                option.textContent = s?.name;
                document.querySelector('#stages_selection')?.appendChild(option);
            });
            durations?.forEach(d => {
                const option = document.createElement('option');
                option.value = d?.id;
                option.textContent = d?.name;
                document.querySelector('#duration_selection')?.appendChild(option);
            });
        })
    }

    _onchangeProjectFilter(ev) {
        this.flag = 1;

        var project_selection = document.querySelector('#project_selection').value;
        var user_selections = document.querySelector('#user_selections').value;
        var partner_selection = document.querySelector('#partner_selection').value;
        var stages_selection = document.querySelector('#stages_selection').value;
        var duration_selection = document.querySelector('#duration_selection').value;

        this.render_project_chart_data();
        this.render_all_task_data(this.state.rowsPerPage, this.state.currentPage);
        this.render_upcoming_table_data(this.state.rowsPerPage, this.state.currentPage);

        var self = this;

        rpc('/project/filter-apply', {
            'data': {
                'project': project_selection,
                'user': user_selections,
                'partner': partner_selection,
                'stage': stages_selection,
                'duration': duration_selection,
            }
        }).then(function (data) {
            self.done_task_data = data['done_task_data'];
            self.closed_task_data = data['closed_task_data'];
            self.all_task_data = data['all_task_data'];
            self.open_task_data = data['open_task_data'];

            document.querySelector('#done_task_data').innerHTML = data['done_task_data'].length;
            document.querySelector('#closed_task_data').innerHTML = data['closed_task_data'].length;
            document.querySelector('#all_task_data').innerHTML = data['all_task_data'].length;
            document.querySelector('#open_task_data').innerHTML = data['open_task_data'].length;
        });
    }

    // ========== Counters ==========
    async fetch_data() {
        this.flag = 0;
        var self = this;
        const result = await rpc('/get/project/task/tiles/data');
        self.is_configured = result['is_configured'];
        self.done_task_data = result['done_task_data'];
        self.closed_task_data = result['closed_task_data'];
        self.all_task_data = result['all_task_data'];
        self.open_task_data = result['open_task_data'];
        self.user_name = result['user_name'];
        self.user_img = result['user_img'];
        return result;
    }

    action_all_task(e) {
        e.stopPropagation();
        e.preventDefault();
        var options = {};
        var action = e.currentTarget.id;
        var domain = false;

        if (action == 'done_task_data1') domain = [["id", "in", this.done_task_data]];
        else if (action == 'closed_task_data1') domain = [["id", "in", this.closed_task_data]];
        else if (action == 'all_task_data1') domain = [["id", "in", this.all_task_data]];
        else if (action == 'open_task_data1') domain = [["id", "in", this.open_task_data]];

        this.action.doAction({
            name: _t("All Tasks"),
            type: 'ir.actions.act_window',
            res_model: 'project.task',
            domain: domain,
            view_mode: 'list,form',
            views: [
                [false, 'list'],
                [false, 'form']
            ],
            target: 'current'
        }, options);
    }

    // ========== Charts ==========
    async render_project_chart_data() {
        var project_selection = document.querySelector('#project_selection').value;
        var user_selections = document.querySelector('#user_selections').value;
        var partner_selection = document.querySelector('#partner_selection').value;
        var stages_selection = document.querySelector('#stages_selection').value;
        var duration_selection = document.querySelector('#duration_selection').value;

        var stages_chart_selection = document.querySelector('#stages_chart_selection').value;
        var project_chart_selection = document.querySelector('#project_chart_selection').value;
        var priority_chart_selection = document.querySelector('#priority_chart_selection').value;
        var project_health_chart_selection = document.querySelector('#project_health_chart_selection').value;
        var governance_chart_selection = document.querySelector('#governance_chart_selection').value;
        var missing_resource_allocation_chart_selection = document.querySelector('#missing_resource_allocation_chart_selection').value;
        var project_cost_chart_selection = document.querySelector('#project_cost_chart_selection').value;

        var self = this;

        await rpc("/project/chart/data", {
            'data': {
                'project_id': project_selection,
                'user_id': user_selections,
                'partner_id': partner_selection,
                'stage_id': stages_selection,
                'duration': duration_selection,
            }
        }).then(function (data) {
            // Group By Stages
            var ctx = document.querySelector("#stages_chart_data");
            new Chart(ctx, {
                type: stages_chart_selection,
                data: data.stages_chart_data,
                options: {
                    maintainAspectRatio: false,
                    onClick: (evt, elements) => {
                        if (elements.length > 0) {
                            const element = elements[0];
                            const clickedIndex = element.index;
                            const clickedLabel = data.stages_chart_data.labels[clickedIndex];
                            const clickedValue = data.stages_chart_data.datasets[0].detail[clickedIndex];
                            self.action.doAction({
                                name: _t(clickedLabel),
                                type: 'ir.actions.act_window',
                                res_model: 'project.task',
                                domain: [["id", "in", clickedValue]],
                                view_mode: 'list,form',
                                target: 'current'
                            });
                        }
                    }
                }
            });

            // Group By Project
            var ctx2 = document.querySelector("#project_chart_data");
            new Chart(ctx2, {
                type: project_chart_selection,
                data: data.project_chart_data,
                options: {
                    maintainAspectRatio: false,
                    onClick: (evt, elements) => {
                        if (elements.length > 0) {
                            const element = elements[0];
                            const clickedIndex = element.index;
                            const clickedLabel = data.project_chart_data.labels[clickedIndex];
                            const clickedValue = data.project_chart_data.datasets[0].detail[clickedIndex];
                            self.action.doAction({
                                name: _t(clickedLabel),
                                type: 'ir.actions.act_window',
                                res_model: 'project.task',
                                domain: [["id", "in", clickedValue]],
                                view_mode: 'list,form',
                                target: 'current'
                            });
                        }
                    }
                }
            });

            // Group By Priority
            if (data.project_priority_chart_data) {
                var ctx3 = document.querySelector("#project_priority_chart_data");
                new Chart(ctx3, {
                    type: priority_chart_selection,
                    data: data.project_priority_chart_data,
                    options: {
                        maintainAspectRatio: false,
                        onClick: (evt, elements) => {
                            if (elements.length > 0) {
                                const element = elements[0];
                                const clickedIndex = element.index;
                                const clickedLabel = data.project_priority_chart_data.labels[clickedIndex];
                                const clickedValue = data.project_priority_chart_data.datasets[0].detail[clickedIndex];
                                self.action.doAction({
                                    name: _t(clickedLabel),
                                    type: 'ir.actions.act_window',
                                    res_model: 'project.task',
                                    domain: [["id", "in", clickedValue]],
                                    view_mode: 'list,form',
                                    target: 'current'
                                });
                            }
                        }
                    }
                });
            }

            // -------- Project Health --------
            if (data.health_chart_data) {
                var ctx4 = document.querySelector("#project_health_chart_data");
                if (self.projectHealthChart) { self.projectHealthChart.destroy(); }
                self.projectHealthChart = new Chart(ctx4, {
                    type: project_health_chart_selection,
                    data: data.health_chart_data,
                    options: {
                        maintainAspectRatio: false,
                        responsive: true,
                        plugins: {
                            tooltip: {
                                callbacks: {
                                    title: (items) => items[0].label,
                                    label: (context) => context.dataset.label + ": " + context.formattedValue,
                                }
                            },
                            legend: { position: 'bottom' },
                        },
                        scales: {
                            x: { stacked: true },
                            y: { stacked: true, beginAtZero: true },
                        },
                        onClick: (evt, elements) => {
                            if (elements.length > 0) {
                                const el = elements[0];
                                const datasetIndex = el.datasetIndex;
                                const index = el.index;
                                const clickedIds = data.health_chart_data.datasets[datasetIndex].detail[index];
                                const clickedLabel = data.health_chart_data.labels[index];
                                self.action.doAction({
                                    name: _t(clickedLabel),
                                    type: 'ir.actions.act_window',
                                    res_model: 'project.project',
                                    domain: [["id", "in", clickedIds]],
                                    view_mode: 'list,form',
                                    target: 'current'
                                });
                            }
                        }
                    }
                });
            }

            // -------- Governance --------
            if (data.governance_chart_data) {
                var ctx5 = document.querySelector("#governance_chart_data");
                if (self.governanceChart) { self.governanceChart.destroy(); }
                self.governanceChart = new Chart(ctx5, {
                    type: governance_chart_selection,
                    data: data.governance_chart_data,
                    options: {
                        maintainAspectRatio: false,
                        responsive: true,
                        plugins: {
                            tooltip: {
                                callbacks: {
                                    title: (items) => items[0].label,
                                    label: (context) => context.dataset.label + ": " + context.formattedValue,
                                }
                            },
                            legend: { position: 'bottom' },
                        },
                        scales: {
                            x: { stacked: true },
                            y: { stacked: true, beginAtZero: true },
                        },
                        onClick: (evt, elements) => {
                            if (elements.length > 0) {
                                const el = elements[0];
                                const datasetIndex = el.datasetIndex;
                                const index = el.index;
                                const clickedIds = data.governance_chart_data.datasets[datasetIndex].detail[index];
                                const clickedLabel = data.governance_chart_data.labels[index];
                                self.action.doAction({
                                    name: _t(clickedLabel + " Governance Projects"),
                                    type: 'ir.actions.act_window',
                                    res_model: 'project.project',
                                    domain: [["id", "in", clickedIds]],
                                    view_mode: 'list,form',
                                    target: 'current'
                                });
                            }
                        }
                    }
                });
            }
            // -------- Missing Resource Allocation --------
            if (data.missing_resource_chart_data) {
                var ctx6 = document.querySelector("#missing_resource_allocation_chart_data");
                if (self.missingResourceChart) { self.missingResourceChart.destroy(); }
                self.missingResourceChart = new Chart(ctx6, {
                    type: missing_resource_allocation_chart_selection,
                    data: data.missing_resource_chart_data,
                    options: {
                        maintainAspectRatio: false,
                        responsive: true,
                        plugins: {
                            tooltip: {
                                callbacks: {
                                    title: (items) => items[0].label,
                                    label: (context) => context.dataset.label + ": " + context.formattedValue,
                                }
                            },
                            legend: { position: 'bottom' },
                        },
                        onClick: (evt, elements) => {
                            if (elements.length > 0) {
                                const el = elements[0];
                                const index = el.index;
                                const clickedIds = data.missing_resource_chart_data.datasets[0].detail[index];
                                const clickedLabel = data.missing_resource_chart_data.labels[index];
                                self.action.doAction({
                                    name: _t(clickedLabel + " Missing Resource Projects"),
                                    type: 'ir.actions.act_window',
                                    res_model: 'project.project',
                                    domain: [["id", "in", clickedIds]],
                                    view_mode: 'list,form',
                                    target: 'current'
                                });
                            }
                        }
                    }
                });
            }

            // -------- Project Cost --------
            if (data.project_cost_chart_data) {
                var ctx7 = document.querySelector("#project_cost_chart_data");
                if (self.projectCostChart) { self.projectCostChart.destroy(); }
                self.projectCostChart = new Chart(ctx7, {
                    type: project_cost_chart_selection,
                    data: data.project_cost_chart_data,
                    options: {
                        maintainAspectRatio: false,
                        responsive: true,
                        interaction: { mode: 'index', intersect: false },
                        plugins: {
                            tooltip: {
                                callbacks: {
                                    title: (items) => items[0].label,
                                    label: (context) => context.dataset.label + ": " + context.formattedValue,
                                }
                            },
                            legend: { position: 'bottom' },
                        },
                        scales: {
                            x: { title: { display: true, text: "Month" } },
                            y: { title: { display: true, text: "Value" }, beginAtZero: true },
                        },
                        onClick: (evt, elements) => {
                            if (elements.length > 0) {
                                const el = elements[0];
                                const datasetIndex = el.datasetIndex;
                                const index = el.index;
                                const clickedIds = data.project_cost_chart_data.datasets[datasetIndex].detail[index];
                                const clickedLabel = data.project_cost_chart_data.labels[index];
                                self.action.doAction({
                                    name: _t(clickedLabel + " Project Costs"),
                                    type: 'ir.actions.act_window',
                                    res_model: 'project.cost',
                                    domain: [["id", "in", clickedIds]],
                                    view_mode: 'list,form',
                                    target: 'current'
                                });
                            }
                        }
                    }
                });
            }


        });
    }

    // ========== Tables ==========
    async render_all_task_data(rowsPerPage, page) {
        var project_selection = document.querySelector('#project_selection').value;
        var user_selections = document.querySelector('#user_selections').value;
        var partner_selection = document.querySelector('#partner_selection').value;
        var stages_selection = document.querySelector('#stages_selection').value;
        var duration_selection = document.querySelector('#duration_selection').value;
        var self = this;

        await rpc("/project/table/data", {
            'data': {
                'project_id': project_selection,
                'user_id': user_selections,
                'partner_id': partner_selection,
                'stage_id': stages_selection,
                'duration': duration_selection,
            }
        }).then(function (data) {
            var all_task_list = data['all_task_list'];
            self.state.totalrows = all_task_list.length;
            var tbody = document.querySelector("#my_table_all_task_list tbody");
            tbody.innerHTML = '';

            const start = (page - 1) * rowsPerPage;
            const end = start + rowsPerPage;
            const paginatedData = all_task_list.slice(start, end);

            paginatedData.forEach(task => {
                var row = document.createElement("tr");
                for (var key in task) {
                    if (key !== 'id') {
                        var cell = document.createElement("td");
                        if (Array.isArray(task[key])) cell.textContent = task[key][1];
                        else if (key === 'create_date') {
                            var arr1 = task[key]?.split('-');
                            cell.textContent = arr1 ? (arr1[2] + '-' + arr1[1] + '-' + arr1[0]) : '-';
                        } else {
                            cell.textContent = task[key] || '-';
                        }
                        row.appendChild(cell);
                    }
                }
                var buttonCell = document.createElement("td");
                var button = document.createElement("button");
                button.textContent = "View";
                button.setAttribute("data-id", task.id);
                button.addEventListener("click", function () {
                    var id = this.getAttribute("data-id");
                    self.action.doAction({
                        name: _t("Task"),
                        type: 'ir.actions.act_window',
                        res_model: 'project.task',
                        domain: [["id", "=", parseInt(id)]],
                        view_mode: 'list,form',
                        views: [
                            [false, 'list'],
                            [false, 'form']
                        ],
                        target: 'current'
                    });
                });
                buttonCell.appendChild(button);
                row.appendChild(buttonCell);
                tbody.appendChild(row);
            });
        });
    }

    async render_upcoming_table_data(rowsPerPage, page) {
        var project_selection = document.querySelector('#project_selection').value;
        var user_selections = document.querySelector('#user_selections').value;
        var partner_selection = document.querySelector('#partner_selection').value;
        var stages_selection = document.querySelector('#stages_selection').value;
        var duration_selection = document.querySelector('#duration_selection').value;
        var self = this;

        await rpc("/project/table/data", {
            'data': {
                'project_id': project_selection,
                'user_id': user_selections,
                'partner_id': partner_selection,
                'stage_id': stages_selection,
                'duration': duration_selection,
            }
        }).then(function (data) {
            var closing_task_list = data['closing_task_list'];
            self.state.totalemprows = closing_task_list.length;
            var tbody = document.querySelector("#my_table_closing_task_list tbody");
            tbody.innerHTML = '';

            const start = (page - 1) * rowsPerPage;
            const end = start + rowsPerPage;
            const paginatedData = closing_task_list.slice(start, end);

            paginatedData.forEach(task => {
                var row = document.createElement("tr");
                for (var key in task) {
                    if (key !== 'id') {
                        var cell = document.createElement("td");
                        if (Array.isArray(task[key])) cell.textContent = task[key][1];
                        else if (key === 'date_deadline') {
                            var arr1 = task[key]?.split('-');
                            cell.textContent = arr1 ? (arr1[2] + '-' + arr1[1] + '-' + arr1[0]) : '-';
                        } else {
                            cell.textContent = task[key] || '-';
                        }
                        row.appendChild(cell);
                    }
                }
                var buttonCell = document.createElement("td");
                var button = document.createElement("button");
                button.textContent = "View";
                button.setAttribute("data-id", task.id);
                button.addEventListener("click", function () {
                    var id = this.getAttribute("data-id");
                    self.action.doAction({
                        name: _t("Task"),
                        type: 'ir.actions.act_window',
                        res_model: 'project.task',
                        domain: [["id", "=", parseInt(id)]],
                        view_mode: 'list,form',
                        views: [
                            [false, 'list'],
                            [false, 'form']
                        ],
                        target: 'current'
                    });
                });
                buttonCell.appendChild(button);
                row.appendChild(buttonCell);
                tbody.appendChild(row);
            });
        });
    }

    // ========== Pagination ==========
    prevPage(e) {
        if (this.state.currentPage > 1) {
            this.state.currentPage--;
            this.render_all_task_data(this.state.rowsPerPage, this.state.currentPage);
            document.getElementById("next_button").disabled = false;
        }
        if (this.state.currentPage == 1) document.getElementById("prev_button").disabled = true;
        else document.getElementById("prev_button").disabled = false;
    }
    nextPage() {
        if ((this.state.currentPage * this.state.rowsPerPage) < this.state.totalrows) {
            this.state.currentPage++;
            this.render_all_task_data(this.state.rowsPerPage, this.state.currentPage);
            document.getElementById("prev_button").disabled = false;
        }
        if (Math.ceil(this.state.totalrows / this.state.rowsPerPage) == this.state.currentPage)
            document.getElementById("next_button").disabled = true;
        else document.getElementById("next_button").disabled = false;
    }

    prevsPage(e) {
        if (this.state.currentempPage > 1) {
            this.state.currentempPage--;
            this.render_upcoming_table_data(this.state.rowsPerPage, this.state.currentempPage);
            document.getElementById("nextt_button").disabled = false;
        }
        if (this.state.currentempPage == 1) document.getElementById("prevs_button").disabled = true;
        else document.getElementById("prevs_button").disabled = false;
    }
    nexttPage() {
        if ((this.state.currentempPage * this.state.rowsPerPage) < this.state.totalemprows) {
            this.state.currentempPage++;
            this.render_upcoming_table_data(this.state.rowsPerPage, this.state.currentempPage);
            document.getElementById("prevs_button").disabled = false;
        }
        if (Math.ceil(this.state.totalemprows / this.state.rowsPerPage) == this.state.currentempPage)
            document.getElementById("nextt_button").disabled = true;
        else document.getElementById("nextt_button").disabled = false;
    }

    // ----------- chart: Stages -----------
    async _onchangeStagesChart(ev) {
        var project_selection = document.querySelector('#project_selection').value;
        var user_selections = document.querySelector('#user_selections').value;
        var partner_selection = document.querySelector('#partner_selection').value;
        var stages_selection = document.querySelector('#stages_selection').value;
        var duration_selection = document.querySelector('#duration_selection').value;
        var stages_chart_selection = document.querySelector('#stages_chart_selection').value;
        var self = this;

        await rpc("/project/stages/chart/data", {
            'data': {
                'project_id': project_selection,
                'user_id': user_selections,
                'partner_id': partner_selection,
                'stage_id': stages_selection,
                'duration': duration_selection,
            }
        }).then(function (data) {
            var ctx = document.querySelector("#stages_chart_data");
            new Chart(ctx, {
                type: stages_chart_selection,
                data: data.stages_chart_data,
                options: {
                    maintainAspectRatio: false,
                    onClick: (evt, elements) => {
                        if (elements.length > 0) {
                            const element = elements[0];
                            const clickedIndex = element.index;
                            const clickedLabel = data.stages_chart_data.labels[clickedIndex];
                            const clickedValue = data.stages_chart_data.datasets[0].detail[clickedIndex];
                            self.action.doAction({
                                name: _t(clickedLabel),
                                type: 'ir.actions.act_window',
                                res_model: 'project.task',
                                domain: [["id", "in", clickedValue]],
                                view_mode: 'list,form',
                                target: 'current'
                            });
                        }
                    }
                }
            });
        });
    }

    // ----------- chart: Project -----------
    async _onchangeProjectChart(ev) {
        var project_chart_selection = document.querySelector('#project_chart_selection').value;
        var project_selection = document.querySelector('#project_selection').value;
        var user_selections = document.querySelector('#user_selections').value;
        var partner_selection = document.querySelector('#partner_selection').value;
        var stages_selection = document.querySelector('#stages_selection').value;
        var duration_selection = document.querySelector('#duration_selection').value;
        var self = this;

        await rpc("/project/project/chart/data", {
            'data': {
                'project_id': project_selection,
                'user_id': user_selections,
                'partner_id': partner_selection,
                'stage_id': stages_selection,
                'duration': duration_selection,
            }
        }).then(function (data) {
            var ctx = document.querySelector("#project_chart_data");
            new Chart(ctx, {
                type: project_chart_selection,
                data: data.project_chart_data,
                options: {
                    maintainAspectRatio: false,
                    onClick: (evt, elements) => {
                        if (elements.length > 0) {
                            const element = elements[0];
                            const clickedIndex = element.index;
                            const clickedLabel = data.project_chart_data.labels[clickedIndex];
                            const clickedValue = data.project_chart_data.datasets[0].detail[clickedIndex];
                            self.action.doAction({
                                name: _t(clickedLabel),
                                type: 'ir.actions.act_window',
                                res_model: 'project.task',
                                domain: [["id", "in", clickedValue]],
                                view_mode: 'list,form',
                                target: 'current'
                            });
                        }
                    }
                }
            });
        });
    }

    // ----------- chart: Priority -----------
    async _onchangePriorityChart(ev) {
        var priority_chart_selection = document.querySelector('#priority_chart_selection').value;
        var project_selection = document.querySelector('#project_selection').value;
        var user_selections = document.querySelector('#user_selections').value;
        var partner_selection = document.querySelector('#partner_selection').value;
        var stages_selection = document.querySelector('#stages_selection').value;
        var duration_selection = document.querySelector('#duration_selection').value;
        var self = this;

        await rpc("/project/priority/chart/data", {
            'data': {
                'project_id': project_selection,
                'user_id': user_selections,
                'partner_id': partner_selection,
                'stage_id': stages_selection,
                'duration': duration_selection,
            }
        }).then(function (data) {
            var ctx = document.querySelector("#project_priority_chart_data");
            new Chart(ctx, {
                type: priority_chart_selection,
                data: data.project_priority_chart_data,
                options: {
                    maintainAspectRatio: false,
                    onClick: (evt, elements) => {
                        if (elements.length > 0) {
                            const element = elements[0];
                            const clickedIndex = element.index;
                            const clickedLabel = data.project_priority_chart_data.labels[clickedIndex];
                            const clickedValue = data.project_priority_chart_data.datasets[0].detail[clickedIndex];
                            self.action.doAction({
                                name: _t(clickedLabel),
                                type: 'ir.actions.act_window',
                                res_model: 'project.task',
                                domain: [["id", "in", clickedValue]],
                                view_mode: 'list,form',
                                target: 'current'
                            });
                        }
                    }
                }
            });
        });
    }
    // ----------- chart: Source -----------
    async _onchangeSourceChart(ev) {
        var source_chart_selection = document.querySelector('#source_chart_selection').value;  // FIXED
        var project_selection = document.querySelector('#project_selection').value;
        var user_selections = document.querySelector('#user_selections').value;
        var partner_selection = document.querySelector('#partner_selection').value;
        var stages_selection = document.querySelector('#stages_selection').value;
        var duration_selection = document.querySelector('#duration_selection').value;
        var self = this;

        await rpc("/project/source/chart/data", {
            'data': {
                'project_id': project_selection,
                'user_id': user_selections,
                'partner_id': partner_selection,
                'stage_id': stages_selection,
                'duration': duration_selection,
            }
        }).then(function (data) {
            var ctx = document.querySelector("#project_source_chart_data");
            new Chart(ctx, {
                type: source_chart_selection,
                data: data.project_source_chart_data,
                options: {
                    maintainAspectRatio: false,
                    onClick: (evt, elements) => {
                        if (elements.length > 0) {
                            const element = elements[0];
                            const clickedIndex = element.index;
                            const clickedLabel = data.project_source_chart_data.labels[clickedIndex];
                            const clickedValue = data.project_source_chart_data.datasets[0].detail[clickedIndex];
                            self.action.doAction({
                                name: _t(clickedLabel),
                                type: 'ir.actions.act_window',
                                res_model: 'project.task',
                                domain: [["id", "in", clickedValue]],
                                view_mode: 'list,form',
                                target: 'current'
                            });
                        }
                    }
                }
            });
        });
    }

    async load_links_data() {
        const res = await rpc("/project/dashboard/links");
        this.dashboard_links = res || [];
        this.render();
    }

    openLinksWizard(ev) {
        this.action.doAction("project_porfolio_management.action_project_dashboard_link_wizard");
    }

    async _onchangeProjectHealthChart(ev) {
        var project_selection = document.querySelector('#project_selection').value;
        var user_selections = document.querySelector('#user_selections').value;
        var partner_selection = document.querySelector('#partner_selection').value;
        var stages_selection = document.querySelector('#stages_selection').value;
        var duration_selection = document.querySelector('#duration_selection').value;
        var chart_type = document.querySelector('#project_health_chart_selection').value;
        var self = this;
        console.log("\n\n==project_selection==",project_selection)
        await rpc("/project/health/chart/data", {
            'data': {
                'project_id': project_selection,
                'user_id': user_selections,
                'partner_id': partner_selection,
                'stage_id': stages_selection,
                'duration': duration_selection,
            }
        }).then(function (data) {
            var ctx = document.querySelector("#project_health_chart_data");
            if (self.projectHealthChart) {
                self.projectHealthChart.destroy();
            }
            self.projectHealthChart = new Chart(ctx, {
                type: chart_type,
                data: data.health_chart_data,
                options: {
                    maintainAspectRatio: false,
                    responsive: true,
                    plugins: {
                        tooltip: {
                            callbacks: {
                                title: function (tooltipItems) {
                                    return tooltipItems[0].label; // manager name
                                },
                                label: function (context) {
                                    return context.dataset.label + ": " + context.formattedValue;
                                }
                            }
                        },
                        legend: { position: 'bottom' },
                    },
                    scales: {
                        x: { stacked: true },
                        y: { stacked: true, beginAtZero: true },
                    },
                    onClick: (evt, elements) => {
                        if (elements.length > 0) {
                            const el = elements[0];
                            const datasetIndex = el.datasetIndex;
                            const index = el.index;
                            const clickedIds = data.health_chart_data.datasets[datasetIndex].detail[index];
                            const clickedLabel = data.health_chart_data.labels[index];
                            self.action.doAction({
                                name: _t(clickedLabel),
                                type: 'ir.actions.act_window',
                                res_model: 'project.project',
                                domain: [["id", "in", clickedIds]],
                                view_mode: 'list,form',
                                target: 'current'
                            });
                        }
                    }
                }
            });
        });
    }

    async _onchangeGovernanceChart(ev) {
        var project_selection = document.querySelector('#project_selection').value;
        var user_selections = document.querySelector('#user_selections').value;
        var partner_selection = document.querySelector('#partner_selection').value;
        var stages_selection = document.querySelector('#stages_selection').value;
        var duration_selection = document.querySelector('#duration_selection').value;
        var chart_type = document.querySelector('#governance_chart_selection').value;
        var self = this;

        await rpc("/project/governance/chart/data", {
            'data': {
                'project_id': project_selection,
                'user_id': user_selections,
                'partner_id': partner_selection,
                'stage_id': stages_selection,
                'duration': duration_selection,
            }
        }).then(function (data) {
            var ctx = document.querySelector("#governance_chart_data");
            if (self.governanceChart) {
                self.governanceChart.destroy();
            }
            self.governanceChart = new Chart(ctx, {
                type: chart_type,
                data: data.governance_chart_data,
                options: {
                    maintainAspectRatio: false,
                    responsive: true,
                    plugins: {
                        tooltip: {
                            callbacks: {
                                title: function (tooltipItems) {
                                    return tooltipItems[0].label; // Manager name
                                },
                                label: function (context) {
                                    return context.dataset.label + ": " + context.formattedValue;
                                }
                            }
                        },
                        legend: { position: 'bottom' },
                    },
                    scales: {
                        x: { stacked: true },
                        y: { stacked: true, beginAtZero: true },
                    },
                    onClick: (evt, elements) => {
                        if (elements.length > 0) {
                            const el = elements[0];
                            const datasetIndex = el.datasetIndex;
                            const index = el.index;
                            const clickedIds = data.governance_chart_data.datasets[datasetIndex].detail[index];
                            const clickedLabel = data.governance_chart_data.labels[index];
                            self.action.doAction({
                                name: _t(clickedLabel + " Governance Projects"),
                                type: 'ir.actions.act_window',
                                res_model: 'project.project',
                                domain: [["id", "in", clickedIds]],
                                view_mode: 'list,form',
                                target: 'current'
                            });
                        }
                    }
                }
            });
        });
    }

    async _onchangeMissingResourceAllocationChart(ev) {
        var project_selection = document.querySelector('#project_selection').value;
        var user_selections = document.querySelector('#user_selections').value;
        var partner_selection = document.querySelector('#partner_selection').value;
        var stages_selection = document.querySelector('#stages_selection').value;
        var duration_selection = document.querySelector('#duration_selection').value;
        var chart_type = document.querySelector('#missing_resource_allocation_chart_selection').value;
        var self = this;

        await rpc("/project/missing/resource/chart/data", {
            'data': {
                'project_id': project_selection,
                'user_id': user_selections,
                'partner_id': partner_selection,
                'stage_id': stages_selection,
                'duration': duration_selection,
            }
        }).then(function (data) {
            var ctx = document.querySelector("#missing_resource_allocation_chart_data");
            new Chart(ctx, {
                type: chart_type,
                data: data.missing_resource_chart_data,
                options: {
                    maintainAspectRatio: false,
                    onClick: (evt, elements) => {
                        if (elements.length > 0) {
                            const element = elements[0];
                            const clickedIndex = element.index;
                            const clickedLabel = data.missing_resource_chart_data.labels[clickedIndex];
                            const clickedValue = data.missing_resource_chart_data.datasets[0].detail[clickedIndex];
                            self.action.doAction({
                                name: _t(clickedLabel),
                                type: 'ir.actions.act_window',
                                res_model: 'project.project',
                                domain: [["id", "in", clickedValue]],
                                view_mode: 'list,form',
                                target: 'current'
                            });
                        }
                    }
                }
            });
        });
    }

    async _onchangeProjectCostChart(ev) {
        var project_selection = document.querySelector('#project_selection').value;
        var user_selections = document.querySelector('#user_selections').value;
        var partner_selection = document.querySelector('#partner_selection').value;
        var stages_selection = document.querySelector('#stages_selection').value;
        var duration_selection = document.querySelector('#duration_selection').value;
        var chart_type = document.querySelector('#project_cost_chart_selection').value || "line";
        var self = this;

        await rpc("/project/cost/chart/data", {
            'data': {
                'project_id': project_selection,
                'user_id': user_selections,
                'partner_id': partner_selection,
                'stage_id': stages_selection,
                'duration': duration_selection,
            }
        }).then(function (data) {
            var ctx = document.querySelector("#project_cost_chart_data");
            if (self.projectCostChart) {
                self.projectCostChart.destroy();
            }
            self.projectCostChart = new Chart(ctx, {
                type: chart_type,
                data: data.project_cost_chart_data,
                options: {
                    maintainAspectRatio: false,
                    responsive: true,
                    interaction: { mode: 'index', intersect: false },
                    plugins: {
                        tooltip: {
                            callbacks: {
                                title: (tooltipItems) => tooltipItems[0].label,
                                label: (context) => context.dataset.label + ": " + context.formattedValue,
                            }
                        },
                        legend: { position: 'bottom' },
                    },
                    scales: {
                        x: { title: { display: true, text: "Month" } },
                        y: { title: { display: true, text: "Value" }, beginAtZero: true },
                    },
                    // ✅ OnClick: open related project.cost records
                    onClick: (evt, elements) => {
                        if (elements.length > 0) {
                            const el = elements[0];
                            const datasetIndex = el.datasetIndex;
                            const index = el.index;
                            const clickedIds = data.project_cost_chart_data.datasets[datasetIndex].detail[index];
                            const clickedLabel = data.project_cost_chart_data.labels[index];
                            if (clickedIds && clickedIds.length > 0) {
                                self.action.doAction({
                                    name: _t(clickedLabel + " Project Costs"),
                                    type: 'ir.actions.act_window',
                                    res_model: 'project.cost',
                                    domain: [["id", "in", clickedIds]],
                                    view_mode: 'list,form',
                                    target: 'current'
                                });
                            }
                        }
                    }
                }
            });
        });
    }

}

ProjectDashboard.template = "projecttaskdashboard";
registry.category("actions").add("open_project_dashboard", ProjectDashboard);
