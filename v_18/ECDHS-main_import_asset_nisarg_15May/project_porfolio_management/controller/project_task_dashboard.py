# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo Project Task Dashboard
#
##############################################################################

import itertools
import operator
from operator import itemgetter
from datetime import date, timedelta
from odoo import http
from odoo.http import request
from collections import defaultdict
import calendar


class ProjectTaskDashboard(http.Controller):
    """Dashboard controller for Project Tasks."""

    # ================= Filters ===========================
    @http.route('/all_project_filter', auth='public', type='json')
    def all_project_filter(self):
        project_list, user_list, partner_list, stages_list = [], [], [], []

        project_ids = request.env['project.project'].search([])
        user_ids = request.env['res.users'].search([])
        partner_ids = request.env['res.partner'].search([])
        stages_ids = request.env['project.task.type'].search([])

        for project in project_ids:
            project_list.append({'name': project.name, 'id': project.id})
        for user in user_ids:
            user_list.append({'name': user.name, 'id': user.id})
        for partner in partner_ids:
            partner_list.append({'name': partner.name, 'id': partner.id})
        for stage in stages_ids:
            stages_list.append({'name': stage.name, 'id': stage.id})
        return [project_list, user_list, partner_list, stages_list]

    # ================= Tiles ===========================
    @http.route('/get/project/task/tiles/data', auth='public', type='json')
    def get_project_tiles_data(self, **kwargs):
        today = date.today()
        all_domain, closing_domain = [], []

        if not kwargs.get('duration'):
            all_domain = [('create_date', '>=', today), ('create_date', '<=', today)]
            closing_domain = [('date_deadline', '=', today)]

        if kwargs:
            if kwargs.get('project_id') and kwargs['project_id'] != 'all':
                project_id = int(kwargs['project_id'])
                all_domain += [('project_id', '=', project_id)]
                closing_domain += [('project_id', '=', project_id)]

            if kwargs.get('user_id') and kwargs['user_id'] != 'all':
                user_id = int(kwargs['user_id'])
                all_domain += [('user_ids', 'in', [user_id])]
                closing_domain += [('user_ids', 'in', [user_id])]

            if kwargs.get('partner_id') and kwargs['partner_id'] != 'all':
                partner_id = int(kwargs['partner_id'])
                all_domain += [('partner_id', '=', partner_id)]
                closing_domain += [('partner_id', '=', partner_id)]

            if kwargs.get('stage_id') and kwargs['stage_id'] != 'all':
                stage_id = int(kwargs['stage_id'])
                all_domain += [('stage_id', '=', stage_id)]
                closing_domain += [('stage_id', '=', stage_id)]

            if kwargs.get('duration') and kwargs['duration'] != "all":
                duration = int(kwargs['duration'])
                filter_date = today - timedelta(days=duration)
                all_domain += [('create_date', '>=', filter_date), ('create_date', '<=', today)]
                closing_domain += [('create_date', '>=', filter_date), ('create_date', '<=', today)]

        user_name = request.env.user.name
        user_img = request.env.user.image_1920

        task_ids = request.env['project.task'].search(all_domain)
        closing_task_ids = request.env['project.task'].search(closing_domain)

        open_task_data, done_task_data, closed_task_data = [], [], []

        for task in task_ids:
            if task.stage_id.fold:  # folded stage = done
                done_task_data.append(task.id)
            else:
                open_task_data.append(task.id)

        for c_task in closing_task_ids:
            closed_task_data.append(c_task.id)

        return {
            'is_configured': True,
            'done_task_data': done_task_data,
            'closed_task_data': closed_task_data,
            'all_task_data': task_ids.ids or [],
            'open_task_data': open_task_data,
            'user_img': user_img,
            'user_name': user_name
        }

    # ================= Charts ===========================
    @http.route('/project/chart/data', auth='public', type='json')
    def get_project_chart_data(self, **kw):
        data = kw['data']
        today = date.today()
        domain = []

        if not data.get('duration'):
            domain = [('create_date', '>=', today), ('create_date', '<=', today)]

        if data:
            if data.get('project_id') and data['project_id'] != 'all':
                domain += [('project_id', '=', int(data['project_id']))]
            if data.get('user_id') and data['user_id'] != 'all':
                domain += [('user_ids', 'in', [int(data['user_id'])])]
            if data.get('partner_id') and data['partner_id'] != 'all':
                domain += [('partner_id', '=', int(data['partner_id']))]
            if data.get('stage_id') and data['stage_id'] != 'all':
                domain += [('stage_id', '=', int(data['stage_id']))]
            if data.get('duration') and data['duration'] != "all":
                duration = int(data['duration'])
                filter_date = today - timedelta(days=duration)
                domain += [('create_date', '>=', filter_date), ('create_date', '<=', today)]

        all_color_list = ['#00daa3', '#f06c67', '#0c9fa1', '#cf9ab5', '#bce459', '#3f8eae',
                          '#ed843f', '#00c4aa', '#966ca2', '#e2d65e', '#d56e80', '#c99a5c',
                          '#61e180', '#bf784b', '#fec863', '#7269ad']

        # ----------- Stage chart -----------
        stage_label, stage_values, stage_ids = [], [], []
        task_stage_data = request.env['project.task'].search_read(domain, fields=['stage_id'])
        # Normalize missing stage_id
        for entry in task_stage_data:
            if not entry['stage_id']:
                entry['stage_id'] = (0, 'Unassigned')
        n_lines = sorted(task_stage_data, key=itemgetter('stage_id'))
        groups = itertools.groupby(n_lines, key=operator.itemgetter('stage_id'))
        lines = [{'stage_id': k, 'values': [x for x in v]} for k, v in groups]

        for line in lines:
            stage_label.append(line.get('stage_id')[1] if line.get('stage_id') else 'Unassigned')
            stage_values.append(len(line.get('values')))
            stage_ids.append([x['id'] for x in line['values']])

        stages_chart_data = {
            'labels': stage_label,
            'datasets': [{
                'label': "Stages",
                'backgroundColor': all_color_list[:len(stage_label)],
                'data': stage_values,
                'detail': stage_ids
            }]
        }

        # ----------- Project chart -----------
        project_label, project_values, project_ids = [], [], []
        project_data = request.env['project.task'].search_read(domain, fields=['project_id'])
        # Normalize missing project_id
        for entry in project_data:
            if not entry['project_id']:
                entry['project_id'] = (0, 'Unassigned')
        n_lines = sorted(project_data, key=itemgetter('project_id'))
        groups = itertools.groupby(n_lines, key=operator.itemgetter('project_id'))
        lines = [{'project_id': k, 'values': [x for x in v]} for k, v in groups]

        for line in lines:
            project_label.append(line.get('project_id')[1] if line.get('project_id') else 'Unassigned')
            project_values.append(len(line.get('values')))
            project_ids.append([x['id'] for x in line['values']])

        project_chart_data = {
            'labels': project_label,
            'datasets': [{
                'label': "Projects",
                'backgroundColor': all_color_list[:len(project_label)],
                'data': project_values,
                'detail': project_ids
            }]
        }

        # ----------- Priority chart -----------
        low, medium, high, very_high = [], [], [], []
        for task in request.env['project.task'].search(domain):
            if task.priority == '0':
                low.append(task.id)
            elif task.priority == '1':
                medium.append(task.id)
            elif task.priority == '2':
                high.append(task.id)
            elif task.priority == '3':
                very_high.append(task.id)

        priority_chart_data = {
            'labels': ['Low', 'Medium', 'High', 'Very High'],
            'datasets': [{
                'label': "Priority",
                'backgroundColor': all_color_list[:4],
                'data': [len(low), len(medium), len(high), len(very_high)],
                'detail': [low, medium, high, very_high]
            }]
        }

        # ----------- Health chart -----------
        rag_map = {
            'done': ('Green', '#28a745'),
            'normal': ('Amber', '#ffc107'),
            'blocked': ('Red', '#dc3545'),
        }
        health_domain = list(domain)
        projects = request.env['project.project'].sudo().search_read(
            health_domain, fields=['health_indicator', 'project_manager_id']
        )
        from collections import defaultdict
        manager_map = defaultdict(lambda: {'done': [], 'normal': [], 'blocked': []})
        for proj in projects:
            manager = proj['project_manager_id'][1] if proj['project_manager_id'] else "Unknown"
            hi = proj['health_indicator']
            if hi in ['done', 'normal', 'blocked']:
                manager_map[manager][hi].append(proj['id'])
        managers = list(manager_map.keys())
        health_datasets = []
        for key, (label, color) in rag_map.items():
            health_datasets.append({
                'label': label,
                'backgroundColor': color,
                'data': [len(manager_map[m][key]) for m in managers],
                'detail': [manager_map[m][key] for m in managers],
            })
        health_chart_data = {
            'labels': managers,
            'datasets': health_datasets,
        }

        # ----------- Governance chart -----------
        gov_domain = list(domain)
        projects = request.env['project.project'].sudo().search(gov_domain)
        manager_map = {}
        for project in projects:
            manager = project.project_manager_id.name if project.project_manager_id else "Unknown"
            if manager not in manager_map:
                manager_map[manager] = {'done': [], 'normal': [], 'blocked': []}
            for gov in project.governance_requirements_ids:
                if gov.rag in ['done', 'normal', 'blocked']:
                    manager_map[manager][gov.rag].append(project.id)
        managers = list(manager_map.keys())
        governance_datasets = []
        for key, (label, color) in rag_map.items():
            governance_datasets.append({
                'label': label,
                'backgroundColor': color,
                'data': [len(set(manager_map[m][key])) for m in managers],
                'detail': [list(set(manager_map[m][key])) for m in managers],
            })
        governance_chart_data = {
            'labels': managers,
            'datasets': governance_datasets,
        }

        # ----------- Missing Resource Allocation chart -----------
        projects = request.env['project.project'].sudo().search(domain)

        missing_manager_map = {}
        for project in projects:
            if not project.resource_allocations_ids:  # Only projects without resources
                manager = project.project_manager_id.name if project.project_manager_id else "Unknown"
                if manager not in missing_manager_map:
                    missing_manager_map[manager] = []
                missing_manager_map[manager].append(project.id)

        missing_labels = list(missing_manager_map.keys())
        missing_values = [len(missing_manager_map[m]) for m in missing_labels]
        missing_details = [missing_manager_map[m] for m in missing_labels]

        missing_resource_chart_data = {
            'labels': missing_labels,
            'datasets': [{
                'label': "Missing Resource Allocation",
                'backgroundColor': all_color_list[:len(missing_labels)],
                'data': missing_values,
                'detail': missing_details,
            }]
        }

        # ----------- Project Cost S-Curve -----------
        cost_domain = list(domain)
        costs = request.env['project.cost'].sudo().search(cost_domain)



        # Group costs by Year-Month
        monthly_data = defaultdict(lambda: {'budget': 0.0, 'spent': 0.0, 'tac': 0.0, 'ids': []})
        for cost in costs:
            if not (cost.year and cost.month):
                continue
            label = f"{calendar.month_abbr[int(cost.month)]} '{str(cost.year)[2:]}"
            monthly_data[label]['budget'] += cost.budget or 0.0
            monthly_data[label]['spent'] += cost.spent or 0.0
            monthly_data[label]['tac'] += cost.total_at_completion or 0.0
            monthly_data[label]['ids'].append(cost.id)

        # Sort by Year/Month
        sorted_labels = sorted(
            monthly_data.keys(),
            key=lambda l: (int("20" + l.split("'")[1]), list(calendar.month_abbr).index(l.split()[0]))
        )

        # Build cumulative values
        cumulative_budget, cumulative_spent, cumulative_tac = [], [], []
        budget_total, spent_total, tac_total = 0, 0, 0
        detail_budget, detail_spent, detail_tac = [], [], []

        for label in sorted_labels:
            budget_total += monthly_data[label]['budget']
            spent_total += monthly_data[label]['spent']
            tac_total += monthly_data[label]['tac']

            cumulative_budget.append(budget_total)
            cumulative_spent.append(spent_total)
            cumulative_tac.append(tac_total)

            detail_budget.append(monthly_data[label]['ids'])
            detail_spent.append(monthly_data[label]['ids'])
            detail_tac.append(monthly_data[label]['ids'])

        project_cost_chart_data = {
            'labels': sorted_labels,
            'datasets': [
                {
                    'label': "Budget",
                    'borderColor': '#20c997',
                    'backgroundColor': '#20c997',
                    'fill': False,
                    'tension': 0.3,
                    'data': cumulative_budget,
                    'detail': detail_budget,
                },
                {
                    'label': "Spent",
                    'borderColor': '#ffc107',
                    'backgroundColor': '#ffc107',
                    'fill': False,
                    'tension': 0.3,
                    'data': cumulative_spent,
                    'detail': detail_spent,
                },
                {
                    'label': "Total at Completion",
                    'borderColor': '#dc3545',
                    'backgroundColor': '#dc3545',
                    'fill': False,
                    'tension': 0.3,
                    'data': cumulative_tac,
                    'detail': detail_tac,
                },
            ]
        }

        return {
            'stages_chart_data': stages_chart_data,
            'project_chart_data': project_chart_data,
            'priority_chart_data': priority_chart_data,
            'health_chart_data': health_chart_data,
            'governance_chart_data': governance_chart_data,
            'missing_resource_chart_data': missing_resource_chart_data,
            'project_cost_chart_data': project_cost_chart_data,
        }

    # ================= Tables ===========================
    @http.route('/project/table/data', auth='public', type='json')
    def get_project_table_data(self, **kw):
        data = kw['data']
        today = date.today()
        domain, closing_domain = [], []

        if not data.get('duration'):
            domain = [('create_date', '>=', today), ('create_date', '<=', today)]
            closing_domain = [('date_deadline', '>=', today)]

        if data:
            if data.get('project_id') and data['project_id'] != 'all':
                domain += [('project_id', '=', int(data['project_id']))]
                closing_domain += [('project_id', '=', int(data['project_id']))]
            if data.get('user_id') and data['user_id'] != 'all':
                domain += [('user_ids', 'in', [int(data['user_id'])])]
                closing_domain += [('user_ids', 'in', [int(data['user_id'])])]
            if data.get('partner_id') and data['partner_id'] != 'all':
                domain += [('partner_id', '=', int(data['partner_id']))]
                closing_domain += [('partner_id', '=', int(data['partner_id']))]
            if data.get('stage_id') and data['stage_id'] != 'all':
                domain += [('stage_id', '=', int(data['stage_id']))]
                closing_domain += [('stage_id', '=', int(data['stage_id']))]
            if data.get('duration') and data['duration'] != "all":
                duration = int(data['duration'])
                filter_date = today - timedelta(days=duration)
                domain += [('create_date', '>=', filter_date), ('create_date', '<=', today)]
                closing_domain += [('date_deadline', '>=', filter_date), ('date_deadline', '>=', today)]

        all_task_list = request.env['project.task'].search_read(domain,
            fields=['name', 'partner_id', 'project_id', 'create_date'],
            order="id desc")

        for task in all_task_list:
            task['create_date'] = task['create_date'].date() if task['create_date'] else False

        closing_task_list = request.env['project.task'].search_read([('date_deadline', '!=', False)] + closing_domain,
            fields=['date_deadline', 'name', 'partner_id', 'project_id'],
            order="id desc")

        return {
            'all_task_list': all_task_list,
            'closing_task_list': closing_task_list,
        }

    # ================= Filter Apply ===========================
    @http.route('/project/filter-apply', auth='public', type='json')
    def project_filter_apply(self, **kw):
        data = kw['data']
        return self.get_project_tiles_data(
            project_id=data['project'],
            user_id=data['user'],
            partner_id=data['partner'],
            stage_id=data['stage'],
            duration=data['duration'],
        )

    @http.route('/project/stages/chart/data', auth='user', type='json')
    def get_project_stages_chart_data(self, **kw):
        """
        Returns chart data for project tasks grouped by stages
        """

        all_color_list = [
            '#00daa3', '#f06c67', '#0c9fa1', '#cf9ab5', '#bce459',
            '#3f8eae', '#ed843f', '#00c4aa', '#966ca2', '#e2d65e',
            '#d56e80', '#c99a5c', '#61e180', '#bf784b', '#fec863', '#7269ad'
        ]

        data = kw.get('data', {})
        today = date.today()
        closing_domain = []

        # Default: today only
        if not data.get('duration'):
            closing_domain = [('create_date', '>=', today), ('create_date', '<=', today)]

        # Filters
        if data:
            if data.get('project_id') and data['project_id'] != 'all':
                closing_domain += [('project_id', '=', int(data['project_id']))]

            if data.get('user_id') and data['user_id'] != 'all':
                closing_domain += [('user_ids', 'in', [int(data['user_id'])])]

            if data.get('partner_id') and data['partner_id'] != 'all':
                closing_domain += [('partner_id', '=', int(data['partner_id']))]

            if data.get('stage_id') and data['stage_id'] != 'all':
                closing_domain += [('stage_id', '=', int(data['stage_id']))]

            if data.get('duration') and data['duration'] != "all":
                duration = int(data['duration'])
                filter_date = today - timedelta(days=duration)
                closing_domain += [('create_date', '>=', filter_date), ('create_date', '<=', today)]

        # Fetch tasks
        task_data = request.env['project.task'].sudo().search_read(
            closing_domain, fields=['stage_id', 'name']
        )
        # Normalize missing stage_id
        for entry in task_data:
            if not entry['stage_id']:
                entry['stage_id'] = (0, 'Unassigned')
        # Group by stage_id
        n_lines = sorted(task_data, key=itemgetter('stage_id'))
        groups = itertools.groupby(n_lines, key=operator.itemgetter('stage_id'))
        lines = [{'stage_id': k, 'values': [x for x in v]} for k, v in groups]

        stage_labels = []
        stage_values = []
        stage_detail_ids = []

        for line in lines:
            stage_labels.append(line.get('stage_id')[1])  # stage name
            stage_values.append(len(line.get('values')))  # count
            stage_detail_ids.append([x['id'] for x in line['values']])  # task IDs

        # Chart.js format
        stages_chart_data = {
            'labels': stage_labels,
            'datasets': [{
                'label': "Stages",
                'backgroundColor': all_color_list[:len(stage_labels)],
                'data': stage_values,
                'detail': stage_detail_ids,
            }]
        }

        return {'stages_chart_data': stages_chart_data}

    @http.route('/project/project/chart/data', auth='user', type='json')
    def get_project_project_chart_data(self, **kw):
        """
        Returns chart data for project tasks grouped by Project
        """

        all_color_list = [
            '#00daa3', '#f06c67', '#0c9fa1', '#cf9ab5', '#bce459',
            '#3f8eae', '#ed843f', '#00c4aa', '#966ca2', '#e2d65e',
            '#d56e80', '#c99a5c', '#61e180', '#bf784b', '#fec863', '#7269ad'
        ]

        data = kw.get('data', {})
        today = date.today()
        domain = []

        # Default: today
        if not data.get('duration'):
            domain = [('create_date', '>=', today), ('create_date', '<=', today)]

        # Apply filters
        if data:
            if data.get('project_id') and data['project_id'] != 'all':
                domain += [('project_id', '=', int(data['project_id']))]

            if data.get('user_id') and data['user_id'] != 'all':
                domain += [('user_ids', 'in', [int(data['user_id'])])]

            if data.get('partner_id') and data['partner_id'] != 'all':
                domain += [('partner_id', '=', int(data['partner_id']))]

            if data.get('stage_id') and data['stage_id'] != 'all':
                domain += [('stage_id', '=', int(data['stage_id']))]

            if data.get('duration') and data['duration'] != "all":
                duration = int(data['duration'])
                filter_date = today - timedelta(days=duration)
                domain += [('create_date', '>=', filter_date), ('create_date', '<=', today)]

        # Fetch task data
        task_data = request.env['project.task'].sudo().search_read(domain, fields=['project_id', 'name'])

        for entry in task_data:
            if entry['project_id'] is False:
                entry['project_id'] = (0, 'No Project')

        # Group by project_id
        n_lines = sorted(task_data, key=itemgetter('project_id'))
        groups = itertools.groupby(n_lines, key=operator.itemgetter('project_id'))
        lines = [{'project_id': k, 'values': [x for x in v]} for k, v in groups]

        project_labels = []
        project_values = []
        project_detail_ids = []

        for line in lines:
            project_labels.append(line.get('project_id')[1])  # Project Name
            project_values.append(len(line.get('values')))  # Count
            project_detail_ids.append([x['id'] for x in line['values']])  # Task IDs

        # Chart.js format
        project_chart_data = {
            'labels': project_labels,
            'datasets': [{
                'label': "Project",
                'backgroundColor': all_color_list[:len(project_labels)],
                'data': project_values,
                'detail': project_detail_ids
            }]
        }

        return {
            'project_chart_data': project_chart_data
        }

    @http.route('/project/priority/chart/data', auth='user', type='json')
    def get_project_priority_chart_data(self, **kw):
        """
        Returns chart data for project tasks grouped by Priority
        """

        all_color_list = [
            '#00daa3', '#f06c67', '#0c9fa1', '#cf9ab5', '#bce459',
            '#3f8eae', '#ed843f', '#00c4aa', '#966ca2', '#e2d65e',
            '#d56e80', '#c99a5c', '#61e180', '#bf784b', '#fec863', '#7269ad'
        ]

        data = kw.get('data', {})
        today = date.today()
        domain = []

        # Default to today if no duration
        if not data.get('duration'):
            domain = [('create_date', '>=', today), ('create_date', '<=', today)]

        # Apply filters
        if data:
            if data.get('project_id') and data['project_id'] != 'all':
                domain += [('project_id', '=', int(data['project_id']))]

            if data.get('user_id') and data['user_id'] != 'all':
                domain += [('user_ids', 'in', [int(data['user_id'])])]

            if data.get('partner_id') and data['partner_id'] != 'all':
                domain += [('partner_id', '=', int(data['partner_id']))]

            if data.get('stage_id') and data['stage_id'] != 'all':
                domain += [('stage_id', '=', int(data['stage_id']))]

            if data.get('duration') and data['duration'] != "all":
                duration = int(data['duration'])
                filter_date = today - timedelta(days=duration)
                domain += [('create_date', '>=', filter_date), ('create_date', '<=', today)]

        # Prepare buckets
        low, medium, high, very_high = [], [], [], []

        # Fetch project tasks
        tasks = request.env['project.task'].sudo().search(domain)

        for task in tasks:
            if task.priority == '0':  # Low
                low.append(task.id)
            elif task.priority == '1':  # Medium
                medium.append(task.id)
            elif task.priority == '2':  # High
                high.append(task.id)
            elif task.priority == '3':  # Very High
                very_high.append(task.id)

        priority_labels = ['Low', 'Medium', 'High', 'Very High']
        priority_values = [len(low), len(medium), len(high), len(very_high)]
        priority_ids = [low, medium, high, very_high]

        # Chart.js format
        project_priority_chart_data = {
            'labels': priority_labels,
            'datasets': [{
                'label': "Priority",
                'backgroundColor': all_color_list[:len(priority_labels)],
                'data': priority_values,
                'detail': priority_ids
            }]
        }

        return {
            'project_priority_chart_data': project_priority_chart_data
        }

    @http.route('/project/source/chart/data', auth='user', type='json')
    def get_project_source_chart_data(self, **kw):
        """
        Returns chart data for project tasks grouped by Source
        (assumes project.task has a Many2one field `source_id`)
        """

        all_color_list = [
            '#00daa3', '#f06c67', '#0c9fa1', '#cf9ab5', '#bce459',
            '#3f8eae', '#ed843f', '#00c4aa', '#966ca2', '#e2d65e',
            '#d56e80', '#c99a5c', '#61e180', '#bf784b', '#fec863', '#7269ad'
        ]

        data = kw.get('data', {})
        today = date.today()
        domain = []

        # Default: today
        if not data.get('duration'):
            domain = [('create_date', '>=', today), ('create_date', '<=', today)]

        # Apply filters
        if data:
            if data.get('project_id') and data['project_id'] != 'all':
                domain += [('project_id', '=', int(data['project_id']))]

            if data.get('user_id') and data['user_id'] != 'all':
                domain += [('user_ids', 'in', [int(data['user_id'])])]

            if data.get('partner_id') and data['partner_id'] != 'all':
                domain += [('partner_id', '=', int(data['partner_id']))]

            if data.get('stage_id') and data['stage_id'] != 'all':
                domain += [('stage_id', '=', int(data['stage_id']))]

            if data.get('duration') and data['duration'] != "all":
                duration = int(data['duration'])
                filter_date = today - timedelta(days=duration)
                domain += [('create_date', '>=', filter_date), ('create_date', '<=', today)]

        # Fetch tasks
        task_data = request.env['project.task'].sudo().search(domain)

        # Transform for grouping
        prepared_data = []
        for task in task_data:
            prepared_data.append({
                'source_id': task.source_id.name or 'None',
                'id': task.id,
                'name': task.name or 'No Name',
            })

        # Group by source_id
        n_lines = sorted(prepared_data, key=itemgetter('source_id'))
        groups = itertools.groupby(n_lines, key=operator.itemgetter('source_id'))
        lines = [{'source_id': k, 'values': [x for x in v]} for k, v in groups]

        source_labels = []
        source_values = []
        source_detail_ids = []

        for line in lines:
            source_labels.append(line.get('source_id')[0:10])  # trim label to 10 chars
            source_values.append(len(line.get('values')))
            source_detail_ids.append([x['id'] for x in line['values']])

        # Chart.js format
        project_source_chart_data = {
            'labels': source_labels,
            'datasets': [{
                'label': "Source",
                'backgroundColor': all_color_list[:len(source_labels)],
                'data': source_values,
                'detail': source_detail_ids
            }]
        }

        return {
            'project_source_chart_data': project_source_chart_data
        }

    @http.route('/project/dashboard/links', auth='user', type='json')
    def get_links(self):
        links = request.env['project.dashboard.link'].sudo().search([('user_id', '=', request.env.user.id)])
        return [
            {
                'id': link.id,
                'name': link.name,
                'url': link.url,
                'icon': link.icon.decode() if link.icon else False,
            }
            for link in links
        ]

    @http.route('/project/health/chart/data', auth='user', type='json')
    def get_project_health_chart_data(self, **kw):
        """
        Returns chart data grouped by Project Manager and Health (G/A/R)
        """
        data = kw.get('data', {})
        today = date.today()
        domain = []
        # Default: today
        if not data.get('duration'):
            domain = [('create_date', '>=', today), ('create_date', '<=', today)]

        # Filters
        if data:
            if data.get('project_id') and data['project_id'] != 'all':
                domain += [('id', '=', int(data['project_id']))]

            if data.get('user_id') and data['user_id'] != 'all':
                domain += [('user_ids', '=', int(data['user_id']))]

            if data.get('partner_id') and data['partner_id'] != 'all':
                domain += [('partner_id', '=', int(data['partner_id']))]

            if data.get('duration') and data['duration'] != "all":
                duration = int(data['duration'])
                filter_date = today - timedelta(days=duration)
                domain += [('create_date', '>=', filter_date), ('create_date', '<=', today)]

        # Colors + labels for Health
        rag_map = {
            'done': ('Green', '#28a745'),
            'normal': ('Amber', '#ffc107'),
            'blocked': ('Red', '#dc3545'),
        }

        # Fetch projects with health + manager
        projects = request.env['project.project'].sudo().search_read(
            domain, fields=['health_indicator', 'project_manager_id']
        )

        manager_map = defaultdict(lambda: {'done': [], 'normal': [], 'blocked': []})

        for proj in projects:
            manager = proj['project_manager_id'][1] if proj['project_manager_id'] else "Unknown"
            hi = proj['health_indicator']
            if hi in ['done', 'normal', 'blocked']:
                manager_map[manager][hi].append(proj['id'])

        managers = list(manager_map.keys())

        datasets = []
        for key, (label, color) in rag_map.items():
            datasets.append({
                'label': label,
                'backgroundColor': color,
                'data': [len(manager_map[m][key]) for m in managers],
                'detail': [manager_map[m][key] for m in managers],
            })
        return {
            'health_chart_data': {
                'labels': managers,
                'datasets': datasets,
            }
        }

    @http.route('/project/governance/chart/data', auth='user', type='json')
    def get_project_governance_chart_data(self, **kw):
        """
        Returns Governance RAG data grouped by Project Manager
        """
        data = kw.get('data', {})
        today = date.today()
        domain = []

        # Default: today
        if not data.get('duration'):
            domain = [('create_date', '>=', today), ('create_date', '<=', today)]

        # Apply filters
        if data:
            if data.get('project_id') and data['project_id'] != 'all':
                domain += [('id', '=', int(data['project_id']))]

            if data.get('user_id') and data['user_id'] != 'all':
                domain += [('user_id', '=', int(data['user_id']))]

            if data.get('partner_id') and data['partner_id'] != 'all':
                domain += [('partner_id', '=', int(data['partner_id']))]

            if data.get('duration') and data['duration'] != "all":
                duration = int(data['duration'])
                filter_date = today - timedelta(days=duration)
                domain += [('create_date', '>=', filter_date), ('create_date', '<=', today)]

        # RAG mapping
        rag_map = {
            'done': ('Green', '#28a745'),
            'normal': ('Amber', '#ffc107'),
            'blocked': ('Red', '#dc3545'),
        }

        # Fetch projects with managers + governance requirements
        projects = request.env['project.project'].sudo().search(domain)

        # Aggregate governance rag by manager
        manager_map = {}
        for project in projects:
            manager = project.project_manager_id.name if project.project_manager_id else "Unknown"
            if manager not in manager_map:
                manager_map[manager] = {'done': [], 'normal': [], 'blocked': []}

            for gov in project.governance_requirements_ids:
                if gov.rag in ['done', 'normal', 'blocked']:
                    manager_map[manager][gov.rag].append(project.id)

        managers = list(manager_map.keys())

        datasets = []
        for key, (label, color) in rag_map.items():
            datasets.append({
                'label': label,
                'backgroundColor': color,
                'data': [len(set(manager_map[m][key])) for m in managers],
                'detail': [list(set(manager_map[m][key])) for m in managers],
            })

        return {
            'governance_chart_data': {
                'labels': managers,
                'datasets': datasets,
            }
        }

    @http.route('/project/missing/resource/chart/data', auth='user', type='json')
    def get_missing_resource_chart_data(self, **kw):
        """
        Returns projects without resource allocations, grouped by Project Manager
        """
        data = kw.get('data', {})
        today = date.today()
        domain = []

        # Default filter: today
        if not data.get('duration'):
            domain = [('create_date', '>=', today), ('create_date', '<=', today)]

        # Apply filters
        if data:
            if data.get('project_id') and data['project_id'] != 'all':
                domain += [('id', '=', int(data['project_id']))]
            if data.get('user_id') and data['user_id'] != 'all':
                domain += [('user_id', '=', int(data['user_id']))]
            if data.get('partner_id') and data['partner_id'] != 'all':
                domain += [('partner_id', '=', int(data['partner_id']))]
            if data.get('duration') and data['duration'] != "all":
                duration = int(data['duration'])
                filter_date = today - timedelta(days=duration)
                domain += [('create_date', '>=', filter_date), ('create_date', '<=', today)]

        # Colors
        color_list = [
            '#00daa3', '#f06c67', '#0c9fa1', '#cf9ab5', '#bce459',
            '#3f8eae', '#ed843f', '#00c4aa', '#966ca2', '#e2d65e',
            '#d56e80', '#c99a5c', '#61e180', '#bf784b', '#fec863', '#7269ad'
        ]

        # Fetch projects
        projects = request.env['project.project'].sudo().search(domain)

        manager_map = {}
        for project in projects:
            if not project.resource_allocations_ids:  # Missing resource allocations
                manager = project.project_manager_id.name if project.project_manager_id else "Unknown"
                if manager not in manager_map:
                    manager_map[manager] = []
                manager_map[manager].append(project.id)

        managers = list(manager_map.keys())
        values = [len(manager_map[m]) for m in managers]
        details = [manager_map[m] for m in managers]

        missing_resource_chart_data = {
            'labels': managers,
            'datasets': [{
                'label': "Missing Resource Allocation",
                'backgroundColor': color_list[:len(managers)],
                'data': values,
                'detail': details,
            }]
        }

        return {'missing_resource_chart_data': missing_resource_chart_data}

    @http.route('/project/cost/chart/data', auth='user', type='json')
    def get_project_cost_chart_data(self, **kw):
        """
        Returns cumulative Budget, Spent, TAC per Year/Month (S-Curve)
        """
        data = kw.get('data', {})
        today = date.today()
        domain = []

        # Default: only today
        if not data.get('duration'):
            domain = [('create_date', '>=', today), ('create_date', '<=', today)]

        # Filters
        if data:
            if data.get('project_id') and data['project_id'] != 'all':
                domain += [('project_id', '=', int(data['project_id']))]
            if data.get('user_id') and data['user_id'] != 'all':
                domain += [('create_uid', '=', int(data['user_id']))]
            if data.get('partner_id') and data['partner_id'] != 'all':
                domain += [('project_id.partner_id', '=', int(data['partner_id']))]
            if data.get('duration') and data['duration'] != "all":
                duration = int(data['duration'])
                filter_date = today - timedelta(days=duration)
                domain += [('create_date', '>=', filter_date), ('create_date', '<=', today)]

        costs = request.env['project.cost'].sudo().search(domain)

        # Group by Year-Month
        monthly_data = defaultdict(lambda: {'budget': 0.0, 'spent': 0.0, 'tac': 0.0, 'ids': []})
        for cost in costs:
            if not (cost.year and cost.month):
                continue
            label = f"{calendar.month_abbr[int(cost.month)]} '{str(cost.year)[2:]}"
            monthly_data[label]['budget'] += cost.budget or 0.0
            monthly_data[label]['spent'] += cost.spent or 0.0
            monthly_data[label]['tac'] += cost.total_at_completion or 0.0
            monthly_data[label]['ids'].append(cost.id)

        # Sort by Year/Month
        sorted_labels = sorted(
            monthly_data.keys(),
            key=lambda l: (int("20" + l.split("'")[1]), list(calendar.month_abbr).index(l.split()[0]))
        )

        # Build cumulative values
        cumulative_budget, cumulative_spent, cumulative_tac = [], [], []
        budget_total, spent_total, tac_total = 0, 0, 0
        detail_budget, detail_spent, detail_tac = [], [], []

        for label in sorted_labels:
            budget_total += monthly_data[label]['budget']
            spent_total += monthly_data[label]['spent']
            tac_total += monthly_data[label]['tac']

            cumulative_budget.append(budget_total)
            cumulative_spent.append(spent_total)
            cumulative_tac.append(tac_total)

            detail_budget.append(monthly_data[label]['ids'])
            detail_spent.append(monthly_data[label]['ids'])
            detail_tac.append(monthly_data[label]['ids'])

        project_cost_chart_data = {
            'labels': sorted_labels,
            'datasets': [
                {
                    'label': "Budget",
                    'borderColor': '#20c997',
                    'backgroundColor': '#20c997',
                    'fill': False,
                    'tension': 0.3,
                    'data': cumulative_budget,
                    'detail': detail_budget,
                },
                {
                    'label': "Spent",
                    'borderColor': '#ffc107',
                    'backgroundColor': '#ffc107',
                    'fill': False,
                    'tension': 0.3,
                    'data': cumulative_spent,
                    'detail': detail_spent,
                },
                {
                    'label': "Total at Completion",
                    'borderColor': '#dc3545',
                    'backgroundColor': '#dc3545',
                    'fill': False,
                    'tension': 0.3,
                    'data': cumulative_tac,
                    'detail': detail_tac,
                },
            ]
        }

        return {'project_cost_chart_data': project_cost_chart_data}
