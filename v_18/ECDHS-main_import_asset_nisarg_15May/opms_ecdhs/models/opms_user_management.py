from odoo import api, fields, models
from odoo.exceptions import ValidationError


class OpmsUserManagement(models.Model):
    _name = "opms.user.management"
    _description = "OPMS User Management Profile"
    _rec_name = "user_id"

    @api.model
    def _apply_opms_access_policy_from_data(self):
        self.env["opms.access.policy.service"].sudo().apply_policy()
        return True

    user_id = fields.Many2one(
        "res.users",
        required=True,
        ondelete="restrict",
        index=True,
    )
    company_id = fields.Many2one("res.company", string="Region/Office", required=True, ondelete="restrict")
    programme_ids = fields.Many2many("opms.programme", string="Programmes", required=True)
    sub_programme_ids = fields.Many2many("opms.sub.programme", string="Sub-Programmes", required=True)
    directorate_ids = fields.Many2many("opms.directorate", string="Directorates", required=True)

    is_opms_submissions_user = fields.Boolean(string="OPMS Submissions Users", default=True)
    is_opms_manager = fields.Boolean(string="OPMS Managers")
    is_opms_director = fields.Boolean(string="OPMS Directors")

    active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            "opms_user_management_user_unique",
            "unique(user_id)",
            "This user is already linked in OPMS User Management.",
        ),
    ]

    @api.constrains("user_id")
    def _check_single_profile_per_user(self):
        for record in self:
            if not record.user_id:
                continue
            duplicate_count = self.with_context(active_test=False).search_count(
                [
                    ("user_id", "=", record.user_id.id),
                    ("id", "!=", record.id),
                ]
            )
            if duplicate_count:
                raise ValidationError("Only one OPMS profile is allowed per user.")

    def _get_opms_groups(self):
        group_map = {
            "is_opms_submissions_user": self.env.ref("opms_ecdhs.group_opms_submissions_user", raise_if_not_found=False),
            "is_opms_manager": self.env.ref("opms_ecdhs.group_opms_manager", raise_if_not_found=False),
            "is_opms_director": self.env.ref("opms_ecdhs.group_opms_director", raise_if_not_found=False),
        }
        return {k: v for k, v in group_map.items() if v}

    def _sanitize_hierarchy(self):
        for record in self:
            vals = {}

            if record.programme_ids:
                allowed_sub_programmes = self.env["opms.sub.programme"].search(
                    [("programme_id", "in", record.programme_ids.ids)]
                )
                valid_sub_programmes = record.sub_programme_ids & allowed_sub_programmes
                if valid_sub_programmes.ids != record.sub_programme_ids.ids:
                    vals["sub_programme_ids"] = [(6, 0, valid_sub_programmes.ids)]
            else:
                valid_sub_programmes = record.sub_programme_ids

            if valid_sub_programmes:
                allowed_directorates = self.env["opms.directorate"].search(
                    [("sub_programme_id", "in", valid_sub_programmes.ids)]
                )
                valid_directorates = record.directorate_ids & allowed_directorates
                if valid_directorates.ids != record.directorate_ids.ids:
                    vals["directorate_ids"] = [(6, 0, valid_directorates.ids)]

            if vals:
                record.with_context(opms_skip_post_write=True).write(vals)

    def _sync_user_groups(self, extra_users=None):
        group_map = self._get_opms_groups()
        if not group_map:
            return

        opms_groups = self.env["res.groups"].browse([grp.id for grp in group_map.values()])
        # During unlink(), self may contain deleted records; only use existing ones.
        users_to_sync = self.with_context(active_test=False).exists().mapped("user_id")
        if extra_users:
            users_to_sync |= extra_users.with_context(active_test=False)

        all_profiles = self.with_context(active_test=False).search([("user_id", "in", users_to_sync.ids)])

        for user in users_to_sync.sudo():
            profiles = all_profiles.filtered(lambda rec: rec.user_id.id == user.id and rec.active)
            desired_groups = self.env["res.groups"]
            if profiles:
                profile = profiles[0]
                if profile.is_opms_submissions_user and group_map.get("is_opms_submissions_user"):
                    desired_groups |= group_map["is_opms_submissions_user"]
                if profile.is_opms_manager and group_map.get("is_opms_manager"):
                    desired_groups |= group_map["is_opms_manager"]
                if profile.is_opms_director and group_map.get("is_opms_director"):
                    desired_groups |= group_map["is_opms_director"]

            updated_groups = (user.groups_id - opms_groups) | desired_groups
            user.write({"groups_id": [(6, 0, updated_groups.ids)]})

        if users_to_sync:
            users_to_sync._sync_opms_scope_from_profile()

        self.env["opms.access.policy.service"].sudo().apply_policy()

    @api.constrains("programme_ids", "sub_programme_ids", "directorate_ids")
    def _check_hierarchy_integrity(self):
        for record in self:
            if record.sub_programme_ids and record.programme_ids:
                if any(sp.programme_id.id not in record.programme_ids.ids for sp in record.sub_programme_ids):
                    raise ValidationError("Selected sub-programmes must belong to selected programmes.")

            if record.directorate_ids and record.sub_programme_ids:
                if any(d.sub_programme_id.id not in record.sub_programme_ids.ids for d in record.directorate_ids):
                    raise ValidationError("Selected directorates must belong to selected sub-programmes.")

    @api.constrains("user_id", "company_id", "programme_ids", "sub_programme_ids", "directorate_ids")
    def _check_required_scope_fields(self):
        for record in self:
            if not record.user_id:
                raise ValidationError("User is required.")
            if not record.company_id:
                raise ValidationError("Region/Office (Company) is required.")
            if not record.programme_ids:
                raise ValidationError("At least one Programme is required.")
            if not record.sub_programme_ids:
                raise ValidationError("At least one Sub-Programme is required.")
            if not record.directorate_ids:
                raise ValidationError("At least one Directorate is required.")

    def _prepare_company_sync_vals(self, vals, user):
        prepared = dict(vals)
        user = user.sudo()

        if user.company_id:
            prepared["company_id"] = user.company_id.id
            return prepared

        selected_company_id = prepared.get("company_id")
        if selected_company_id:
            user.write({"company_id": selected_company_id})
        return prepared

    @api.model_create_multi
    def create(self, vals_list):
        prepared_vals_list = []
        for vals in vals_list:
            prepared = dict(vals)
            user = self.env["res.users"].sudo().browse(prepared.get("user_id"))
            if user.exists():
                prepared = self._prepare_company_sync_vals(prepared, user)
            prepared_vals_list.append(prepared)

        records = super().create(prepared_vals_list)
        records._sanitize_hierarchy()
        records._sync_user_groups()
        return records

    def write(self, vals):
        old_users = self.with_context(active_test=False).mapped("user_id")
        if "user_id" in vals or "company_id" in vals:
            result = True
            for record in self:
                prepared = dict(vals)
                user_id = prepared.get("user_id") or record.user_id.id
                user = self.env["res.users"].sudo().browse(user_id)
                if user.exists():
                    prepared = record._prepare_company_sync_vals(prepared, user)
                result = super(OpmsUserManagement, record).write(prepared) and result
        else:
            result = super().write(vals)
        if self.env.context.get("opms_skip_post_write"):
            return result
        self._sanitize_hierarchy()
        self._sync_user_groups(extra_users=old_users)
        return result

    def unlink(self):
        old_users = self.with_context(active_test=False).mapped("user_id")
        result = super().unlink()
        self._sync_user_groups(extra_users=old_users)
        return result
