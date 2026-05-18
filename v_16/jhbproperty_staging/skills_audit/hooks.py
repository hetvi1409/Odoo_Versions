
from odoo import api, SUPERUSER_ID

DEFAULT_ROLES = [
    ('SCM Intern', 'basic'),
    ('SCM Officer', 'intermediate'),
    ('SCM Manager', 'advanced'),
    ('Head of SCM', 'expert'),
]

LEVELS = ['basic', 'intermediate', 'advanced', 'expert']

def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    Role = env['scs.job.role']
    Requirement = env['scs.role.requirement']
    Competency = env['scs.competency']

    # Create baseline roles if not exists
    roles = {}
    for name, level in DEFAULT_ROLES:
        role = Role.search([('name', '=', name)], limit=1)
        if not role:
            role = Role.create({'name': name})
        roles[name] = (role, level)

    # Map all competencies with required level per role
    all_comp = Competency.search([])
    for role_name, (role, level) in roles.items():
        for comp in all_comp:
            if not Requirement.search([('role_id', '=', role.id), ('competency_id', '=', comp.id)], limit=1):
                Requirement.create({
                    'role_id': role.id,
                    'competency_id': comp.id,
                    'required_level': level,
                })
