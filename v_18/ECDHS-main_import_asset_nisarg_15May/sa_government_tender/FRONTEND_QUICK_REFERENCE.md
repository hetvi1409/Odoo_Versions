# SA Government Tender - Frontend Development Quick Reference

## Quick Links

### Frontend URLs
```
Public URLs (No login required):
  /sagovtenders                          - Browse all open tenders
  /sagovtender/<hex_token>               - View tender details
  /supplier/register                     - Register new supplier

Authenticated URLs (Portal/Internal users):
  /sagovtender/<hex_token>/bid           - Bid submission form
  /sagovtender/<hex_token>/bid/submit    - Submit bid (POST)
  /my/bids                               - View submitted bids
  /my/bid/<bid_id>                       - View bid details
  /supplier/profile                      - View/edit supplier profile
  /supplier/profile/update               - Update profile (POST)
```

## File Structure

```
sa_government_tender/
├── controllers/
│   ├── __init__.py
│   ├── main.py                    # Tender listing & bidding
│   └── supplier_portal.py         # Supplier registration & profile
├── models/
│   ├── sagovtender.py             # Added: access_token field
│   └── res_partner.py             # Added: company_registration_number field
├── views/templates/
│   ├── tender_pages.xml           # Tender list, detail, not available
│   ├── bid_pages.xml              # Bid form, success, error, my bids
│   └── supplier_pages.xml         # Registration, profile
├── data/
│   └── website_menus.xml          # Website menu items
└── FRONTEND_IMPLEMENTATION_GUIDE.md
```

## Key Models & Fields

### sagovtender.tender
```python
access_token = fields.Char()  # NEW: Unique hex identifier (e.g., "a3f2e1d8...")
state = fields.Selection()     # draft, scm_processing, advertised, briefing,
                               # bid_submission, opening, compliance, etc.
closing_date = fields.Datetime()  # Bid submission deadline
publication_date = fields.Date()  # When tender was published
title = fields.Char()            # Tender title
estimated_value = fields.Monetary()  # Budget
```

### res.partner (Supplier)
```python
company_registration_number = fields.Char()  # NEW: Company reg number
csd_number = fields.Char()                   # CSD registration number
csd_registered = fields.Boolean()
tax_clearance_number = fields.Char()
tax_clearance_expiry = fields.Date()
coid_number = fields.Char()
bbbee_level = fields.Selection()
bbbee_certificate_number = fields.Char()
bbbee_expiry_date = fields.Date()
is_blacklisted = fields.Boolean()            # Cannot bid if true
is_company = fields.Boolean()                # Must be true to bid
```

### sagovtender.bid
```python
tender_id = fields.Many2one('sagovtender.tender')
partner_id = fields.Many2one('res.partner')  # Bidder
bid_amount = fields.Monetary()               # Bid price
submission_date = fields.Datetime()
state = fields.Selection()  # draft, submitted, opened, compliant, etc.
sbd1_complete to sbd9_complete = fields.Boolean()  # SBD checklist
```

## API Examples

### Get tender by access token
```python
tender = request.env['sagovtender.tender'].sudo().search([
    ('access_token', '=', 'a3f2e1d8c9b4a2f7')
], limit=1)
```

### Check for duplicate suppliers
```python
# By CSD number
existing = request.env['res.partner'].sudo().search([
    ('csd_number', '=', 'value')
])

# By Company Registration number
existing = request.env['res.partner'].sudo().search([
    ('company_registration_number', '=', 'value')
])
```

### Create new bid
```python
bid = request.env['sagovtender.bid'].sudo().create({
    'tender_id': tender.id,
    'partner_id': partner.id,
    'bid_amount': 100000.00,
    'submission_date': fields.Datetime.now(),
    'sbd1_complete': True,
    # ... other SBD fields
})
```

### Get user's bids
```python
partner = request.env.user.partner_id
bids = request.env['sagovtender.bid'].sudo().search([
    ('partner_id', '=', partner.id)
])
```

## Template Variables Available

### Tender List Page
```python
tenders          # List of sagovtender.tender records
pager            # Pagination object
search           # Search string from query parameter
```

### Tender Detail Page
```python
tender           # sagovtender.tender record
is_open          # Boolean: closing_date > now
user_bid         # Existing bid or None
```

### Bid Form Page
```python
tender           # sagovtender.tender record
partner          # Current user's partner record
```

### Bid Success Page
```python
tender           # sagovtender.tender record
bid              # sagovtender.bid record (newly created)
```

### My Bids Page
```python
bids             # List of sagovtender.bid records
pager            # Pagination object
```

### Supplier Registration Form
```python
countries        # res.country records
states           # res.country.state records
```

## Common Patterns

### Check if user is authenticated
```python
if request.env.user and not request.env.user._is_public():
    # User is logged in
    partner = request.env.user.partner_id
else:
    # User is public/anonymous
```

### Check tender state for public access
```python
if tender.state in ['advertised', 'briefing', 'bid_submission', 'opening']:
    # Show to public
```

### Check if tender is open for bidding
```python
if tender.closing_date and fields.Datetime.now() < tender.closing_date:
    is_open = True
else:
    is_open = False
```

### Render response
```python
return request.render('sa_government_tender.template_name', {
    'variable': value,
})
```

### Redirect response
```python
return request.redirect('/sagovtenders')
```

## Error Handling

### Validate required fields
```python
if not post.get('field_name'):
    errors.append("Field Name is required")
```

### Handle duplicate supplier
```python
try:
    partner = request.env['res.partner'].sudo().create(vals)
except ValidationError as e:
    return request.render('error_template', {'error': str(e)})
```

### Check access
```python
if tender.state not in ['advertised', 'bid_submission']:
    return request.render('sa_government_tender.tender_not_available', {
        'message': 'This tender is not available for public viewing.'
    })
```

## Testing in Browser

### Public Access (No login)
1. Visit `http://localhost:8069/sagovtenders`
2. Click on a tender to view details
3. Try to submit bid → Should redirect to login

### Supplier Registration
1. Visit `http://localhost:8069/supplier/register`
2. Fill form with test data
3. Use unique CSD number
4. Submit → Should see success page

### Authenticated Access
1. Login with supplier credentials
2. Visit `http://localhost:8069/my/bids`
3. Click on a tender from `/sagovtenders`
4. Submit bid on `/sagovtender/<token>/bid`

## Debugging Tips

### Check template context
```xml
<!-- In QWeb template -->
<t t-debug="pdb"/>
```

### Log in controller
```python
import logging
_logger = logging.getLogger(__name__)
_logger.warning(f"Debug message: {variable}")
```

### Check field access
```python
# In Python console
tender = env['sagovtender.tender'].browse(1)
print(tender.access_token)
```

### Verify tender state for public
```python
# Tenderers must be in these states to display
tender.state in ['advertised', 'briefing', 'bid_submission', 'opening']
```

## Security Checklist

- [ ] CSRF token in all forms
- [ ] Access token not sequential (using hex)
- [ ] Supplier blacklist checked before bid submission
- [ ] Duplicate supplier prevention active
- [ ] Company blacklist enforced
- [ ] Closing date validation in place
- [ ] Authentication required for bid submission
- [ ] Only own bids visible in /my/bids

## Performance Optimization

### Reduce queries
```python
# Use select_related for many2one fields
tenders = request.env['sagovtender.tender'].sudo().search(
    [...],
).read(['id', 'name', 'title', 'closing_date'])
```

### Paginate large lists
```python
# Already implemented in list pages
# Default: 10 items per page
tenders_per_page = 10
offset = (page - 1) * tenders_per_page
```

### Cache static content
```python
# CSS and JS in static/src/ are cached
```

## Customization Examples

### Add custom field to registration
1. Add field to `res.partner` model
2. Add form control to `supplier_registration_form` template
3. Add to `supplier_registration_submit` controller in POST handling

### Change page styling
1. Edit `views/templates/*.xml` files
2. Modify CSS classes (Bootstrap 4 framework)
3. Add custom CSS to `static/src/css/style.css`

### Add new tender status check
1. Modify `is_open` computation in controller
2. Update template to show new status

## Common Issues & Solutions

### Issue: "Tender not found"
- Check access token is correct
- Verify tender exists and is published
- Check user has correct access level

### Issue: "Cannot submit bid"
- Verify user is authenticated
- Check tender closing date hasn't passed
- Check if partner is company (is_company = True)
- Check if partner is blacklisted

### Issue: "Duplicate supplier error"
- Verify CSD number is unique
- Verify Company Reg number is unique
- Check both fields are not empty (empty strings allowed)

### Issue: Email not sending
- Verify Odoo email configured
- Check email template exists
- Check server logs for errors

---

## Support Resources

- [Odoo Framework Documentation](https://www.odoo.com/documentation/)
- [QWeb Template Reference](https://www.odoo.com/documentation/18.0/developer/reference/frontend/qweb.html)
- [ORM API Reference](https://www.odoo.com/documentation/18.0/developer/reference/orm.html)
- [HTTP Controller Reference](https://www.odoo.com/documentation/18.0/developer/reference/http.html)

---

Last Updated: 2025-01-07
SA Government Tender Module v18.0
