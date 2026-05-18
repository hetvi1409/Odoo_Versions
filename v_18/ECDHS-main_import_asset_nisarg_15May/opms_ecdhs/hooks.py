def post_init_hook(env):
    env["opms.app.plan"]._ensure_opms_fiscal_years()
    env["opms.annual.target"]._backfill_annual_links()
    env["opms.label.service"].apply_backend_labels()
    env["opms.access.policy.service"].sudo().apply_policy()
