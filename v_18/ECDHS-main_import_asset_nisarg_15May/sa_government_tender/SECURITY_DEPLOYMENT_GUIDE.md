# Security Hardening - Deployment Instructions

## Quick Start

This module has been comprehensively secured against web-based attacks. Follow these steps for secure deployment.

## ✅ Changes Applied

### Security Improvements Implemented:
1. ✅ Input validation and sanitization
2. ✅ XSS protection (HTML sanitization)
3. ✅ SQL injection prevention (ORM enforcement)
4. ✅ CSRF protection (verified)
5. ✅ File upload security
6. ✅ Access control hardening
7. ✅ Rate limiting
8. ✅ Security logging
9. ✅ Cryptographic improvements
10. ✅ Data validation constraints

### Files Modified:
- `controllers/main.py` - Enhanced security controls
- `controllers/supplier_portal.py` - Input validation
- `models/sagovtender.py` - Model constraints
- `models/sagovtender_bid.py` - Bid validation
- `models/res_partner.py` - Partner validation
- `security/sagovtender_security.xml` - Access rules

### Documentation Added:
- `SECURITY.md` - Comprehensive security guide
- `SECURITY_CHECKLIST.md` - Implementation checklist
- `SECURITY_QUICK_REFERENCE.md` - Developer guide
- `SECURITY_IMPLEMENTATION_REPORT.md` - Detailed report

## 🚀 Deployment Steps

### 1. Backup Current System
```bash
# Backup database
pg_dump your_database > backup_$(date +%Y%m%d).sql

# Backup file storage
tar -czf filestore_backup_$(date +%Y%m%d).tar.gz /path/to/filestore
```

### 2. Update Module Code
```bash
cd /path/to/sa_government_tender
git pull origin main  # Or your branch with security fixes
```

### 3. Restart Odoo Service
```bash
sudo systemctl restart odoo
# or
sudo service odoo restart
```

### 4. Update Module in Odoo
- Log in as administrator
- Go to Apps
- Find "SA Government Tender Management"
- Click "Upgrade" button
- Wait for upgrade to complete

### 5. Verify Security Features
Run these checks:

#### Check 1: Access Control
- Log in as portal user
- Try to access `/sagovtenders`
- Verify only published tenders visible
- Try to access another user's bid (should fail)

#### Check 2: Input Validation
- Try searching with `<script>alert('test')</script>`
- Verify it's sanitized
- Try entering negative bid amount (should be rejected)

#### Check 3: File Upload
- Try uploading a `.exe` file (should be rejected)
- Try uploading 60MB file (should be rejected)
- Try uploading valid PDF (should work)

#### Check 4: Rate Limiting
- Submit 4 bids quickly (4th should be blocked)
- Wait 5 minutes and try again (should work)

### 6. Configure Production Server

#### Enable HTTPS (Critical!)
```bash
# Example for Apache
sudo a2enmod ssl
sudo systemctl restart apache2

# Update Odoo config
# /etc/odoo/odoo.conf
proxy_mode = True
```

#### Configure Firewall
```bash
# Allow only necessary ports
sudo ufw allow 443/tcp  # HTTPS
sudo ufw allow 22/tcp   # SSH
sudo ufw enable
```

#### Secure Database Access
```bash
# Edit PostgreSQL config
# /etc/postgresql/*/main/pg_hba.conf
# Ensure only localhost can connect:
local   all             all                                     peer
host    all             all             127.0.0.1/32            md5
```

#### Set Secure Passwords
```bash
# Change Odoo admin password via interface
# Use strong password (16+ chars, mixed case, numbers, symbols)

# Change database password
sudo -u postgres psql
ALTER USER odoo_user WITH PASSWORD 'strong_password_here';
```

## 🔍 Post-Deployment Verification

### Security Checklist
- [ ] HTTPS enabled and working
- [ ] Admin password is strong
- [ ] Database password changed
- [ ] Firewall configured
- [ ] Debug mode disabled in production
- [ ] All ports except 443/22 closed
- [ ] Backups configured and tested
- [ ] Monitoring enabled
- [ ] Log rotation configured
- [ ] Security logs reviewed

### Test Security Features
```bash
# Test SQL injection (should be blocked)
curl "https://your-domain.com/sagovtenders?search=%27%20OR%20%271%27%3D%271"

# Test XSS (should be sanitized)
# Try submitting <script>alert('xss')</script> in search

# Test file upload restrictions
# Try uploading .exe file (should fail)

# Test access control
# Try accessing /my/bid/999 from another user (should fail)
```

## 📊 Monitoring

### Check Security Logs Daily
```bash
# Odoo logs
tail -f /var/log/odoo/odoo-server.log | grep -i "warning\|error"

# Look for suspicious patterns:
grep "Invalid access token" /var/log/odoo/odoo-server.log
grep "Rate limit" /var/log/odoo/odoo-server.log
grep "Unauthorized access" /var/log/odoo/odoo-server.log
```

### Set Up Alerts
Configure email alerts for:
- Failed login attempts (>5 in 1 hour)
- Rate limit violations
- File upload violations
- Database errors
- System resource alerts

## 🚨 Incident Response

### If You Detect a Security Issue:

1. **Immediate Actions**:
   ```bash
   # Take snapshot/backup
   # Isolate affected system if needed
   # Check logs for extent of compromise
   ```

2. **Investigation**:
   - Review security logs
   - Check access logs
   - Identify affected users/data
   - Document timeline

3. **Remediation**:
   - Apply security patches
   - Reset compromised credentials
   - Notify affected users (if required)
   - Update security measures

4. **Post-Incident**:
   - Conduct root cause analysis
   - Update security procedures
   - Provide training if needed
   - Document lessons learned

## 📞 Support & Resources

### Documentation
- `SECURITY.md` - Comprehensive security documentation
- `SECURITY_CHECKLIST.md` - Implementation checklist
- `SECURITY_QUICK_REFERENCE.md` - Developer guide
- `SECURITY_IMPLEMENTATION_REPORT.md` - Detailed changes

### Security Testing
- OWASP ZAP: https://www.zaproxy.org/
- Burp Suite: https://portswigger.net/burp
- nmap: https://nmap.org/

### Training Resources
- OWASP Top 10: https://owasp.org/Top10/
- Odoo Security: https://www.odoo.com/documentation/security
- Python Security: https://docs.python.org/3/library/security_warnings.html

## ✨ Quick Wins

After deployment, you've achieved:
- ✅ Protection against SQL injection
- ✅ XSS attack prevention
- ✅ CSRF protection
- ✅ Secure file uploads
- ✅ Rate limiting
- ✅ Enhanced access control
- ✅ Comprehensive logging
- ✅ Input validation
- ✅ Data integrity constraints

## 🎯 Next Steps

### Week 1
- Monitor logs daily
- Check for any issues
- Verify all features working
- User acceptance testing

### Month 1
- Review security logs weekly
- Check access patterns
- Update any issues found
- User feedback collection

### Ongoing
- Monthly security reviews
- Quarterly penetration testing
- Annual security audit
- Continuous improvement

## ⚡ Quick Reference Commands

```bash
# View security logs
sudo tail -f /var/log/odoo/odoo-server.log | grep -E "WARNING|ERROR"

# Restart Odoo
sudo systemctl restart odoo

# Check Odoo status
sudo systemctl status odoo

# View database connections
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"

# Check disk space
df -h

# Check memory usage
free -h

# Update system packages
sudo apt update && sudo apt upgrade -y
```

## 📋 Rollback Plan

If issues occur:

```bash
# 1. Stop Odoo
sudo systemctl stop odoo

# 2. Restore database backup
sudo -u postgres psql
DROP DATABASE your_database;
CREATE DATABASE your_database;
\q
sudo -u postgres psql your_database < backup_YYYYMMDD.sql

# 3. Restore filestore (if needed)
cd /path/to/odoo
rm -rf filestore/your_database
tar -xzf filestore_backup_YYYYMMDD.tar.gz

# 4. Restart Odoo
sudo systemctl start odoo

# 5. Check logs
tail -f /var/log/odoo/odoo-server.log
```

## ✅ Success Criteria

Deployment is successful when:
- [ ] Module upgrades without errors
- [ ] All existing features work correctly
- [ ] Security tests pass
- [ ] No performance degradation
- [ ] Logs show no errors
- [ ] Users can access system normally
- [ ] Bids can be submitted successfully
- [ ] File uploads work correctly
- [ ] Access control works as expected

---

**Need Help?**
- Check `SECURITY.md` for detailed documentation
- Review logs for specific error messages
- Test in staging environment first
- Contact support if issues persist

**Last Updated**: January 21, 2026
**Module Version**: 1.0+ (Security Hardened)
