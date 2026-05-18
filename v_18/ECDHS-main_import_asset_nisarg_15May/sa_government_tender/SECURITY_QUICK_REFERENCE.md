# Security Quick Reference Guide

## For Developers Working on This Module

### ⚠️ Critical Security Rules

#### 1. NEVER Use Raw SQL
```python
# ❌ WRONG - SQL Injection Risk
self.env.cr.execute(f"SELECT * FROM tender WHERE name = '{name}'")

# ✅ CORRECT - Use ORM
self.env['sagovtender.tender'].search([('name', '=', name)])
```

#### 2. Always Validate User Input
```python
# ❌ WRONG - No validation
search = kwargs.get('search')
domain.append(('name', 'ilike', search))

# ✅ CORRECT - Sanitize first
search = self._sanitize_search_input(kwargs.get('search', ''))
if search:
    domain.append(('name', 'ilike', search))
```

#### 3. Avoid sudo() When Possible
```python
# ❌ WRONG - Bypasses security
bid = request.env['sagovtender.bid'].sudo().search([('id', '=', bid_id)])

# ✅ CORRECT - Let access rules work
bid = request.env['sagovtender.bid'].search([
    ('id', '=', bid_id),
    ('partner_id', '=', request.env.user.partner_id.id)
])
```

#### 4. Sanitize HTML Fields
```python
# ❌ WRONG - XSS vulnerability
description = fields.Html(string='Description')

# ✅ CORRECT - Enable sanitization
description = fields.Html(
    string='Description',
    sanitize=True,
    sanitize_tags=True,
    sanitize_attributes=True
)
```

#### 5. Always Use CSRF Protection
```python
# ❌ WRONG - No CSRF protection
@http.route('/submit', type='http', auth='user', methods=['POST'])

# ✅ CORRECT - CSRF enabled
@http.route('/submit', type='http', auth='user', methods=['POST'], csrf=True)
```

#### 6. Validate File Uploads
```python
# ❌ WRONG - No validation
file_data = request.httprequest.files['file'].read()
attachment.create({'datas': file_data})

# ✅ CORRECT - Validate everything
ALLOWED_TYPES = ('.pdf', '.doc', '.docx')
MAX_SIZE = 50 * 1024 * 1024
filename = werkzeug.utils.secure_filename(file.filename)
if not filename.endswith(ALLOWED_TYPES):
    raise UserError("Invalid file type")
```

#### 7. Add Model Constraints
```python
# ✅ ALWAYS add validation constraints
@api.constrains('bid_amount')
def _check_bid_amount(self):
    for record in self:
        if record.bid_amount <= 0:
            raise ValidationError("Amount must be positive")
        if record.bid_amount > 999999999999.99:
            raise ValidationError("Amount too large")
```

#### 8. Log Security Events
```python
# ✅ ALWAYS log security-relevant actions
_logger.warning(f"Invalid token attempt from IP: {request.httprequest.remote_addr}")
_logger.info(f"Bid submitted: {bid.id} by partner {partner.id}")
```

### 🔒 Security Checklist for New Features

Before committing new code, verify:

- [ ] All user inputs are validated
- [ ] No raw SQL queries used
- [ ] sudo() only used when absolutely necessary
- [ ] CSRF protection enabled on POST routes
- [ ] HTML fields have sanitization enabled
- [ ] File uploads are validated
- [ ] Access rules defined for new models
- [ ] Error messages don't leak sensitive data
- [ ] Security events are logged
- [ ] Model constraints added for data integrity

### 🛡️ Common Attack Patterns to Test

#### SQL Injection
Test inputs:
```
' OR '1'='1
'; DROP TABLE tender; --
' UNION SELECT password FROM users --
```

#### XSS (Cross-Site Scripting)
Test inputs:
```html
<script>alert('XSS')</script>
<img src=x onerror=alert('XSS')>
<svg onload=alert('XSS')>
javascript:alert('XSS')
```

#### Path Traversal (File Upload)
Test filenames:
```
../../etc/passwd
..\..\..\windows\system32
shell.php.jpg
malicious.exe
```

#### CSRF Testing
- Submit forms without CSRF token
- Use CSRF token from different session
- Use expired CSRF token

### 📝 Secure Coding Templates

#### Secure Controller Method
```python
@http.route(['/secure/endpoint'], type='http', auth='user', methods=['POST'], website=True, csrf=True)
def secure_endpoint(self, **post):
    """Secure endpoint template"""
    # 1. Validate inputs
    value = self._sanitize_input(post.get('value', ''), max_length=200)

    try:
        numeric_value = int(post.get('number', 0))
        if numeric_value < 0:
            raise ValueError()
    except (ValueError, TypeError):
        return self._error_response("Invalid input")

    # 2. Check authorization
    partner = request.env.user.partner_id
    if not partner:
        _logger.warning(f"Unauthorized access attempt")
        return request.render('website.403')

    # 3. Rate limiting
    recent_actions = self._check_rate_limit(partner.id)
    if recent_actions > LIMIT:
        return self._error_response("Too many requests")

    # 4. Business logic with try/except
    try:
        record = request.env['model'].create({
            'field': value,
            'partner_id': partner.id
        })
        _logger.info(f"Record created: {record.id}")
        return self._success_response(record)
    except Exception as e:
        _logger.exception("Error creating record")
        return self._error_response("Operation failed")
```

#### Secure Model with Constraints
```python
class SecureModel(models.Model):
    _name = 'secure.model'
    _description = 'Secure Model'

    name = fields.Char(required=True)
    amount = fields.Monetary()
    description = fields.Html(
        sanitize=True,
        sanitize_tags=True,
        sanitize_attributes=True
    )

    @api.constrains('amount')
    def _check_amount(self):
        for record in self:
            if record.amount < 0:
                raise ValidationError("Amount cannot be negative")
            if record.amount > 999999999999.99:
                raise ValidationError("Amount exceeds limit")

    @api.constrains('name')
    def _check_name(self):
        for record in self:
            if len(record.name) < 2:
                raise ValidationError("Name too short")
            if len(record.name) > 200:
                raise ValidationError("Name too long")
```

### 🚨 Emergency Response

If you discover a security vulnerability:

1. **STOP** - Don't commit if it's already found
2. **DOCUMENT** - Write down the vulnerability details
3. **NOTIFY** - Alert the security team immediately
4. **FIX** - Create patch with security team
5. **TEST** - Thoroughly test the fix
6. **DEPLOY** - Emergency deployment if needed
7. **REVIEW** - Post-incident review

### 📚 Additional Resources

- OWASP Top 10: https://owasp.org/www-project-top-ten/
- Odoo Security: https://www.odoo.com/documentation/14.0/developer/reference/security.html
- Python Security: https://python.readthedocs.io/en/stable/library/security_warnings.html

### ✅ Code Review Checklist

When reviewing pull requests, check:

1. **Input Validation**
   - [ ] All user inputs validated
   - [ ] Appropriate length limits
   - [ ] Type checking performed

2. **SQL Safety**
   - [ ] No raw SQL
   - [ ] ORM used correctly
   - [ ] Domain filters safe

3. **XSS Prevention**
   - [ ] HTML sanitization enabled
   - [ ] Template escaping correct
   - [ ] No unsafe t-raw usage

4. **Authentication**
   - [ ] Proper auth decorators
   - [ ] Authorization checks present
   - [ ] No sudo() abuse

5. **File Handling**
   - [ ] File type validation
   - [ ] Size limits enforced
   - [ ] Filenames sanitized

6. **Error Handling**
   - [ ] No sensitive data in errors
   - [ ] Proper logging
   - [ ] User-friendly messages

7. **Testing**
   - [ ] Security tests included
   - [ ] Edge cases covered
   - [ ] Attack patterns tested

---

**Remember**: Security is not optional. When in doubt, ask!

**Last Updated**: January 21, 2026
