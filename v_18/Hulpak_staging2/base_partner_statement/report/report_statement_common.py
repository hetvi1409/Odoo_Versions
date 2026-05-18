# Copyright 2018 ForgeFlow, S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import datetime, timedelta

from odoo import _, api, fields, models

import logging
_logger = logging.getLogger(__name__)


class ReportStatementCommon(models.AbstractModel):
    """Abstract Report Statement for use in other models"""

    _name = "statement.common"
    _description = "Statement Reports Common"

    def _get_opening_balance(self, date, partner_id, company_id):
        """
        Opening balance as-of `date` for THIS partner only.

        - Sums posted receivable/payable move lines with aml.date < date
        - Adjusts for partial reconciliations with apr.max_date < date
        - Returns company-currency balance (same sign convention as aml.balance)

        :param date: datetime.date or 'YYYY-MM-DD'
        :param company: res.company (defaults to env.company)
        :param account_types: tuple/list of account_account.account_type values
                              default: ('asset_receivable','liability_payable')
                              customers only: ('asset_receivable',)
                              suppliers only: ('liability_payable',)
        :return: float
        """
        company_id = [company_id]
        company = self.env['res.company'].sudo().browse(company_id)
        if company.child_ids:
            company_id += company.child_ids.ids
        account_types = ("asset_receivable", "liability_payable_x")

        # query = """
        #         SELECT
        #             COALESCE(SUM(
        #                 aml.balance
        #                 - COALESCE(pr_debit.amount, 0)
        #                 + COALESCE(pr_credit.amount, 0)
        #             ), 0.0) AS opening_balance
        #         FROM account_move_line aml
        #         JOIN account_move am ON am.id = aml.move_id
        #         JOIN account_account aa ON aa.id = aml.account_id

        #         LEFT JOIN LATERAL (
        #             SELECT SUM(apr.amount) AS amount
        #             FROM account_partial_reconcile apr
        #             WHERE apr.debit_move_id = aml.id
        #             AND apr.max_date < %(date)s
        #         ) pr_debit ON TRUE

        #         LEFT JOIN LATERAL (
        #             SELECT SUM(apr.amount) AS amount
        #             FROM account_partial_reconcile apr
        #             WHERE apr.credit_move_id = aml.id
        #             AND apr.max_date < %(date)s
        #         ) pr_credit ON TRUE

        #         WHERE aml.partner_id = %(partner_id)s
        #         AND aml.company_id = %(company_id)s
        #         AND aml.date < %(date)s
        #         AND aml.display_type IS NULL
        #         AND am.state = 'posted'
        #         AND aa.account_type = ANY(%(account_types)s)
        #     """
        query = """
                SELECT
                    COALESCE(SUM(aml.balance), 0.0) AS opening_balance
                FROM account_move_line aml
                JOIN account_move am ON am.id = aml.move_id
                JOIN account_account aa ON aa.id = aml.account_id
                WHERE aml.partner_id = %(partner_id)s
                AND aml.company_id = ANY(%(company_id)s)
                AND aml.date < %(date)s
                AND am.state = 'posted'
                AND aa.account_type = ANY(%(account_types)s)
            """
        params = {
            "date": date,
            "partner_id": partner_id,
            "company_id": company_id,
            "account_types": list(account_types),
        }
        self.env.cr.execute(query, params)
        row = self.env.cr.fetchone()
        return float(row[0] or 0.0)

    def _get_invoice_address(self, part):
        inv_addr_id = part.address_get(["invoice"]).get("invoice", part.id)
        return self.env["res.partner"].browse(inv_addr_id)

    def _get_title(self, partner, **kwargs):
        raise NotImplementedError

    def _get_aging_buckets_title(self, partner, **kwargs):
        kwargs["context"] = {
            "lang": partner.lang,
        }
        return _("Aging Report at %(ending_date)s in %(currency)s", **kwargs)

    def _format_date_to_partner_lang(
        self, date, date_format="%Y-%m-%d"
    ):
        if isinstance(date, str):
            date = datetime.strptime(date, "%Y-%m-%d")
        return date.strftime(date_format) if date else ""

    def _get_account_display_lines(
        self, company_id, partner_ids, date_start, date_end, account_type
    ):
        raise NotImplementedError

    def _get_account_initial_balance(
        self, company_id, partner_ids, date_start, account_type
    ):
        return {}

    def _get_account_display_prior_lines(
        self, company_id, partner_ids, date_start, date_end, account_type
    ):
        return {}

    def _get_account_display_reconciled_lines(
        self, company_id, partner_ids, date_start, date_end, account_type
    ):
        return {}

    def _get_account_display_ending_lines(
        self, company_id, partner_ids, date_start, date_end, account_type
    ):
        return {}

    def _show_buckets_sql_q1(self, partners, date_end, account_type):
        partners = str(tuple(partners)).replace(",)", ")").replace("()","(0)")
        excluded_accounts_ids = str(tuple(self.env.context.get("excluded_accounts_ids", []))).replace(",)", ")").replace("()","(0)") or (-1,)
        show_only_overdue = self.env.context.get("show_only_overdue", False)
        x = self.env.context
        nno_followup = self.env.context.get("no_followup", False)
        if nno_followup:
            nno_followup = " AND COALESCE(l.no_followup,false) = false "
        else:
            nno_followup = " "
        invonly = " "
        if self.env.context.get("statement_type", False) == "Outstanding Statement":
            invonly = """ AND ( m.move_type IN ( 'out_invoice', 'out_refund', 'in_invoice', 'in_refund' ) OR m.id IN (672270, 675880) OR j.type IN ('cash','bank') ) """

        return str(
            self._cr.mogrify(
                """
            SELECT l.partner_id, l.currency_id, l.company_id, l.move_id,
            CASE WHEN l.balance > 0.0
                THEN l.balance - sum(coalesce(pd.amount, 0.0))
                ELSE l.balance + sum(coalesce(pc.amount, 0.0))
            END AS open_due,
            CASE WHEN l.balance > 0.0
                THEN l.amount_currency - sum(coalesce(pd.debit_amount_currency, 0.0))
                ELSE l.amount_currency + sum(coalesce(pc.credit_amount_currency, 0.0))
            END AS open_due_currency,
            l.date_maturity,
            l.date,
            COALESCE(l.invoice_date, l.date) as invoice_date,
            COALESCE(l.invoice_date, l.date) as statement_date,
            COALESCE(l.date_maturity, l.invoice_date) as statement_due_date,
            l.no_followup,
            COALESCE(l.date_maturity, COALESCE(l.invoice_date, l.date)) AS sort_date
            FROM account_move_line l
            JOIN account_move m ON (l.move_id = m.id)
            JOIN account_account aa ON (aa.id = l.account_id)
            JOIN account_journal j ON (m.journal_id = j.id)
            LEFT JOIN (SELECT pr.*
                FROM account_partial_reconcile pr
                INNER JOIN account_move_line l2
                ON pr.credit_move_id = l2.id
                WHERE l2.date <= '{date_end}'
            ) as pd ON pd.debit_move_id = l.id
            LEFT JOIN (SELECT pr.*
                FROM account_partial_reconcile pr
                INNER JOIN account_move_line l2
                ON pr.debit_move_id = l2.id
                WHERE l2.date <= '{date_end}'
            ) as pc ON pc.credit_move_id = l.id
            WHERE l.partner_id IN {partners}
                AND aa.id not in {excluded_accounts_ids}
                AND (
                  (pd.id IS NOT NULL AND
                      pd.max_date <= '{date_end}') OR
                  (pc.id IS NOT NULL AND
                      pc.max_date <= '{date_end}') OR
                  (pd.id IS NULL AND pc.id IS NULL)
                ) AND l.date <= '{date_end}'
                  AND m.state IN ('posted')
                AND aa.account_type = '{account_type}'
                AND CASE
                    WHEN {show_only_overdue}
                    THEN COALESCE(l.date_maturity, l.date) <= '{date_end}'
                    ELSE TRUE
                END
                {nno_followup}
                {invonly}
            GROUP BY l.partner_id, l.currency_id, l.date, l.invoice_date, l.date_maturity, l.no_followup,
                l.amount_currency, l.balance, l.move_id, l.company_id, l.id
            ORDER BY sort_date
        """.format(**locals()),
            ),
            "utf-8",
        )

    def _show_buckets_sql_q2(self, date_end, minus_30, minus_60, minus_90, minus_120):
        return str(
            self._cr.mogrify(
                """
            SELECT partner_id, currency_id, date_maturity, invoice_date, date, no_followup, open_due,
                open_due_currency, move_id, company_id,
                COALESCE(invoice_date, date) AS sort_date,
            CASE
                WHEN %(date_end)s <= COALESCE(invoice_date, date) AND currency_id is null
                    THEN open_due
                WHEN %(date_end)s <= COALESCE(invoice_date, date) AND currency_id is not null
                    THEN open_due_currency
                ELSE 0.0
            END as current,
            CASE
                WHEN %(minus_30)s < COALESCE(invoice_date, date)
                    AND COALESCE(invoice_date, date) < %(date_end)s
                    AND currency_id is null
                THEN open_due
                WHEN %(minus_30)s < COALESCE(invoice_date, date)
                    AND COALESCE(invoice_date, date) < %(date_end)s
                    AND currency_id is not null
                THEN open_due_currency
                ELSE 0.0
            END as b_1_30,
            CASE
                WHEN %(minus_60)s < COALESCE(invoice_date, date)
                    AND COALESCE(invoice_date, date) <= %(minus_30)s
                    AND currency_id is null
                THEN open_due
                WHEN %(minus_60)s < COALESCE(invoice_date, date)
                    AND COALESCE(invoice_date, date) <= %(minus_30)s
                    AND currency_id is not null
                THEN open_due_currency
                ELSE 0.0
            END as b_30_60,
            CASE
                WHEN %(minus_90)s < COALESCE(invoice_date, date)
                    AND COALESCE(invoice_date, date) <= %(minus_60)s
                    AND currency_id is null
                THEN open_due
                WHEN %(minus_90)s < COALESCE(invoice_date, date)
                    AND COALESCE(invoice_date, date) <= %(minus_60)s
                    AND currency_id is not null
                THEN open_due_currency
                ELSE 0.0
            END as b_60_90,
            CASE
                WHEN %(minus_120)s < COALESCE(invoice_date, date)
                    AND COALESCE(invoice_date, date) <= %(minus_90)s
                    AND currency_id is null
                THEN open_due
                WHEN %(minus_120)s < COALESCE(invoice_date, date)
                    AND COALESCE(invoice_date, date) <= %(minus_90)s
                    AND currency_id is not null
                THEN open_due_currency
                ELSE 0.0
            END as b_90_120,
            CASE
                WHEN COALESCE(invoice_date, date) <= %(minus_120)s
                    AND currency_id is null
                THEN open_due
                WHEN COALESCE(invoice_date, date) <= %(minus_120)s
                    AND currency_id is not null 
                THEN open_due_currency
                ELSE 0.0
            END as b_over_120
            FROM Q1
            -- GROUP BY partner_id, currency_id, date_maturity, open_due, open_due_currency, move_id, company_id
        """,
                locals(),
            ),
            "utf-8",
        )

    def _show_buckets_sql_q3(self, company_id):
        company_id = [company_id]
        company = self.env['res.company'].sudo().browse(company_id)
        if company.child_ids:
            company_id += company.child_ids.ids
        return str(
            self._cr.mogrify(
                """
            SELECT Q2.partner_id, current, b_1_30, b_30_60, b_60_90, b_90_120,
                                b_over_120,
            COALESCE(Q2.currency_id, c.currency_id) AS currency_id
            FROM Q2
            JOIN res_company c ON (c.id = Q2.company_id)
            WHERE c.id = ANY(%(company_id)s)
        """,
                locals(),
            ),
            "utf-8",
        )

    def _show_buckets_sql_q4(self):
        return """
            SELECT partner_id, currency_id, sum(current) as current,
                sum(b_1_30) as b_1_30, sum(b_30_60) as b_30_60,
                sum(b_60_90) as b_60_90, sum(b_90_120) as b_90_120,
                sum(b_over_120) as b_over_120
            FROM Q3
            GROUP BY partner_id, currency_id
        """

    def _get_bucket_dates(self, date_end, aging_type):
        return getattr(
            self, f"_get_bucket_dates_{aging_type}", self._get_bucket_dates_days
        )(date_end)

    def _get_bucket_dates_days(self, date_end):
        return {
            "date_end": date_end,
            "minus_30": date_end - timedelta(days=30),
            "minus_60": date_end - timedelta(days=60),
            "minus_90": date_end - timedelta(days=90),
            "minus_120": date_end - timedelta(days=120),
        }

    def _get_bucket_dates_months(self, date_end):
        res = {}
        d = date_end
        for k in ("date_end", "minus_30", "minus_60", "minus_90", "minus_120"):
            res[k] = d
            d = d.replace(day=1) - timedelta(days=1)
        return res

    def _get_account_show_buckets(
        self, company_id, partner_ids, date_end, account_type, aging_type
    ):
        buckets = dict(map(lambda x: (x, []), partner_ids))
        partners = tuple(partner_ids)
        full_dates = self._get_bucket_dates(date_end, aging_type)
        # pylint: disable=E8103
        # All input queries are properly escaped - false positive
        sqlstr = """
            WITH Q1 AS ({}),
                Q2 AS ({}),
                Q3 AS ({}),
                Q4 AS ({})
            SELECT partner_id, currency_id, current, b_1_30, b_30_60, b_60_90,
                b_90_120, b_over_120,
                current+b_1_30+b_30_60+b_60_90+b_90_120+b_over_120
                AS balance
            FROM Q4
            GROUP BY partner_id, currency_id, current, b_1_30, b_30_60,
                b_60_90, b_90_120, b_over_120""".format(
                self._show_buckets_sql_q1(partners, date_end, account_type),
                self._show_buckets_sql_q2(
                    full_dates["date_end"],
                    full_dates["minus_30"],
                    full_dates["minus_60"],
                    full_dates["minus_90"],
                    full_dates["minus_120"],
                ),
                self._show_buckets_sql_q3(company_id),
                self._show_buckets_sql_q4(),
            )
        self.env.cr.execute(sqlstr)
        for row in self.env.cr.dictfetchall():
            buckets[row.pop("partner_id")].append(row)
        return buckets

    def _get_bucket_labels(self, date_end, aging_type):
        return getattr(
            self, f"_get_bucket_labels_{aging_type}", self._get_bucket_dates_days
        )(date_end)

    def _get_bucket_labels_days(self, date_end):
        return [
            _("Current"),
            _("1 - 30 Days"),
            _("31 - 60 Days"),
            _("61 - 90 Days"),
            _("91 - 120 Days"),
            _("121 Days +"),
            _("Total"),
        ]

    def _get_bucket_labels_months(self, date_end):
        return [
            _("Current"),
            _("1 Month"),
            _("2 Months"),
            _("3 Months"),
            _("4 Months"),
            _("Older"),
            _("Total"),
        ]

    def _get_line_currency_defaults(
        self, currency_id, currencies, balance_forward, amount_due
    ):
        if currency_id not in currencies:
            # This will only happen if currency is inactive
            currencies[currency_id] = self.env["res.currency"].browse(currency_id)
        return (
            {
                "prior_lines": [],
                "lines": [],
                "ending_lines": [],
                "buckets": [],
                "balance_forward": balance_forward,
                "amount_due": amount_due,
                "ending_balance": 0.0,
            },
            currencies,
        )

    def _add_currency_line(self, line, currency):
        return [line]

    def _add_currency_prior_line(self, line, currency):
        return [line]

    def _add_currency_ending_line(self, line, currency):
        return [line]

    @api.model
    def _get_report_values(self, docids, data=None):
        # flake8: noqa: C901
        """
        @return: returns a dict of parameters to pass to qweb report.
          the most important pair is {'data': res} which contains all
          the data for each partner.  It is structured like:
            {partner_id: {
                'start': date string,
                'end': date_string,
                'today': date_string
                'currencies': {
                    currency_id: {
                        'lines': [{'date': date string, ...}, ...],
                        'balance_forward': float,
                        'amount_due': float,
                        'buckets': {
                            'p1': float, 'p2': ...
                  }
              }
          }
        }
        """
        company_id = data["company_id"]
        partner_ids = data["partner_ids"]
        date_start = data.get("date_start")
        if date_start and isinstance(date_start, str):
            date_start = datetime.strptime(
                date_start, "%Y-%m-%d"
            ).date()
        date_end = data["date_end"]
        if isinstance(date_end, str):
            date_end = datetime.strptime(date_end, "%Y-%m-%d").date()
        account_type = data["account_type"]
        excluded_accounts_ids = data["excluded_accounts_ids"]
        if excluded_accounts_ids:
            self = self.with_context(
                excluded_accounts_ids=excluded_accounts_ids,
            )
        show_only_overdue = data["show_only_overdue"]
        if show_only_overdue:
            self = self.with_context(
                show_only_overdue=show_only_overdue,
            )
        no_followup = data["no_followup"]
        if no_followup:
            self = self.with_context(
                no_followup=no_followup,
            )
        aging_type = data["aging_type"]
        is_activity = data.get("is_activity")
        is_detailed = data.get("is_detailed")
        today = fields.Date.context_today(self)
        amount_field = data.get("amount_field", "amount")

        # There should be relatively few of these, so to speed performance
        # we cache them - default needed if partner lang not set
        self._cr.execute(
            """
            SELECT p.id, l.date_format
            FROM res_partner p LEFT JOIN res_lang l ON p.lang=l.code
            WHERE p.id IN %(partner_ids)s
            """,
            {"partner_ids": tuple(partner_ids)},
        )
        date_formats = {r[0]: r[1] for r in self._cr.fetchall()}
        #default_fmt = self.env["res.lang"]._lang_get(self.env.user.lang).date_format
        default_fmt = "%Y-%m-%d"
        currencies = {x.id: x for x in self.env["res.currency"].search([])}

        res = {}
        # get base data
        prior_day = date_start # - timedelta(days=1) if date_start else None
        prior_lines = (
            self._get_account_display_prior_lines(
                company_id, partner_ids, prior_day, prior_day, account_type
            )
            if is_detailed
            else {}
        )
        lines = self._get_account_display_lines(
            company_id, partner_ids, date_start, date_end, account_type
        )
        ending_lines = (
            self._get_account_display_ending_lines(
                company_id, partner_ids, date_start, date_end, account_type
            )
            if is_detailed
            else {}
        )
        reconciled_lines = (
            self._get_account_display_reconciled_lines(
                company_id, partner_ids, date_start, date_end, account_type
            )
            if is_activity
            else {}
        )
        balances_forward = self._get_account_initial_balance(
            company_id, partner_ids, date_start, account_type
        )

        if data["show_aging_buckets"]:
            buckets = self._get_account_show_buckets(
                company_id, partner_ids, date_end, account_type, aging_type
            )
            bucket_labels = self._get_bucket_labels(date_end, aging_type)
        else:
            bucket_labels = {}

        # organize and format for report
        format_date = self._format_date_to_partner_lang
        partners_to_remove = set()
        for partner_id in partner_ids:
            res[partner_id] = {
                "today": today, #format_date(today, date_formats.get(partner_id, default_fmt)),
                "start": date_start.strftime("%d/%m/%Y") if date_start else None, #format_date( date_start, default_fmt  ),
                "end": date_end.strftime("%d/%m/%Y"), #format_date(date_end, default_fmt),
                "end_date": date_end,
                "end_str": date_end.strftime("%d/%m/%Y"),
                "prior_day": prior_day.strftime("%d/%m/%Y") if prior_day else None, #format_date(                    prior_day, date_formats.get(partner_id, default_fmt)  ),
                "currencies": {},
                "balance_forward": self._get_opening_balance(date_start, partner_id, company_id)
            }
            currency_dict = res[partner_id]["currencies"]

            for line in balances_forward.get(partner_id, []):
                (
                    currency_dict[line["currency_id"]],
                    currencies,
                ) = self._get_line_currency_defaults(
                    line["currency_id"],
                    currencies,
                    line["balance"],
                    0.0 if is_detailed else line["balance"]
                )

            for line in prior_lines.get(partner_id, []):
                if line["currency_id"] not in currency_dict:
                    (
                        currency_dict[line["currency_id"]],
                        currencies,
                    ) = self._get_line_currency_defaults(
                        line["currency_id"], currencies, 0.0, 0.0
                    )
                line_currency = currency_dict[line["currency_id"]]
                # if not line["no_followup"]:
                #     line_currency["amount_due"] += line[amount_field]
                line_currency["amount_due"] += line["open_amount"]
                line["balance"] = line_currency["amount_due"]
                line["date"] = format_date(
                    line["date"], date_formats.get(partner_id, default_fmt)
                )
                line["invoice_date"] = format_date(
                    line.get("invoice_date"), date_formats.get(partner_id, default_fmt)
                )
                line["statement_date_str"] = format_date(
                    line.get("statement_date"), "%d/%m/%Y"
                )
                line["statement_due_date_str"] = format_date(
                    line.get("statement_due_date"), "%d/%m/%Y"
                )
                line["date_maturity"] = format_date(
                    line["date_maturity"], date_formats.get(partner_id, default_fmt)
                )
                line_currency["prior_lines"].extend(
                    self._add_currency_prior_line(line, currencies[line["currency_id"]])
                )

            for line in lines[partner_id]:
                if line["currency_id"] not in currency_dict:
                    (
                        currency_dict[line["currency_id"]],
                        currencies,
                    ) = self._get_line_currency_defaults(
                        line["currency_id"], currencies, 0.0, 0.0
                    )
                line_currency = currency_dict[line["currency_id"]]
                if not is_activity:
                    line_currency["amount_due"] += line[amount_field]
                    line["balance"] = line_currency["amount_due"]
                else:
                    line_currency["ending_balance"] += line[amount_field]
                    line["balance"] = line_currency["ending_balance"]
                line["outside-date-rank"] = False
                # line["date"] = format_date(
                #     line["date"], date_formats.get(partner_id, default_fmt)
                # )
                # line["invoice_date"] = format_date(
                #     line["invoice_date"], date_formats.get(partner_id, default_fmt)
                # )
                line["statement_date_str"] = format_date(
                    line.get("statement_date"), "%d/%m/%Y"
                )
                line["statement_due_date_str"] = format_date(
                    line.get("statement_due_date"), "%d/%m/%Y"
                )
                # line["date_maturity"] = format_date(
                #     line["date_maturity"], date_formats.get(partner_id, default_fmt)
                # )
                line["reconciled_line"] = False
                if is_activity:
                    line["open_amount"] = 0.0
                    line["applied_amount"] = 0.0
                line_currency["lines"].extend( 
                    self._add_currency_line(line, currencies[line["currency_id"]])
                )
                for line2 in reconciled_lines:
                    if line2["id"] in line["ids"]:
                        line2["reconciled_line"] = True
                        line2["applied_amount"] = line2["open_amount"]
                        if line2["date"] >= date_start and line2["date"] <= date_end:
                            line2["outside-date-rank"] = False
                            line["applied_amount"] += line2["open_amount"]
                        else:
                            line2["outside-date-rank"] = True
                        line2["date"] = format_date(
                            line2["date"], date_formats.get(partner_id, default_fmt)
                        )
                        line2["date_maturity"] = format_date(
                            line2["date_maturity"],
                            date_formats.get(partner_id, default_fmt),
                        )
                        if is_detailed:
                            line_currency["lines"].extend(
                                self._add_currency_line(
                                    line2, currencies[line["currency_id"]]
                                )
                            )
                if is_activity:
                    line["open_amount"] = line["amount"] + line["applied_amount"]
                    line_currency["amount_due"] += line["open_amount"]

            if is_detailed:
                for line_currency in currency_dict.values():
                    line_currency["amount_due"] = 0.0

            for line in ending_lines.get(partner_id, []):
                line_currency = currency_dict[line["currency_id"]]
                line_currency["amount_due"] += line["open_amount"]
                if not is_activity:
                    line["balance"] = line_currency["amount_due"] 
                else:
                    line["balance"] = line_currency["ending_balance"]
                line["date"] = format_date(
                    line["date"], date_formats.get(partner_id, default_fmt)
                )
                line["invoice_date"] = format_date(
                    line.get("invoice_date"), date_formats.get(partner_id, default_fmt)
                )
                line["statement_date_str"] = format_date(
                    line.get("statement_date"), "%d/%m/%Y"
                )
                line["statement_due_date_str"] = format_date(
                    line.get("statement_due_date"), "%d/%m/%Y"
                )
                line["date_maturity"] = format_date(
                    line["date_maturity"], date_formats.get(partner_id, default_fmt)
                )
                line_currency["ending_lines"].extend(
                    self._add_currency_ending_line(
                        line, currencies[line["currency_id"]]
                    )
                )

            if data["show_aging_buckets"]:
                for line in buckets[partner_id]:
                    if line["currency_id"] not in currency_dict:
                        (
                            currency_dict[line["currency_id"]],
                            currencies,
                        ) = self._get_line_currency_defaults(
                            line["currency_id"], currencies, 0.0, 0.0
                        )
                    line_currency = currency_dict[line["currency_id"]]
                    line_currency["buckets"] = line

            if len(partner_ids) > 1:
                values = currency_dict.values()
                if not any([v["lines"] or v["balance_forward"] for v in values]):
                    if data["filter_non_due_partners"]:
                        partners_to_remove.add(partner_id)
                        continue
                    else:
                        res[partner_id]["no_entries"] = True
                if data["filter_negative_balances"]:
                    if not all([v["amount_due"] >= 0.0 for v in values]):
                        partners_to_remove.add(partner_id)

        for partner in partners_to_remove:
            del res[partner]
            partner_ids.remove(partner)

        return {
            "doc_ids": partner_ids,
            "doc_model": "res.partner",
            "docs": self.env["res.partner"].browse(partner_ids),
            "data": res,
            "company": self.env["res.company"].browse(company_id),
            "Currencies": currencies,
            "account_type": account_type,
            "excluded_accounts_ids": excluded_accounts_ids,
            "show_only_overdue": show_only_overdue,
            "is_detailed": is_detailed,
            "bucket_labels": bucket_labels,
            "get_inv_addr": self._get_invoice_address,
            "get_title": self._get_title,
            "get_aging_buckets_title": self._get_aging_buckets_title,
        }