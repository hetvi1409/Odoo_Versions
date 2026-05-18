# Security Documentation - SA Government Tender Module

## Overview

This document outlines the comprehensive security measures implemented in the SA Government Tender Management Module to protect against various web-based attacks and vulnerabilities.

## Security Features Implemented

### 1. Input Validation & Sanitization

#### Controller Level
- **Search Input Sanitization**: All search inputs are sanitized to prevent XSS attacks
  - Maximum length limits (200 characters)
  - HTML tag stripping
  - Special character validation

- **Email Validation**: RFC-compliant email validation using regex patterns
  - Format: `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`

- **Phone Validation**: International phone number validation
  - Digit-only validation after removing separators
  - Length constraints (7-15 digits)

- **Access Token Validation**: Hexadecimal token format validation
  - Pattern: `^[a-f0-9]{32,64}$`
  - Prevents SQL injection and path traversal

#### Model Level Constraints
- **Monetary Value Constraints**:
  - No negative values allowed
  - Maximum value: 999,999,999,999.99
  - Prevents overflow attacks

- **Date Validation**:
  - Logical date order enforcement
  - Publication < Closing < Opening dates

- **Uniqueness Constraints**:
  - CSD numbers (unique per supplier)
  - Company registration numbers (unique per supplier)
  - One bid per supplier per tender

### 2. XSS (Cross-Site Scripting) Protection

#### HTML Field Sanitization
All HTML fields are configured with comprehensive sanitization:
```python
sanitize=True
sanitize_tags=True
sanitize_attributes=True
sanitize_style=True
```

Protected fields:
- `tender.description`
- `tender.advertisement_text`

#### Template Security
- Use `t-esc` for text output (automatic escaping)
- Avoid `t-raw` unless absolutely necessary
- All user-generated content is escaped before rendering

### 3. SQL Injection Protection

#### ORM Usage
- Strict use of Odoo ORM for all database operations
- No raw SQL queries
- Parameterized searches using domain filters

#### Domain Validation
- All search domains use safe operators: `=`, `ilike`, `in`
- No user input directly concatenated into domains
- Input sanitization before domain construction

### 4. CSRF (Cross-Site Request Forgery) Protection

All form submissions include CSRF protection:
```python
@http.route(..., csrf=True)
```

Forms include CSRF tokens:
```xml
<input type="hidden" name="csrf_token" t-att-value="request.csrf_token()"/>
```

### 5. Authentication & Authorization

#### Access Control Rules
- **Multi-level access groups**:
  - Base User: Own requisitions only
  - SCM Officer: Tender management
  - Finance Officer: Budget confirmation
  - BEC Member: Bid evaluation
  - BAC Member: Award decisions
  - Tender Manager: Full access

#### Record-Level Security (RLS)
- Portal users see only published tenders
- Suppliers see only their own bids
- Users see only their own requisitions (unless elevated permissions)

#### Bid Submission Rules
- Authentication required (`auth='user'`)
- Company verification
- Blacklist checking
- Duplicate bid prevention

### 6. File Upload Security

#### Validation Measures
- **File Type Restrictions**: Only allowed extensions
  - Documents: .pdf, .doc, .docx
  - Spreadsheets: .xls, .xlsx
  - Images: .jpg, .jpeg, .png
  - Archives: .zip

- **File Size Limits**:
  - Per file: 50MB maximum
  - Per submission: 20 files maximum

- **Filename Sanitization**:
  - `werkzeug.utils.secure_filename()` for path traversal prevention
  - Removes directory separators and special characters

- **Privacy Controls**:
  - `public=False` on attachments
  - Files accessible only through proper authentication

### 7. Rate Limiting

#### Bid Submission Protection
- Maximum 3 bid submissions per 5 minutes per partner
- Prevents spam and DOS attacks
- Logged for security monitoring

#### Registration Protection
- IP-based rate limiting (framework for future enhancement)
- Prevents automated account creation

### 8. Cryptographic Security

#### Access Token Generation
- Cryptographically secure tokens using `secrets.token_hex(32)`
- 64-character hexadecimal strings
- Unpredictable and unique
- Checked for uniqueness on creation

### 9. Sensitive Data Protection

#### Minimal sudo() Usage
- Removed excessive `sudo()` calls
- Proper access rules enforced
- sudo() only used where absolutely necessary (public tender listing)

#### Data Minimization
- Only necessary fields exposed in public views
- Sensitive bid data hidden until appropriate state
- Evaluation data restricted to committee members

### 10. Security Logging

#### Comprehensive Event Logging
Logged security events:
- Invalid access token attempts
- Failed authentication attempts
- Unauthorized access attempts
- Rate limit violations
- File upload violations
- Bid submission activities

Log levels:
- `WARNING`: Security violations
- `INFO`: Normal security events
- `ERROR`: Critical security failures

### 11. Error Handling

#### Secure Error Messages
- Generic messages for public users
- Detailed logs for administrators
- No sensitive information in user-facing errors
- No stack traces exposed to end users

#### Exception Handling
```python
try:
    # Operations
except ValidationError as e:
    # User-friendly message
except Exception as e:
    _logger.exception("Detailed error for admin")
    # Generic message to user
```

## Security Best Practices

### For Developers

1. **Never bypass ORM**: Always use ORM methods, never raw SQL
2. **Validate all input**: Sanitize and validate all user inputs
3. **Use access rules**: Define proper record rules instead of using sudo()
4. **Log security events**: Use appropriate log levels for security monitoring
5. **Test with malicious input**: Test with XSS payloads, SQL injection attempts
6. **Keep dependencies updated**: Regularly update Odoo and Python packages

### For Administrators

1. **Monitor logs**: Regularly review security logs for suspicious activity
2. **Review access rights**: Periodically audit user permissions
3. **Enable HTTPS**: Always use HTTPS in production
4. **Backup regularly**: Maintain secure, encrypted backups
5. **Update regularly**: Apply security patches promptly
6. **Use strong passwords**: Enforce strong password policies
7. **Enable 2FA**: Use two-factor authentication for admin accounts

## Testing Security

### Recommended Security Tests

1. **SQL Injection Tests**:
   - Try special characters in search fields: `' OR '1'='1`
   - Test with SQL keywords in inputs

2. **XSS Tests**:
   - Submit `<script>alert('XSS')</script>` in text fields
   - Test with various XSS payloads

3. **CSRF Tests**:
   - Submit forms without CSRF tokens
   - Use tokens from different sessions

4. **Access Control Tests**:
   - Try accessing other users' bids
   - Attempt to view draft tenders as public user

5. **File Upload Tests**:
   - Upload malicious file types (.exe, .sh)
   - Upload oversized files
   - Upload files with path traversal names

## Vulnerability Response

If you discover a security vulnerability:

1. **Do NOT** open a public issue
2. Email security details to the module maintainer
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

## Security Updates Log

### Version 1.0 - Initial Security Hardening (January 2026)

**Implemented:**
- Input validation and sanitization across all controllers
- XSS protection with HTML field sanitization
- SQL injection prevention through ORM enforcement
- CSRF token validation on all forms
- File upload security with type/size validation
- Rate limiting on bid submissions and registrations
- Cryptographically secure access token generation
- Comprehensive security logging
- Model-level validation constraints
- Access control rules refinement
- Secure error handling

**Removed:**
- Excessive sudo() usage
- Unvalidated user inputs
- Raw SQL queries (none found)

**Enhanced:**
- Access token length (32 -> 64 chars)
- File upload restrictions
- Bid submission validation
- Email and phone validation

## Compliance

This module implements security controls aligned with:
- OWASP Top 10 Web Application Security Risks
- SA Government SCM Regulations
- POPIA (Protection of Personal Information Act)
- General Data Protection Principles

## Security Contact

For security-related questions or to report vulnerabilities, contact the development team through secure channels.

---

**Last Updated**: January 2026
**Security Review Status**: ✅ Hardened
**Next Review Date**: July 2026
