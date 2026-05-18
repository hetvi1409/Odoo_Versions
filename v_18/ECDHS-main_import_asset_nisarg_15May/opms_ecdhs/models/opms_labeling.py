import json

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource
from odoo.tools.convert import convert_file


OPMS_LABEL_DEFINITIONS = {
    "app_plan": {
        "title": "APP Plans",
        "default": {"singular": "APP Plan", "plural": "APP Plans"},
        "options": {
            "default": {"label": "APP Plans", "singular": "APP Plan", "plural": "APP Plans"},
            "portfolio": {"label": "Portfolios", "singular": "Portfolio", "plural": "Portfolios"},
        },
    },
    "programme": {
        "title": "Programmes",
        "default": {"singular": "Programme", "plural": "Programmes"},
        "options": {
            "default": {"label": "Programmes", "singular": "Programme", "plural": "Programmes"},
            "project": {"label": "Projects", "singular": "Project", "plural": "Projects"},
        },
    },
    "sub_programme": {
        "title": "Sub-Programmes",
        "default": {"singular": "Sub-Programme", "plural": "Sub-Programmes"},
        "options": {
            "default": {"label": "Sub-Programmes", "singular": "Sub-Programme", "plural": "Sub-Programmes"},
            "sub_project": {"label": "Sub-Projects", "singular": "Sub-Project", "plural": "Sub-Projects"},
        },
    },
    "directorate": {
        "title": "Directorates",
        "default": {"singular": "Directorate", "plural": "Directorates"},
        "options": {
            "default": {"label": "Directorates", "singular": "Directorate", "plural": "Directorates"},
            "child_sub_programme": {
                "label": "Child-Sub-Programmes",
                "singular": "Child-Sub-Programme",
                "plural": "Child-Sub-Programmes",
            },
            "child_sub_project": {
                "label": "Child-Sub-Projects",
                "singular": "Child-Sub-Project",
                "plural": "Child-Sub-Projects",
            },
        },
    },
    "outcome": {
        "title": "Outcomes",
        "default": {"singular": "Outcome", "plural": "Outcomes"},
        "options": {
            "default": {"label": "Outcomes", "singular": "Outcome", "plural": "Outcomes"},
            "strategy": {"label": "Strategies", "singular": "Strategy", "plural": "Strategies"},
            "key_performance_area": {
                "label": "Key Performance Areas",
                "singular": "Key Performance Area",
                "plural": "Key Performance Areas",
            },
        },
    },
    "output": {
        "title": "Outputs",
        "default": {"singular": "Output", "plural": "Outputs"},
        "options": {
            "default": {"label": "Outputs", "singular": "Output", "plural": "Outputs"},
            "goal": {"label": "Goals", "singular": "Goal", "plural": "Goals"},
            "strategic_objective": {
                "label": "Strategic Objectives",
                "singular": "Strategic Objective",
                "plural": "Strategic Objectives",
            },
        },
    },
    "output_indicator": {
        "title": "Output Indicators",
        "default": {"singular": "Output Indicator", "plural": "Output Indicators"},
        "options": {
            "default": {
                "label": "Output Indicators",
                "singular": "Output Indicator",
                "plural": "Output Indicators",
            },
            "objective": {"label": "Objectives", "singular": "Objective", "plural": "Objectives"},
            "key_performance_indicator": {
                "label": "Key Performance Indicators",
                "singular": "Key Performance Indicator",
                "plural": "Key Performance Indicators",
            },
        },
    },
    "annual": {
        "title": "Annuals",
        "default": {"singular": "Annual", "plural": "Annuals"},
        "options": {
            "default": {"label": "Annuals", "singular": "Annual", "plural": "Annuals"},
            "long_term_plan": {
                "label": "Long Term Plans",
                "singular": "Long Term Plan",
                "plural": "Long Term Plans",
            },
        },
    },
    "quarterly_target": {
        "title": "Quarterly Targets",
        "default": {"singular": "Quarterly Target", "plural": "Quarterly Targets"},
        "options": {
            "default": {
                "label": "Quarterly Targets",
                "singular": "Quarterly Target",
                "plural": "Quarterly Targets",
            },
            "medium_term_plan": {
                "label": "Medium Term Plans",
                "singular": "Medium Term Plan",
                "plural": "Medium Term Plans",
            },
        },
    },
    "quarter": {
        "title": "Quarters",
        "default": {"singular": "Quarter", "plural": "Quarters"},
        "options": {
            "default": {"label": "Quarters", "singular": "Quarter", "plural": "Quarters"},
            "short_term_plan": {
                "label": "Short Term Plans",
                "singular": "Short Term Plan",
                "plural": "Short Term Plans",
            },
        },
    },
}


class OpmsLabelService(models.AbstractModel):
    _name = "opms.label.service"
    _description = "OPMS Dynamic Label Service"

    @api.model
    def _param_key(self, term_key, suffix):
        return f"opms_ecdhs.labels.{term_key}.{suffix}"

    @api.model
    def _get_custom_overrides(self):
        value = self.env["ir.config_parameter"].sudo().get_param("opms_ecdhs.labels.custom_overrides", "{}")
        try:
            parsed = json.loads(value or "{}")
        except Exception:
            parsed = {}
        if not isinstance(parsed, dict):
            return {}
        return {str(k): str(v) for k, v in parsed.items() if str(k).strip() and str(v).strip()}

    @api.model
    def get_effective_terms(self):
        params = self.env["ir.config_parameter"].sudo()
        terms = {}
        for key, definition in OPMS_LABEL_DEFINITIONS.items():
            option_key = params.get_param(self._param_key(key, "option"), "default")
            option_map = definition["options"]
            if option_key == "other":
                singular = (params.get_param(self._param_key(key, "other_singular"), "") or "").strip()
                plural = (params.get_param(self._param_key(key, "other_plural"), "") or "").strip()
                singular = singular or definition["default"]["singular"]
                plural = plural or definition["default"]["plural"]
            else:
                selected = option_map.get(option_key) or option_map["default"]
                singular = selected["singular"]
                plural = selected["plural"]
            terms[key] = {
                "singular": singular,
                "plural": plural,
                "option": option_key,
                "title": definition["title"],
                "default_singular": definition["default"]["singular"],
                "default_plural": definition["default"]["plural"],
            }
        return terms

    @api.model
    def get_runtime_replacements(self):
        terms = self.get_effective_terms()
        replacements = {}
        for _key, data in terms.items():
            source_singular = data["default_singular"]
            source_plural = data["default_plural"]
            replacements[source_singular] = data["singular"]
            replacements[source_plural] = data["plural"]

        custom_overrides = self._get_custom_overrides()
        replacements.update(custom_overrides)
        return {
            "terms": terms,
            "replacements": replacements,
        }

    @api.model
    def apply_backend_labels(self):
        data = self.get_runtime_replacements()
        terms = data["terms"]
        menu_values = {
            "opms_ecdhs.menu_opms_planning_root": terms["programme"]["plural"],
            "opms_ecdhs.menu_opms_outputs_root": terms["output"]["plural"],
            "opms_ecdhs.menu_opms_annuals_root": terms["annual"]["plural"],
            "opms_ecdhs.menu_opms_quarters_root": terms["quarter"]["plural"],
            "opms_ecdhs.menu_opms_app_plan": terms["app_plan"]["plural"],
            "opms_ecdhs.menu_opms_programme": terms["programme"]["plural"],
            "opms_ecdhs.menu_opms_sub_programme": terms["sub_programme"]["plural"],
            "opms_ecdhs.menu_opms_directorate": terms["directorate"]["plural"],
            "opms_ecdhs.menu_opms_output": terms["output"]["plural"],
            "opms_ecdhs.menu_opms_output_indicator": terms["output_indicator"]["plural"],
            "opms_ecdhs.menu_opms_annual": terms["annual"]["plural"],
            "opms_ecdhs.menu_opms_quarter": terms["quarter"]["plural"],
            "opms_ecdhs.menu_opms_quarterly_target": terms["quarterly_target"]["plural"],
        }
        for xmlid, label in menu_values.items():
            menu = self.env.ref(xmlid, raise_if_not_found=False)
            if menu:
                menu.sudo().write({"name": label})

        action_values = {
            "opms_ecdhs.action_opms_app_plan": terms["app_plan"]["plural"],
            "opms_ecdhs.action_opms_programme": terms["programme"]["plural"],
            "opms_ecdhs.action_opms_sub_programme": terms["sub_programme"]["plural"],
            "opms_ecdhs.action_opms_directorate": terms["directorate"]["plural"],
            "opms_ecdhs.action_opms_output": terms["output"]["plural"],
            "opms_ecdhs.action_opms_output_indicator": terms["output_indicator"]["plural"],
            "opms_ecdhs.action_opms_annual": terms["annual"]["plural"],
            "opms_ecdhs.action_opms_quarter": terms["quarter"]["plural"],
            "opms_ecdhs.action_opms_quarterly_target": terms["quarterly_target"]["plural"],
        }
        for xmlid, label in action_values.items():
            action = self.env.ref(xmlid, raise_if_not_found=False)
            if action:
                action.sudo().write({"name": label})

        self._apply_hard_bound_backend_strings(terms)

    @api.model
    def _apply_hard_bound_backend_strings(self, terms):
        replacements = self._hard_bound_replacements(terms)
        self._apply_replacements_to_module_views(replacements)
        self._apply_replacements_to_module_mail_templates(replacements)

    @api.model
    def _hard_bound_replacements(self, terms):
        replacements = {
            "APP Plans": terms["app_plan"]["plural"],
            "APP Plan": terms["app_plan"]["singular"],
            "Programmes": terms["programme"]["plural"],
            "Programme": terms["programme"]["singular"],
            "Sub-Programmes": terms["sub_programme"]["plural"],
            "Sub-Programme": terms["sub_programme"]["singular"],
            "Directorates": terms["directorate"]["plural"],
            "Directorate": terms["directorate"]["singular"],
            "Outputs": terms["output"]["plural"],
            "Output": terms["output"]["singular"],
            "Output Output Indicators": terms["output_indicator"]["plural"],
            "Output Output Indicator": terms["output_indicator"]["singular"],
            "Output Indicators": terms["output_indicator"]["plural"],
            "Output Indicator": terms["output_indicator"]["singular"],
            "Annual Targets": terms["annual"]["plural"],
            "Indicator Years": terms["annual"]["plural"],
            "Indicator Year": terms["annual"]["singular"],
            "Quarterly Targets": terms["quarterly_target"]["plural"],
            "Quarterly Target": terms["quarterly_target"]["singular"],
            "Qtrly Targets": terms["quarterly_target"]["plural"],
            "Quarters": terms["quarter"]["plural"],
            "Quarter": terms["quarter"]["singular"],
        }

        custom = self._get_custom_overrides()
        replacements.update(custom)
        return sorted(replacements.items(), key=lambda item: len(item[0]), reverse=True)

    @api.model
    def _module_record_ids(self, model_name):
        data = self.env["ir.model.data"].sudo().search(
            [("module", "=", "opms_ecdhs"), ("model", "=", model_name)]
        )
        return data.mapped("res_id")

    @api.model
    def _replace_text(self, content, replacements):
        if not content:
            return content
        updated = content
        for source, target in replacements:
            if source and target and source != target:
                updated = updated.replace(source, target)
        return updated

    @api.model
    def _apply_replacements_to_module_views(self, replacements):
        excluded_view_xmlids = {
            "view_res_config_settings_opms_dedicated",
            "view_res_config_settings_opms_dynamic_labels",
        }
        model_data = self.env["ir.model.data"].sudo().search(
            [
                ("module", "=", "opms_ecdhs"),
                ("model", "=", "ir.ui.view"),
                ("name", "not in", list(excluded_view_xmlids)),
            ]
        )
        view_ids = model_data.mapped("res_id")
        if not view_ids:
            return
        views = self.env["ir.ui.view"].sudo().browse(view_ids).exists()
        for view in views:
            arch = view.arch_db or ""
            updated_arch = self._replace_text(arch, replacements)
            if updated_arch != arch:
                view.write({"arch_db": updated_arch})

    @api.model
    def _apply_replacements_to_module_mail_templates(self, replacements):
        template_ids = self._module_record_ids("mail.template")
        if not template_ids:
            return
        templates = self.env["mail.template"].sudo().browse(template_ids).exists()
        for template in templates:
            values = {}
            subject = template.subject or ""
            body = template.body_html or ""
            updated_subject = self._replace_text(subject, replacements)
            updated_body = self._replace_text(body, replacements)
            if updated_subject != subject:
                values["subject"] = updated_subject
            if updated_body != body:
                values["body_html"] = updated_body
            if values:
                template.write(values)


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    opms_enable_narratives = fields.Boolean(
        string="Enable Narratives",
        default=False,
        help="When disabled, the Narrative field is hidden on the portal submission form and the Narratives columns are removed from the indicator results table.",
    )

    opms_custom_label_overrides = fields.Text(
        string="Custom Label Overrides (JSON)",
        help='Optional JSON map for future terms, for example: {"Legacy Label": "New Label"}.',
    )

    opms_access_level = fields.Selection(
        [
            ("off", "No Limits"),
            ("basic", "Basic (Submissions and Related Data)"),
            ("strict", "Strict (All OPMS Data Lists and Records)"),
        ],
        string="Data Access Level",
        default="off",
        config_parameter="opms_ecdhs.access.level",
        help="Choose how strongly OPMS data visibility is restricted.",
    )
    opms_limit_company = fields.Boolean(
        string="Limit Users To Their Region/Office",
        default=False,
        config_parameter="opms_ecdhs.access.limit_company",
    )
    opms_limit_programme = fields.Boolean(
        string="Limit Users To Their Programmes",
        default=False,
        config_parameter="opms_ecdhs.access.limit_programme",
    )
    opms_limit_sub_programme = fields.Boolean(
        string="Limit Users To Their Sub-Programmes",
        default=False,
        config_parameter="opms_ecdhs.access.limit_sub_programme",
    )
    opms_limit_directorate = fields.Boolean(
        string="Limit Users To Their Directorates",
        default=False,
        config_parameter="opms_ecdhs.access.limit_directorate",
    )
    opms_empty_behavior = fields.Selection(
        [
            ("allow", "If no assignment, show all"),
            ("deny", "If no assignment, show nothing"),
        ],
        string="If Nothing Is Assigned",
        default="allow",
        config_parameter="opms_ecdhs.access.empty_behavior",
    )
    opms_require_active_profile = fields.Boolean(
        string="Require Active OPMS User Profile",
        default=False,
        config_parameter="opms_ecdhs.access.require_active_profile",
        help="If enabled, users without an active OPMS profile cannot access scoped OPMS data.",
    )
    opms_applies_to = fields.Selection(
        [
            ("profiled", "Users with OPMS User Profiles"),
            ("opms_groups", "Users in OPMS Role Groups"),
            ("both", "Both of the Above"),
        ],
        string="Apply Limits To",
        default="profiled",
        config_parameter="opms_ecdhs.access.applies_to",
    )
    opms_admin_bypass = fields.Boolean(
        string="Allow System Admin Users To See Everything",
        default=True,
        config_parameter="opms_ecdhs.access.admin_bypass",
    )

    opms_app_import_notify_step = fields.Integer(
        string="APP Import Progress Notify Step",
        default=250,
        config_parameter="opms_ecdhs.app_import_notify_step",
        help="Show an APP import progress checkpoint after this many processed rows.",
    )
    opms_app_import_history_batch_size = fields.Integer(
        string="APP Import History Batch Size",
        default=500,
        config_parameter="opms_ecdhs.app_import_history_batch_size",
        help="Number of import history line records inserted per batch during APP import.",
    )
    opms_copy_previous_notify_step = fields.Integer(
        string="Copy Previous Progress Notify Step",
        default=1,
        config_parameter="opms_ecdhs.copy_previous_notify_step",
        help="Show a copy-progress checkpoint after this many APP Plans are processed.",
    )
    opms_demo_seed_chunk_size = fields.Integer(
        string="Demo Seed Chunk Size",
        default=300,
        config_parameter="opms_ecdhs.demo_seed_chunk_size",
        help="Number of demo submissions created per chunk.",
    )
    opms_demo_seed_prep_notify_step = fields.Integer(
        string="Demo Seed Preparation Notify Step",
        default=500,
        config_parameter="opms_ecdhs.demo_seed_prep_notify_step",
        help="Show a demo seed preparation checkpoint after this many targets are scanned.",
    )
    opms_demo_seed_create_notify_every_chunks = fields.Integer(
        string="Demo Seed Create Notify Every Chunks",
        default=2,
        config_parameter="opms_ecdhs.demo_seed_create_notify_every_chunks",
        help="Show a demo seed creation checkpoint after this many create chunks.",
    )

    for _term_key, _definition in OPMS_LABEL_DEFINITIONS.items():
        _selection = [
            ("default", _definition["options"]["default"]["label"]),
        ]
        for _option_key, _option in _definition["options"].items():
            if _option_key == "default":
                continue
            _selection.append((_option_key, _option["label"]))
        _selection.append(("other", "Other"))

        locals()[f"opms_{_term_key}_option"] = fields.Selection(
            selection=_selection,
            string=f"{_definition['title']} option",
            default="default",
            config_parameter=f"opms_ecdhs.labels.{_term_key}.option",
        )
        locals()[f"opms_{_term_key}_other_singular"] = fields.Char(
            string=f"{_definition['title']} custom singular",
            config_parameter=f"opms_ecdhs.labels.{_term_key}.other_singular",
        )
        locals()[f"opms_{_term_key}_other_plural"] = fields.Char(
            string=f"{_definition['title']} custom plural",
            config_parameter=f"opms_ecdhs.labels.{_term_key}.other_plural",
        )

    del _term_key, _definition, _selection

    @api.model
    def get_values(self):
        values = super().get_values()
        values["opms_custom_label_overrides"] = self.env["ir.config_parameter"].sudo().get_param(
            "opms_ecdhs.labels.custom_overrides", "{}"
        )
        values["opms_enable_narratives"] = self.env["ir.config_parameter"].sudo().get_param(
            "opms_ecdhs.enable_narratives", "0"
        ) != "0"
        return values

    def set_values(self):
        self.ensure_one()
        self._validate_custom_overrides_json()
        result = super().set_values()
        self.env["ir.config_parameter"].sudo().set_param(
            "opms_ecdhs.labels.custom_overrides", (self.opms_custom_label_overrides or "").strip() or "{}"
        )
        self.env["ir.config_parameter"].sudo().set_param(
            "opms_ecdhs.enable_narratives", "1" if self.opms_enable_narratives else "0"
        )
        self.env["opms.label.service"].apply_backend_labels()
        self.env["opms.access.policy.service"].sudo().apply_policy()
        return result

    def _validate_custom_overrides_json(self):
        raw = (self.opms_custom_label_overrides or "").strip() or "{}"
        try:
            parsed = json.loads(raw)
        except Exception as exc:
            raise ValidationError(f"Custom label overrides must be valid JSON: {exc}")
        if not isinstance(parsed, dict):
            raise ValidationError("Custom label overrides JSON must be an object/dictionary.")
        for key, value in parsed.items():
            if not str(key).strip() or not str(value).strip():
                raise ValidationError("Custom label override keys and values must be non-empty strings.")

    @api.constrains(
        "opms_app_import_notify_step",
        "opms_app_import_history_batch_size",
        "opms_copy_previous_notify_step",
        "opms_demo_seed_chunk_size",
        "opms_demo_seed_prep_notify_step",
        "opms_demo_seed_create_notify_every_chunks",
    )
    def _check_opms_performance_tuning_values(self):
        for record in self:
            checks = [
                ("APP Import Progress Notify Step", record.opms_app_import_notify_step, 50, 5000),
                ("APP Import History Batch Size", record.opms_app_import_history_batch_size, 100, 5000),
                ("Copy Previous Progress Notify Step", record.opms_copy_previous_notify_step, 1, 100),
                ("Demo Seed Chunk Size", record.opms_demo_seed_chunk_size, 50, 2000),
                ("Demo Seed Preparation Notify Step", record.opms_demo_seed_prep_notify_step, 100, 10000),
                ("Demo Seed Create Notify Every Chunks", record.opms_demo_seed_create_notify_every_chunks, 1, 50),
            ]
            for label, value, min_value, max_value in checks:
                if value < min_value or value > max_value:
                    raise ValidationError(
                        f"{label} must be between {min_value} and {max_value}."
                    )

    def action_reset_opms_labels_to_defaults(self):
        if self:
            self.ensure_one()
        module_name = "opms_ecdhs"
        xml_files = [
            "data/opms_submission_reminder_templates.xml",
            "views/opms_views.xml",
            "views/opms_import_wizard_views.xml",
            "views/opms_submission_period_wizard_views.xml",
            "views/opms_submission_reminder_wizard_views.xml",
            "views/opms_user_groups_views.xml",
            "views/opms_settings_views.xml",
            "views/opms_menus.xml",
            "views/portal_templates/opms_portal_submission_templates.xml",
            "views/portal_templates/opms_portal_all_submissions.xml",
        ]

        for file_path in xml_files:
            absolute_path = get_module_resource(module_name, file_path)
            if not absolute_path:
                raise ValidationError(f"Could not locate module source file: {file_path}")
            convert_file(self.env, module_name, file_path, {}, mode="update", noupdate=False, kind="data")

        params = self.env["ir.config_parameter"].sudo()
        for key in OPMS_LABEL_DEFINITIONS:
            params.set_param(f"opms_ecdhs.labels.{key}.option", "default")
            params.set_param(f"opms_ecdhs.labels.{key}.other_singular", "")
            params.set_param(f"opms_ecdhs.labels.{key}.other_plural", "")
        params.set_param("opms_ecdhs.labels.custom_overrides", "{}")

        self.env["opms.label.service"].apply_backend_labels()

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "OPMS Labels Reset",
                "message": "OPMS labels were restored from module source and reset to defaults.",
                "type": "success",
                "sticky": False,
                "next": {"type": "ir.actions.client", "tag": "reload"},
            },
        }

    def action_reset_opms_access_to_relaxed_defaults(self):
        if self:
            self.ensure_one()

        params = self.env["ir.config_parameter"].sudo()
        relaxed_defaults = {
            "opms_ecdhs.access.level": "off",
            "opms_ecdhs.access.limit_company": "0",
            "opms_ecdhs.access.limit_programme": "0",
            "opms_ecdhs.access.limit_sub_programme": "0",
            "opms_ecdhs.access.limit_directorate": "0",
            "opms_ecdhs.access.empty_behavior": "allow",
            "opms_ecdhs.access.require_active_profile": "0",
            "opms_ecdhs.access.applies_to": "profiled",
            "opms_ecdhs.access.admin_bypass": "1",
        }
        for key, value in relaxed_defaults.items():
            params.set_param(key, value)

        self.env["opms.access.policy.service"].sudo().apply_policy()

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "OPMS Access Controls Reset",
                "message": "All OPMS access controls were reset to relaxed defaults.",
                "type": "success",
                "sticky": False,
                "next": {"type": "ir.actions.client", "tag": "reload"},
            },
        }