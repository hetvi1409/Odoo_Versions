# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import OrderedDict
from dateutil.relativedelta import relativedelta
from operator import itemgetter
from markupsafe import Markup


from odoo import fields, http, _
from odoo.http import request
from odoo.tools import date_utils, groupby as groupbyelem
from odoo.osv.expression import AND, OR
from odoo.addons.portal.controllers import portal


from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.addons.project.controllers.portal import ProjectCustomerPortal


class TimesheetCustomerPortal(CustomerPortal):

    @http.route(['/my/timesheets', '/my/timesheets/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_timesheets(self, page=1, sortby=None, filterby=None, search=None, search_in='all', groupby='none',
                             **kw):
        Timesheet = request.env['account.analytic.line']
        domain = Timesheet._timesheet_get_portal_domain()

        domain += [('user_id', '=', request.env.uid)]

        Timesheet_sudo = Timesheet.sudo()

        values = self._prepare_portal_layout_values()
        _items_per_page = 100

        searchbar_sortings = self._get_searchbar_sortings()
        searchbar_inputs = self._get_searchbar_inputs()
        searchbar_groupby = self._get_searchbar_groupby()

        today = fields.Date.today()
        quarter_start, quarter_end = date_utils.get_quarter(today)
        last_week = today + relativedelta(weeks=-1)
        last_month = today + relativedelta(months=-1)
        last_year = today + relativedelta(years=-1)

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'today': {'label': _('Today'), 'domain': [("date", "=", today)]},
            'week': {'label': _('This week'), 'domain': [('date', '>=', date_utils.start_of(today, "week")),
                                                         ('date', '<=', date_utils.end_of(today, 'week'))]},
            'month': {'label': _('This month'), 'domain': [('date', '>=', date_utils.start_of(today, 'month')),
                                                           ('date', '<=', date_utils.end_of(today, 'month'))]},
            'year': {'label': _('This year'), 'domain': [('date', '>=', date_utils.start_of(today, 'year')),
                                                         ('date', '<=', date_utils.end_of(today, 'year'))]},
            'quarter': {'label': _('This Quarter'),
                        'domain': [('date', '>=', quarter_start), ('date', '<=', quarter_end)]},
            'last_week': {'label': _('Last week'), 'domain': [('date', '>=', date_utils.start_of(last_week, "week")),
                                                              ('date', '<=', date_utils.end_of(last_week, 'week'))]},
            'last_month': {'label': _('Last month'),
                           'domain': [('date', '>=', date_utils.start_of(last_month, 'month')),
                                      ('date', '<=', date_utils.end_of(last_month, 'month'))]},
            'last_year': {'label': _('Last year'), 'domain': [('date', '>=', date_utils.start_of(last_year, 'year')),
                                                              ('date', '<=', date_utils.end_of(last_year, 'year'))]},
        }

        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        if not filterby:
            filterby = 'all'
        domain = AND([domain, searchbar_filters[filterby]['domain']])

        if search and search_in:
            domain += self._get_search_domain(search_in, search)

        timesheet_count = Timesheet_sudo.search_count(domain)
        pager = portal_pager(
            url="/my/timesheets",
            url_args={'sortby': sortby, 'search_in': search_in, 'search': search, 'filterby': filterby,
                      'groupby': groupby},
            total=timesheet_count,
            page=page,
            step=_items_per_page
        )

        def get_timesheets():
            groupby_mapping = self._get_groupby_mapping()
            field = groupby_mapping.get(groupby, None)
            orderby = '%s, %s' % (field, order) if field else order
            timesheets = Timesheet_sudo.search(domain, order=orderby, limit=_items_per_page, offset=pager['offset'])
            if field:
                if groupby == 'date':
                    raw_timesheets_group = Timesheet_sudo.read_group(
                        domain, ["unit_amount:sum", "ids:array_agg(id)"], ["date:day"]
                    )
                    grouped_timesheets = [(Timesheet_sudo.browse(group["ids"]), group["unit_amount"]) for group in
                                          raw_timesheets_group]
                else:
                    time_data = Timesheet_sudo.read_group(domain, [field, 'unit_amount:sum'], [field])
                    mapped_time = dict([(m[field][0] if m[field] else False, m['unit_amount']) for m in time_data])
                    grouped_timesheets = [(Timesheet_sudo.concat(*g), mapped_time[k.id]) for k, g in
                                          groupbyelem(timesheets, itemgetter(field))]
                return timesheets, grouped_timesheets
            grouped_timesheets = [(
                timesheets,
                sum(Timesheet_sudo.search(domain).mapped('unit_amount'))
            )] if timesheets else []
            return timesheets, grouped_timesheets

        timesheets, grouped_timesheets = get_timesheets()

        values.update({
            'timesheets': timesheets,
            'grouped_timesheets': grouped_timesheets,
            'page_name': 'timesheet',
            'default_url': '/my/timesheets',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'search_in': search_in,
            'search': search,
            'sortby': sortby,
            'groupby': groupby,
            'searchbar_inputs': searchbar_inputs,
            'searchbar_groupby': searchbar_groupby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
            'is_uom_day': request.env['account.analytic.line']._is_timesheet_encode_uom_day(),
        })
        return request.render("hr_timesheet.portal_my_timesheets", values)
class CustomerPortal(portal.CustomerPortal):


    def _prepare_my_tickets_values(self, page=1, date_begin=None, date_end=None, sortby=None, filterby='all', search=None, groupby='none', search_in='content'):
        values = self._prepare_portal_layout_values()
        domain = self._prepare_helpdesk_tickets_domain()
        domain += [('user_id', '=', request.env.uid)]


        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'reference': {'label': _('Reference'), 'order': 'id'},
            'name': {'label': _('Subject'), 'order': 'name'},
            'user': {'label': _('Assigned to'), 'order': 'user_id'},
            'stage': {'label': _('Stage'), 'order': 'stage_id'},
            'update': {'label': _('Last Stage Update'), 'order': 'date_last_stage_update desc'},
        }
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'assigned': {'label': _('Assigned'), 'domain': [('user_id', '!=', False)]},
            'unassigned': {'label': _('Unassigned'), 'domain': [('user_id', '=', False)]},
            'open': {'label': _('Open'), 'domain': [('close_date', '=', False)]},
            'closed': {'label': _('Closed'), 'domain': [('close_date', '!=', False)]},
        }
        searchbar_inputs = {
            'content': {'input': 'content', 'label': Markup(_('Search <span class="nolabel"> (in Content)</span>'))},
            'ticket_ref': {'input': 'ticket_ref', 'label': _('Search in Reference')},
            'message': {'input': 'message', 'label': _('Search in Messages')},
            'user': {'input': 'user', 'label': _('Search in Assigned to')},
            'status': {'input': 'status', 'label': _('Search in Stage')},
        }
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'stage': {'input': 'stage_id', 'label': _('Stage')},
            'user': {'input': 'user_id', 'label': _('Assigned to')},
        }

        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        if filterby in ['last_message_sup', 'last_message_cust']:
            discussion_subtype_id = request.env.ref('mail.mt_comment').id
            messages = request.env['mail.message'].search_read([('model', '=', 'helpdesk.ticket'), ('subtype_id', '=', discussion_subtype_id)], fields=['res_id', 'author_id'], order='date desc')
            last_author_dict = {}
            for message in messages:
                if message['res_id'] not in last_author_dict:
                    last_author_dict[message['res_id']] = message['author_id'][0]

            ticket_author_list = request.env['helpdesk.ticket'].search_read(fields=['id', 'partner_id'])
            ticket_author_dict = dict([(ticket_author['id'], ticket_author['partner_id'][0] if ticket_author['partner_id'] else False) for ticket_author in ticket_author_list])

            last_message_cust = []
            last_message_sup = []
            ticket_ids = set(last_author_dict.keys()) & set(ticket_author_dict.keys())
            for ticket_id in ticket_ids:
                if last_author_dict[ticket_id] == ticket_author_dict[ticket_id]:
                    last_message_cust.append(ticket_id)
                else:
                    last_message_sup.append(ticket_id)

            if filterby == 'last_message_cust':
                domain = AND([domain, [('id', 'in', last_message_cust)]])
            else:
                domain = AND([domain, [('id', 'in', last_message_sup)]])

        else:
            domain = AND([domain, searchbar_filters[filterby]['domain']])

        if date_begin and date_end:
            domain = AND([domain, [('create_date', '>', date_begin), ('create_date', '<=', date_end)]])

        # search
        if search and search_in:
            search_domain = []
            if search_in == 'ticket_ref':
                search_domain = OR([search_domain, [('ticket_ref', 'ilike', search)]])
            if search_in == 'content':
                search_domain = OR([search_domain, ['|', ('name', 'ilike', search), ('description', 'ilike', search)]])
            if search_in == 'user':
                search_domain = OR([search_domain, [('user_id', 'ilike', search)]])
            if search_in == 'message':
                discussion_subtype_id = request.env.ref('mail.mt_comment').id
                search_domain = OR([search_domain, [('message_ids.body', 'ilike', search), ('message_ids.subtype_id', '=', discussion_subtype_id)]])
            if search_in == 'status':
                search_domain = OR([search_domain, [('stage_id', 'ilike', search)]])
            domain = AND([domain, search_domain])

        # pager
        tickets_count = request.env['helpdesk.ticket'].search_count(domain)
        pager = portal_pager(
            url="/my/tickets",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'search_in': search_in, 'search': search, 'groupby': groupby, 'filterby': filterby},
            total=tickets_count,
            page=page,
            step=self._items_per_page
        )

        tickets = request.env['helpdesk.ticket'].search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_tickets_history'] = tickets.ids[:100]

        if groupby != 'none':
            grouped_tickets = [request.env['helpdesk.ticket'].concat(*g) for k, g in groupbyelem(tickets, itemgetter(searchbar_groupby[groupby]['input']))]
        else:
            grouped_tickets = [tickets]

        values.update({
            'date': date_begin,
            'grouped_tickets': grouped_tickets,
            'page_name': 'ticket',
            'default_url': '/my/tickets',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_filters': searchbar_filters,
            'searchbar_inputs': searchbar_inputs,
            'searchbar_groupby': searchbar_groupby,
            'sortby': sortby,
            'groupby': groupby,
            'search_in': search_in,
            'search': search,
            'filterby': filterby,
        })
        return values

    @http.route(['/my/tickets', '/my/tickets/page/<int:page>'], type='http', auth="user", website=True)
    def my_helpdesk_tickets(self, page=1, date_begin=None, date_end=None, sortby=None, filterby='all', search=None, groupby='none', search_in='content', **kw):
        values = self._prepare_my_tickets_values(page, date_begin, date_end, sortby, filterby, search, groupby, search_in)
        return request.render("helpdesk.portal_helpdesk_ticket", values)

    @http.route(['/my/signatures', '/my/signatures/page/<int:page>'], type='http', auth='user', website=True)
    def portal_my_signatures(self, page=1, date_begin=None, date_end=None, sortby=None, search=None, search_in='all',
                             groupby='none', filterby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner_id = request.env.user.partner_id
        user_id = request.env.uid

        SignRequestItem = request.env['sign.request.item'].sudo()

        default_domain = [
            ('partner_id', '=', partner_id.id),
            '|', ('sign_request_id.state', '=', 'refused'),
            '|', ('state', '=', 'completed'),
            ('is_mail_sent', '=', True)
        ]

        # Assign domain to variable we will work with
        domain = list(default_domain)  # Make a copy

        searchbar_sortings = {
            'new': {'label': _('Newest'), 'order': 'sign_request_id desc'},
            'date': {'label': _('Signing Date'), 'order': 'signing_date desc'},
        }

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': default_domain},
            'tosign': {'label': _('To sign'), 'domain': AND(
                [default_domain, [('state', '=', 'sent'), ('sign_request_id.state', '=', 'sent')]])},
            'completed': {'label': _('Completed'), 'domain': AND([default_domain, [('state', '=', 'completed')]])},
            'signed': {'label': _('Fully Signed'),
                       'domain': AND([default_domain, [('sign_request_id.state', '=', 'signed')]])},
        }

        searchbar_inputs = {
            'all': {'input': 'all', 'label': Markup(_('Search <span class="nolabel"> (in Document)</span>'))},
        }

        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'state': {'input': 'state', 'label': _('Status')},
        }

        if not sortby:
            sortby = 'new'
        sort_order = searchbar_sortings[sortby]['order']

        if not filterby:
            filterby = 'all'
        domain = list(searchbar_filters[filterby]['domain'])

        if date_begin and date_end:
            domain = AND([domain, [('signing_date', '>', date_begin), ('signing_date', '<=', date_end)]])

        if search and search_in:
            domain = AND([domain, [('reference', 'ilike', search)]])

        pager = portal_pager(
            url='/my/signatures',
            url_args={
                'date_begin': date_begin,
                'date_end': date_end,
                'sortby': sortby,
                'filterby': filterby,
                'search_in': search_in,
                'search': search
            },
            total=SignRequestItem.search_count(domain),
            page=page,
            step=self._items_per_page
        )

        if groupby == 'state':
            sort_order = 'state, %s' % sort_order

        sign_requests_items = SignRequestItem.search(domain, order=sort_order, limit=self._items_per_page,
                                                     offset=pager['offset'])
        request.session['my_signatures_history'] = sign_requests_items.ids[:100]

        if groupby == 'state':
            grouped_signatures = [SignRequestItem.concat(*g) for k, g in
                                  groupbyelem(sign_requests_items, itemgetter('state'))]
        else:
            grouped_signatures = [sign_requests_items]

        values.update({
            'date': date_begin,
            'grouped_signatures': grouped_signatures,
            'page_name': 'signatures',
            'pager': pager,
            'default_url': '/my/signatures',
            'searchbar_sortings': searchbar_sortings,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'searchbar_groupby': searchbar_groupby,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'groupby': groupby,
            'sortby': sortby,
            'filterby': filterby,
        })
        return request.render('sign.sign_portal_my_requests', values)