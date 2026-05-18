from odoo import fields, models

class HrJobRevert(models.TransientModel):
    """Hr jobs Revert"""
    _name = 'hr.job.revert'
    _description = "Hr jobs Revert"

    job_id = fields.Many2one('hr.job', string="Job")
    comments = fields.Text(string="Comments", required=True)

    def action_submit(self):
        """Submit button"""
        job = self.job_id
        body = "Revert Comment: %s" % self.comments
        job.message_post(body=body)
        if not job.approval_state:
            job.requisition_state = 'draft'
        if job.approval_state == 'department_line_manager_approve':
            job.approval_state = ''
        if job.approval_state == 'department_line_executive_approval':
            job.approval_state = 'department_line_manager_approve'
        if job.approval_state == 'od_manager_approval':
            job.approval_state = 'department_line_executive_approval'
        if job.approval_state == 'cost_management_accounting_approval':
            job.approval_state = 'od_manager_approval'