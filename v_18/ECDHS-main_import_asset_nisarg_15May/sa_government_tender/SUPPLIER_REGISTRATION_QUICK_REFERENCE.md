# Supplier Registration Quick Reference

## 🎯 What Was Implemented

When a supplier registers, the system now:
1. ✅ Creates a **portal user** automatically
2. ✅ Sets default password to **supplier's email address**
3. ✅ Sends **confirmation email** with account details
4. ✅ Includes **password reset link** (Odoo's native functionality)
5. ✅ Displays temporary password on success page

---

## 📧 Email Template Details

**Template ID:** `sa_government_tender.email_template_supplier_registration`

**Email Includes:**
- Welcome message
- Account details (company name, email, CSD number)
- **Temporary password** (= email address)
- **Password reset link** for immediate password change
- Portal access features list
- Login button

---

## 🔐 Password Information

### Default Password:
```
Username: supplier@email.com
Password: supplier@email.com  (same as email)
```

### Security Flow:
1. User registers → Portal account created
2. Default password = email address
3. Password reset link sent via email
4. User can either:
   - Use reset link to set new password (recommended)
   - Login with default password, then change it

---

## 📁 Files Modified

| File | Changes |
|------|---------|
| `controllers/supplier_portal.py` | Added password setting & custom email sending |
| `data/sagovemail_template_data.xml` | Created new email template |
| `views/templates/supplier_pages.xml` | Updated success page with password info |

---

## 🧪 Quick Test

### Test Registration:
1. Go to: `/supplier/register`
2. Fill form with test data
3. Submit registration
4. Check for:
   - Success message displayed
   - Email received (check spam folder)
   - Portal user created
   - Can login with email as password

### Test Email:
```python
# In Odoo shell
partner = env['res.partner'].search([('email', '=', 'test@example.com')], limit=1)
template = env.ref('sa_government_tender.email_template_supplier_registration')
template.send_mail(partner.id, force_send=True)
```

---

## 🚀 Deployment Steps

### 1. Update Module:
```bash
./odoo-bin -u sa_government_tender -d your_database
```

### 2. Verify Email Configuration:
- Settings > General Settings > Discuss
- Outgoing Mail Server configured
- Test email delivery

### 3. Test Registration:
- Create test supplier account
- Verify email received
- Test password reset link
- Test login with default password

---

## 🔍 Troubleshooting

### Email Not Sent?
```bash
# Check logs
tail -f /var/log/odoo/odoo.log | grep -i "registration"

# Verify template exists
# Settings > Technical > Email Templates
# Search: "Supplier: Registration Confirmation"
```

### Password Not Working?
- Ensure it's exactly the email address (no spaces)
- Try password reset link from email
- Check if user is active: `Settings > Users & Companies > Users`

### Template Not Found Error?
```bash
# Update module data
./odoo-bin -u sa_government_tender -d your_database --stop-after-init
```

---

## 📊 Key Code Snippets

### Setting Default Password:
```python
user._set_password(email)  # Sets password to email address
```

### Sending Confirmation Email:
```python
template = request.env.ref('sa_government_tender.email_template_supplier_registration')
user.action_reset_password()  # Generate reset token
template.sudo().send_mail(partner.id, force_send=True)
```

### Template Reference:
```xml
<field name="email_to">${object.email}</field>
<field name="subject">Welcome! Your Supplier Registration is Complete</field>
```

---

## ✅ Verification Checklist

- [ ] Module upgraded successfully
- [ ] Email template created in database
- [ ] Registration form works
- [ ] Portal user created automatically
- [ ] Default password (email) works for login
- [ ] Confirmation email received
- [ ] Password reset link works
- [ ] Success page shows temporary password
- [ ] Duplicate email blocked
- [ ] Error handling works

---

## 💡 Best Practices

### For Administrators:
- Monitor registration logs regularly
- Test email delivery periodically
- Keep backup of email templates
- Review security settings monthly

### For Suppliers:
- Use password reset link immediately after registration
- Change default password to strong password
- Keep registration email for reference
- Contact support if issues arise

---

## 🔗 Related Documentation

- Full Implementation Guide: `SUPPLIER_REGISTRATION_IMPLEMENTATION.md`
- Security Guidelines: `SECURITY.md`
- Frontend Guide: `FRONTEND_IMPLEMENTATION_GUIDE.md`

---

## 📞 Support

**Registration Issues:**
- Check: `/var/log/odoo/odoo.log`
- Test URL: `/supplier/register`
- Admin Panel: Settings > Users & Companies > Portal Users

**Email Issues:**
- Check: Settings > Technical > Email > Failed Messages
- Test: Settings > General Settings > Outgoing Mail Server > Test Connection
