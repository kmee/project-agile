# -*- coding: utf-8 -*-
# Copyright 2017 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp import api, fields, models, SUPERUSER_ID, _


class UserStoryType(models.Model):
    _name = 'user.story.type'
    _description = 'User Story Type'
    _order = 'sequence, id'

    def _get_mail_template_id_domain(self):
        return [('model', '=', 'user.story')]

    def _get_default_project_ids(self):
        default_project_id = self.env.context.get('default_project_id')
        return [default_project_id] if default_project_id else None

    name = fields.Char(string='Stage Name', required=True, translate=True)
    description = fields.Text(translate=True)
    sequence = fields.Integer(default=1)
    project_ids = fields.Many2many(
        'project.project',
        'user_story_type_rel',
        'type_id', 'project_id', string='Projects',
        default=_get_default_project_ids)
    legend_priority = fields.Char(
        string='Priority Management Explanation', translate=True,
        help='Explanation text to help users using the star and priority '
             'mechanism on stages or issues that are in this stage.')
    legend_blocked = fields.Char(
        string='Kanban Blocked Explanation', translate=True,
        help='Override the default value displayed for the blocked state '
             'for kanban selection, when the task or issue is in that stage.')
    legend_done = fields.Char(
        string='Kanban Valid Explanation', translate=True,
        help='Override the default value displayed for the done state for '
             'kanban selection, when the task or issue is in that stage.')
    legend_normal = fields.Char(
        string='Kanban Ongoing Explanation', translate=True,
        help='Override the default value displayed for the normal state for '
             'kanban selection, when the task or issue is in that stage.')
    mail_template_id = fields.Many2one(
        'mail.template',
        string='Email Template',
        domain=lambda self: self._get_mail_template_id_domain(),
        help="If set an email will be sent to the customer when the task or"
             " issue reaches this step.")
    fold = fields.Boolean(
        string='Folded in Kanban',
        help='This stage is folded in the kanban view when there are no '
             'records in that stage to display.')


class UserStory(models.Model):

    _inherit = 'user.story'
    _order = "priority desc, sequence, date, name, id"

    def _get_default_state(self):
        """ Gives default state """
        project_id = self.env.context.get('default_project_id')
        if not project_id:
            return False
        return self.stage_find(project_id, [('fold', '=', False)])

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        search_domain = [('id', 'in', stages.ids)]
        if 'default_project_id' in self.env.context:
            search_domain = ['|', ('project_ids', '=', self.env.context['default_project_id'])] + search_domain

        stage_ids = stages._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)


    sequence = fields.Integer('Sequence', select=True, help="Gives the sequence order when displaying a list of tasks.")
    state = fields.Many2one(
        'user.story.type',
        string='Stage',
        track_visibility='onchange',
        index=True,
        default=_get_default_state,
        group_expand='_read_group_states',
        copy=False,
    )
    help = fields.Boolean(
        default='False',
    )
    kanban_state = fields.Selection([
            ('normal', 'In Progress'),
            ('done', 'Ready for next stage'),
            ('blocked', 'Blocked')
        ], string='Kanban State',
        default='normal',
        track_visibility='onchange',
        required=True, copy=False,
        help="A task's kanban state indicates special situations affecting it:\n"
             " * Normal is the default situation\n"
             " * Blocked indicates something is preventing the progress of this task\n"
             " * Ready for next stage indicates the task is ready to be pulled to the next stage"
    )

    def stage_find(self, section_id, domain=[], order='sequence'):
        """ Override of the base.stage method
            Parameter of the stage search taken from the lead:
            - section_id: if set, sta
            ges must belong to this section or
              be a default stage; if not set, stages must be default
              stages
        """
        # collect all section_ids
        section_ids = []
        if section_id:
            section_ids.append(section_id)
        section_ids.extend(self.mapped('project_id').ids)
        search_domain = []
        if section_ids:
            search_domain = [('|')] * (len(section_ids) - 1)
            for section_id in section_ids:
                search_domain.append(('project_ids', '=', section_id))
        search_domain += list(domain)
        # perform search, return the first found
        return self.env['project.task.type'].search(search_domain, order=order, limit=1).id


    @api.onchange('project_id')
    def _onchange_project(self):
        if self.project_id:
            self.partner_id = self.project_id.partner_id
            self.state = self.stage_find(self.project_id.id, [('fold', '=', False)])
        else:
            self.state = False

    @api.multi
    def write(self, vals):
        now = fields.Datetime.now()
        # stage change: update date_last_stage_update
        if 'state' in vals:
            vals['date_last_stage_update'] = now
            # reset kanban state when changing stage
            if 'kanban_state' not in vals:
                vals['kanban_state'] = 'normal'
        # user_id change: update date_assign
        if vals.get('user_id'):
            vals['date_assign'] = now

        result = super(UserStory, self).write(vals)

        return result

    # ---------------------------------------------------
    # Mail gateway
    # ---------------------------------------------------

    @api.multi
    def _track_template(self, tracking):
        res = super(UserStory, self)._track_template(tracking)
        test_task = self[0]
        changes, tracking_value_ids = tracking[test_task.id]
        if 'state' in changes and test_task.state.mail_template_id:
            res['state'] = (test_task.state.mail_template_id, {'composition_mode': 'mass_mail'})
        return res

    @api.multi
    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'kanban_state' in init_values and self.kanban_state == 'blocked':
            return 'project.mt_task_blocked'
        elif 'kanban_state' in init_values and self.kanban_state == 'done':
            return 'project.mt_task_ready'
        elif 'user_id' in init_values and self.user_id:  # assigned -> new
            return 'project.mt_task_new'
        elif 'state' in init_values and self.state and self.state.sequence <= 1:  # start stage -> new
            return 'project.mt_task_new'
        elif 'state' in init_values:
            return 'project.mt_task_stage'
        return super(UserStory, self)._track_subtype(init_values)

    color = fields.Integer(string='Color Index')
    priority = fields.Integer(
        string=u'Sequence', related='priority_level.sequence', store=True)   



