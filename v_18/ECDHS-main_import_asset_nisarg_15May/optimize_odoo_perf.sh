#!/bin/bash

# Odoo Performance Optimization Script
# Addresses timeout and slow loading issues

echo "================================================"
echo "Odoo Performance Optimization Tool"
echo "================================================"
echo ""

# Configuration
ODOO_CONFIG="${ODOO_CONFIG:-/Users/benjaminmaimba/Documents/Odoo/Odoo18/Odoo_18.0.Enterprise/ecdhs_v18_enterprise/odoo.conf}"
DB_NAME="ecdhs_enterprise_v18_local"
DB_USER="odoo"

echo "1. Checking Odoo configuration..."
echo "================================================"
echo ""

if [ ! -f "$ODOO_CONFIG" ]; then
    echo "⚠️  Config file not found: $ODOO_CONFIG"
    echo "   Please update the path in this script"
    exit 1
fi

echo "Found Odoo config at: $ODOO_CONFIG"
echo ""

# Check current timeout settings
echo "Current Odoo timeout settings:"
grep -E "(limit_time_real|limit_time_cpu|limit_request)" "$ODOO_CONFIG" 2>/dev/null || echo "   (using defaults)"
echo ""

echo "2. Database Performance Check..."
echo "================================================"
echo ""

# Check PostgreSQL configuration
echo "PostgreSQL shared_buffers (should be 25% of RAM):"
sudo -u postgres psql -c "SHOW shared_buffers;" 2>/dev/null || echo "   (unable to check)"

echo ""
echo "PostgreSQL work_mem (should be 2-4MB for decent systems):"
sudo -u postgres psql -c "SHOW work_mem;" 2>/dev/null || echo "   (unable to check)"

echo ""
echo "3. Database Statistics..."
echo "================================================"
echo ""

# Check table sizes
echo "Largest tables in $DB_NAME:"
psql -U "$DB_USER" -d "$DB_NAME" -c "
SELECT
    schemaname,
    tablename,
    ROUND(pg_total_relation_size(schemaname||'.'||tablename)/1024/1024, 2) as size_mb,
    n_live_tup as row_count
FROM pg_stat_user_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 15;
" 2>/dev/null || echo "   (unable to check)"

echo ""
echo "4. Missing Indexes Check..."
echo "================================================"
echo ""

# Check for unused indexes
echo "Potentially unused indexes (could be dropped):"
psql -U "$DB_USER" -d "$DB_NAME" -c "
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    pg_size_pretty(pg_relation_size(indexrelid)) as size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  AND indexname NOT LIKE 'pg_toast%'
ORDER BY pg_relation_size(indexrelid) DESC
LIMIT 10;
" 2>/dev/null || echo "   (unable to check)"

echo ""
echo "5. Recommended Configuration Changes..."
echo "================================================"
echo ""

cat <<'RECOMMENDATIONS'
To fix the timeout issues, make these changes:

A. Increase Odoo timeouts in your config file:
   Location: /Users/benjaminmaimba/Documents/Odoo/Odoo18/Odoo_18.0.Enterprise/ecdhs_v18_enterprise/odoo.conf

   Find these sections and update:
   [options]
   limit_time_real = 600          # Was 120, increase to 600 (10 minutes)
   limit_time_cpu = 500           # Was 100, increase to 500
   limit_request = 8192           # Increase from default
   max_cron_threads = 1           # Reduce from default to prevent conflicts

   # Connection pool settings
   db_maxconn = 10                # Limit connections to avoid pool exhaustion

B. Optimize PostgreSQL (requires admin/sudo):

   Run these SQL commands as postgres user:

   psql -U postgres -d ecdhs_enterprise_v18_local

   -- Enable query optimization
   ANALYZE;

   -- Reindex tables
   REINDEX DATABASE ecdhs_enterprise_v18_local;

C. Module Loading Optimization:

   - Disable unused modules in Odoo UI before demo installation
   - Install modules in smaller batches
   - Use --without-demo to skip demo data initially

D. Database Maintenance:

   - Vacuum the database: VACUUM ANALYZE;
   - Check for long-running queries during startup
   - Monitor with: watch -n 2 'psql -U odoo -d ecdhs_enterprise_v18_local -c "SELECT count(*) FROM pg_stat_activity;"'

RECOMMENDATIONS

echo ""
echo "6. Quick Fix (temporary)..."
echo "================================================"
echo ""

read -p "Do you want to automatically update Odoo timeout settings? (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Backup original config
    cp "$ODOO_CONFIG" "${ODOO_CONFIG}.backup.$(date +%s)"
    echo "✓ Backed up config to: ${ODOO_CONFIG}.backup.*"

    # Update timeout values
    if grep -q "limit_time_real" "$ODOO_CONFIG"; then
        sed -i.bak 's/limit_time_real.*/limit_time_real = 600/' "$ODOO_CONFIG"
        echo "✓ Updated limit_time_real to 600"
    else
        echo "limit_time_real = 600" >> "$ODOO_CONFIG"
        echo "✓ Added limit_time_real = 600"
    fi

    if grep -q "limit_time_cpu" "$ODOO_CONFIG"; then
        sed -i.bak 's/limit_time_cpu.*/limit_time_cpu = 500/' "$ODOO_CONFIG"
        echo "✓ Updated limit_time_cpu to 500"
    else
        echo "limit_time_cpu = 500" >> "$ODOO_CONFIG"
        echo "✓ Added limit_time_cpu = 500"
    fi

    if ! grep -q "max_cron_threads" "$ODOO_CONFIG"; then
        echo "max_cron_threads = 1" >> "$ODOO_CONFIG"
        echo "✓ Added max_cron_threads = 1"
    fi

    echo ""
    echo "⚠️  RESTART ODOO for changes to take effect"
fi

echo ""
echo "================================================"
echo "Next Steps:"
echo "================================================"
echo "1. Update the timeout values in odoo.conf"
echo "2. Restart Odoo: kill previous processes and restart"
echo "3. Run database ANALYZE: psql -U odoo -d ecdhs_enterprise_v18_local -c 'ANALYZE;'"
echo "4. Monitor logs: tail -f ~/.odoo.log or check server output"
echo "5. Check if demo installation completes without timeout"
echo ""
