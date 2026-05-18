# 🔧 ISSUE FIXED - Website Links Not Working

## Problem Identified ✅
The main `__init__.py` file was missing the `controllers` import, which prevented the website routes from being registered with Odoo.

## Solution Applied ✅
Added `from . import controllers` to `/sa_government_tender/__init__.py`

**Before:**
```python
from . import models
from . import wizard
```

**After:**
```python
from . import controllers
from . import models
from . import wizard
```

---

## 🚀 Deployment Steps

### 1. Restart Odoo Server
```bash
# Stop Odoo
sudo systemctl stop odoo

# Start Odoo
sudo systemctl start odoo

# Or restart
sudo systemctl restart odoo
```

**Alternative (if using Odoo.sh or manual start):**
```bash
# Kill the process
pkill -f odoo-bin

# Start again
./odoo-bin -c /path/to/odoo.conf
```

### 2. Upgrade the Module
1. Go to **Apps** menu in Odoo
2. Remove "Apps" filter
3. Search for "SA Government Tender"
4. Click the **⋮** menu button
5. Click **Upgrade**

---

## ✅ Testing Checklist

### Test URLs Directly in Browser

#### Public URLs (No Login Required)
- [ ] `http://localhost:8069/sagovtenders` - Should show tender listing
- [ ] `http://localhost:8069/supplier/register` - Should show registration form
- [ ] Click on any tender → Should show tender details page
- [ ] Try search on tender listing → Should filter results

#### Authenticated URLs (Requires Login)
1. Login as a portal user or create one:
   - [ ] Register at `/supplier/register`
   - [ ] Check email for password reset link
   - [ ] Set password and login

2. Test authenticated routes:
   - [ ] `http://localhost:8069/my/bids` - Should show "My Bids" page
   - [ ] `http://localhost:8069/supplier/profile` - Should show profile page
   - [ ] Click "Submit Bid" on any tender → Should show bid form
   - [ ] Try submitting a bid → Should create bid

### Test Website Menus
- [ ] Check top navigation bar for:
  - **Open Tenders** link
  - **Supplier Registration** link
  - **My Bids** link (when logged in)
  - **My Profile** link (when logged in)

### Test Functionality
- [ ] Search tenders by keyword
- [ ] Pagination on tender list (if > 10 tenders)
- [ ] Download tender documents
- [ ] View briefing session info
- [ ] Register new supplier
  - [ ] Try duplicate CSD number → Should show error
  - [ ] Try duplicate Company Reg number → Should show error
- [ ] Submit bid (when logged in)
  - [ ] Try duplicate bid → Should show "Already Submitted"
  - [ ] Check SBD checklist works
  - [ ] Upload documents
- [ ] View submitted bids
- [ ] Update supplier profile

---

## 🐛 Troubleshooting

### If Routes Still Don't Work

#### 1. Check Server Logs
```bash
# View live logs
tail -f /var/log/odoo/odoo-server.log

# Or if using custom location
tail -f /path/to/odoo.log
```

**Look for:**
- `ImportError` messages
- `NameError` or `AttributeError`
- Route registration messages
- Any error related to `sa_government_tender`

#### 2. Verify Module is Properly Loaded
In Odoo Python console (Settings → Technical → Python Code):
```python
# Check if controllers are loaded
from odoo.addons.sa_government_tender import controllers
print(controllers)

# Check if routes are registered
from odoo.http import root
routes = [r for r in root.controllers.get('http', {}) if 'sagov' in str(r).lower()]
print(routes)
```

#### 3. Check for Syntax Errors
```bash
cd /path/to/sa_government_tender
python3 -m py_compile controllers/main.py
python3 -m py_compile controllers/supplier_portal.py
python3 -m py_compile __init__.py
```

#### 4. Force Module Reload
In Odoo interface:
1. Activate **Developer Mode** (Settings → Activate Developer Mode)
2. Go to Apps
3. Search "SA Government Tender"
4. Click **⋮** → **Upgrade**
5. Check "Remove all filters" if module doesn't appear

#### 5. Clear Browser Cache
- Press `Ctrl+Shift+R` (or `Cmd+Shift+R` on Mac) to hard refresh
- Or clear browser cache completely

#### 6. Verify Dependencies
Ensure `website` module is installed:
1. Go to **Apps**
2. Search for "Website"
3. Should show as "Installed"
4. If not, install it first

---

## 🔍 Verification Commands

### Check if Module is Installed
```bash
# In Odoo shell
./odoo-bin shell -d <database_name> -c <config_file>

# Then run:
env['ir.module.module'].search([('name', '=', 'sa_government_tender')])
```

### Check if Routes are Registered
```python
# In Odoo Python console
from odoo.http import root
controllers = root.controllers.get('http', {})
tender_routes = [r for r in controllers.keys() if 'sagovtender' in r or 'supplier' in r]
print(tender_routes)
```

### Test Route Manually
```python
# In Odoo shell
from odoo.addons.sa_government_tender.controllers import main
print(dir(main.SagovTenderWebsiteController))
```

---

## 📊 Expected Results

### Working URLs
When properly configured, you should see:

**`/sagovtenders`:**
```
✅ Page loads
✅ Shows tender listing
✅ Search bar appears
✅ Pagination works
✅ Can click on tenders
```

**`/sagovtender/<token>`:**
```
✅ Page loads
✅ Shows tender details
✅ Documents available for download
✅ "Submit Bid" button visible
✅ Briefing info displayed
```

**`/supplier/register`:**
```
✅ Page loads
✅ Form displays all fields
✅ Can fill and submit
✅ Duplicate prevention works
```

**`/my/bids` (logged in):**
```
✅ Page loads
✅ Shows submitted bids
✅ Pagination works
✅ Can click to view details
```

---

## 📞 Still Having Issues?

### Check These Files
1. **`__init__.py`** - Should have controllers import ✅
2. **`controllers/__init__.py`** - Should import main and supplier_portal ✅
3. **`controllers/main.py`** - Should have route decorators ✅
4. **`controllers/supplier_portal.py`** - Should have route decorators ✅
5. **`__manifest__.py`** - Should have 'website' in depends ✅
6. **`data/website_menus.xml`** - Should be in data list ✅

### Common Errors and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| 404 Not Found | Routes not registered | Restart Odoo + Upgrade module |
| ImportError | Missing controllers import | Fixed in __init__.py ✅ |
| Template not found | XML files not loaded | Check manifest data list |
| Access Denied | Wrong auth level | Check route @http.route auth parameter |
| CSRF Error | Missing token | Check forms have csrf_token |

---

## ✅ Completion Checklist

- [x] Fixed `__init__.py` to import controllers
- [ ] Restarted Odoo server
- [ ] Upgraded module
- [ ] Tested `/sagovtenders` URL
- [ ] Tested `/supplier/register` URL
- [ ] Tested authenticated routes
- [ ] Verified menus appear
- [ ] Tested bid submission
- [ ] Checked logs for errors

---

## 📝 Summary

**Issue:** Website links and menus not working
**Root Cause:** Missing `controllers` import in main `__init__.py`
**Fix Applied:** Added `from . import controllers`
**Next Steps:** Restart Odoo → Upgrade module → Test URLs

**Status:** ✅ FIXED - Ready for testing after Odoo restart

---

**Date:** January 7, 2026
**Module:** SA Government Tender v18.0
**Fix:** Controller registration issue resolved
