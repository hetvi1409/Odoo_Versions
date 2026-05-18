from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = "res.users"
    _description = "Users (OPMS Scope Extension)"

    opms_scope_profile_active = fields.Boolean(string="OPMS Scope Profile Active", default=False, index=True)
    opms_scope_company_id = fields.Many2one("res.company", string="OPMS Scope Company", index=True)
    opms_scope_programme_ids = fields.Many2many(
        "opms.programme",
        "res_users_opms_programme_rel",
        "res_users_id",
        "opms_programme_id",
        string="OPMS Scope Programmes",
    )
    opms_scope_sub_programme_ids = fields.Many2many(
        "opms.sub.programme",
        "res_users_opms_sub_programme_rel",
        "res_users_id",
        "opms_sub_programme_id",
        string="OPMS Scope Sub-Programmes",
    )
    opms_scope_directorate_ids = fields.Many2many(
        "opms.directorate",
        "res_users_opms_directorate_rel",
        "res_users_id",
        "opms_directorate_id",
        string="OPMS Scope Directorates",
    )

    def _sync_opms_scope_from_profile(self):
        users = self.with_context(active_test=False).sudo()
        if not users:
            return

        profiles = (
            self.env["opms.user.management"]
            .with_context(active_test=False)
            .sudo()
            .search([("user_id", "in", users.ids)], order="id desc")
        )
        profile_by_user = {}
        for profile in profiles:
            if profile.user_id.id not in profile_by_user:
                profile_by_user[profile.user_id.id] = profile

        for user in users:
            profile = profile_by_user.get(user.id)
            if profile and profile.active:
                vals = {
                    "opms_scope_profile_active": True,
                    "opms_scope_company_id": profile.company_id.id or False,
                    "opms_scope_programme_ids": [(6, 0, profile.programme_ids.ids)],
                    "opms_scope_sub_programme_ids": [(6, 0, profile.sub_programme_ids.ids)],
                    "opms_scope_directorate_ids": [(6, 0, profile.directorate_ids.ids)],
                }
            else:
                vals = {
                    "opms_scope_profile_active": False,
                    "opms_scope_company_id": False,
                    "opms_scope_programme_ids": [(6, 0, [])],
                    "opms_scope_sub_programme_ids": [(6, 0, [])],
                    "opms_scope_directorate_ids": [(6, 0, [])],
                }
            user.write(vals)


class OpmsAccessPolicyService(models.AbstractModel):
    _name = "opms.access.policy.service"
    _description = "OPMS Access Policy Service"

    def _param_bool(self, key, default=False):
        raw = self.env["ir.config_parameter"].sudo().get_param(key, "1" if default else "0")
        return str(raw).lower() in {"1", "true", "yes", "on"}

    def _param_str(self, key, default):
        return self.env["ir.config_parameter"].sudo().get_param(key, default)

    def _get_policy_config(self):
        return {
            "level": self._param_str("opms_ecdhs.access.level", "off"),
            "limit_company": self._param_bool("opms_ecdhs.access.limit_company", False),
            "limit_programme": self._param_bool("opms_ecdhs.access.limit_programme", False),
            "limit_sub_programme": self._param_bool("opms_ecdhs.access.limit_sub_programme", False),
            "limit_directorate": self._param_bool("opms_ecdhs.access.limit_directorate", False),
            "empty_behavior": self._param_str("opms_ecdhs.access.empty_behavior", "allow"),
            "require_active_profile": self._param_bool("opms_ecdhs.access.require_active_profile", False),
            "applies_to": self._param_str("opms_ecdhs.access.applies_to", "profiled"),
            "admin_bypass": self._param_bool("opms_ecdhs.access.admin_bypass", True),
        }

    def _rule_target_map(self):
        # level: basic = operational data models, strict = include hierarchy models
        return {
            "opms_ecdhs.rule_opms_programme_scoped_access": {
                "level": "strict",
                "company": False,
                "programme": True,
                "sub_programme": False,
                "directorate": False,
                "programme_field": "id",
            },
            "opms_ecdhs.rule_opms_sub_programme_scoped_access": {
                "level": "strict",
                "company": False,
                "programme": True,
                "sub_programme": True,
                "directorate": False,
                "sub_programme_field": "id",
            },
            "opms_ecdhs.rule_opms_directorate_scoped_access": {
                "level": "strict",
                "company": False,
                "programme": True,
                "sub_programme": True,
                "directorate": True,
                "directorate_field": "id",
            },
            "opms_ecdhs.rule_opms_output_scoped_access": {"level": "strict", "company": False, "programme": True, "sub_programme": True, "directorate": True},
            "opms_ecdhs.rule_opms_output_indicator_scoped_access": {"level": "strict", "company": False, "programme": True, "sub_programme": True, "directorate": True},
            "opms_ecdhs.rule_opms_app_plan_scoped_access": {"level": "strict", "company": True, "programme": False, "sub_programme": False, "directorate": False},
            "opms_ecdhs.rule_opms_quarter_scoped_access": {"level": "strict", "company": True, "programme": False, "sub_programme": False, "directorate": False},
            "opms_ecdhs.rule_opms_annual_scoped_access": {"level": "basic", "company": True, "programme": True, "sub_programme": True, "directorate": True},
            "opms_ecdhs.rule_opms_annual_target_scoped_access": {"level": "basic", "company": True, "programme": True, "sub_programme": True, "directorate": True},
            "opms_ecdhs.rule_opms_quarterly_target_scoped_access": {"level": "basic", "company": True, "programme": True, "sub_programme": True, "directorate": True},
            "opms_ecdhs.rule_opms_narrative_scoped_access": {"level": "basic", "company": True, "programme": True, "sub_programme": True, "directorate": True},
            "opms_ecdhs.rule_opms_evidence_scoped_access": {"level": "basic", "company": True, "programme": True, "sub_programme": True, "directorate": True},
            "opms_ecdhs.rule_opms_reporting_submission_scoped_access": {"level": "basic", "company": True, "programme": True, "sub_programme": True, "directorate": True},
        }

    def _expr_for_many2many_scope(self, model_field, user_field, empty_behavior):
        if empty_behavior == "allow":
            return (
                f"([(1,'=',1)] if not user.{user_field}.ids "
                f"else [('{model_field}','in', user.{user_field}.ids)])"
            )
        return f"[('{model_field}','in', user.{user_field}.ids)]"

    def _expr_for_company_scope(self, empty_behavior):
        if empty_behavior == "allow":
            return (
                "([(1,'=',1)] if not user.opms_scope_company_id.id "
                "else [('financial_year.company_id','=', user.opms_scope_company_id.id)])"
            )
        return "[('financial_year.company_id','=', user.opms_scope_company_id.id)]"

    def _build_domain_expression(self, cfg, rule_meta):
        parts = []

        if cfg["require_active_profile"]:
            parts.append("([(1,'=',1)] if user.opms_scope_profile_active else [('id','=',0)])")

        if cfg["limit_company"] and rule_meta.get("company"):
            parts.append(self._expr_for_company_scope(cfg["empty_behavior"]))

        if cfg["limit_programme"] and rule_meta.get("programme"):
            programme_field = rule_meta.get("programme_field", "programme_id")
            parts.append(self._expr_for_many2many_scope(programme_field, "opms_scope_programme_ids", cfg["empty_behavior"]))

        if cfg["limit_sub_programme"] and rule_meta.get("sub_programme"):
            sub_programme_field = rule_meta.get("sub_programme_field", "sub_programme_id")
            parts.append(
                self._expr_for_many2many_scope(sub_programme_field, "opms_scope_sub_programme_ids", cfg["empty_behavior"])
            )

        if cfg["limit_directorate"] and rule_meta.get("directorate"):
            directorate_field = rule_meta.get("directorate_field", "directorate_id")
            parts.append(self._expr_for_many2many_scope(directorate_field, "opms_scope_directorate_ids", cfg["empty_behavior"]))

        if not parts:
            return "[(1,'=',1)]"

        return " + ".join(f"({part})" for part in parts)

    def _get_target_users(self, cfg):
        Users = self.env["res.users"].with_context(active_test=False).sudo()
        target_users = Users.browse()

        if cfg["applies_to"] in {"profiled", "both"}:
            if cfg["require_active_profile"]:
                target_users |= Users.search([("opms_scope_profile_active", "=", True)])
            else:
                profiled = (
                    self.env["opms.user.management"]
                    .with_context(active_test=False)
                    .sudo()
                    .search([])
                    .mapped("user_id")
                )
                target_users |= profiled

        if cfg["applies_to"] in {"opms_groups", "both"}:
            group_xmlids = [
                "opms_ecdhs.group_opms_submissions_user",
                "opms_ecdhs.group_opms_manager",
                "opms_ecdhs.group_opms_director",
            ]
            group_ids = []
            for xmlid in group_xmlids:
                group = self.env.ref(xmlid, raise_if_not_found=False)
                if group:
                    group_ids.append(group.id)
            if group_ids:
                target_users |= Users.search([("groups_id", "in", group_ids)])

        if cfg["admin_bypass"]:
            admin_users = Users.search([
                "|",
                ("groups_id", "in", [self.env.ref("base.group_system").id]),
                ("groups_id", "in", [self.env.ref("base.group_erp_manager").id]),
            ])
            target_users -= admin_users

        return target_users

    def _apply_scoped_group_membership(self, cfg):
        scoped_group = self.env.ref("opms_ecdhs.group_opms_scoped_access", raise_if_not_found=False)
        if not scoped_group:
            return

        all_users = self.env["res.users"].with_context(active_test=False).sudo().search([])
        target_users = self._get_target_users(cfg)
        current_users = scoped_group.users.with_context(active_test=False)

        to_add = target_users - current_users
        to_remove = current_users - target_users

        if to_add:
            to_add.write({"groups_id": [(4, scoped_group.id)]})
        if to_remove:
            to_remove.write({"groups_id": [(3, scoped_group.id)]})

        # Keep user scope cache in sync for both included and excluded users
        (target_users | to_remove)._sync_opms_scope_from_profile()

    def apply_policy(self):
        cfg = self._get_policy_config()

        # Always keep user scope cache current before policy evaluation
        all_profile_users = (
            self.env["opms.user.management"].with_context(active_test=False).sudo().search([]).mapped("user_id")
        )
        if all_profile_users:
            all_profile_users._sync_opms_scope_from_profile()

        self._apply_scoped_group_membership(cfg)

        rule_map = self._rule_target_map()
        for xmlid, meta in rule_map.items():
            rule = self.env.ref(xmlid, raise_if_not_found=False)
            if not rule:
                continue

            level = cfg["level"]
            if level == "off":
                rule.sudo().write({"active": False})
                continue

            if level == "basic" and meta["level"] == "strict":
                rule.sudo().write({"active": False})
                continue

            domain_expression = self._build_domain_expression(cfg, meta)
            rule.sudo().write({
                "domain_force": domain_expression,
                "active": True,
            })
