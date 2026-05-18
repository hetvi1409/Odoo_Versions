# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from . import models
from . import wizard
from . import report


def pre_init_hook(env):
    """Check if documents module needs to be installed"""
    # Check if documents_fleet is installed
    cr = env.cr
    cr.execute("""
        SELECT id FROM ir_module_module
        WHERE name = 'documents_fleet' AND state = 'installed'
    """)
    if cr.fetchone():
        # documents_fleet is installed, check if documents is installed
        cr.execute("""
            SELECT id FROM ir_module_module
            WHERE name = 'documents' AND state IN ('installed', 'to upgrade')
        """)
        if not cr.fetchone():
            # Mark documents for installation
            cr.execute("""
                UPDATE ir_module_module
                SET state = 'to install'
                WHERE name = 'documents' AND state = 'uninstalled'
            """)
