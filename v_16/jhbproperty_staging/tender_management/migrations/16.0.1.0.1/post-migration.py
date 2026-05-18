def migrate(cr, version):
    cr.execute(
        """
        ALTER TABLE tender_document
        ADD COLUMN IF NOT EXISTS tender_rfq_id integer
        """
    )
