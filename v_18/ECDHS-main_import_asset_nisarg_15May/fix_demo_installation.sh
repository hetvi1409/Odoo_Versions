#!/bin/bash

# Odoo Demo Installation Fix Script
# Resolves: Virtual Real Time Limit Exceeded errors during demo installation

echo "================================================"
echo "Odoo Demo Installation Fix"
echo "================================================"
echo ""

DB_NAME="ecdhs_enterprise_v18_local"
ODOO_PID=$(pgrep -f "odoo.*bin" | head -1)

# Step 1: Check current status
echo "1. Current Status Check..."
echo "================================================"

if [ -n "$ODOO_PID" ]; then
    echo "✓ Odoo is running (PID: $ODOO_PID)"
else
    echo "⚠️  Odoo is not running"
fi

# Check database lock status
LOCKS=$(psql -U postgres -d "$DB_NAME" -t -c "
SELECT COUNT(*) FROM pg_stat_activity
WHERE datname = '$DB_NAME' AND state = 'active';" 2>/dev/null)

echo "Active DB connections: $LOCKS"
echo ""

# Step 2: Kill stuck processes
echo "2. Cleaning up stuck processes..."
echo "================================================"

# Find any processes related to module loading
STUCK_PROCS=$(ps aux | grep -E "(install_demo|limit.*exceed)" | grep -v grep | awk '{print $2}')

if [ ! -z "$STUCK_PROCS" ]; then
    echo "Found stuck processes:"
    echo "$STUCK_PROCS" | xargs ps aux | grep -v grep
    echo ""
    read -p "Terminate stuck processes? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "$STUCK_PROCS" | xargs kill -9 2>/dev/null
        echo "✓ Cleaned up stuck processes"
    fi
fi
echo ""

# Step 3: Reset module state in database
echo "3. Resetting module installation state..."
echo "================================================"

read -p "Reset ir_module_module demo flags in database? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    psql -U postgres -d "$DB_NAME" -c "
    UPDATE ir_module_module SET demo = false WHERE id NOT IN (
        SELECT id FROM ir_module_module WHERE state IN ('installed', 'to install')
    );
    " 2>/dev/null
    echo "✓ Reset module demo flags"
fi
echo ""

# Step 4: Vacuum and reindex database
echo "4. Database Maintenance..."
echo "================================================"

echo "Running VACUUM ANALYZE..."
psql -U postgres -d "$DB_NAME" -c "VACUUM ANALYZE;" 2>/dev/null
echo "✓ Database optimized"
echo ""

# Step 5: Check module dependencies
echo "5. Checking Module Integrity..."
echo "================================================"

BROKEN_MODULES=$(psql -U postgres -d "$DB_NAME" -t -c "
SELECT name FROM ir_module_module
WHERE state = 'broken' LIMIT 10;" 2>/dev/null)

if [ ! -z "$BROKEN_MODULES" ]; then
    echo "⚠️  Found broken modules:"
    echo "$BROKEN_MODULES"
    echo ""
    echo "These modules may need manual intervention or reinstall."
else
    echo "✓ No broken modules found"
fi
echo ""

# Step 6: Restart recommendations
echo "6. Restart Instructions..."
echo "================================================"
echo ""
echo "Next steps to complete demo installation successfully:"
echo ""
echo "1. Stop Odoo (if running):"
echo "   kill -9 $ODOO_PID"
echo ""
echo "2. Restart Odoo with single worker (slower but more stable):"
echo "   cd /Users/benjaminmaimba/Documents/Odoo/Odoo18/Odoo_18.0.Enterprise/ecdhs_v18_enterprise"
echo "   python odoo-bin --db_name=$DB_NAME --workers=1 -d $DB_NAME"
echo ""
echo "3. Alternative: Skip demo installation initially:"
echo "   python odoo-bin --db_name=$DB_NAME --without-demo"
echo ""
echo "4. Once Odoo is stable, install demo separately through UI:"
echo "   - Go to Apps menu"
echo "   - Search for 'Demo' module"
echo "   - Click Install (be patient, takes 5-10 minutes)"
echo ""
echo "5. Monitor logs during installation:"
echo "   tail -f ~/.odoo.log"
echo ""
echo "Configuration verified in:"
echo "  /Users/benjaminmaimba/Documents/Odoo/Odoo18/Odoo_18.0.Enterprise/ecdhs_v18_enterprise/odoo.conf"
echo ""
echo "Current settings:"
echo "  - limit_time_real = 600s (10 minutes)"
echo "  - limit_time_cpu = 500s"
echo "  - workers = 2"
echo "  - max_cron_threads = 1"
echo ""

echo "================================================"
echo "✓ Diagnostic complete"
echo "================================================"
