# coding: utf-8

from openerp import models, fields, api


class UserStory(models.Model):
    _inherit = 'user.story'

    @api.multi
    @api.depends(
	'task_ids.work_ids', 
	'task_ids.work_ids.to_invoice',
	'task_ids.work_ids.invoiceables_hours',
	'task_ids.work_ids.unit_amount',
	'task_ids.work_ids.line_id.invoiceables_hours',
	'task_ids.work_ids.line_id.unit_amount'
    )
    def _compute_hours(self):
	for us in self:
	    hat = self.env['hr.analytic.timesheet'].search([(
		'task_id', 'in', us.task_ids.ids
               )])
            us.invoiceable_hours= sum(i.invoiceables_hours for i in hat if i.to_invoice)
            us.effective_hours = sum(i.unit_amount for i in hat)

    invoiceable_hours = fields.Float(
        compute='_compute_hours',
        store=True,
    )

    effective_hours = fields.Float(
        compute='_compute_hours',
        store=True,
    )

