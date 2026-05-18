#!/bin/bash

# Odoo WebSocket Configuration Fix
# Resolves: "Couldn't bind the websocket. Is the connection opened on the evented port (8072)?"

echo "================================================"
echo "Odoo WebSocket Diagnosis & Fix"
echo "================================================"
echo ""

ODOO_CONFIG="/Users/benjaminmaimba/Documents/Odoo/Odoo18/Odoo_18.0.Enterprise/ecdhs_v18_enterprise/odoo.conf"
WS_PORT="8072"

echo "1. Checking WebSocket Configuration..."
echo "================================================"
echo ""

# Check if websocket port is configured
if grep -q "websocket_port\|evented_port" "$ODOO_CONFIG"; then
    echo "WebSocket configuration found:"
    grep -E "websocket_port|evented_port" "$ODOO_CONFIG"
else
    echo "⚠️  WebSocket configuration NOT FOUND in odoo.conf"
fi

echo ""
echo "2. Checking Port Status..."
echo "================================================"
echo ""

# Check if port is already in use
if lsof -i ":$WS_PORT" >/dev/null 2>&1; then
    echo "✓ Port $WS_PORT is already in use by:"
    lsof -i ":$WS_PORT" | tail -1
else
    echo "⚠️  Port $WS_PORT is NOT in use"
    echo "   (This is normal if Odoo isn't running yet)"
fi

echo ""
echo "3. Checking Firewall..."
echo "================================================"
echo ""

# Check macOS firewall status
FIREWALL_STATUS=$(defaults read /Library/Preferences/com.apple.security.firewall globalstate 2>/dev/null)
case "$FIREWALL_STATUS" in
  0) echo "✓ Firewall is OFF" ;;
  1) echo "⚠️  Firewall is ON (may block port $WS_PORT)" ;;
  2) echo "⚠️  Firewall is ON and in stealth mode (may block port $WS_PORT)" ;;
  *) echo "⚠️  Could not determine firewall status" ;;
esac

echo ""
echo "4. Checking HTTP Server Configuration..."
echo "================================================"
echo ""

# Check if http port is configured
if grep -q "^http_port\|^xmlrpc_port" "$ODOO_CONFIG"; then
    echo "HTTP/XML-RPC configuration:"
    grep -E "^http_port|^xmlrpc_port" "$ODOO_CONFIG"
else
    echo "⚠️  HTTP port configuration not found (using defaults)"
fi

echo ""
echo "5. Checking for Multiple Odoo Instances..."
echo "================================================"
echo ""

RUNNING=$(ps aux | grep -E "[o]doo.*bin" | wc -l)
if [ "$RUNNING" -gt 0 ]; then
    echo "Found $RUNNING Odoo processes:"
    ps aux | grep -E "[o]doo.*bin" | awk '{print "  PID: " $2 " - " $11 " " $12 " " $13 " " $14}'
else
    echo "✓ No Odoo processes running"
fi

echo ""
echo "6. Recommended Fix..."
echo "================================================"
echo ""

# Add websocket configuration if missing
if ! grep -q "websocket_port" "$ODOO_CONFIG"; then
    echo "Adding WebSocket configuration..."
    cat >> "$ODOO_CONFIG" <<'WEBSOCKET_CONF'

# WebSocket Configuration for Real-time Features
websocket_port = 8072
WEBSOCKET_CONF
    echo "✓ Added websocket_port = 8072 to odoo.conf"
else
    echo "✓ WebSocket configuration already present"
fi

echo ""
echo "7. Startup Instructions..."
echo "================================================"
echo ""

echo "To properly start Odoo with WebSocket support:"
echo ""
echo "Option A: Standard Multi-Worker Mode (Recommended)"
echo "  cd /Users/benjaminmaimba/Documents/Odoo/Odoo18/Odoo_18.0.Enterprise/ecdhs_v18_enterprise"
echo "  python odoo-bin --workers=2"
echo ""
echo "Option B: Development Mode (Single Worker)"
echo "  python odoo-bin --workers=0 --dev=all"
echo ""
echo "Option C: Custom Ports"
echo "  python odoo-bin --xmlrpc-port=8069 --websocket-port=8072"
echo ""
echo "Verify WebSocket is working:"
echo "  1. Open browser to http://localhost:8069"
echo "  2. Check browser console for WebSocket connection"
echo "  3. Or test: curl -i -N http://localhost:8072/websocket"
echo ""

echo "================================================"
echo "Configuration file updated:"
echo "  $ODOO_CONFIG"
echo "================================================"
