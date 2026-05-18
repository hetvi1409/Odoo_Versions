def pre_init_hook(env):
    """Keep helpdesk_ticket schema in sync before module init.

    Some staging databases may miss columns added by this addon if code was
    deployed without a full module upgrade. This guard creates missing columns
    so registry/model loading does not fail with UndefinedColumn.
    """
    cr = env.cr

    column_sql = {
        "region": "ALTER TABLE helpdesk_ticket ADD COLUMN IF NOT EXISTS region integer",
        "category": "ALTER TABLE helpdesk_ticket ADD COLUMN IF NOT EXISTS category varchar",
        "department_id": "ALTER TABLE helpdesk_ticket ADD COLUMN IF NOT EXISTS department_id integer",
        "enquirer_name": "ALTER TABLE helpdesk_ticket ADD COLUMN IF NOT EXISTS enquirer_name varchar",
        "enquirer_surname": "ALTER TABLE helpdesk_ticket ADD COLUMN IF NOT EXISTS enquirer_surname varchar",
        "id_number": "ALTER TABLE helpdesk_ticket ADD COLUMN IF NOT EXISTS id_number varchar",
        "contact_number": "ALTER TABLE helpdesk_ticket ADD COLUMN IF NOT EXISTS contact_number varchar",
        "email": "ALTER TABLE helpdesk_ticket ADD COLUMN IF NOT EXISTS email varchar",
        "channel": "ALTER TABLE helpdesk_ticket ADD COLUMN IF NOT EXISTS channel varchar",
        "facebook_message_id": "ALTER TABLE helpdesk_ticket ADD COLUMN IF NOT EXISTS facebook_message_id varchar",
        "facebook_sender_id": "ALTER TABLE helpdesk_ticket ADD COLUMN IF NOT EXISTS facebook_sender_id varchar",
        "facebook_page_id": "ALTER TABLE helpdesk_ticket ADD COLUMN IF NOT EXISTS facebook_page_id varchar",
    }

    for sql in column_sql.values():
        cr.execute(sql)
