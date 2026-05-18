#!/bin/bash

# Database Lock Checker and Cleaner for Odoo
# Usage: ./clear_db_locks.sh [database_name]

DB_NAME="${1:-ecdhs_enterprise_v18_local}"
DB_USER="${PGUSER:-odoo}"

echo "================================================"
echo "Odoo Database Lock Checker and Cleaner"
echo "================================================"
echo "Database: $DB_NAME"
echo ""

# Check if PostgreSQL is running
if ! pg_isready -q; then
    echo "❌ PostgreSQL is not running!"
    exit 1
fi

echo "✓ PostgreSQL is running"
echo ""

# 1. Check for running Odoo processes
echo "1. Checking for Odoo processes..."
echo "------------------------------------------------"
ODOO_PIDS=$(ps aux | grep -E "[o]doo.*($DB_NAME|server)" | awk '{print $2}')
if [ -z "$ODOO_PIDS" ]; then
    echo "✓ No Odoo processes found"
else
    echo "⚠️  Found Odoo processes:"
    ps aux | grep -E "[o]doo.*($DB_NAME|server)" | awk '{print "   PID: " $2 " - " $11 " " $12 " " $13}'
    echo ""
    read -p "Kill these Odoo processes? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "$ODOO_PIDS" | xargs kill -9 2>/dev/null
        echo "✓ Odoo processes terminated"
    fi
fi
echo ""

# 2. Check for blocking queries
echo "2. Checking for blocking queries..."
echo "------------------------------------------------"
BLOCKING_QUERY="
SELECT
    blocked.pid AS blocked_pid,
    blocking.pid AS blocking_pid,
    blocked.usename AS blocked_user,
    blocking.usename AS blocking_user,
    blocked.query AS blocked_query,
    blocking.query AS blocking_query
FROM pg_stat_activity AS blocked
JOIN pg_stat_activity AS blocking
    ON blocking.pid = ANY(pg_blocking_pids(blocked.pid))
WHERE blocked.datname = '$DB_NAME';
"

BLOCKING_RESULT=$(psql -U "$DB_USER" -d "$DB_NAME" -t -c "$BLOCKING_QUERY" 2>/dev/null)

if [ -z "$BLOCKING_RESULT" ] || [ "$BLOCKING_RESULT" = "" ]; then
    echo "✓ No blocking queries found"
else
    echo "⚠️  Found blocking queries:"
    echo "$BLOCKING_RESULT"
    echo ""

    # Get blocking PIDs
    BLOCKING_PIDS=$(psql -U "$DB_USER" -d "$DB_NAME" -t -c "
        SELECT DISTINCT blocking.pid
        FROM pg_stat_activity AS blocked
        JOIN pg_stat_activity AS blocking
            ON blocking.pid = ANY(pg_blocking_pids(blocked.pid))
        WHERE blocked.datname = '$DB_NAME';
    " 2>/dev/null | tr -d ' ')

    if [ ! -z "$BLOCKING_PIDS" ]; then
        read -p "Terminate blocking processes? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            for pid in $BLOCKING_PIDS; do
                psql -U "$DB_USER" -d "$DB_NAME" -c "SELECT pg_terminate_backend($pid);" >/dev/null 2>&1
                echo "✓ Terminated process $pid"
            done
        fi
    fi
fi
echo ""

# 3. Check for idle in transaction connections
echo "3. Checking for idle transactions (>2 minutes)..."
echo "------------------------------------------------"
IDLE_QUERY="
SELECT
    pid,
    usename,
    state,
    query_start,
    NOW() - query_start AS duration,
    LEFT(query, 60) AS query_preview
FROM pg_stat_activity
WHERE datname = '$DB_NAME'
  AND state = 'idle in transaction'
  AND NOW() - state_change > INTERVAL '2 minutes'
ORDER BY state_change;
"

IDLE_RESULT=$(psql -U "$DB_USER" -d "$DB_NAME" -t -c "$IDLE_QUERY" 2>/dev/null)

if [ -z "$IDLE_RESULT" ] || [ "$IDLE_RESULT" = "" ]; then
    echo "✓ No long-running idle transactions"
else
    echo "⚠️  Found idle transactions:"
    psql -U "$DB_USER" -d "$DB_NAME" -c "$IDLE_QUERY" 2>/dev/null
    echo ""

    # Get idle PIDs
    IDLE_PIDS=$(psql -U "$DB_USER" -d "$DB_NAME" -t -c "
        SELECT pid
        FROM pg_stat_activity
        WHERE datname = '$DB_NAME'
          AND state = 'idle in transaction'
          AND NOW() - state_change > INTERVAL '2 minutes';
    " 2>/dev/null | tr -d ' ')

    if [ ! -z "$IDLE_PIDS" ]; then
        read -p "Terminate idle transactions? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            for pid in $IDLE_PIDS; do
                psql -U "$DB_USER" -d "$DB_NAME" -c "SELECT pg_terminate_backend($pid);" >/dev/null 2>&1
                echo "✓ Terminated process $pid"
            done
        fi
    fi
fi
echo ""

# 4. Check all active connections
echo "4. Active connections summary..."
echo "------------------------------------------------"
psql -U "$DB_USER" -d "$DB_NAME" -c "
SELECT
    COUNT(*) as total_connections,
    COUNT(*) FILTER (WHERE state = 'active') as active,
    COUNT(*) FILTER (WHERE state = 'idle') as idle,
    COUNT(*) FILTER (WHERE state = 'idle in transaction') as idle_in_transaction
FROM pg_stat_activity
WHERE datname = '$DB_NAME';
" 2>/dev/null
echo ""

# 5. Check for locks on ir_module_module table
echo "5. Checking locks on ir_module_module table..."
echo "------------------------------------------------"
LOCK_QUERY="
SELECT
    l.pid,
    l.mode,
    l.granted,
    a.usename,
    a.state,
    LEFT(a.query, 80) AS query
FROM pg_locks l
JOIN pg_stat_activity a ON l.pid = a.pid
JOIN pg_class c ON l.relation = c.oid
WHERE c.relname = 'ir_module_module'
  AND a.datname = '$DB_NAME';
"

LOCK_RESULT=$(psql -U "$DB_USER" -d "$DB_NAME" -t -c "$LOCK_QUERY" 2>/dev/null)

if [ -z "$LOCK_RESULT" ] || [ "$LOCK_RESULT" = "" ]; then
    echo "✓ No locks on ir_module_module table"
else
    echo "⚠️  Found locks on ir_module_module:"
    psql -U "$DB_USER" -d "$DB_NAME" -c "$LOCK_QUERY" 2>/dev/null
fi
echo ""

echo "================================================"
echo "✓ Lock check complete"
echo "================================================"
echo ""
echo "Recommendations:"
echo "- If locks persist, restart PostgreSQL: brew services restart postgresql"
echo "- Check Odoo config for multiple instances"
echo "- Close pgAdmin or other DB tools with open transactions"
echo ""
