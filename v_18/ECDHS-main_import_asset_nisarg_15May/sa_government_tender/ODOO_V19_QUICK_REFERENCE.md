# ODOO V19 QUICK REFERENCE GUIDE
## SA Government Tender Management Module

**Module:** sa_government_tender
**Odoo Version:** v19
**Last Updated:** February 5, 2026

---

## 🎯 QUICK MIGRATION CHECKLIST

### ✅ Completed Changes:

- [x] **Tree → List:** All `<tree>` tags replaced with `<list>`
- [x] **Chatter Update:** All `<div class="oe_chatter">` replaced with `<chatter/>`
- [x] **Many2One Options:** Added to ALL many2one fields in XML
- [x] **No States/Attrs:** All using `invisible`, `readonly`, `required`
- [x] **XML Validation:** All files pass syntax validation

---

## 📝 ODOO V19 SYNTAX QUICK REFERENCE

### List Views (formerly Tree Views)

**❌ OLD (Odoo v17 and earlier):**
```xml
<tree string="My Records">
    <field name="name"/>
    <field name="partner_id"/>
</tree>
```

**✅ NEW (Odoo v18+):**
```xml
<list string="My Records">
    <field name="name"/>
    <field name="partner_id"/>
</list>
```

---

### Chatter / Communication Panel

**❌ OLD (Odoo v18 and earlier):**
```xml
<div class="oe_chatter">
    <field name="message_follower_ids"/>
    <field name="activity_ids"/>
    <field name="message_ids"/>
</div>
```

**✅ NEW (Odoo v19):**
```xml
<chatter/>
```

---

### Many2One Field Options

**❌ OLD (Missing options):**
```xml
<field name="partner_id"/>
```

**✅ NEW (With restrictions):**
```xml
<field name="partner_id" options="{'no_create': True,'no_quick_create': True,'no_create_edit': True}"/>
```

**Options Explained:**
- `no_create: True` - Removes "Create" option from dropdown
- `no_quick_create: True` - Removes quick create popup
- `no_create_edit: True` - Removes "Create and Edit" option

---

### Visibility / Readonly / Required

**❌ OLD (Using attrs/states):**
```xml
<field name="amount" attrs="{'invisible': [('state', '!=', 'done')], 'readonly': [('state', '=', 'done')]}"/>
<field name="status" states="draft,sent"/>
```

**✅ NEW (Using direct attributes):**
```xml
<field name="amount" invisible="state != 'done'" readonly="state == 'done'"/>
<field name="status" invisible="state not in ['draft', 'sent']"/>
```

---

### Button Visibility

**❌ OLD (Using attrs):**
```xml
<button name="action_confirm" string="Confirm" attrs="{'invisible': [('state', '!=', 'draft')]}"/>
```

**✅ NEW (Using invisible):**
```xml
<button name="action_confirm" string="Confirm" invisible="state != 'draft'"/>
```

---

### Status Bar Widget

**✅ CORRECT (Always worked):**
```xml
<field name="state" widget="statusbar"/>
```

**✅ ALSO CORRECT (With visible states):**
```xml
<field name="state" widget="statusbar" statusbar_visible="draft,sent,done"/>
```

---

### Badge Widget for Status

**✅ CORRECT:**
```xml
<field name="state" widget="badge"
       decoration-success="state == 'done'"
       decoration-warning="state == 'pending'"
       decoration-danger="state == 'rejected'"/>
```

---

### List Decorations

**✅ CORRECT:**
```xml
<list decoration-success="state == 'done'"
      decoration-info="state == 'draft'"
      decoration-warning="state == 'pending'"
      decoration-danger="state == 'rejected'"
      decoration-muted="state == 'cancelled'">
    <field name="name"/>
    <field name="state"/>
</list>
```

**Available Decorations:**
- `decoration-success` - Green
- `decoration-info` - Blue
- `decoration-warning` - Orange
- `decoration-danger` - Red
- `decoration-muted` - Gray
- `decoration-bf` - Bold font
- `decoration-it` - Italic font

---

## 🔧 COMMON PATTERNS

### Form View with Header and Chatter

```xml
<form>
    <header>
        <button name="action_confirm" string="Confirm"
                type="object" class="btn-primary"
                invisible="state != 'draft'"/>
        <field name="state" widget="statusbar"/>
    </header>
    <sheet>
        <div class="oe_button_box" name="button_box">
            <button name="action_view_invoices" type="object"
                    class="oe_stat_button" icon="fa-file-text">
                <field name="invoice_count" widget="statbutton"/>
            </button>
        </div>
        <group>
            <field name="name"/>
            <field name="partner_id"
                   options="{'no_create': True,'no_quick_create': True,'no_create_edit': True}"/>
        </group>
    </sheet>
    <chatter/>
</form>
```

---

### List View with Actions

```xml
<list string="Records" editable="bottom"
      decoration-success="state == 'done'">
    <field name="sequence" widget="handle"/>
    <field name="name"/>
    <field name="partner_id"
           options="{'no_create': True,'no_quick_create': True,'no_create_edit': True}"/>
    <field name="state" widget="badge"/>
    <button name="action_approve" string="Approve"
            type="object" icon="fa-check"
            invisible="state != 'pending'"/>
</list>
```

---

### Notebook with Multiple Pages

```xml
<notebook>
    <page string="General" name="general">
        <group>
            <field name="name"/>
            <field name="date"/>
        </group>
    </page>
    <page string="Details" name="details" invisible="state == 'draft'">
        <field name="line_ids">
            <list editable="bottom">
                <field name="product_id"
                       options="{'no_create': True,'no_quick_create': True,'no_create_edit': True}"/>
                <field name="quantity"/>
            </list>
        </field>
    </page>
</notebook>
```

---

### Kanban View

```xml
<kanban>
    <field name="name"/>
    <field name="state"/>
    <templates>
        <t t-name="kanban-box">
            <div class="oe_kanban_global_click">
                <div class="o_kanban_record_top">
                    <strong><field name="name"/></strong>
                </div>
                <div class="o_kanban_record_body">
                    <field name="partner_id"
                           options="{'no_create': True,'no_quick_create': True,'no_create_edit': True}"/>
                </div>
                <div class="o_kanban_record_bottom">
                    <field name="state" widget="badge"/>
                </div>
            </div>
        </t>
    </templates>
</kanban>
```

---

### Search View

```xml
<search>
    <field name="name"/>
    <field name="partner_id"
           options="{'no_create': True,'no_quick_create': True,'no_create_edit': True}"/>
    <filter name="draft" string="Draft" domain="[('state','=','draft')]"/>
    <filter name="done" string="Done" domain="[('state','=','done')]"/>
    <separator/>
    <group expand="0" string="Group By">
        <filter name="group_partner" string="Partner" context="{'group_by':'partner_id'}"/>
        <filter name="group_state" string="Status" context="{'group_by':'state'}"/>
    </group>
</search>
```

---

## 🚫 DEPRECATED FEATURES (DO NOT USE)

### ❌ Tree Tag (use list instead)
```xml
<!-- DEPRECATED -->
<tree>...</tree>

<!-- USE THIS -->
<list>...</list>
```

---

### ❌ Old Chatter Structure
```xml
<!-- DEPRECATED -->
<div class="oe_chatter">
    <field name="message_follower_ids"/>
    <field name="activity_ids"/>
    <field name="message_ids"/>
</div>

<!-- USE THIS -->
<chatter/>
```

---

### ❌ States Attribute
```xml
<!-- DEPRECATED -->
<field name="amount" states="draft,sent"/>

<!-- USE THIS -->
<field name="amount" invisible="state not in ['draft', 'sent']"/>
```

---

### ❌ Attrs Attribute
```xml
<!-- DEPRECATED -->
<field name="amount" attrs="{'invisible': [('state', '!=', 'done')]}"/>

<!-- USE THIS -->
<field name="amount" invisible="state != 'done'"/>
```

---

## 💡 BEST PRACTICES

### 1. Always Add Options to Many2One Fields
```xml
<!-- RECOMMENDED -->
<field name="partner_id"
       options="{'no_create': True,'no_quick_create': True,'no_create_edit': True}"/>
```

### 2. Use Descriptive String Attributes
```xml
<!-- GOOD -->
<list string="Purchase Requisitions">
    <field name="name" string="Requisition Number"/>
</list>
```

### 3. Use Widget for Better UX
```xml
<!-- MONETARY FIELDS -->
<field name="amount" widget="monetary"/>

<!-- PERCENTAGE FIELDS -->
<field name="progress" widget="progressbar"/>

<!-- BOOLEAN FIELDS -->
<field name="active" widget="boolean_toggle"/>

<!-- STATUS FIELDS -->
<field name="state" widget="badge"/>
```

### 4. Use Decorations for Visual Feedback
```xml
<list decoration-success="state == 'approved'"
      decoration-danger="state == 'rejected'">
    ...
</list>
```

### 5. Group Related Fields
```xml
<group>
    <group string="Basic Information">
        <field name="name"/>
        <field name="date"/>
    </group>
    <group string="Financial">
        <field name="amount" widget="monetary"/>
        <field name="currency_id"/>
    </group>
</group>
```

---

## 🔍 FIELD DOMAIN EXAMPLES

### Basic Domain
```xml
<field name="partner_id" domain="[('customer_rank', '>', 0)]"/>
```

### Domain with Parent Field
```xml
<field name="product_id" domain="[('categ_id', '=', category_id)]"/>
```

### Complex Domain
```xml
<field name="line_id" domain="[
    ('state', '=', 'draft'),
    ('partner_id', '=', partner_id),
    ('date', '>=', date_from),
    ('date', '<=', date_to)
]"/>
```

### Domain with OR
```xml
<field name="product_id" domain="[
    '|',
    ('type', '=', 'product'),
    ('type', '=', 'consu')
]"/>
```

---

## 📊 WIDGETS REFERENCE

### Common Field Widgets:

| Widget | Use Case | Example |
|--------|----------|---------|
| `monetary` | Currency amounts | `<field name="amount" widget="monetary"/>` |
| `percentage` | Percentage values | `<field name="discount" widget="percentage"/>` |
| `progressbar` | Progress indicators | `<field name="progress" widget="progressbar"/>` |
| `badge` | Status fields | `<field name="state" widget="badge"/>` |
| `statusbar` | State workflow | `<field name="state" widget="statusbar"/>` |
| `boolean_toggle` | On/off switches | `<field name="active" widget="boolean_toggle"/>` |
| `html` | Rich text editor | `<field name="description" widget="html"/>` |
| `image` | Image fields | `<field name="image" widget="image"/>` |
| `many2many_tags` | Tag display | `<field name="tag_ids" widget="many2many_tags"/>` |
| `selection_badge` | Selection as badge | `<field name="priority" widget="selection_badge"/>` |
| `handle` | Drag handle (sequence) | `<field name="sequence" widget="handle"/>` |
| `statbutton` | Statistics button | `<field name="count" widget="statbutton"/>` |

---

## 🎨 DECORATION COLORS

### List/Tree Decorations:

| Decoration | Color | Use Case |
|------------|-------|----------|
| `decoration-success` | Green | Completed, Approved |
| `decoration-info` | Blue | In Progress, Info |
| `decoration-warning` | Orange | Warning, Pending |
| `decoration-danger` | Red | Error, Rejected |
| `decoration-muted` | Gray | Cancelled, Archived |
| `decoration-bf` | Bold | Emphasis |
| `decoration-it` | Italic | Secondary info |

**Example:**
```xml
<list decoration-success="state == 'done'"
      decoration-warning="amount > 10000"
      decoration-danger="date_due < current_date">
```

---

## 🔐 SECURITY & ACCESS

### Record Rules in XML:
```xml
<record id="rule_my_records" model="ir.rule">
    <field name="name">My Records</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="domain_force">[('user_id', '=', user.id)]</field>
    <field name="groups" eval="[(4, ref('base.group_user'))]"/>
</record>
```

### Access Rights in CSV:
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_user,my.model.user,model_my_model,base.group_user,1,1,1,0
access_my_model_manager,my.model.manager,model_my_model,base.group_system,1,1,1,1
```

---

## 🛠️ TROUBLESHOOTING

### Issue: Fields Not Showing
**Solution:** Check `invisible` attribute:
```xml
<!-- WRONG - always hidden -->
<field name="amount" invisible="1"/>

<!-- CORRECT - conditionally hidden -->
<field name="amount" invisible="state != 'done'"/>
```

---

### Issue: Many2One Allows Creation
**Solution:** Add proper options:
```xml
<field name="partner_id"
       options="{'no_create': True,'no_quick_create': True,'no_create_edit': True}"/>
```

---

### Issue: Chatter Not Showing
**Solution:** Use `<chatter/>` tag:
```xml
<!-- WRONG -->
<div class="oe_chatter">...</div>

<!-- CORRECT -->
<chatter/>
```

---

### Issue: Tree View Not Loading
**Solution:** Replace with `<list>`:
```xml
<!-- WRONG -->
<tree>...</tree>

<!-- CORRECT -->
<list>...</list>
```

---

## 📞 GETTING HELP

### Documentation:
- **Odoo v19 Docs:** https://www.odoo.com/documentation/19.0/
- **View Architecture:** https://www.odoo.com/documentation/19.0/th/developer/reference/user_interface/view_architectures.html
- **Module Report:** ODOO_V19_UPGRADE_REPORT.md

### Common Commands:
```bash
# Update module
odoo-bin -u sa_government_tender -d database_name

# Check logs
tail -f /var/log/odoo/odoo-server.log

# Validate XML
xmllint --noout views/*.xml
```

---

## ✅ PRE-DEPLOYMENT CHECKLIST

- [ ] All `<tree>` tags replaced with `<list>`
- [ ] All `<div class="oe_chatter">` replaced with `<chatter/>`
- [ ] All many2one fields have options in XML
- [ ] No `states=` attributes in use
- [ ] No `attrs=` attributes in use
- [ ] XML validation passed
- [ ] Module upgrade tested
- [ ] User acceptance testing completed

---

**🎉 You're Ready for Odoo v19!**

All changes have been implemented and validated. Your module is now fully compliant with Odoo v19 standards.

---

*Quick Reference Guide - Last Updated: February 5, 2026*
