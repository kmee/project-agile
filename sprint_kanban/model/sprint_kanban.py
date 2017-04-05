# coding: utf-8

from odoo import models, fields


class SprintKanban(models.Model):

    def set_done(self):
        self.write(ids, {'state': 'done'})
        return True

    def set_cancel(self):

        self.write(ids, {'state': 'cancelled'})
        return True

    def set_pending(self):
        self.write(ids, {'state': 'pending'})
        return True

    def set_open(self):
        self.write(ids, {'state': 'open'})
        return True

    _name = 'sprint.kanban'
    _inherit = ['mail.thread', 'ir.needaction_mixin']


    use_phases = fields.Boolean('Phases'
                                     help="""Check this field if you plan
                                             to use phase-based scheduling"""),
    name = fields.Char('Name Sprint', 264, required=True)
    project_id = fields.Many2one('project.project', 'Project'
                                      ondelete="cascade"),
    description = fields.Text('Description')
    datestart = fields.Date('Start Date')
    dateend = fields.Date('End Date')
    color = fields.Integer('Color Index')
    members = fields.Many2many('res.users', 'project_user_rel'
                                    'project_id', 'uid', 'Project Members',
                                    states={'close': [('readonly', True)],
                                            'cancelled': [('readonly', True)],
                                            }),
    priority = fields.Selection([('4', 'Very Low')
                                      ('3', 'Low'),
                                      ('2', 'Medium'),
                                      ('1', 'Important'),
                                      ('0', 'Very important')],
                                     'Priority', index=True),
    state = fields.Selection([('draft', 'New')
                                   ('open', 'In Progress'),
                                   ('cancelled', 'Cancelled'),
                                   ('pending', 'Pending'),
                                   ('done', 'Done')],
                                  'Status', required=True,),
    user_id = fields.Many2one('res.users', 'Assigned to')
    kanban_state = fields.Selection([('normal', 'Normal')
                                          ('blocked', 'Blocked'),
                                          ('done', 'Ready To Pull')],
                                         'Kanban State',
                                         help="""A task's kanban state indicate
                                                 special situations
                                                 affecting it:\n
                                               * Normal is the default
                                                 situation\n"
                                               * Blocked indicates something
                                                 is preventing the progress
                                                 of this task\n
                                               * Ready To Pull indicates the
                                                 task is ready to be pulled
                                                 to the next stage""",
                                         readonly=True, required=False),


    def set_kanban_state_blocked(self):
        self.write(ids, {'kanban_state': 'blocked'})
        return False

    def set_kanban_state_normal(self):
        self.write(ids, {'kanban_state': 'normal'})
        return False

    def set_kanban_state_done(self):
        self.write(ids, {'kanban_state': 'done'})
        return False

    def set_priority(self, priority, *args):
        return self.write(ids, {'priority': priority})

    def set_high_priority(self, *args):
        return self.set_priority(ids, '1')

    def set_normal_priority(self, *args):
        return self.set_priority(ids, '2')

    _defaults = {
        'state': 'draft',
        'priority': '1',
    }


class SprintKanbanTasks(models.Model):

    _inherit = 'project.task'


    use_phases = fields.Boolean('Phases'
                                     help="""Check this field if you plan
                                             to use phase-based scheduling"""),
    sprint_id = fields.Many2one('sprint.kanban', 'Sprint'
                                     ondelete="cascade"),
    url_branch = fields.Char('Url Branch', 264)
    merge_proposal = fields.Char('Merge Proposal', 264)
    blueprint = fields.Char('Blueprint', 264)
    res_id = fields.Char('Revno', 64)

