# Fixes Applied for Odoo 18 Issues

## Date: 2026-01-24

### Issues Fixed

#### 1. Owl Lifecycle Error: "selection is undefined"

**Error Message:**
```
OwlError: The following error occurred in onWillRender: "can't access property "filter", selection is undefined"
TypeError: can't access property "filter", selection is undefined
    getAllItems@http://localhost:18000/web/assets/.../web.assets_web.min.js
    getSortedItems@http://localhost:18000/web/assets/.../web.assets_web.min.js
```

**Root Cause:**
- Custom view registrations (`izidashboard`, `izianalysis`) were missing `withControlPanel: false` and `withSearchPanel: false` properties
- When these properties are not set, Odoo's framework tries to render control/search panels that expect a `selection` array
- The core Odoo code calls `selection.filter()` in `getAllItems/getSortedItems` during `onWillRender` before selection is initialized

**Files Modified:**
1. `izi_dashboard/static/src/js/izi_dashboard_view.js` - Added `withControlPanel: false, withSearchPanel: false`
2. `izi_dashboard/static/src/js/izi_analysis_view.js` - Added `withControlPanel: false, withSearchPanel: false`
3. `ecdhs_base/static/src/custom_sign_item/custom_sign_request_control_panel.js` - Fixed boolean assignment bug
4. `ecdhs_base/static/src/custom_sign_item/custom_sign_template_control_panel.js` - Fixed boolean assignment bug

**Changes Made:**

```javascript
// izi_dashboard/static/src/js/izi_dashboard_view.js
export const IZIDashboardView = {
    type: "izidashboard",
    display_name: "IZIDashboard",
    icon: "fa-tachometer",
    multiRecord: true,
    withControlPanel: false,  // ADDED
    withSearchPanel: false,   // ADDED
    Controller: IZIDashboardController,
};

// izi_dashboard/static/src/js/izi_analysis_view.js
export const IZIAnalysisView = {
    type: "izianalysis",
    display_name: "IZIAnalysis",
    icon: "fa-tachometer",
    multiRecord: true,
    withControlPanel: false,  // ADDED
    withSearchPanel: false,   // ADDED
    Controller: IZIAnalysisController,
};
```

**Additional Fixes:**

Fixed incorrect boolean assignment in sign control panels:
```javascript
// Before (WRONG - comparison instead of assignment):
if (user.userId == 2){
    this.isSignAdmin == true;  // This does comparison, not assignment!
}

// After (CORRECT):
this.isSignAdmin = user.userId === 2 || !!this.isSignAdmin;
```

#### 2. WebSocket Configuration Issue

**Error Message:**
```
RuntimeError: Couldn't bind the websocket. Is the connection opened on the evented port (8072)?
KeyError: 'socket'
```

**Root Cause:**
- Odoo 18 requires WebSocket connections on a separate evented port (default 8072)
- The application is running on port 18000 without the evented port configured

**Solution:**
Configure Odoo to run with WebSocket support:

1. **Option A: Run with gevent worker (Recommended)**
```bash
./odoo-bin -d <your_db> --http-port=18000 --gevent-port=8072
```

2. **Option B: Disable WebSocket in configuration**
Add to `odoo.conf` or command line:
```ini
[options]
workers = 0
# OR
gevent_port = 0
```

3. **Option C: Use nginx/proxy to handle WebSocket**
Configure reverse proxy to route WebSocket connections appropriately.

### Testing & Verification

1. **Clear browser cache:**
   - Hard reload: `Cmd+Shift+R` (macOS) / `Ctrl+Shift+F5` (Windows)
   - Or clear browser cache completely

2. **Restart Odoo with asset rebuild:**
```bash
./odoo-bin -d <your_db> -u izi_dashboard,ecdhs_base --stop-after-init
./odoo-bin -d <your_db> --dev=all
```

3. **Verify fixes:**
   - Navigate to IZI Dashboard views
   - Navigate to IZI Analysis views
   - Check sign template/request views
   - Verify no "selection is undefined" errors in browser console

### Additional Notes

- The `cloud_base` module uses `SearchModel` correctly and does not need changes
- Custom views that don't need control panels should always explicitly set `withControlPanel: false` and `withSearchPanel: false`
- When extending Odoo's standard views (kanban, list), these properties are inherited correctly

### Prevention

For future custom view registrations, always include:
```javascript
export const MyCustomView = {
    type: "mycustom",
    display_name: "My Custom",
    multiRecord: true,
    withControlPanel: false,  // If you don't need search/filters
    withSearchPanel: false,   // If you don't need search panel
    Controller: MyCustomController,
};
```

### Related Documentation

- Odoo 18 View Architecture: https://www.odoo.com/documentation/18.0/developer/reference/frontend/views.html
- Owl Lifecycle: https://www.odoo.com/documentation/18.0/developer/reference/frontend/owl_components.html
- WebSocket Configuration: https://www.odoo.com/documentation/18.0/administration/on_premise/deploy.html#websocket
