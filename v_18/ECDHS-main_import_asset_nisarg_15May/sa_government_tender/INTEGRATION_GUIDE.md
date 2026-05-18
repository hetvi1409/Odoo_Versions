# Integration Guide - Linking Procurement Methods to Tender Models

## Overview

This guide shows how to integrate the new configurable procurement methods and preference point systems with existing tender management models.

---

## Step 1: Add Fields to Tender Model

### File: `models/sagovtender.py`

Add these fields after existing procurement_method selection:

```python
class SagovTender(models.Model):
    _name = 'sagov.tender'

    # ... existing fields ...

    # NEW: Link to configurable procurement method
    procurement_method_config_id = fields.Many2one(
        'sagovprocurement.method',
        string='Procurement Method Configuration',
        help='Link to configurable procurement method per PFMA/MFMA/PPPFA',
        tracking=True
    )

    # NEW: Link to configurable preference point system
    preference_point_system_config_id = fields.Many2one(
        'sagovpreference.point.system',
        string='Preference Point System Configuration',
        help='Link to configurable preference point system',
        tracking=True
    )

    # NEW: Dynamically load workflow stages
    workflow_stage_ids = fields.One2many(
        related='procurement_method_config_id.workflow_stage_ids',
        string='Workflow Stages',
        readonly=True
    )

    # NEW: Dynamically load document requirements
    document_requirement_ids = fields.One2many(
        related='procurement_method_config_id.document_requirement_ids',
        string='Document Requirements',
        readonly=True
    )

    # NEW: Dynamically load evaluation criteria
    evaluation_criteria_ids = fields.One2many(
        related='procurement_method_config_id.evaluation_criteria_ids',
        string='Evaluation Criteria',
        readonly=True
    )

    # ... rest of model ...
```

---

## Step 2: Add Computed Methods

### In `models/sagovtender.py`

```python
@api.onchange('estimated_value')
def _onchange_estimated_value(self):
    """
    Suggest procurement method based on estimated value
    """
    if self.estimated_value:
        method = self.env['sagovprocurement.method'].get_applicable_method(
            self.estimated_value
        )
        if method:
            self.procurement_method_config_id = method
            # Auto-select preference system if configured
            if method.preference_point_system_ids:
                self.preference_point_system_config_id = method.preference_point_system_ids[0]

@api.onchange('procurement_method_config_id')
def _onchange_procurement_method_config(self):
    """
    When procurement method changes, update related fields
    """
    if self.procurement_method_config_id:
        # Suggest preference system
        if self.procurement_method_config_id.preference_point_system_ids:
            self.preference_point_system_config_id = (
                self.procurement_method_config_id.preference_point_system_ids[0]
            )

        # Update evaluation criteria
        self.evaluation_criteria_ids = self.procurement_method_config_id.evaluation_criteria_ids

def get_workflow_stages(self):
    """Get ordered workflow stages for this tender"""
    if self.procurement_method_config_id:
        return self.procurement_method_config_id.get_workflow_sequence()
    return []

def get_required_documents(self):
    """Get all required documents for this tender"""
    if self.procurement_method_config_id:
        return self.procurement_method_config_id.get_document_requirements()
    return []

def validate_procurement_method_compliance(self):
    """Validate that selected method meets compliance requirements"""
    if not self.procurement_method_config_id:
        raise ValidationError('Procurement method must be selected')

    method = self.procurement_method_config_id

    # Check value thresholds
    if self.estimated_value < method.min_value:
        raise ValidationError(
            f'Estimated value (R{self.estimated_value}) is below minimum '
            f'for {method.name} (R{method.min_value})'
        )

    if method.max_value > 0 and self.estimated_value > method.max_value:
        raise ValidationError(
            f'Estimated value (R{self.estimated_value}) exceeds maximum '
            f'for {method.name} (R{method.max_value})'
        )

    # Check preference system for value range
    if method.preference_point_system_ids and self.preference_point_system_config_id:
        pref_system = self.preference_point_system_config_id
        if self.estimated_value < pref_system.minimum_applicable_value:
            raise ValidationError(
                f'Estimated value (R{self.estimated_value}) is below minimum '
                f'for {pref_system.name} (R{pref_system.minimum_applicable_value})'
            )

    return True
```

---

## Step 3: Update Tender Form View

### File: `views/sagovtender_views.xml`

```xml
<!-- Add to tender form after existing procurement_method field -->

<group string="Procurement Method Configuration">
    <field name="procurement_method_config_id" required="1"/>
    <field name="preference_point_system_config_id"
           attrs="{'required': [('procurement_method_config_id.requires_bec_evaluation', '=', True)]}"/>
</group>

<!-- Show workflow stages -->
<notebook>
    <page string="Workflow Stages" name="workflow_stages">
        <field name="workflow_stage_ids" readonly="1">
            <list>
                <field name="sequence"/>
                <field name="name"/>
                <field name="responsible_group"/>
                <field name="stage_type"/>
                <field name="required"/>
            </list>
        </field>
    </page>

    <page string="Document Requirements" name="doc_requirements">
        <field name="document_requirement_ids" readonly="1">
            <list>
                <field name="sequence"/>
                <field name="name"/>
                <field name="document_type"/>
                <field name="mandatory"/>
                <field name="valid_days"/>
            </list>
        </field>
    </page>

    <page string="Evaluation Criteria" name="eval_criteria">
        <field name="evaluation_criteria_ids" readonly="1">
            <list>
                <field name="sequence"/>
                <field name="name"/>
                <field name="criteria_type"/>
                <field name="weight_percentage"/>
            </list>
        </field>
    </page>
</notebook>
```

---

## Step 4: Add to Bid Evaluation Model

### File: `models/sagovbid_evaluation.py`

```python
class SagovBidEvaluation(models.Model):
    _name = 'sagov.bid.evaluation'

    # ... existing fields ...

    # Link to procurement method for evaluation criteria
    procurement_method_config_id = fields.Many2one(
        'sagovprocurement.method',
        string='Procurement Method',
        related='tender_id.procurement_method_config_id',
        readonly=True
    )

    # Link to preference system for scoring
    preference_point_system_config_id = fields.Many2one(
        'sagovpreference.point.system',
        string='Preference Point System',
        related='tender_id.preference_point_system_config_id',
        readonly=True
    )

    # Computed fields for scoring
    evaluation_criteria_ids = fields.One2many(
        'sagov.bid.evaluation.criteria',
        'evaluation_id',
        string='Evaluation Criteria'
    )

    @api.onchange('tender_id')
    def _onchange_tender(self):
        """Load evaluation criteria from tender's procurement method"""
        if self.tender_id and self.tender_id.procurement_method_config_id:
            method = self.tender_id.procurement_method_config_id
            criteria_data = []
            for criteria in method.get_evaluation_criteria():
                criteria_data.append((0, 0, {
                    'criteria_id': criteria.id,
                    'name': criteria.name,
                    'criteria_type': criteria.criteria_type,
                    'weight_percentage': criteria.weight_percentage,
                    'pass_fail': criteria.pass_fail,
                    'scoring_min': criteria.scoring_min,
                    'scoring_max': criteria.scoring_max,
                }))
            self.evaluation_criteria_ids = criteria_data

    def calculate_preference_score(self):
        """Calculate preference score using configured system"""
        if not self.preference_point_system_config_id:
            return 0.0

        # Build supplier attributes dictionary
        supplier_attrs = {
            'bbbee_level': self.supplier_id.bbbee_level or 0,
            'is_women_owned': self.supplier_id.is_women_owned or False,
            'is_youth_owned': self.supplier_id.is_youth_owned or False,
            'local_content_percentage': self.supplier_id.local_content_percentage or 0,
            'is_sme': self.supplier_id.is_sme or False,
            'is_pwd_owner': self.supplier_id.is_pwd_owner or False,
        }

        return self.preference_point_system_config_id.calculate_preference_score(
            supplier_attrs
        )

    def calculate_final_bid_score(self):
        """Calculate final bid score combining price and preference"""
        if not self.preference_point_system_config_id:
            return self.price_score

        pref_score = self.calculate_preference_score()
        final = self.preference_point_system_config_id.calculate_final_score(
            self.price_score or 0,
            pref_score
        )
        return final
```

---

## Step 5: Add to Annual Procurement Plan

### File: `models/annual_procurement_plan.py`

```python
class SagovAnnualProcurementPlan(models.Model):
    _name = 'sagov.annual.procurement.plan'

    # ... existing fields ...

    # Link to procurement method
    procurement_method_config_id = fields.Many2one(
        'sagovprocurement.method',
        string='Procurement Method',
        help='Recommended procurement method based on estimated value'
    )

    @api.onchange('estimated_value')
    def _onchange_estimated_value(self):
        """Suggest procurement method based on value"""
        if self.estimated_value:
            method = self.env['sagovprocurement.method'].get_applicable_method(
                self.estimated_value
            )
            if method:
                self.procurement_method_config_id = method

    def create_tender_from_app_line(self):
        """Create tender with procurement method from APP line"""
        # ... existing code ...
        tender_vals = {
            # ... existing values ...
            'procurement_method_config_id': self.procurement_method_config_id.id,
        }
        # ... rest of method ...
```

---

## Step 6: Add Compliance Validation

### File: `models/sagovtender.py`

```python
def button_validate_compliance(self):
    """Validate tender complies with procurement method requirements"""
    if not self.procurement_method_config_id:
        raise ValidationError('Procurement method must be selected')

    method = self.procurement_method_config_id

    # Validate value thresholds
    self.validate_procurement_method_compliance()

    # Check required documents
    required_docs = method.get_document_requirements()
    missing_docs = []
    for req_doc in required_docs:
        if req_doc.mandatory:
            # Check if document is attached
            if not self.env['ir.attachment'].search_count([
                ('res_model', '=', 'sagov.tender'),
                ('res_id', '=', self.id),
                ('name', 'ilike', req_doc.name)
            ]):
                missing_docs.append(req_doc.name)

    if missing_docs:
        raise ValidationError(
            f'Missing required documents:\n' + '\n'.join(missing_docs)
        )

    # Check workflow stage completion
    current_stage = self._get_current_workflow_stage()
    if not current_stage:
        raise ValidationError('Invalid workflow state')

    # Check committee requirements
    if method.requires_bsc_approval and not self.bsc_approval_id:
        raise ValidationError('BSC Approval is required for this procurement method')

    if method.requires_bec_evaluation and not self.bec_evaluation_ids:
        raise ValidationError('BEC Evaluation is required for this procurement method')

    if method.requires_bac_review and not self.bac_review_ids:
        raise ValidationError('BAC Review is required for this procurement method')

    # If all validations pass
    self.message_post(body='Procurement method compliance validated successfully')
    return True
```

---

## Step 7: Add Reports/Dashboards

### Example Dashboard Definition

```python
# In new file: models/procurement_method_dashboard.py

class ProcurementMethodDashboard(models.TransientModel):
    _name = 'procurement.method.dashboard'
    _description = 'Procurement Method Dashboard'

    def get_method_usage_stats(self):
        """Get statistics on procurement method usage"""
        Tender = self.env['sagov.tender']

        methods = self.env['sagovprocurement.method'].search([])
        stats = []

        for method in methods:
            tender_count = Tender.search_count([
                ('procurement_method_config_id', '=', method.id),
                ('state', '=', 'done')
            ])

            total_value = Tender.search([
                ('procurement_method_config_id', '=', method.id),
                ('state', '=', 'done')
            ]).mapped('approved_budget')

            stats.append({
                'method_name': method.name,
                'tender_count': tender_count,
                'total_value': sum(total_value),
                'avg_value': sum(total_value) / tender_count if tender_count > 0 else 0,
                'compliance_status': 'Compliant' if method.validate_compliance() else 'Non-compliant'
            })

        return stats

    def get_preference_system_usage(self):
        """Get preference system usage statistics"""
        Tender = self.env['sagov.tender']

        systems = self.env['sagovpreference.point.system'].search([])
        usage = []

        for system in systems:
            tender_count = Tender.search_count([
                ('preference_point_system_config_id', '=', system.id),
                ('state', '=', 'done')
            ])

            usage.append({
                'system_name': system.name,
                'tender_count': tender_count,
                'price_weight': system.price_weight_percentage,
                'preference_weight': system.preference_weight_percentage
            })

        return usage
```

---

## Step 8: Add Security/Access Rules

### File: `security/ir.model.access.csv`

```
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_sagovprocurement_method_user,sagovprocurement.method user,model_sagovprocurement_method,group_scm_user,1,0,0,0
access_sagovprocurement_method_manager,sagovprocurement.method manager,model_sagovprocurement_method,group_scm_manager,1,1,1,1
access_sagovpreference_point_system_user,sagovpreference.point.system user,model_sagovpreference_point_system,group_scm_user,1,0,0,0
access_sagovpreference_point_system_manager,sagovpreference.point.system manager,model_sagovpreference_point_system,group_scm_manager,1,1,1,1
access_sagovprocurement_workflow_stage_user,sagovprocurement.workflow.stage user,model_sagovprocurement_workflow_stage,group_scm_user,1,0,0,0
access_sagovprocurement_workflow_stage_manager,sagovprocurement.workflow.stage manager,model_sagovprocurement_workflow_stage,group_scm_manager,1,1,1,1
```

---

## Testing Integration

### Test Cases

```python
# In tests/test_procurement_method_integration.py

def test_tender_procurement_method_onchange():
    """Test that tender auto-selects procurement method on value change"""
    tender = self.env['sagov.tender'].create({
        'name': 'Test Tender',
        'estimated_value': 50000,
    })

    assert tender.procurement_method_config_id.code == 'open_rfq_r30k_r300k'
    assert tender.preference_point_system_config_id.code == 'system_80_20'

def test_bid_evaluation_criteria_loading():
    """Test that bid evaluation loads criteria from procurement method"""
    # Create tender with competitive bid method
    tender = self.env['sagov.tender'].create({
        'name': 'Test Competitive Bid',
        'estimated_value': 25000000,  # R25M
        'procurement_method_config_id': self.ref('procurement_method_competitive_bid_r50m')
    })

    # Create bid evaluation
    evaluation = self.env['sagov.bid.evaluation'].create({
        'tender_id': tender.id
    })

    # Should have loaded criteria from method
    assert len(evaluation.evaluation_criteria_ids) > 0
    assert any(c.name == 'Technical Compliance' for c in evaluation.evaluation_criteria_ids)

def test_preference_score_calculation():
    """Test preference score calculation using configured system"""
    pref_system = self.ref('preference_point_system_80_20')

    supplier_attrs = {
        'bbbee_level': 1,  # Level 1 BEE
        'is_women_owned': True,
        'is_youth_owned': False,
        'local_content_percentage': 100,
        'is_sme': False,
        'is_pwd_owner': False,
    }

    score = pref_system.calculate_preference_score(supplier_attrs)

    # 15 (B-BBEE) + 3 (Women) + 4 (Local) = 22
    # But max is 20, so should cap at 20
    assert score == 20.0

def test_final_score_calculation():
    """Test final bid score combining price and preference"""
    pref_system = self.ref('preference_point_system_80_20')

    # Price: 75/100, Preference: 18/20
    final = pref_system.calculate_final_score(75, 18)

    # (75/100 * 80) + (18/20 * 20) = 60 + 18 = 78
    assert final == 78.0
```

---

## Conclusion

This integration connects the new configurable procurement methods and preference point systems with the existing tender management workflow, enabling:

✅ Dynamic method selection based on value
✅ Automated workflow configuration
✅ Compliance validation
✅ Preference point calculation
✅ Audit trail tracking
✅ Regulatory reporting

All configurations are centralized and easily maintainable without code changes.
